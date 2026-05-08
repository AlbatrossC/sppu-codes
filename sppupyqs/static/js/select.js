// SPPU PYQs - Search and Navigation
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('paper-search');
    const mobileSearchToggle = document.querySelector('.mobile-search-toggle');
    const searchContainer = document.getElementById('searchContainer');
    const searchDropdown = document.getElementById('searchDropdown');
    const breadcrumb = document.getElementById('breadcrumb');
    const header = document.querySelector('header');

    // Mobile search toggle
    if (mobileSearchToggle) {
        mobileSearchToggle.addEventListener('click', () => {
            searchContainer.classList.toggle('active');
            mobileSearchToggle.classList.toggle('active');
            if (searchContainer.classList.contains('active')) {
                searchInput.focus();
            }
        });
    }

    // Client-side search
    let searchData = [];
    let activeIndex = -1;

    fetch('/static/search.1.json')
        .then(res => res.json())
        .then(data => {
            searchData = data;
        })
        .catch(() => {
            console.warn('Failed to load search index');
        });

    function scoreMatch(item, query) {
        const sn = item.subject_name.toLowerCase();
        const bn = item.branch_name.toLowerCase();
        const bc = item.branch_code.toLowerCase();
        const sl = item.subject_link.toLowerCase();
        const kw = item.keywords.toLowerCase();
        const abbr = (item.abbreviation || "").toLowerCase();

        let score = 0;

        if (sn === query) {
            score = 100;
        } else if (sn.startsWith(query)) {
            score = 80;
        } else if (abbr === query) {
            score = 75;
        } else if (new RegExp('\\b' + query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).test(sn)) {
            score = 70;
        } else if (sn.includes(query)) {
            score = 60;
        }

        if (abbr && abbr !== query && abbr.startsWith(query)) {
            score += 15;
        }

        if (kw.includes(query)) {
            score += 20;
        }

        if (bn.includes(query)) {
            score += 5;
        }

        if (bc.includes(query)) {
            score += 3;
        }

        if (sl.includes(query)) {
            score += 3;
        }

        return score;
    }

    searchInput.addEventListener('input', function () {
        const query = this.value.trim().toLowerCase();

        if (query.length < 2) {
            searchDropdown.style.display = 'none';
            searchDropdown.innerHTML = '';
            activeIndex = -1;
            return;
        }

        const scored = [];
        for (const item of searchData) {
            const score = scoreMatch(item, query);
            if (score > 0) {
                scored.push({ item, score });
            }
        }

        scored.sort((a, b) => b.score - a.score);

        const results = scored.slice(0, 10);

        searchDropdown.innerHTML = '';
        activeIndex = -1;

        if (!results.length) {
            searchDropdown.innerHTML = '<div class="search-no-results">No results found</div>';
            searchDropdown.style.display = 'block';
            return;
        }

        results.forEach((entry, idx) => {
            const item = entry.item;
            const row = document.createElement('div');
            row.classList.add('search-result-row');
            row.innerHTML = `
                <span class="result-subject">${item.subject_name}</span>
                <span class="result-branch">${item.branch_name} &mdash; Sem ${item.sem_no}</span>
            `;
            row.addEventListener('click', () => {
                window.location.href = '/' + item.subject_link;
            });
            row.addEventListener('mouseenter', () => {
                activeIndex = idx;
                updateActiveRow();
            });
            searchDropdown.appendChild(row);
        });

        searchDropdown.style.display = 'block';
    });

    searchInput.addEventListener('keydown', function (e) {
        const rows = searchDropdown.querySelectorAll('.search-result-row');
        if (!rows.length) return;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            activeIndex = (activeIndex + 1) % rows.length;
            updateActiveRow();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            activeIndex = activeIndex <= 0 ? rows.length - 1 : activeIndex - 1;
            updateActiveRow();
        } else if (e.key === 'Enter' && activeIndex >= 0) {
            e.preventDefault();
            rows[activeIndex].click();
        }
    });

    function updateActiveRow() {
        const rows = searchDropdown.querySelectorAll('.search-result-row');
        rows.forEach((row, i) => {
            row.classList.toggle('active', i === activeIndex);
        });
    }

    document.addEventListener('click', function (e) {
        if (!searchContainer.contains(e.target)) {
            searchDropdown.style.display = 'none';
        }
    });

    searchInput.addEventListener('focus', function () {
        if (searchDropdown.children.length) {
            searchDropdown.style.display = 'block';
        }
    });

    // Responsive search bar visibility
    function updateSearchBarVisibility() {
        if (window.innerWidth >= 900) {
            searchContainer.classList.add('active');
            searchContainer.style.display = 'flex';
        } else if (!searchContainer.classList.contains('active')) {
            searchContainer.style.display = '';
        }
    }

    updateSearchBarVisibility();
    window.addEventListener('resize', updateSearchBarVisibility);

    // Navigation
    function clearActive() {
        document.querySelectorAll('.nav-level').forEach(el => el.classList.remove('active'));
    }

    function updateBreadcrumb(path) {
        breadcrumb.innerHTML = '';
        if (path.length === 0) {
            const span = document.createElement('span');
            span.classList.add('breadcrumb-item', 'active');
            span.textContent = 'Branches';
            breadcrumb.appendChild(span);
            return;
        }

        path.forEach((item, index) => {
            const span = document.createElement('span');
            span.classList.add('breadcrumb-item');
            if (index === path.length - 1) {
                span.classList.add('active');
            } else {
                span.classList.add('clickable');
                span.onclick = item.onClick;
            }
            span.textContent = item.name;
            breadcrumb.appendChild(span);

            if (index < path.length - 1) {
                const separator = document.createElement('span');
                separator.classList.add('breadcrumb-separator');
                separator.innerHTML = '&rsaquo;';
                breadcrumb.appendChild(separator);
            }
        });
    }

    window.showSemesters = function (branch) {
        clearActive();
        document.getElementById(`${branch.replaceAll(' ', '_')}-sems`).classList.add('active');
        updateBreadcrumb([
            { name: 'Branches', onClick: () => showBranches() },
            { name: branch }
        ]);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    window.showSubjects = function (branch, sem) {
        clearActive();
        document.getElementById(`${branch.replaceAll(' ', '_')}-${sem.replaceAll(' ', '_')}-subjects`).classList.add('active');
        updateBreadcrumb([
            { name: 'Branches', onClick: () => showBranches() },
            { name: branch, onClick: () => showSemesters(branch) },
            { name: sem }
        ]);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    window.showBranches = function () {
        clearActive();
        document.getElementById('branches').classList.add('active');
        updateBreadcrumb([]);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    updateBreadcrumb([]);
});
