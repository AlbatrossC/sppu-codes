'use strict';

class Tutorial {
  constructor() {
    this.steps = [
      {
        element: '.control-group:nth-child(2)',
        title: '<svg class="tutorial-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M2 12h20"/></svg> Exam Type',
        content: 'Switch between <strong>INSEM</strong> and <strong>ENDSEM</strong> papers with one click.',
        position: 'bottom',
        spotlightPadding: 8
      },
      {
        element: '.control-group:nth-child(1)',
        title: '<svg class="tutorial-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M3 12h18M3 18h18"/></svg> Layout View',
        content: 'Choose <strong>single</strong> or <strong>grid</strong> view to see 1-4 papers at once.',
        position: 'bottom',
        spotlightPadding: 8
      },
      {
        element: '.date-selector',
        title: '<svg class="tutorial-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 3v18M18 3v18M3 6h18M3 18h18"/></svg> Select Date',
        content: 'Pick a year to load that exam paper instantly.',
        position: 'right',
        elementFinder: () => document.querySelector('.date-selector'),
        spotlightPadding: 6
      },
      {
        element: '#fullscreen-btn',
        title: '<svg class="tutorial-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3h6v6H3zM15 3h6v6h-6zM3 15h6v6H3zM15 15h6v6h-6z"/></svg> Fullscreen',
        content: 'Expand to <strong>fullscreen</strong> for focused studying.',
        position: 'left',
        spotlightPadding: 6
      },
      {
        element: 'header',
        title: '<svg class="tutorial-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 13l4 4L19 7"/></svg> Ready to Go!',
        content: '<strong>View</strong>, <strong>compare</strong>, and <strong>customize</strong> your exam prep. Good luck!',
        position: 'bottom',
        spotlightPadding: 10
      }
    ];
    this.currentStep = 0;
    this.elements = {};
    this.isRunning = false;
  }

  initialize() {
    document.addEventListener('DOMContentLoaded', () => {
      if (localStorage.getItem('pdfViewerTutorialShown')) return;
      setTimeout(() => this.start(), 800);
    });
  }

  createElements() {
    this.elements.overlay = document.createElement('div');
    this.elements.overlay.id = 'tutorial-overlay';

    this.elements.spotlight = document.createElement('div');
    this.elements.spotlight.id = 'tutorial-spotlight';

    this.elements.tooltip = document.createElement('div');
    this.elements.tooltip.id = 'tutorial-tooltip';
    this.elements.tooltip.setAttribute('role', 'dialog');
    this.elements.tooltip.setAttribute('aria-live', 'polite');

    this.elements.tooltipContent = document.createElement('div');
    this.elements.tooltipContent.id = 'tutorial-content';

    this.elements.tooltipButtons = document.createElement('div');
    this.elements.tooltipButtons.id = 'tutorial-buttons';

    this.elements.nextButton = document.createElement('button');
    this.elements.nextButton.id = 'tutorial-next';
    this.elements.nextButton.textContent = 'Next';
    this.elements.nextButton.setAttribute('aria-label', 'Next tutorial step');

    this.elements.skipButton = document.createElement('button');
    this.elements.skipButton.id = 'tutorial-skip';
    this.elements.skipButton.textContent = 'Skip Tutorial';
    this.elements.skipButton.setAttribute('aria-label', 'Skip tutorial');

    this.elements.tooltipButtons.appendChild(this.elements.nextButton);
    this.elements.tooltipButtons.appendChild(this.elements.skipButton);
    this.elements.tooltip.appendChild(this.elements.tooltipContent);
    this.elements.tooltip.appendChild(this.elements.tooltipButtons);

    document.body.appendChild(this.elements.overlay);
    document.body.appendChild(this.elements.spotlight);
    document.body.appendChild(this.elements.tooltip);

    this.addStyles();
  }

  addStyles() {
    const style = document.createElement('style');
    style.textContent = `
      :root {
        --primary-color: #3b82f6;
        --primary-hover: #2563eb;
        --tooltip-bg: rgba(30, 30, 30, 0.95);
        --text-color: #ffffff;
        --accent-color: #60a5fa;
      }

      #tutorial-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.6);
        z-index: 1000;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.5s ease-in-out;
      }

      #tutorial-spotlight {
        position: absolute;
        border-radius: 8px;
        background-color: transparent;
        border: 3px solid var(--primary-color);
        pointer-events: none;
        z-index: 1001;
        transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        animation: spotlight-pulse 2s infinite;
        clip-path: none;
      }

      .spotlight-hole {
        position: absolute;
        background-color: transparent;
        z-index: 1001;
        pointer-events: none;
      }

      @keyframes spotlight-pulse {
        0% { border-color: var(--primary-color); }
        50% { border-color: var(--primary-hover); }
        100% { border-color: var(--primary-color); }
      }

      #tutorial-tooltip {
        position: absolute;
        background-color: var(--tooltip-bg);
        border: 1px solid var(--primary-color);
        border-radius: 8px;
        padding: 16px;
        z-index: 1002;
        max-width: min(90vw, 320px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: system-ui, -apple-system, sans-serif;
        animation: fadeIn 0.5s ease-out;
        color: var(--text-color);
      }

      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }

      #tutorial-content {
        margin-bottom: 16px;
        font-size: clamp(14px, 2vw, 15px);
        line-height: 1.6;
      }

      #tutorial-content h3 {
        margin: 0 0 12px;
        color: var(--primary-color);
        font-size: clamp(16px, 2.5vw, 18px);
        display: flex;
        align-items: center;
        gap: 8px;
      }

      #tutorial-content strong,
      #tutorial-content em {
        color: var(--accent-color);
        font-weight: 600;
      }

      #tutorial-buttons {
        display: flex;
        gap: 8px;
        justify-content: flex-end;
      }

      #tutorial-buttons button {
        background-color: var(--primary-color);
        border: none;
        border-radius: 4px;
        color: var(--text-color);
        padding: 6px 12px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        transition: background-color 0.2s ease;
      }

      #tutorial-buttons button:hover {
        background-color: var(--primary-hover);
      }

      #tutorial-buttons button:focus {
        outline: 2px solid var(--primary-color);
        outline-offset: 2px;
      }

      #tutorial-skip {
        background-color: transparent !important;
        border: 1px solid var(--primary-color) !important;
      }

      #tutorial-skip:hover {
        background-color: rgba(59, 130, 246, 0.1) !important;
      }

      .tutorial-icon {
        width: 20px;
        height: 20px;
        flex-shrink: 0;
      }

      @media (max-width: 768px) {
        #tutorial-tooltip {
          max-width: 90vw;
          padding: 12px;
        }

        #tutorial-buttons button {
          padding: 6px 12px;
          font-size: 13px;
        }
      }

      @media (prefers-reduced-motion: reduce) {
        #tutorial-spotlight,
        #tutorial-tooltip,
        #tutorial-buttons button {
          transition: none;
          animation: none;
        }
      }
    `;
    document.head.appendChild(style);
  }

  async showStep(index) {
    try {
      const step = this.steps[index];
      let targetElement = step.elementFinder 
        ? await this.waitForElement(step.elementFinder, 5000)
        : document.querySelector(step.element);

      if (!targetElement) {
        console.warn(`Element ${step.element} not found`);
        return this.nextStep();
      }

      const rect = targetElement.getBoundingClientRect();
      const padding = step.spotlightPadding || 8;

      // Fix: Store original element dimensions before spotlight
      if (step.element === '.date-selector') {
        targetElement.dataset.originalWidth = targetElement.style.width || '';
        targetElement.dataset.originalMaxWidth = targetElement.style.maxWidth || '';
      }

      Object.assign(this.elements.spotlight.style, {
        top: `${rect.top - padding}px`,
        left: `${rect.left - padding}px`,
        width: `${rect.width + padding * 2}px`,
        height: `${rect.height + padding * 2}px`,
        opacity: '1'
      });

      const holeLeft = (rect.left - padding) / window.innerWidth * 100;
      const holeTop = (rect.top - padding) / window.innerHeight * 100;
      const holeWidth = (rect.width + padding * 2) / window.innerWidth * 100;
      const holeHeight = (rect.height + padding * 2) / window.innerHeight * 100;
      
      this.elements.overlay.style.clipPath = `polygon(
        0% 0%, 
        100% 0%, 
        100% 100%, 
        0% 100%,
        0% 0%,
        ${holeLeft}% ${holeTop}%,
        ${holeLeft}% ${holeTop + holeHeight}%,
        ${holeLeft + holeWidth}% ${holeTop + holeHeight}%,
        ${holeLeft + holeWidth}% ${holeTop}%,
        ${holeLeft}% ${holeTop}%
      )`;

      // Fix: Prevent date-selector from expanding during tutorial
      if (step.element === '.date-selector') {
        targetElement.style.width = `${rect.width}px`;
        targetElement.style.maxWidth = `${rect.width}px`;
      }

      targetElement.style.position = 'relative';
      targetElement.style.zIndex = '1001';

      const tooltipWidth = this.elements.tooltip.offsetWidth || 320;
      const tooltipHeight = this.elements.tooltip.offsetHeight || 200;
      let tooltipTop, tooltipLeft;

      switch (step.position) {
        case 'top':
          tooltipTop = rect.top - tooltipHeight - 16;
          tooltipLeft = rect.left + (rect.width - tooltipWidth) / 2;
          break;
        case 'bottom':
          tooltipTop = rect.bottom + 16;
          tooltipLeft = rect.left + (rect.width - tooltipWidth) / 2;
          break;
        case 'left':
          tooltipTop = rect.top + (rect.height - tooltipHeight) / 2;
          tooltipLeft = rect.left - tooltipWidth - 16;
          break;
        case 'right':
          tooltipTop = rect.top + (rect.height - tooltipHeight) / 2;
          tooltipLeft = rect.right + 16;
          break;
      }

      tooltipTop = Math.max(16, Math.min(window.innerHeight - tooltipHeight - 16, tooltipTop));
      tooltipLeft = Math.max(16, Math.min(window.innerWidth - tooltipWidth - 16, tooltipLeft));

      Object.assign(this.elements.tooltip.style, {
        top: `${tooltipTop}px`,
        left: `${tooltipLeft}px`,
        opacity: '1'
      });

      this.elements.tooltipContent.innerHTML = `<h3>${step.title}</h3><p>${step.content}</p>`;
      this.elements.nextButton.textContent = index < this.steps.length - 1 ? 'Next' : 'Finish';

      this.currentStep = index;
      this.elements.nextButton.focus();
    } catch (error) {
      console.error('Error showing tutorial step:', error);
      this.endTutorial();
    }
  }

  async waitForElement(finder, timeout) {
    const start = Date.now();
    while (Date.now() - start < timeout) {
      const element = finder();
      if (element) return element;
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    return null;
  }

  nextStep() {
    // Fix: Reset any previous element styles before moving to the next step
    if (this.currentStep >= 0 && this.currentStep < this.steps.length) {
      const currentStepElement = this.steps[this.currentStep].element;
      const currentElement = document.querySelector(currentStepElement);
      
      if (currentElement && currentStepElement === '.date-selector') {
        currentElement.style.width = currentElement.dataset.originalWidth || '';
        currentElement.style.maxWidth = currentElement.dataset.originalMaxWidth || '';
      }
    }

    if (this.currentStep < this.steps.length - 1) {
      this.showStep(this.currentStep + 1);
    } else {
      this.endTutorial();
    }
  }

  start() {
    if (this.isRunning) return;
    this.isRunning = true;

    this.createElements();
    this.elements.overlay.style.opacity = '1';

    this.elements.nextButton.addEventListener('click', () => this.nextStep());
    this.elements.skipButton.addEventListener('click', () => this.endTutorial());

    document.addEventListener('keydown', (e) => {
      if (!this.isRunning) return;
      if (e.key === 'Enter' || e.key === 'ArrowRight') this.nextStep();
      if (e.key === 'Escape') this.endTutorial();
    });

    this.showStep(0);
  }

  endTutorial() {
    if (!this.isRunning) return;
    this.isRunning = false;

    [this.elements.overlay, this.elements.spotlight, this.elements.tooltip].forEach(el => {
      el.style.transition = 'opacity 0.5s ease';
      el.style.opacity = '0';
    });

    this.elements.overlay.style.clipPath = 'none';

    // Fix: Reset all element styles when ending the tutorial
    document.querySelectorAll('.control-group, .date-selector, #fullscreen-btn, header').forEach(el => {
      if (el) {
        el.style.zIndex = '';
        el.style.position = '';
        
        // Restore original width for date-selector
        if (el.classList.contains('date-selector')) {
          el.style.width = el.dataset.originalWidth || '';
          el.style.maxWidth = el.dataset.originalMaxWidth || '';
        }
      }
    });

    setTimeout(() => {
      Object.values(this.elements).forEach(el => el?.remove());
      this.elements = {};
    }, 500);

    localStorage.setItem('pdfViewerTutorialShown', 'true');
  }
}

const tutorial = new Tutorial();
tutorial.initialize();