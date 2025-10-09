from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from rest_framework.exceptions import NotFound

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
    
    
    def post(self, request):
        request.data["owner"] = request.user.id
        book_to_add = BookSerializer(data=request.data)
        try:
           book_to_add.is_valid()
           book_to_add.save()
           return Response(book_to_add.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Error")
            # the below is necessary because two different formats of errors are possible. string or object format.
            # if it's string then e.__dict__ returns an empty dict {}
            # so we'll check it's a dict first, and if it's empty (falsey) then we'll use str() to convert to a string
            return Response(e.__dict__ if e.__dict__ else str(e), status=status.HTTP_422_UNPROCESSABLE_ENTITY)


# class BookDetailView(APIView):
#     permission_classes = (IsAuthenticatedOrReadOnly, ) # sets the permission levels of the specific view by passing in the rest framework authentication class

#     # custom method to retrieve a book from the DB and error if it's not found
#     def get_book(self, pk):
#         try:
#             return Book.objects.get(pk=pk)
#         except Book.DoesNotExist:
#             raise NotFound(detail="Can't find that book") # <-- import the NotFound exception from rest_framwork.exceptions

#     def get(self, _request, pk):
#         try:
#             book = Book.objects.get(pk=pk)
#             serialized_book = BookSerializer(book)
#             return Response(serialized_book.data, status=status.HTTP_200_OK)
#         except Book.DoesNotExist:
#             raise NotFound(detail="Can't find that book") # <-- import the NotFound exception from rest_framwork.exceptions

#     def put(self, request, pk):
#         book_to_update = self.get_book(pk=pk)
#         if book_to_update.owner != request.user:
#             return Response(status=status.HTTP_401_UNAUTHORIZED)

#         updated_book = BookSerializer(book_to_update, data=request.data)
#         if updated_book.is_valid():
#             updated_book.save()
#             return Response(updated_book.data, status=status.HTTP_202_ACCEPTED)

#         return Response(updated_book.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

#     def delete(self, request, pk):
#         book_to_delete = self.get_book(pk=pk)

#         if book_to_delete.owner != request.user:
#             return Response(status=status.HTTP_401_UNAUTHORIZED)

#         book_to_delete.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
    
