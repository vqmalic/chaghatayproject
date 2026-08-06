const searchBox = document.getElementById('search-box');
const suggestionsBox = document.getElementById('suggestions');

let debounceTimer = null;
let latestRequestId = 0;

searchBox.addEventListener('input', () => {
    const query = searchBox.value.trim();

    clearTimeout(debounceTimer);

    if (!query) {
        suggestionsBox.style.display = 'none';
        suggestionsBox.innerHTML = '';
        return;
    }

    debounceTimer = setTimeout(() => {
        fetchSuggestions(query);
    }, 180);
});

async function fetchSuggestions(query) {
    const requestId = ++latestRequestId;

    const response = await fetch(`/api/search/?q=${encodeURIComponent(query)}`);
    const data = await response.json();

    // if a newer request has since been fired, discard this stale response
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

// hide dropdown when clicking elsewhere
document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-container')) {
        suggestionsBox.style.display = 'none';
    }
});