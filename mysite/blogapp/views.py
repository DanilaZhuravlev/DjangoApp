from django.shortcuts import render
from django.views.generic import ListView

from blogapp.models import Article


class ArticlesListView(ListView):
    template_name = 'blogapp/article_list.html'
    model = Article
    context_object_name = 'articles'

    def get_queryset(self):
        return Article.objects.select_related('author', 'category').prefetch_related('tags').defer('content')



