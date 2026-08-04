from django.views.generic import ListView, DetailView
from .models import Entry

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