const statsModal = document.getElementById('stats-modal');
const statsButton = document.getElementById('menu-stats');
const closeModalButton = document.getElementById('close-modal'); 

// Function to open the modal
statsButton.addEventListener('click', () => {
    statsModal.classList.remove('hidden');
});

// Function to close the modal
closeModalButton.addEventListener('click', () => {
    statsModal.classList.add('hidden'); 
});

// Close modal when clicking outside of the content
window.addEventListener('click', (event) => {
    if (event.target === statsModal) {
        statsModal.classList.add('hidden'); 
    }
});
document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const headerActions = document.querySelector('.header__actions');
    const menuOverlay = document.querySelector('.menu-overlay');
    const body = document.body;

    // Add animation delay to menu items
    const menuItems = headerActions.children;
    Array.from(menuItems).forEach((item, index) => {
        item.style.setProperty('--item-index', index);
    });

    menuToggle.addEventListener('click', function() {
        headerActions.classList.toggle('active');
        menuOverlay.classList.toggle('active');
        menuToggle.classList.toggle('active'); // Add this line
        body.style.overflow = headerActions.classList.contains('active') ? 'hidden' : '';
    });

    // Close menu when clicking overlay
    menuOverlay.addEventListener('click', function() {
        headerActions.classList.remove('active');
        menuOverlay.classList.remove('active');
        menuToggle.classList.remove('active'); // Add this line
        body.style.overflow = '';
    });
});