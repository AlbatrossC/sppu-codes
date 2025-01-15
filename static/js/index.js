const statsModal = document.getElementById('stats-modal');
const statsButton = document.getElementById('menu-stats');
const closeModalButton = document.getElementById('close-modal');

// Open stats modal
statsButton.addEventListener('click', () => {
    statsModal.classList.remove('hidden');
});

// Close stats modal
closeModalButton.addEventListener('click', () => {
    statsModal.classList.add('hidden');
});

// Close stats modal when clicking outside of it
window.addEventListener('click', (event) => {
    if (event.target === statsModal) {
        statsModal.classList.add('hidden');
    }
});

// On DOMContentLoaded event
document.addEventListener('DOMContentLoaded', function () {
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const headerActions = document.querySelector('.header__actions');
    const menuOverlay = document.querySelector('.menu-overlay');
    const body = document.body;

    const menuItems = headerActions.children;

    // Set custom property for each menu item
    Array.from(menuItems).forEach((item, index) => {
        item.style.setProperty('--item-index', index);
    });

    // Toggle mobile menu
    menuToggle.addEventListener('click', function () {
        headerActions.classList.toggle('active');
        menuOverlay.classList.toggle('active');
        menuToggle.classList.toggle('active');
        body.style.overflow = headerActions.classList.contains('active') ? 'hidden' : '';
    });

    // Close mobile menu when clicking on the overlay
    menuOverlay.addEventListener('click', function () {
        headerActions.classList.remove('active');
        menuOverlay.classList.remove('active');
        menuToggle.classList.remove('active');
        body.style.overflow = '';
    });
});
