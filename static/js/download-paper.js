// Lazy Download + Zip client for question-papers (vanilla JS)
// Exposes: window.DownloadPaper.handleClick(event, button)

(function () {
	// Utility: get status element
	function setStatus(msg, level = "info") {
		const el = document.getElementById("download-status");
		if (!el) return;
		el.textContent = msg;
		el.dataset.status = level;
	}

	// Simple script loader (idempotent)
	const _scriptCache = {};
	function loadScript(url) {
		if (_scriptCache[url]) return _scriptCache[url];
		_scriptCache[url] = new Promise((resolve, reject) => {
			const s = document.createElement("script");
			s.src = url;
			s.async = true;
			s.onload = () => resolve();
			s.onerror = (e) => reject(new Error("Failed to load " + url));
			document.head.appendChild(s);
		});
		return _scriptCache[url];
	}

	// Match exam rule
	function matchesExam(name, type) {
		name = name.toLowerCase();
		if (type === "insem") return name.startsWith("insem");
		if (type === "endsem") return name.startsWith("endsem") || name.startsWith("other");
		return name.endsWith(".pdf"); // all PDFs
	}

	// Extract subject_link from path /question-papers/{subject_link}
	function getSubjectLinkFromPath() {
		const parts = location.pathname.split("/").filter(Boolean);
		const idx = parts.indexOf("question-papers");
		if (idx >= 0 && parts.length > idx + 1) return parts[idx + 1];
		return null;
	}

	// Fetch JSON with basic error handling
	async function safeFetchJson(url) {
		const resp = await fetch(url);
		if (!resp.ok) {
			const text = await resp.text().catch(()=>"");
			const err = new Error(`HTTP ${resp.status} - ${text}`);
			err.status = resp.status;
			throw err;
		}
		return resp.json();
	}

	// Main handler
	async function handleClick(event, button) {
		try {
			event && event.preventDefault && event.preventDefault();

			const examType = (button && button.dataset && button.dataset.download) || (event && event.target && event.target.dataset && event.target.dataset.download);
			if (!examType) {
				setStatus("Invalid download type.", "error");
				return;
			}

			const buttons = document.querySelectorAll('button[data-download]');
			buttons.forEach(b => b.disabled = true);

			setStatus("Resolving subject metadata...", "info");

			const subject_link = getSubjectLinkFromPath();
			if (!subject_link) {
				setStatus("Invalid subject URL. Cannot determine subject.", "error");
				buttons.forEach(b => b.disabled = false);
				return;
			}

			let list;
			try {
				list = await safeFetchJson("/api/question-papers/list");
			} catch (err) {
				setStatus("Failed to fetch metadata. Please try again.", "error");
				buttons.forEach(b => b.disabled = false);
				return;
			}

			const meta = Array.isArray(list) && list.find(x => x.subject_link === subject_link);
			if (!meta) {
				setStatus("Subject not found in metadata.", "error");
				buttons.forEach(b => b.disabled = false);
				return;
			}

			const repoPath = meta.repo_path;
			const subjectName = meta.subject_name || subject_link;

			setStatus("Querying GitHub for files...", "info");

			const ghApiUrl = `https://api.github.com/repos/AlbatrossC/sppu-codes/contents/${encodeURIComponent(repoPath)}?ref=question-papers`;

			let ghList;
			try {
				const resp = await fetch(ghApiUrl);
				if (resp.status === 403) {
					const remaining = resp.headers.get("X-RateLimit-Remaining");
					if (remaining === "0") {
						setStatus("GitHub API rate limit exceeded. Please wait and try again later.", "error");
						buttons.forEach(b => b.disabled = false);
						return;
					}
					setStatus("Access denied by GitHub API. Try again later.", "error");
					buttons.forEach(b => b.disabled = false);
					return;
				}
				if (!resp.ok) {
					setStatus(`GitHub API error: ${resp.status}`, "error");
					buttons.forEach(b => b.disabled = false);
					return;
				}
				ghList = await resp.json();
			} catch (err) {
				setStatus("Network error while contacting GitHub. Check your connection.", "error");
				buttons.forEach(b => b.disabled = false);
				return;
			}

			if (!Array.isArray(ghList)) {
				setStatus("Unexpected GitHub response.", "error");
				buttons.forEach(b => b.disabled = false);
				return;
			}

			const pdfItems = ghList
				.filter(item => item.type === "file" && item.name.toLowerCase().endsWith(".pdf"))
				.filter(item => {
					if (examType === "all") return true;
					return matchesExam(item.name, examType);
				})
				.map(i => ({ name: i.name, download_url: i.download_url }));

			if (!pdfItems.length) {
				setStatus("No matching PDF files found for selected exam type.", "error");
				buttons.forEach(b => b.disabled = false);
				return;
			}

			setStatus(`Found ${pdfItems.length} PDF(s). Preparing download...`, "info");

			const jszipUrl = "https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js";
			const filesaverUrl = "https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js";
			setStatus("Loading ZIP libraries...", "info");
			try {
				await loadScript(jszipUrl);
				await loadScript(filesaverUrl);
			} catch (err) {
				setStatus("Failed to load ZIP libraries. Please try again.", "error");
				buttons.forEach(b => b.disabled = false);
				return;
			}
			if (typeof JSZip === "undefined" || typeof saveAs === "undefined") {
				setStatus("ZIP libraries unavailable after load.", "error");
				buttons.forEach(b => b.disabled = false);
				return;
			}

			const zip = new JSZip();

			const concurrency = 3;
			let idx = 0;
			let downloaded = 0;
			let failed = 0;

			setStatus(`Downloading files (0/${pdfItems.length})...`, "info");

			async function worker() {
				while (true) {
					let current;
					if (idx >= pdfItems.length) break;
					current = pdfItems[idx++];
					try {
						const r = await fetch(current.download_url);
						if (!r.ok) throw new Error(`Failed ${r.status}`);
						const ab = await r.arrayBuffer();
						zip.file(current.name, ab);
						downloaded++;
						setStatus(`Downloading files (${downloaded}/${pdfItems.length})...`, "info");
					} catch (e) {
						console.error("Download error", current.name, e);
						failed++;
						setStatus(`Some files failed to download. (${failed} failed)`, "warning");
					}
				}
			}

			const workers = [];
			for (let i = 0; i < Math.min(concurrency, pdfItems.length); i++) workers.push(worker());
			await Promise.all(workers);

			if (downloaded === 0) {
				setStatus("All downloads failed. Aborting.", "error");
				buttons.forEach(b => b.disabled = false);
				return;
			}

			setStatus("Creating ZIP file...", "info");
			try {
				const blob = await zip.generateAsync({ type: "blob" }, meta => {
					const pct = Math.round((meta.percent || 0));
					setStatus(`Creating ZIP: ${pct}%`, "info");
				});
				const safeExam = examType.toLowerCase();
				const zipName = `${subjectName.replace(/\s+/g, "_")}-${safeExam}.zip`;
				saveAs(blob, zipName);
				setStatus("Download started. Thank you!", "success");

				// --- NEW: send optional server-side Discord notification (no URLs included) ---
				(function fireNotify() {
					try {
						const notifyPayload = {
							subject_link: subject_link,
							subject_name: subjectName,
							exam_type: examType,
							file_count: downloaded,
							success: true
						};
						// fire-and-forget; don't block UX
						fetch('/api/notify-download', {
							method: 'POST',
							headers: { 'Content-Type': 'application/json' },
							body: JSON.stringify(notifyPayload)
						}).catch(function(e){ console.warn('notify-download failed', e); });
					} catch (e) {
						console.warn('notify-download error', e);
					}
				})();
				// --- END notify ---
			} catch (err) {
				console.error(err);
				setStatus("Failed to create ZIP file.", "error");
			} finally {
				buttons.forEach(b => b.disabled = false);
			}
		} catch (err) {
			console.error(err);
			setStatus("Unexpected error occurred. See console.", "error");
			const buttons = document.querySelectorAll('button[data-download]');
			buttons.forEach(b => b.disabled = false);
		}
	}

	// expose public API
	window.DownloadPaper = {
		handleClick
	};
})();
