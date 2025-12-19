// =============================================================================
// Google Tag Manager + Fonts (Deferred)
// =============================================================================
(function () {
    function loadGTM() {
        const script = document.createElement('script');
        script.src = 'https://www.googletagmanager.com/gtag/js?id=G-1R5FFVKTF8';
        script.async = true;

        script.onload = function () {
            window.dataLayer = window.dataLayer || [];
            function gtag() { window.dataLayer.push(arguments); }
            gtag('js', new Date());
            gtag('config', 'G-1R5FFVKTF8');
        };

        document.head.appendChild(script);
    }

    function loadGoogleFonts() {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://fonts.googleapis.com/css2?family=Fira+Code&display=swap';
        document.head.appendChild(link);
    }

    setTimeout(loadGTM, 3000);
    document.addEventListener('DOMContentLoaded', loadGoogleFonts);
})();

// =============================================================================
// Modal Backdrop
// =============================================================================
const backdrop = document.createElement('div');
backdrop.className = 'modal-backdrop';
document.body.appendChild(backdrop);

// =============================================================================
// Answer Cache (subject-question-fileIndex)
// =============================================================================
const answerCache = new Map();

// =============================================================================
// Load Answer (API-driven)
// =============================================================================
async function loadAnswer(subject, questionNo, title, button, fileName, fileIndex) {
    const cacheKey = `${subject}-${questionNo}-${fileIndex}`;

    const questionItem = button.closest('.question-item');
    if (!questionItem) return;

    const answerBox = questionItem.querySelector('.answer-box');
    if (!answerBox) return;

    const questionTitle = answerBox.querySelector('h3');
    const codeContent = answerBox.querySelector('pre');

    // Show modal
    answerBox.style.display = 'block';
    backdrop.style.display = 'block';
    document.body.style.overflow = 'hidden';

    questionTitle.textContent = title;
    codeContent.textContent = 'Loading...';
    button.disabled = true;

    // Serve from cache
    if (answerCache.has(cacheKey)) {
        codeContent.textContent = answerCache.get(cacheKey);
        button.disabled = false;
        return;
    }

    try {
        const response = await fetch(
            `/api/${subject}/${questionNo}?no_question=1&split=${fileIndex}`
        );

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const text = await response.text();
        codeContent.textContent = text.trim();
        answerCache.set(cacheKey, text.trim());

    } catch (err) {
        console.error('Answer load error:', err);
        codeContent.textContent = 'Failed to load answer.';
        alert('Failed to load answer. Please try again.');
    } finally {
        button.disabled = false;
    }
}

// =============================================================================
// Copy Code
// =============================================================================
function copyCode(elementId) {
    const codeElement = document.getElementById(elementId);
    if (!codeElement) return;

    const text = codeElement.innerText;
    const btn = codeElement.closest('.answer-box').querySelector('.copy-btn');

    navigator.clipboard.writeText(text).then(() => {
        btn.textContent = 'Copied!';
        btn.classList.add('copied');

        setTimeout(() => {
            btn.textContent = 'Copy Code';
            btn.classList.remove('copied');
        }, 3000);
    }).catch(() => {
        alert('Copy failed. Please copy manually.');
    });
}

// =============================================================================
// Close Modal
// =============================================================================
function closeBox(boxId) {
    const box = document.getElementById(boxId);
    if (!box) return;

    box.style.display = 'none';
    backdrop.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// =============================================================================
// Global Escape + Backdrop Click
// =============================================================================
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.answer-box[style*="display: block"]');
        if (openModal) closeBox(openModal.id);
    }
});

backdrop.addEventListener('click', () => {
    const openModal = document.querySelector('.answer-box[style*="display: block"]');
    if (openModal) closeBox(openModal.id);
});
