console.log(`
SPPU Codes search initialized.
Source: https://github.com/AlbatrossC/sppu-codes
`);

document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('subject-search');
    const mobileSearchToggle = document.querySelector('.mobile-search-toggle');
    const searchContainer = document.querySelector('.search-container');
    const header = document.querySelector('header');

    let searchDropdown = document.querySelector('.search-dropdown');
    if (!searchDropdown) {
        searchDropdown = document.createElement('div');
        searchDropdown.className = 'search-dropdown';
        document.body.appendChild(searchDropdown);
    }

    let isLoaded = false;
    const MAX_RESULTS = 10;
    let codeResults = [];

    const HARDCODED_SUBJECTS = [
        { subject_link: 'oop', subject_name: 'Object-Oriented Programming Lab' },
        { subject_link: 'cgl', subject_name: 'Computer Graphics Lab' },
        { subject_link: 'dsl', subject_name: 'Data Structures Laboratory' },
        { subject_link: 'iotl', subject_name: 'Internet of Things Laboratory' },
        { subject_link: 'dsal', subject_name: 'Data Structures and Algorithms Laboratory' },
        { subject_link: 'dbms', subject_name: 'Database Management System' },
        { subject_link: 'cnl', subject_name: 'Computer Networks Laboratory' },
        { subject_link: 'ai', subject_name: 'Artificial Intelligence Laboratory' },
        { subject_link: 'ann', subject_name: 'Artificial Neural Network' },
        { subject_link: 'ds', subject_name: 'Data Science' },
        { subject_link: 'nlp', subject_name: 'Natural Language Processing' },
        { subject_link: 'cs', subject_name: 'Cyber Security' }
    ];

    function normalize(value) {
        return (value || '').toLowerCase().replace(/[^a-z0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();
    }

    function score(query, subject) {
        const q = normalize(query);
        const code = normalize(subject.subject_link);
        const name = normalize(subject.subject_name);
        if (!q) return Infinity;
        if (code.startsWith(q) || name.startsWith(q)) return 0;
        if (code.includes(q) || name.includes(q)) return 1;
        return Math.min(Math.abs(code.length - q.length), Math.abs(name.length - q.length)) + 2;
    }

    function highlight(text, query) {
        if (!query) return text;
        const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        return text.replace(new RegExp(`(${escaped})`, 'ig'), '<mark>$1</mark>');
    }

    async function loadSearchData() {
        if (isLoaded) return;
        try {
            const res = await fetch('/api/subjects/search');
            if (!res.ok) throw new Error('search load failed');
            const data = await res.json();
            codeResults = Array.isArray(data) && data.length ? data : HARDCODED_SUBJECTS;
        } catch (_error) {
            codeResults = HARDCODED_SUBJECTS;
        }
        isLoaded = true;
    }

    function renderResults(items, query) {
        searchDropdown.innerHTML = '';
        if (!items.length) {
            searchDropdown.innerHTML = `<div class="search-no-results">No subjects found for "${query}"</div>`;
            return;
        }

        const section = document.createElement('div');
        section.className = 'search-section';
        section.innerHTML = '<div class="search-section-header">Codes</div>';
        const list = document.createElement('div');
        list.className = 'search-section-list';

        items.slice(0, MAX_RESULTS).forEach(item => {
            const row = document.createElement('div');
            row.className = 'search-result-row code-row';
            row.innerHTML = `
                <span class="result-name">${highlight(item.subject_name, query)}</span>
                <span class="result-shortcode">${(item.subject_link || '').toUpperCase()}</span>
                <span class="result-type-label">CODE</span>
            `;
            row.addEventListener('click', () => {
                window.location.href = `/${item.subject_link}`;
            });
            list.appendChild(row);
        });

        section.appendChild(list);
        searchDropdown.appendChild(section);
    }

    function positionDropdown() {
        const rect = searchInput.getBoundingClientRect();
        if (window.innerWidth <= 899) {
            searchDropdown.style.position = 'fixed';
            const topOffset = header.offsetHeight + (searchContainer.classList.contains('active') ? searchContainer.offsetHeight : 0);
            searchDropdown.style.top = `${topOffset}px`;
            searchDropdown.style.left = '0';
            searchDropdown.style.width = '100vw';
            searchDropdown.style.maxWidth = '100vw';
        } else {
            searchDropdown.style.position = 'absolute';
            searchDropdown.style.top = `${rect.bottom + window.scrollY + 4}px`;
            searchDropdown.style.left = `${rect.left + window.scrollX}px`;
            searchDropdown.style.width = `${rect.width}px`;
            searchDropdown.style.maxWidth = `${rect.width}px`;
        }
        searchDropdown.style.display = 'block';
        searchDropdown.style.zIndex = '3000';
    }

    function updateSearchBarVisibility() {
        if (window.innerWidth >= 900) {
            searchContainer.classList.add('active');
            searchContainer.style.display = 'flex';
        } else if (!searchContainer.classList.contains('active')) {
            searchContainer.style.display = '';
        }
    }

    async function handleSearch() {
        const query = searchInput.value.trim();
        if (!query) {
            searchDropdown.style.display = 'none';
            return;
        }
        await loadSearchData();
        const matches = codeResults
            .map(item => ({ item, weight: score(query, item) }))
            .filter(entry => entry.weight <= 6)
            .sort((a, b) => a.weight - b.weight)
            .map(entry => entry.item);
        renderResults(matches, query);
        positionDropdown();
    }

    updateSearchBarVisibility();
    window.addEventListener('resize', updateSearchBarVisibility);
    window.addEventListener('resize', () => searchDropdown.style.display === 'block' && positionDropdown());
    window.addEventListener('scroll', () => searchDropdown.style.display === 'block' && window.innerWidth > 899 && positionDropdown());

    if (mobileSearchToggle) {
        mobileSearchToggle.addEventListener('click', async (event) => {
            event.stopPropagation();
            searchContainer.classList.toggle('active');
            if (searchContainer.classList.contains('active')) {
                await loadSearchData();
                setTimeout(() => searchInput.focus(), 150);
            } else {
                searchDropdown.style.display = 'none';
            }
        });
    }

    searchInput.addEventListener('focus', handleSearch);
    searchInput.addEventListener('input', handleSearch);
    searchInput.addEventListener('blur', () => setTimeout(() => { searchDropdown.style.display = 'none'; }, 200));
    document.addEventListener('mousedown', (event) => {
        if (!searchDropdown.contains(event.target) && event.target !== searchInput) {
            searchDropdown.style.display = 'none';
        }
    });
});
