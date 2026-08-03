from django.urls import path
from .views import EntryListView, EntryDetailView

urlpatterns = [
    path('', EntryListView.as_view(), name='entry_list'),
    path('entry/<int:pk>/', EntryDetailView.as_view(), name='entry_detail'),
]