// Cached DOM elements
const DOM = {
    pdfContainer: document.getElementById('pdf-container'),
    subjectDisplay: document.getElementById('subject-display'),
    pdfCount: document.getElementById('pdf-count'),
    examType: document.getElementById('exam-type'),
    fullscreenBtn: document.getElementById('fullscreen-btn'),
    backBtn: document.getElementById('back-btn')
};

// Global state with cache
const state = {
    pdfPath: new URLSearchParams(window.location.search).get('pdf'),
    pdfFiles: [],
    isRendering: false,
    cache: new Map() // Added cache for rendered PDFs
};

// Utility functions
const debounce = (func, wait) => {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
};

// Lazy load observer
const lazyLoadObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const iframe = entry.target.querySelector('iframe[data-src]');
            if (iframe && !iframe.src) {
                iframe.src = iframe.dataset.src;
                observer.unobserve(entry.target);
            }
        }
    });
}, { rootMargin: '200px' });

// Fetch PDF files with caching
async function fetchPDFFiles() {
    try {
        if (state.cache.has(state.pdfPath)) {
            state.pdfFiles = state.cache.get(state.pdfPath);
            renderPDFs();
            return;
        }

        DOM.pdfContainer.innerHTML = '<div class="no-pdf-message">Loading PDFs... <div class="loader"></div></div>';
        
        const response = await fetch(`/api/directories?path=${encodeURIComponent(state.pdfPath)}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const files = await response.json();
        state.pdfFiles = files
            .filter(file => file.toLowerCase().endsWith('.pdf'))
            .map(file => ({
                date: file.replace('.pdf', ''),
                link: `/static/pyqs/${state.pdfPath}/${file}`
            }));
        
        state.cache.set(state.pdfPath, state.pdfFiles);
        
        if (!state.pdfFiles.length) {
            DOM.pdfContainer.innerHTML = '<div class="no-pdf-message">No PDFs found in this directory.</div>';
            return;
        }
        
        renderPDFs();
    } catch (error) {
        DOM.pdfContainer.innerHTML = `<div class="no-pdf-message">Failed to load PDFs: ${error.message}</div>`;
    }
}

// Set subject display
function setSubjectDisplay() {
    DOM.subjectDisplay.textContent = state.pdfPath ? state.pdfPath.split('/').pop() : 'No Subject Selected';
}

// Filter PDFs (memoized)
const filterPDFs = ((cache = new Map()) => {
    return (examType) => {
        const key = examType.toLowerCase();
        if (cache.has(key)) return cache.get(key);
        
        const result = state.pdfFiles.filter(file => file.date.toLowerCase().includes(key));
        cache.set(key, result);
        return result;
    };
})();

// Optimized render PDFs
function renderPDFs() {
    if (state.isRendering) return;
    state.isRendering = true;

    requestAnimationFrame(() => {
        const count = parseInt(DOM.pdfCount.value);
        const examType = DOM.examType.value;
        const filteredData = filterPDFs(examType);
        
        DOM.pdfContainer.className = `grid-${count}`;
        DOM.pdfContainer.innerHTML = filteredData.length ? '' : '<div class="no-pdf-message">No question papers available.</div>';
        
        if (!filteredData.length) {
            state.isRendering = false;
            return;
        }

        const fragment = document.createDocumentFragment();
        const maxRender = Math.min(count, filteredData.length);
        
        for (let i = 0; i < count; i++) {
            const div = document.createElement('div');
            div.className = 'pdf-viewer';

            if (i < maxRender) {
                const loaderContainer = document.createElement('div');
                loaderContainer.className = 'loader-container';
                loaderContainer.innerHTML = '<div class="loader"></div>';
                div.appendChild(loaderContainer);
                
                div.appendChild(createDateSelector(filteredData, i));
                
                const iframe = document.createElement('iframe');
                iframe.dataset.src = `/static/pdfjs/web/viewer.html?file=${encodeURIComponent(filteredData[i].link)}`;
                iframe.style.width = '100%';
                iframe.style.height = '100%';
                iframe.style.border = 'none';
                iframe.onload = () => loaderContainer.remove();
                div.appendChild(iframe);
                
                lazyLoadObserver.observe(div);
            } else {
                div.innerHTML = '<div class="no-more-papers">No more Question Papers available</div>';
            }

            fragment.appendChild(div);
        }

        DOM.pdfContainer.appendChild(fragment);
        state.isRendering = false;
    });
}

// Create date selector with caching
function createDateSelector(data, initialIndex) {
    const div = document.createElement('div');
    div.className = 'date-selector';
    const select = document.createElement('select');

    data.forEach((item, index) => {
        select.appendChild(new Option(item.date, index));
    });

    select.value = initialIndex;
    
    select.addEventListener('change', debounce((event) => {
        const selectedIndex = parseInt(event.target.value);
        const pdfUrl = data[selectedIndex].link;
        const pdfViewer = div.closest('.pdf-viewer');
        
        const loaderContainer = document.createElement('div');
        loaderContainer.className = 'loader-container';
        loaderContainer.innerHTML = '<div class="loader"></div>';
        pdfViewer.appendChild(loaderContainer);
        
        const iframe = pdfViewer.querySelector('iframe');
        if (iframe) {
            iframe.onload = () => loaderContainer.remove();
            iframe.src = `/static/pdfjs/web/viewer.html?file=${encodeURIComponent(pdfUrl)}`;
        }
    }, 100));
    
    div.appendChild(select);
    return div;
}

// Toggle fullscreen
function toggleFullscreen() {
    document.fullscreenElement ? 
        document.exitFullscreen() : 
        document.documentElement.requestFullscreen();
}

// Update fullscreen button
function updateFullscreenButton() {
    DOM.fullscreenBtn.innerHTML = document.fullscreenElement ? 
        `<svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 14h6m0 0v6m0-6l-7 7m17-11h-6m0 0V4m0 6l7-7"/>
        </svg> Exit Fullscreen` :
        `<svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/>
        </svg> Fullscreen`;
}

// Event listeners
function setupEventListeners() {
    const debouncedRender = debounce(renderPDFs, 100); // Reduced debounce time
    
    DOM.pdfCount.addEventListener('change', debouncedRender);
    DOM.examType.addEventListener('change', debouncedRender);
    DOM.fullscreenBtn.addEventListener('click', toggleFullscreen);
    DOM.backBtn.addEventListener('click', () => window.location.href = '/questionpapers');
    document.addEventListener('fullscreenchange', updateFullscreenButton);
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && document.fullscreenElement) document.exitFullscreen();
    });
}

// Initialize
function init() {
    setSubjectDisplay();
    setupEventListeners();
    
    state.pdfPath ? 
        fetchPDFFiles() : 
        DOM.pdfContainer.innerHTML = '<div class="no-pdf-message">No PDF path provided. Please select a subject.</div>';
}

document.addEventListener('DOMContentLoaded', init);

// Cleanup on unload
window.addEventListener('unload', () => {
    lazyLoadObserver.disconnect();
});