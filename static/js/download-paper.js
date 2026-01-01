// Lazy Download + Zip client for question-papers (vanilla JS)
// Exposes: window.DownloadPaper.handleClick(event, button)

(function () {
	// Utility: get status element and update progress
	function setStatus(msg, level = "info", progress = null) {
		const statusEl = document.getElementById("download-status");
		const containerEl = document.getElementById("download-status-container");
		const progressFillEl = document.getElementById("download-progress-fill");
		const percentageEl = document.getElementById("download-percentage");
		
		if (!statusEl || !containerEl) return;
		
		// Show container if hidden
		if (containerEl.style.display === "none") {
			containerEl.style.display = "flex";
		}
		
		// Update status text
		statusEl.textContent = msg;
		statusEl.dataset.status = level;
		
		// Update progress bar
		if (progress !== null && progressFillEl) {
			const progressPercent = Math.min(Math.max(progress, 0), 100);
			progressFillEl.style.width = progressPercent + "%";
			progressFillEl.dataset.status = level;
			
			// Update percentage display
			if (percentageEl) {
				if (progressPercent > 0 && progressPercent < 100) {
					percentageEl.textContent = progressPercent + "%";
					percentageEl.style.display = "inline";
				} else {
					percentageEl.style.display = "none";
				}
			}
		}
	}
	
	// Reset status display
	function resetStatus() {
		const containerEl = document.getElementById("download-status-container");
		const progressFillEl = document.getElementById("download-progress-fill");
		const percentageEl = document.getElementById("download-percentage");
		
		if (containerEl) containerEl.style.display = "none";
		if (progressFillEl) {
			progressFillEl.style.width = "0%";
			delete progressFillEl.dataset.status;
		}
		if (percentageEl) {
			percentageEl.textContent = "";
			percentageEl.style.display = "none";
		}
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
				setStatus("Unable to determine download type. Please try again.", "error", 0);
				return;
			}

			const buttons = document.querySelectorAll('button[data-download]');
			buttons.forEach(b => b.disabled = true);

			// Reset status display
			resetStatus();
			setStatus("Preparing download...", "info", 5);

			const subject_link = getSubjectLinkFromPath();
			if (!subject_link) {
				setStatus("Could not identify the subject. Please refresh and try again.", "error", 0);
				buttons.forEach(b => b.disabled = false);
				return;
			}

			setStatus("Fetching subject information...", "info", 10);

			let list;
			try {
				list = await safeFetchJson("/api/question-papers/list");
			} catch (err) {
				setStatus("Unable to connect to server. Please check your connection and try again.", "error", 0);
				buttons.forEach(b => b.disabled = false);
				return;
			}

			const meta = Array.isArray(list) && list.find(x => x.subject_link === subject_link);
			if (!meta) {
				setStatus("Subject information not found. Please contact support if this persists.", "error", 0);
				buttons.forEach(b => b.disabled = false);
				return;
			}

			const repoPath = meta.repo_path;
			const subjectName = meta.subject_name || subject_link;

			setStatus("Searching for available papers...", "info", 20);

			const ghApiUrl = `https://api.github.com/repos/AlbatrossC/sppu-codes/contents/${encodeURIComponent(repoPath)}?ref=question-papers`;

			let ghList;
			try {
				const resp = await fetch(ghApiUrl);
				if (resp.status === 403) {
					const remaining = resp.headers.get("X-RateLimit-Remaining");
					if (remaining === "0") {
						setStatus("Service temporarily unavailable. Please wait a moment and try again.", "error", 0);
						buttons.forEach(b => b.disabled = false);
						return;
					}
					setStatus("Access temporarily restricted. Please try again in a few moments.", "error", 0);
					buttons.forEach(b => b.disabled = false);
					return;
				}
				if (!resp.ok) {
					setStatus("Unable to retrieve paper list. Please try again later.", "error", 0);
					buttons.forEach(b => b.disabled = false);
					return;
				}
				ghList = await resp.json();
			} catch (err) {
				setStatus("Connection error. Please check your internet connection and try again.", "error", 0);
				buttons.forEach(b => b.disabled = false);
				return;
			}

			if (!Array.isArray(ghList)) {
				setStatus("Unexpected response format. Please try again or contact support.", "error", 0);
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
				setStatus("No papers found for the selected exam type. Please try a different option.", "error", 0);
				buttons.forEach(b => b.disabled = false);
				return;
			}

			setStatus(`Found ${pdfItems.length} paper${pdfItems.length > 1 ? 's' : ''}. Getting ready...`, "info", 30);

			const jszipUrl = "https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js";
			const filesaverUrl = "https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js";
			setStatus("Loading required tools...", "info", 35);
			try {
				await loadScript(jszipUrl);
				await loadScript(filesaverUrl);
			} catch (err) {
				setStatus("Failed to initialize download tools. Please refresh and try again.", "error", 0);
				buttons.forEach(b => b.disabled = false);
				return;
			}
			if (typeof JSZip === "undefined" || typeof saveAs === "undefined") {
				setStatus("Download tools not available. Please refresh the page and try again.", "error", 0);
				buttons.forEach(b => b.disabled = false);
				return;
			}

			const zip = new JSZip();

			const concurrency = 3;
			let idx = 0;
			let downloaded = 0;
			let failed = 0;
			const totalFiles = pdfItems.length;
			const downloadStartProgress = 40;
			const downloadEndProgress = 85;

			setStatus(`Downloading ${totalFiles} paper${totalFiles > 1 ? 's' : ''}...`, "info", downloadStartProgress);

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
						
						// Calculate progress: download phase is 40% to 85%
						const downloadProgress = downloadStartProgress + 
							((downloaded / totalFiles) * (downloadEndProgress - downloadStartProgress));
						const progressPercent = Math.round(downloadProgress);
						
						if (failed === 0) {
							setStatus(`Downloaded ${downloaded} of ${totalFiles} paper${totalFiles > 1 ? 's' : ''}...`, "info", progressPercent);
						} else {
							setStatus(`Downloaded ${downloaded} of ${totalFiles} (${failed} failed)...`, "warning", progressPercent);
						}
					} catch (e) {
						console.error("Download error", current.name, e);
						failed++;
						const downloadProgress = downloadStartProgress + 
							((downloaded / totalFiles) * (downloadEndProgress - downloadStartProgress));
						setStatus(`Downloading... (${downloaded} downloaded, ${failed} failed)`, "warning", Math.round(downloadProgress));
					}
				}
			}

			const workers = [];
			for (let i = 0; i < Math.min(concurrency, pdfItems.length); i++) workers.push(worker());
			await Promise.all(workers);

			if (downloaded === 0) {
				setStatus("All downloads failed. Please check your connection and try again.", "error", 0);
				buttons.forEach(b => b.disabled = false);
				return;
			}

			setStatus("Creating ZIP archive...", "info", 85);
			try {
				const blob = await zip.generateAsync({ type: "blob" }, meta => {
					const pct = Math.round((meta.percent || 0));
					// ZIP creation phase is 85% to 95%
					const zipProgress = 85 + (pct * 0.1);
					setStatus(`Creating ZIP file... ${pct}%`, "info", Math.round(zipProgress));
				});
				const safeExam = examType.toLowerCase();
				const zipName = `${subjectName.replace(/\s+/g, "_")}-${safeExam}.zip`;
				saveAs(blob, zipName);
				setStatus("Download complete! Your ZIP file is ready.", "success", 100);
				
				// Hide status after 3 seconds on success
				setTimeout(() => {
					resetStatus();
				}, 3000);

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
				setStatus("Failed to create ZIP file. Please try again.", "error", 0);
			} finally {
				buttons.forEach(b => b.disabled = false);
			}
		} catch (err) {
			console.error(err);
			setStatus("An unexpected error occurred. Please try again or contact support if the issue persists.", "error", 0);
			const buttons = document.querySelectorAll('button[data-download]');
			buttons.forEach(b => b.disabled = false);
		}
	}

	// expose public API
	window.DownloadPaper = {
		handleClick
	};
})();
