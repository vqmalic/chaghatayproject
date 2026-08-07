from django.urls import path
from dictionary import views

urlpatterns = [
    path('entry/<int:pk>/', views.EntryDetailView.as_view(), name='entry_detail'),
    path('', views.home, name='home'),
    path('api/search/', views.search_suggestions, name='search_suggestions'),
    path('search/', views.search_results, name='search_results'),
    path("about/", views.AboutView.as_view(), name="about"),
    path("help/", views.HelpView.as_view(), name="help"),
]