# Importing views and path for the index/list view
from django.urls import path
from .views import BookListView, BookDetailView

urlpatterns = [
  path('', BookListView.as_view()),
  path('<int:pk>/', BookDetailView.as_view()),

]
