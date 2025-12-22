// Mobile Menu Functionality
document.addEventListener('DOMContentLoaded', function() {
    const menuBtn = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobileMenu');
    const closeBtn = document.getElementById('closeMenuBtn');
    const body = document.body;

    if (!menuBtn || !mobileMenu) return;

    // Close menu function
    function closeMenu() {
        mobileMenu.classList.remove('open');
        menuBtn.classList.remove('active');
        body.style.overflow = '';
    }

    // Open menu function
    function openMenu() {
        mobileMenu.classList.add('open');
        menuBtn.classList.add('active');
        body.style.overflow = 'hidden';
    }

    // Toggle menu open/close
    function toggleMenu() {
        if (mobileMenu.classList.contains('open')) {
            closeMenu();
        } else {
            openMenu();
        }
    }

    // Menu button click
    menuBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        toggleMenu();
    });

    // Close button click
    if (closeBtn) {
        closeBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            closeMenu();
        });
    }

    // Close on link click
    mobileMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', closeMenu);
    });

    // Close on outside click
    document.addEventListener('click', function(e) {
        if (mobileMenu.classList.contains('open') && 
            !mobileMenu.contains(e.target) && 
            !menuBtn.contains(e.target)) {
            closeMenu();
        }
    });

    // Close on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && mobileMenu.classList.contains('open')) {
            closeMenu();
        }
    });

    // Handle resize - close menu if switching to desktop
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 900 && mobileMenu.classList.contains('open')) {
            closeMenu();
        }
    });
});