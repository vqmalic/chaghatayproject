const searchBox = document.getElementById('search-box');
const suggestionsBox = document.getElementById('suggestions');
const modeRadios = document.querySelectorAll('input[name="search-mode"]');

let debounceTimer = null;
let latestRequestId = 0;
let highlightedIndex = -1;
let currentResults = []; // keep the raw result data around so Enter/click can navigate

function getMode() {
    return document.querySelector('input[name="search-mode"]:checked').value;
}

function isPersoArabic(text) {
    return /[\u0600-\u06FF]/.test(text);
}

searchBox.addEventListener('input', () => {
    const query = searchBox.value.trim();

    clearTimeout(debounceTimer);

    if (!query) {
        suggestionsBox.style.display = 'none';
        suggestionsBox.innerHTML = '';
        currentResults = [];
        highlightedIndex = -1;
        return;
    }

    debounceTimer = setTimeout(() => {
        searchBox.classList.toggle('persoarabic', isPersoArabic(query));
        fetchSuggestions(query, getMode());
    }, 180);
});

searchBox.addEventListener('keydown', (e) => {
    const items = suggestionsBox.querySelectorAll('.suggestion-item');
    const dropdownOpen = suggestionsBox.style.display === 'block' && items.length > 0;

    if (e.key === 'ArrowDown') {
        if (!dropdownOpen) return;
        e.preventDefault(); // stop the cursor from jumping to the end of the input
        highlightedIndex = (highlightedIndex + 1) % items.length;
        updateHighlight(items);
        return;
    }

    if (e.key === 'ArrowUp') {
        if (!dropdownOpen) return;
        e.preventDefault();
        highlightedIndex = (highlightedIndex - 1 + items.length) % items.length;
        updateHighlight(items);
        return;
    }

    if (e.key === 'Escape') {
        suggestionsBox.style.display = 'none';
        highlightedIndex = -1;
        return;
    }

    if (e.key !== 'Enter') return;

    // If a suggestion is highlighted, Enter selects it instead of submitting raw text
    if (dropdownOpen && highlightedIndex >= 0 && currentResults[highlightedIndex]) {
        window.location.href = `/entry/${currentResults[highlightedIndex].id}/`;
        return;
    }

    const query = searchBox.value.trim();
    if (!query) return;

    window.location.href = `/search/?q=${encodeURIComponent(query)}&mode=${getMode()}`;
});

function updateHighlight(items) {
    items.forEach((item, i) => {
        item.classList.toggle('highlighted', i === highlightedIndex);
    });

    // keep the highlighted item visible if the list scrolls
    if (highlightedIndex >= 0) {
        items[highlightedIndex].scrollIntoView({ block: 'nearest' });
    }
}

modeRadios.forEach(radio => {
    radio.addEventListener('change', () => {
        const query = searchBox.value.trim();
        if (query) fetchSuggestions(query, getMode());
    });
});

async function fetchSuggestions(query, mode) {
    const requestId = ++latestRequestId;

    const response = await fetch(`/api/search/?q=${encodeURIComponent(query)}&mode=${mode}`);
    const data = await response.json();

    if (requestId !== latestRequestId) return;

    renderSuggestions(data.results);
}

function renderSuggestions(results) {
    currentResults = results;
    highlightedIndex = -1; // reset on every new result set

    if (results.length === 0) {
        suggestionsBox.style.display = 'none';
        suggestionsBox.innerHTML = '';
        return;
    }

    suggestionsBox.innerHTML = results.map(r => `
        <div class="suggestion-item" data-id="${r.id}">
            <div class="suggestion-persoarabic persoarabic">${r.persoarabic}</div>
            <div>${r.latin_strict}${r.latin_phonetic ? ` (${r.latin_phonetic})` : ''}</div>
            <div class="suggestion-snippet">${r.snippet}</div>
        </div>
    `).join('');

    suggestionsBox.style.display = 'block';

    const items = document.querySelectorAll('.suggestion-item');
    items.forEach((item, i) => {
        item.addEventListener('click', () => {
            window.location.href = `/entry/${item.dataset.id}/`;
        });
        item.addEventListener('mouseenter', () => {
            highlightedIndex = i;
            updateHighlight(items);
        });
    });
}

document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-container')) {
        suggestionsBox.style.display = 'none';
    }
});