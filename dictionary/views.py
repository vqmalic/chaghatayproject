from django.views.generic import ListView
from .models import Entry

class EntryListView(ListView):
    model = Entry
    template_name = 'dictionary/entry_list.html'
    context_object_name = 'entries'
    paginate_by = 50
    ordering = ['latin_strict_stripped']