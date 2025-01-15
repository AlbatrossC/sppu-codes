// Modal functionality
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
    // Mobile menu functionality
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

    // Search functionality
    const searchInput = document.getElementById('subject-search');
    const subjectItems = document.querySelectorAll('.subject-list li');
    let searchTimeout;

    // Function to highlight matching text
    function highlightMatch(item, searchTerm) {
        if (searchTerm === '') {
            // Reset highlights
            item.querySelector('.short-form').innerHTML = item.querySelector('.short-form').textContent;
            item.querySelector('.full-name').innerHTML = item.querySelector('.full-name').textContent;
            return;
        }

        const highlightText = (text, term) => {
            const regex = new RegExp(`(${term})`, 'gi');
            return text.replace(regex, '<mark style="background-color: rgba(45, 118, 204, 0.2); color: var(--text-primary); padding: 0 2px; border-radius: 2px;">$1</mark>');
        };

        const shortForm = item.querySelector('.short-form');
        const fullName = item.querySelector('.full-name');

        shortForm.innerHTML = highlightText(shortForm.textContent, searchTerm);
        fullName.innerHTML = highlightText(fullName.textContent, searchTerm);
    }

    // Function to perform search
    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase().trim();

        subjectItems.forEach(item => {
            const shortForm = item.querySelector('.short-form').textContent.toLowerCase();
            const fullName = item.querySelector('.full-name').textContent.toLowerCase();
            
            if (shortForm.includes(searchTerm) || fullName.includes(searchTerm)) {
                item.classList.remove('hidden');
                highlightMatch(item, searchTerm);
            } else {
                item.classList.add('hidden');
            }
        });

        // Add "no results" message if all items are hidden
        const allHidden = Array.from(subjectItems).every(item => item.classList.contains('hidden'));
        let noResultsMsg = document.querySelector('.no-results-message');
        
        if (allHidden && searchTerm !== '') {
            if (!noResultsMsg) {
                noResultsMsg = document.createElement('div');
                noResultsMsg.className = 'no-results-message';
                noResultsMsg.style.textAlign = 'center';
                noResultsMsg.style.padding = '2rem';
                noResultsMsg.style.color = 'var(--text-muted)';
                subjectItems[0].parentNode.appendChild(noResultsMsg);
            }
            noResultsMsg.textContent = `No subjects found matching "${searchInput.value}"`;
            noResultsMsg.style.display = 'block';
        } else if (noResultsMsg) {
            noResultsMsg.style.display = 'none';
        }
    }

    // Add search input event listener with debouncing
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(performSearch, 300); // Debounce for 300ms
    });

    // Clear search when clicking the clear button (x) in the input
    searchInput.addEventListener('search', performSearch);

    // Initialize search on page load (in case there's a value)
    if (searchInput.value) {
        performSearch();
    }
});