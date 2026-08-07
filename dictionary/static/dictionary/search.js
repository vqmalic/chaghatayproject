const searchBox = document.getElementById('search-box');
const suggestionsBox = document.getElementById('suggestions');
const modeRadios = document.querySelectorAll('input[name="search-mode"]');

let debounceTimer = null;
let latestRequestId = 0;

function getMode() {
    return document.querySelector('input[name="search-mode"]:checked').value;
}

searchBox.addEventListener('input', () => {
    const query = searchBox.value.trim();

    clearTimeout(debounceTimer);

    if (!query) {
        suggestionsBox.style.display = 'none';
        suggestionsBox.innerHTML = '';
        return;
    }

    debounceTimer = setTimeout(() => {
        fetchSuggestions(query, getMode());
    }, 180);
});

searchBox.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter') return;

    const query = searchBox.value.trim();
    if (!query) return;

    window.location.href = `/search/?q=${encodeURIComponent(query)}&mode=${getMode()}`;
});

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

    document.querySelectorAll('.suggestion-item').forEach(item => {
        item.addEventListener('click', () => {
            window.location.href = `/entry/${item.dataset.id}/`;
        });
    });
}

document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-container')) {
        suggestionsBox.style.display = 'none';
    }
});