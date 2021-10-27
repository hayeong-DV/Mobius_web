from django.shortcuts import render
from django.views.generic import(
    ListView, DetailView, TemplateView,
    CreateView, UpdateView, DeleteView
)
# Create your views here.
class HomeView(TemplateView):
    template_name = 'administrator/main/main.html'