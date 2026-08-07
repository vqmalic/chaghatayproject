from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Entry
from .search import search_entries

def home(request):
    return render(request, 'dictionary/home.html')

def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    mode = request.GET.get('mode', 'chag_to_eng')

    if not query:
        return JsonResponse({'results': []})

    entries = search_entries(query, limit=8, mode=mode)

    results = []
    for entry in entries:
        if mode == 'eng_to_chag':
            # show the definition that actually matched, not just the first one
            matched_def = entry.definition_set.filter(
                definition_text__icontains=query
            ).first()
            snippet = (matched_def.definition_text[:80] + '…') if matched_def else ''
        else:
            first_def = entry.definition_set.first()
            snippet = (first_def.definition_text[:80] + '…') if first_def else ''

        results.append({
            'id': entry.id,
            'persoarabic': entry.persoarabic,
            'latin_strict': entry.latin_strict,
            'latin_phonetic': entry.latin_phonetic,
            'snippet': snippet,
        })

    return JsonResponse({'results': results})

def search_results(request):
    query = request.GET.get('q', '').strip()
    mode = request.GET.get('mode', 'chag_to_eng')

    entries = search_entries(query, limit=200, mode=mode) if query else []

    return render(request, 'dictionary/search_results.html', {
        'query': query,
        'mode': mode,
        'entries': entries,
    })

class EntryListView(ListView):
    model = Entry
    template_name = 'dictionary/entry_list.html'
    context_object_name = 'entries'
    paginate_by = 50
    ordering = ['latin_strict_stripped']

class EntryDetailView(DetailView):
    model = Entry
    template_name = 'dictionary/entry_detail.html'
    context_object_name = 'entry'