from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Entry
from .search import search_entries

def home(request):
    return render(request, 'dictionary/home.html')

def search_suggestions(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return JsonResponse({'results': []})

    entries = search_entries(query, limit=8)

    results = []
    for entry in entries:
        first_def = entry.definition_set.first()
        results.append({
            'id': entry.id,
            'persoarabic': entry.persoarabic,
            'latin_strict': entry.latin_strict,
            'latin_phonetic': entry.latin_phonetic,
            'snippet': (first_def.definition_text[:80] + '…') if first_def else '',
        })

    return JsonResponse({'results': results})

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