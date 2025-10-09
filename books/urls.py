# Importing views and path for the index/list view
from django.urls import path
from .views import BookListView

urlpatterns = [
  path('', BookListView.as_view()),
]
