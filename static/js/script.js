// =============================================================================
// Configuration & Constants
// =============================================================================
const CONFIG = {
    GTM_DELAY: 3000,
    COPY_FEEDBACK_DURATION: 3000,
    CACHE_ENABLED: true,
    LOG_LEVEL: 'info' // 'debug', 'info', 'warn', 'error'
};

// =============================================================================
// Logger Utility
// =============================================================================
const Logger = {
    levels: { debug: 0, info: 1, warn: 2, error: 3 },
    currentLevel: CONFIG.LOG_LEVEL,
    
    _shouldLog(level) {
        return this.levels[level] >= this.levels[this.currentLevel];
    },
    
    debug(message, ...args) {
        if (this._shouldLog('debug')) {
            console.debug(`[DEBUG] ${message}`, ...args);
        }
    },
    
    info(message, ...args) {
        if (this._shouldLog('info')) {
            console.info(`[INFO] ${message}`, ...args);
        }
    },
    
    warn(message, ...args) {
        if (this._shouldLog('warn')) {
            console.warn(`[WARN] ${message}`, ...args);
        }
    },
    
    error(message, ...args) {
        if (this._shouldLog('error')) {
            console.error(`[ERROR] ${message}`, ...args);
        }
    },
    
    group(label) {
        if (this._shouldLog('debug')) {
            console.group(label);
        }
    },
    
    groupEnd() {
        if (this._shouldLog('debug')) {
            console.groupEnd();
        }
    }
};

// =============================================================================
// Google Tag Manager + Fonts (Deferred Loading)
// =============================================================================
(function initializeExternalResources() {
    Logger.info('Initializing external resources');
    
    function loadGTM() {
        Logger.debug('Loading Google Tag Manager');
        const script = document.createElement('script');
        script.src = 'https://www.googletagmanager.com/gtag/js?id=G-1R5FFVKTF8';
        script.async = true;

        script.onload = function() {
            window.dataLayer = window.dataLayer || [];
            function gtag() { window.dataLayer.push(arguments); }
            gtag('js', new Date());
            gtag('config', 'G-1R5FFVKTF8');
            Logger.info('Google Tag Manager loaded successfully');
        };

        script.onerror = function() {
            Logger.error('Failed to load Google Tag Manager');
        };

        document.head.appendChild(script);
    }

    function loadGoogleFonts() {
        Logger.debug('Loading Google Fonts');
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://fonts.googleapis.com/css2?family=Fira+Code&display=swap';
        
        link.onload = function() {
            Logger.info('Google Fonts loaded successfully');
        };
        
        link.onerror = function() {
            Logger.warn('Failed to load Google Fonts');
        };
        
        document.head.appendChild(link);
    }

    setTimeout(loadGTM, CONFIG.GTM_DELAY);
    document.addEventListener('DOMContentLoaded', loadGoogleFonts);
})();

// =============================================================================
// Modal Backdrop Creation
// =============================================================================
(function createModalBackdrop() {
    Logger.debug('Creating modal backdrop');
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop';
    backdrop.setAttribute('role', 'presentation');
    backdrop.setAttribute('aria-hidden', 'true');
    document.body.appendChild(backdrop);
    Logger.info('Modal backdrop created');
})();

// =============================================================================
// Answer Cache Management
// =============================================================================
const AnswerCache = {
    _cache: new Map(),
    _stats: {
        hits: 0,
        misses: 0,
        total: 0
    },
    
    generateKey(subject, questionNo, fileIndex) {
        return `${subject}-${questionNo}-${fileIndex}`;
    },
    
    has(key) {
        return this._cache.has(key);
    },
    
    get(key) {
        this._stats.total++;
        if (this._cache.has(key)) {
            this._stats.hits++;
            Logger.debug(`Cache HIT for key: ${key}`);
            return this._cache.get(key);
        }
        this._stats.misses++;
        Logger.debug(`Cache MISS for key: ${key}`);
        return null;
    },
    
    set(key, value) {
        this._cache.set(key, value);
        Logger.debug(`Cache SET for key: ${key}, size: ${value.length} chars`);
    },
    
    clear() {
        const size = this._cache.size;
        this._cache.clear();
        Logger.info(`Cache cleared, removed ${size} entries`);
    },
    
    getStats() {
        return {
            ...this._stats,
            hitRate: this._stats.total > 0 
                ? (this._stats.hits / this._stats.total * 100).toFixed(2) + '%'
                : '0%',
            size: this._cache.size
        };
    },
    
    logStats() {
        const stats = this.getStats();
        Logger.group('Cache Statistics');
        Logger.info(`Total requests: ${stats.total}`);
        Logger.info(`Cache hits: ${stats.hits}`);
        Logger.info(`Cache misses: ${stats.misses}`);
        Logger.info(`Hit rate: ${stats.hitRate}`);
        Logger.info(`Cache size: ${stats.size} entries`);
        Logger.groupEnd();
    }
};

// =============================================================================
// Modal Management
// =============================================================================
const ModalManager = {
    _activeModal: null,
    _backdrop: null,
    
    init() {
        this._backdrop = document.querySelector('.modal-backdrop');
        Logger.debug('Modal manager initialized');
    },
    
    show(answerBox) {
        if (!answerBox) {
            Logger.error('Cannot show modal: answerBox is null or undefined');
            return false;
        }
        
        this._activeModal = answerBox;
        answerBox.style.display = 'block';
        answerBox.setAttribute('aria-hidden', 'false');
        
        if (this._backdrop) {
            this._backdrop.style.display = 'block';
            this._backdrop.setAttribute('aria-hidden', 'false');
        }
        
        document.body.style.overflow = 'hidden';
        Logger.info(`Modal opened: ${answerBox.id}`);
        return true;
    },
    
    hide(answerBox) {
        if (!answerBox) {
            Logger.error('Cannot hide modal: answerBox is null or undefined');
            return false;
        }
        
        answerBox.style.display = 'none';
        answerBox.setAttribute('aria-hidden', 'true');
        
        if (this._backdrop) {
            this._backdrop.style.display = 'none';
            this._backdrop.setAttribute('aria-hidden', 'true');
        }
        
        document.body.style.overflow = 'auto';
        this._activeModal = null;
        Logger.info(`Modal closed: ${answerBox.id}`);
        return true;
    },
    
    hideActive() {
        if (this._activeModal) {
            this.hide(this._activeModal);
        }
    }
};

// Initialize modal manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    ModalManager.init();
});

// =============================================================================
// Load Answer Function (API-driven with enhanced error handling)
// =============================================================================
async function loadAnswer(subject, questionNo, title, button, fileName, fileIndex) {
    Logger.group(`Loading Answer`);
    Logger.info(`Subject: ${subject}, Question: ${questionNo}, File: ${fileName}, Index: ${fileIndex}`);
    
    const startTime = performance.now();
    const cacheKey = AnswerCache.generateKey(subject, questionNo, fileIndex);

    // Find the question item and answer box
    const questionItem = button.closest('.question-item');
    if (!questionItem) {
        Logger.error('Question item not found in DOM');
        Logger.groupEnd();
        return;
    }

    const answerBox = questionItem.querySelector('.answer-box');
    if (!answerBox) {
        Logger.error('Answer box not found in question item');
        Logger.groupEnd();
        return;
    }

    const questionTitle = answerBox.querySelector('h3');
    const codeContent = answerBox.querySelector('pre');

    if (!questionTitle || !codeContent) {
        Logger.error('Question title or code content element not found');
        Logger.groupEnd();
        return;
    }

    // Show modal
    ModalManager.show(answerBox);

    // Set title and loading state
    questionTitle.textContent = title;
    codeContent.textContent = 'Loading...';
    codeContent.classList.add('loading');
    button.disabled = true;
    Logger.debug('Button disabled, loading state set');

    // Check cache first
    if (CONFIG.CACHE_ENABLED && AnswerCache.has(cacheKey)) {
        const cachedContent = AnswerCache.get(cacheKey);
        codeContent.textContent = cachedContent;
        codeContent.classList.remove('loading');
        button.disabled = false;
        
        const loadTime = (performance.now() - startTime).toFixed(2);
        Logger.info(`Answer loaded from cache in ${loadTime}ms`);
        Logger.groupEnd();
        return;
    }

    // Fetch from API
    const apiUrl = `/api/${subject}/${questionNo}?no_question=1&split=${fileIndex}`;
    Logger.debug(`Fetching from API: ${apiUrl}`);

    try {
        const response = await fetch(apiUrl);
        
        Logger.debug(`Response status: ${response.status} ${response.statusText}`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const text = await response.text();
        const trimmedText = text.trim();
        
        Logger.debug(`Response received: ${trimmedText.length} characters`);

        codeContent.textContent = trimmedText;
        codeContent.classList.remove('loading');
        
        // Cache the result
        if (CONFIG.CACHE_ENABLED) {
            AnswerCache.set(cacheKey, trimmedText);
        }

        const loadTime = (performance.now() - startTime).toFixed(2);
        Logger.info(`Answer loaded successfully in ${loadTime}ms`);

    } catch (error) {
        Logger.error('Failed to load answer', error);
        codeContent.textContent = `Error: Failed to load answer.\n\nDetails: ${error.message}\n\nPlease try again or check the GitHub repository.`;
        codeContent.classList.remove('loading');
        codeContent.classList.add('error');
        
        // Show user-friendly alert
        alert(`Failed to load answer: ${error.message}\n\nPlease try again or visit the GitHub repository.`);
    } finally {
        button.disabled = false;
        Logger.debug('Button re-enabled');
        Logger.groupEnd();
    }
}

// =============================================================================
// Copy Code Function (Enhanced with better feedback)
// =============================================================================
function copyCode(elementId) {
    Logger.group('Copy Code');
    Logger.info(`Copying content from element: ${elementId}`);
    
    const codeElement = document.getElementById(elementId);
    if (!codeElement) {
        Logger.error(`Element not found: ${elementId}`);
        Logger.groupEnd();
        return;
    }

    const text = codeElement.innerText;
    const answerBox = codeElement.closest('.answer-box');
    
    if (!answerBox) {
        Logger.error('Answer box not found for copy button');
        Logger.groupEnd();
        return;
    }
    
    const btn = answerBox.querySelector('.copy-btn');
    
    if (!btn) {
        Logger.error('Copy button not found');
        Logger.groupEnd();
        return;
    }

    Logger.debug(`Text length: ${text.length} characters`);

    // Use modern clipboard API
    navigator.clipboard.writeText(text)
        .then(() => {
            Logger.info('Text copied to clipboard successfully');
            
            // Update button state
            const originalText = btn.textContent;
            btn.textContent = 'Copied!';
            btn.classList.add('copied');
            btn.disabled = true;

            // Reset button after delay
            setTimeout(() => {
                btn.textContent = originalText;
                btn.classList.remove('copied');
                btn.disabled = false;
                Logger.debug('Copy button state reset');
            }, CONFIG.COPY_FEEDBACK_DURATION);
        })
        .catch((error) => {
            Logger.error('Failed to copy text to clipboard', error);
            
            // Fallback: show manual copy instruction
            alert('Copy failed. Please select the text manually and press Ctrl+C (or Cmd+C on Mac).');
            
            // Try to select the text for manual copying
            try {
                const range = document.createRange();
                range.selectNodeContents(codeElement);
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
                Logger.info('Text selected for manual copying');
            } catch (selectError) {
                Logger.error('Failed to select text', selectError);
            }
        })
        .finally(() => {
            Logger.groupEnd();
        });
}

// =============================================================================
// Close Modal Function (Enhanced)
// =============================================================================
function closeBox(boxId) {
    Logger.info(`Closing modal: ${boxId}`);
    
    const box = document.getElementById(boxId);
    if (!box) {
        Logger.error(`Modal not found: ${boxId}`);
        return;
    }

    ModalManager.hide(box);
}

// =============================================================================
// Global Event Listeners
// =============================================================================
(function setupGlobalListeners() {
    Logger.debug('Setting up global event listeners');
    
    // Escape key handler
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            Logger.debug('Escape key pressed');
            ModalManager.hideActive();
        }
    });

    // Backdrop click handler
    document.addEventListener('click', (event) => {
        if (event.target.classList.contains('modal-backdrop')) {
            Logger.debug('Backdrop clicked');
            ModalManager.hideActive();
        }
    });
    
    Logger.info('Global event listeners set up successfully');
})();

// =============================================================================
// Performance Monitoring (Development)
// =============================================================================
if (window.performance && window.performance.timing) {
    window.addEventListener('load', () => {
        setTimeout(() => {
            const perfData = window.performance.timing;
            const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
            const domReadyTime = perfData.domContentLoadedEventEnd - perfData.navigationStart;
            
            Logger.group('Performance Metrics');
            Logger.info(`Page load time: ${pageLoadTime}ms`);
            Logger.info(`DOM ready time: ${domReadyTime}ms`);
            Logger.groupEnd();
        }, 0);
    });
}

// =============================================================================
// Expose utilities to window for debugging
// =============================================================================
if (CONFIG.LOG_LEVEL === 'debug') {
    window.AnswerCache = AnswerCache;
    window.ModalManager = ModalManager;
    window.Logger = Logger;
    Logger.info('Debug utilities exposed to window object');
}

// =============================================================================
// Service initialization log
// =============================================================================
Logger.info('Script initialized successfully');
Logger.info(`Cache enabled: ${CONFIG.CACHE_ENABLED}`);
Logger.info(`Log level: ${CONFIG.LOG_LEVEL}`);