(function () {
    const openBtn = document.getElementById('open-download');
    const modal = document.getElementById('download-modal');
    const overlay = modal && modal.querySelector('.download-modal-overlay');
    const closeButtons = modal && modal.querySelectorAll('[data-close]');
    const subjectBadge = document.getElementById('demo-subject');
    const modalSubject = document.getElementById('modal-subject');

    function openModal() {
        const subject = (subjectBadge && subjectBadge.textContent.trim()) || 'Subject';
        if (modalSubject) modalSubject.textContent = subject;
        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
    }

    function closeModal() {
        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
    }

    if (openBtn) openBtn.addEventListener('click', openModal);
    if (overlay) overlay.addEventListener('click', closeModal);
    if (closeButtons) closeButtons.forEach(btn => btn.addEventListener('click', closeModal));

    // keyboard: Esc to close
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) closeModal();
    });

    // Wire download buttons to show placeholder link (#). This keeps hooks for backend later.
    const zipButtons = document.querySelectorAll('.download-zip-btn');
    zipButtons.forEach(btn => {
        btn.addEventListener('click', (ev) => {
            // placeholder behavior — link is "#". Prevent default navigation while still allowing future href.
            // Could show a tiny feedback animation in the future.
            ev.preventDefault();
            // For now simply close the modal to simulate action
            closeModal();
            // In future: set btn.href to real URL before triggering navigation.
        });
    });
})();
