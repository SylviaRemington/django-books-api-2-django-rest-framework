from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Book
from .serializers import BookSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly # IsAuthenticatedOrReadOnly specifies that a view is secure on all methods except get requests

# Create your views here.
# Starting with the GET method to retrieve all books.
class BookListView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, ) # sets the permission levels of the specific view by passing in the rest framework authentication class
    # handle a GET request in the BookListView
    def get(self, _request):
        # go to the database and get all the books
        books = Book.objects.all()
        # translate the books from the database to a usable form
        serialized_books = BookSerializer(books, many=True)
        # return the serialized data and a 200 status code
        return Response(serialized_books.data, status=status.HTTP_200_OK)
    