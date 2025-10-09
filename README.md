# Lecture Practice of Creating Django Rest Framework API

<br>

# Django Rest Framework API Step By Step Instructions

Author: Tristan Hall

This file will guide you through building an API in Django using the rest framework library, a powerful toolkit for building Web APIs. **(django-rest-framework-walkthrough/step-by-step.md - For full file with images, please contact Tristan Hall who created this content.)**
<hr>

## Setting up the Django Books Api app.

1. Create a directory for the application in your projects directory:

```bash
mkdir ~/code/ga/projects/django-books-api
cd ~/code/ga/projects/django-books-api
```

2. Install the package by running `pipenv install django`. After this you should have 2 files: Pipfile and Pipfile.lock.
   These are essentially the same as a package.json and a package-lock.json in a node/express app.

```bash
pipenv install django
```

The terminal output will look something like this:

<div>
    <img src="./images/install-django.png" width="500px" />
</div>

3. Enter the shell by running `pipenv shell`

```bash
pipenv shell
```

The output will look a bit like this:

<div>
    <img src="./images/pipenv-shell-feedback.png" width="500px" />
</div>

4. To start a project run `django-admin startproject project .`

```bash
django-admin startproject project .
```

You should see that a folder called project has been created in the project directory, along with a `manage.py` file.

5. Run `pipenv install psycopg2-binary` (this is a db-adapter which allows us to use postgresql)

```bash
pipenv install psycopg2-binary
```

If you look in your Pipfile now, you should see that you have 2 dependencies: django and psycopg2-binary.

<div>
    <img src="./images/pipfile.png" width="500px" />
</div>

6. Install autopep8 as a development dependency - this is a code formatter that will automatically format your Python code to follow PEP 8 style guidelines.

```bash
pipenv install autopep8 --dev
```

7. Install the django rest framework `pipenv install djangorestframework`

```bash
pipenv install djangorestframework
```

then add `rest_framework` to the installed apps in our project settings.py

<div>
    <img src="./images/installed-rest-framework.png" width="500px" />
</div>

8. We need our local install of postgres to be running so if it's not, please start it with `brew services start postgresql@16`

```bash
brew services start postgresql@16
```

## VSCode

- Head to your `project/settings.py` file in the project folder
- Replace the `DATABASES` object with the following:

```python
DATABASES = { # added this to use postgres as the database instead of the default sqlite. do this before running the initial migrations or you will need to do it again
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'books-api',
        'HOST': 'localhost',
        'PORT': 5432
    }
}
```

- Make a database by running the terminal command `createdb books-api`

  > This name must match the name of the db in the settings.py file (in the DATABASE.NAME that we just put into the settings)

```bash
createdb books-api
```

# Building The Authentication Flow and Adding Users

1. Start the app with the command `django-admin startapp authentication`

```bash
django-admin startapp authentication
```

2. Register the app in the INSTALLED APPS in the project settings.py

<div>
    <img src="./images/installed-authentication.png" width="500px" />
</div>

3. Django already has a user model, it's how we add a superuser. In `project/settings.py`, add the below to specifiy which model we intend to use:

```python
AUTH_USER_MODEL = 'authentication.User'
```

4. in `authentication/models.py` we'll add our new model.

django already has password, password confirmation & username so we don't need to add them. It doesnt make email required so want to change that. By defining these fields we make them required.

By default, django already has a user model (the one for superusers etc) and it's called the AbstractUser
we want to build on top of that.

```python
from django.db import models
from django.contrib.auth.models import AbstractUser # user model that already exists in django

class User(AbstractUser): # we extend the AbstractUser and add the fields that we want for our users
    email = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    profile_image = models.CharField(max_length=300)
```

5. makemigrations, migrate and runserver

```bash
python manage.py makemigrations &&
python manage.py migrate &&
python manage.py runserver
```

- You should now be able to see the landing page if you navigate to http://localhost:8000 in the browser

<div>
    <img src="./images/homescreen.png" width="500px" />
</div>

## Building The Authentication Flow and Adding Users

Register User model on the admin app. get_user_model is a method that when invoked returns whatever model that our app is set up to use. In settings.py we specified that we will use our own custom model 'authentication.User' so this is what will be returned

Put this in the `authentication/admin.py` file:

```python
from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()
admin.site.register(User) # then we'll register this to the admin as usual

```

## Creating a superuser (admin user)

- Stop the server `ctrl+c`
- Create superuser `python manage.py createsuperuser`
- You can now login to the admin area of your app by going to `http://localhost:8000/admin`

## Creating users through the API

Let's install PyJWT, a Python library that provides tools for encoding and decoding JSON Web Tokens (JWTs). JWTs are a compact, URL-safe means of representing claims between two parties. They are commonly used for authentication and information exchange in web applications. PyJWT will help us implement token-based authentication in our API.

```sh
pipenv install pyjwt
```

1. Lets create a file that will handle our authentication flow. Create a new file in the authentication folder called `authentication.py`

fill out auth file:

```python
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.conf import settings # show secret key in settings.py
import jwt

User = get_user_model()

# BasicAuthentication has stuff built in like password & email validation

class JWTAuthentication(BasicAuthentication): # assertain users permissions # requests come through here # assign a permission level # if valid token -> given permission to see secure things
    def authenticate(self, request): # check requets has token and return if so
        header = request.headers.get('Authorization')

        # if no headers, just return to end the request
        if not header:
            return None

        # if token is wrong format, throw error
        if not header.startswith('Bearer'):
            raise PermissionDenied(detail='Invalid Auth token')

        # pass all checks, store token in variable
        token = header.replace('Bearer ', '')

        # get payload with users id from token & algorithms
        try:
            # can show https://jwt.io again so they can see the alg and the secret
            # HS256 is default, it will be this unless we specify a different alg when we sign the token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            # find user with that id in db
            user = User.objects.get(pk=payload.get('sub'))
            print('USER ->', user)
            # issue with the token

        # if we get an error when decoding it will fall into the below exception
        except jwt.exceptions.InvalidTokenError:
            raise PermissionDenied(detail='Invalid Token')

        # If the user does not exist it will fall into the below
        except User.DoesNotExist:
            raise PermissionDenied(detail='User Not Found')

        # if all good, return user and the token
        return (user, token)
```

2. We now need to add REST_FRAMEWORK into the `project/settings.py`:

The first part is telling Django to render in JSON, although the serializers are doing this for us we can confirm here.
Second part is telling rest_framework and django that we are using the JWTAuthentication class we just created as the default

```python
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'authentication.authentication.JWTAuthentication'
        ],
}
```

3. Let's create the serializer for a user. In the authentication folder, create a `serializers.py` file.

Here we'll create our serializer but add a function called validate to run our validation checks

```python
from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation # function runs when creating superuser
from django.contrib.auth.hashers import make_password # hashes password for us
from django.core.exceptions import ValidationError

User = get_user_model()

class UserSerializer(serializers.ModelSerializer): # never converted to json and returned in response
    password = serializers.CharField(write_only=True) # write_only=True ensures never sent back in JSON
    password_confirmation = serializers.CharField(write_only=True)

    # validate function is going to:
    # check our passwords match
    # hash our passwords
    # add back to database
    def validate(self, data): # data comes from the request body
        print('DATA',data)
        # remove fields from request body and save to vars
        password = data.pop('password')
        password_confirmation = data.pop('password_confirmation')

        # check if they match
        if password != password_confirmation:
            raise ValidationError({'password_confirmation': 'do not match'})

        # checks if password is valid, comment this out so it works
        try:
            password_validation.validate_password(password=password)
        except ValidationError as err:
            print('VALIDATION ERROR')
            raise ValidationError({ 'password': err.messages })

        # hash the password, reassigning value on dict
        data['password'] = make_password(password)

        print('DATA ->', data)
        return data

    class Meta:
        model = User
        fields = '__all__'
```

4. Now let's make the view for registering a user. In `authentication/views.py` add this class:

```python
from rest_framework.views import APIView # main API controller class
from rest_framework.response import Response #response class, like res object in express
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from datetime import datetime, timedelta # creates timestamps in dif formats
from django.contrib.auth import get_user_model # gets user model we are using
from django.conf import settings # import our settings for our secret
from .serializers import UserSerializer
import jwt # import jwt

User = get_user_model() # Save user model to User var

class RegisterView(APIView):

    def post(self, request):
        user_to_create = UserSerializer(data=request.data)
        print('USER CREATE', user_to_create)
        if user_to_create.is_valid():
            user_to_create.save()
            return Response({'message': 'Registration successful'}, status=status.HTTP_202_ACCEPTED)
        return Response(user_to_create.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
```

5. Now let's create the file for our auth URLS. Create `authentication/urls.py` and add this code to it:

```python
from django.urls import path
from .views import RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view())
]
```

6. Add the authentication urls to the `project/urls.py`

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls'))
]
```

7. Start the app and test the endpoint with a tool such as postman:

```bash
python manage.py runserver
```

- endpoint: http://localhost:8000/auth/register
- req method: POST
- req body:

```json
{
  "email": "testuser@test.com",
  "password": "TestPassword!1",
  "password_confirmation": "TestPassword!1",
  "first_name": "test_firstname",
  "last_name": "test_lastname",
  "profile_image": "some_random_string",
  "username": "test_username"
}
```

If everything is working, you should see "registration successfull" in the response.

## ADD THE LOGIN VIEW

1. Go to `authentication/views.py and add the login class under the register class:

```python
class LoginView(APIView):

    def post(self, request):
        # get data from the request
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user_to_login = User.objects.get(email=email) # get user with email
        except User.DoesNotExist:
            raise PermissionDenied(detail='Invalid Credentials') # throw error
        if not user_to_login.check_password(password):
            raise PermissionDenied(detail='Invalid Credentials')

        # timedelta can be used to calculate the difference between dates - passing 7 days gives you 7 days represented as a date that we can add to datetime.now() to get the date 7 days from now
        dt = datetime.now() + timedelta(days=7) # validity of token
        token = jwt.encode(
            {'sub': str(user_to_login.id), 'exp': int(dt.strftime('%s'))}, # strftime -> string from time and turning it into a number
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        return Response({ 'token': token, 'message': f"Welcome back {user_to_login.username}"})
```

2. Now go to `authentication/urls.py` and add a url for loggin in.

```python
from django.urls import path
from .views import RegisterView, LoginView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view())
]
```

3. test the endpoint:

- endpoint: http://localhost:8000/auth/login
- req method: POST
- req body:

```json
{
  "email": "testuser@test.com",
  "password": "TestPassword!1"
}
```

If everything is working, you should see the token and a message "Welcome back test_username" being returned.

# Adding The Books App

1. Let's create the books app:

```bash
django-admin startapp books
```

2. Add it to the list of installed apps in the `project/settings.py`

<div>
    <img src="./images/books-installed.png" width="500px" />
</div>

3. Create the model in `books/models.py`

```python
from django.db import models

# Create your models here.
class Book(models.Model):
    def __str__(self):
        return f'{self.title} - {self.author}'

    # models.CharField is the data type and means "string"
    title = models.CharField(max_length=80, unique=True)
    author = models.CharField(max_length=80)
    genre = models.CharField(max_length=60)
    year = models.FloatField()
    owner = models.ForeignKey(
        "authentication.User",
        related_name = "books",
        on_delete = models.CASCADE
    )
```

4. Register the model in the `books/admin.py`

```python
from django.contrib import admin

# Register your models here.
from .models import Book

admin.site.register(Book)
```

5. Inside the books folder create a new file called `serializers.py`

> We need a serializer to convert python objects into JSON

- In the `serializers.py` file add these imports:

```python
from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
  class Meta:
    model = Book
    fields = '__all__'
```

6. Next we will create the views in `books/views.py`. We will start with the GET method to retrieve all books.

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Book
from .serializers import BookSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly # IsAuthenticatedOrReadOnly specifies that a view is secure on all methods except get requests

# Create your views here.

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
```

7. Make a new file called `urls.py` . Add the imports for the views and the path for the index/list view:

```python
from django.urls import path
from .views import BookListView

urlpatterns = [
  path('', BookListView.as_view()),
]
```

8. inside `project/urls.py` add the books urls

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('books/', include('books.urls')),
]
```

9. With the app running, test the endpoint with a tool such as postman:

- endpoint: http://localhost:8000/auth/books
- req method: GET

if everything is working, you should see an empty list of books being returned with a 200 status code.

# Creating a book - POST method

1. Go to your `books/views.py` and add this function in the BooksListView:

```python
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
```

2. With the app running, test the endpoint with a tool such as postman:

Make sure the owner is a valid user id.

- endpoint: http://localhost:8000/auth/books
- req method: POST
- req body:

```json
{
  "title": "test_title",
  "author": "test_author",
  "genre": "test_genre",
  "year": 2025
}
```

if everything is working, you should see the new book returned, including the "owner".

# Handling a Single Book

1. In the `books/views.py`, add the BookDetailView class. This will handle GET, PUT and DELETE methods for a single book (read, update and delete).

> you will also need to add the NotFound class to the imports, so the entire file will now look like this:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound

from .models import Book
from .serializers import BookSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly # IsAuthenticatedOrReadOnly specifies that a view is secure on all methods except get requests

# Create your views here.

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

class BookDetailView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, ) # sets the permission levels of the specific view by passing in the rest framework authentication class

    # custom method to retrieve a book from the DB and error if it's not found
    def get_book(self, pk):
        try:
            return Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            raise NotFound(detail="Can't find that book") # <-- import the NotFound exception from rest_framwork.exceptions

    def get(self, _request, pk):
        try:
            book = Book.objects.get(pk=pk)
            serialized_book = BookSerializer(book)
            return Response(serialized_book.data, status=status.HTTP_200_OK)
        except Book.DoesNotExist:
            raise NotFound(detail="Can't find that book") # <-- import the NotFound exception from rest_framwork.exceptions

    def put(self, request, pk):
        book_to_update = self.get_book(pk=pk)
        if book_to_update.owner != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        updated_book = BookSerializer(book_to_update, data=request.data)
        if updated_book.is_valid():
            updated_book.save()
            return Response(updated_book.data, status=status.HTTP_202_ACCEPTED)

        return Response(updated_book.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def delete(self, request, pk):
        book_to_delete = self.get_book(pk=pk)

        if book_to_delete.owner != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        book_to_delete.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

2. Add a url to the `books/urls.py`:

```python
from django.urls import path
from .views import BookListView, BookDetailView

urlpatterns = [
  path('', BookListView.as_view()),
  path('<int:pk>/', BookDetailView.as_view()),
]
```

3. With the app running, test the endpoints with a tool such as postman:

Start with fetching a single book:

- endpoint: http://localhost:8000/auth/books/1/
- req method: GET

if everything is working, you should see the book returned.

Now test the update method:

- endpoint: http://localhost:8000/auth/books/1/
- req method: PUT
- req body

```json
{
  "id": 1,
  "title": "updated_title",
  "author": "updated_author",
  "genre": "updated_genre",
  "year": 2025.0,
  "owner": 1
}
```

if everything is working, you should see the updated book returned.

Now test the delete method:

- endpoint: http://localhost:8000/auth/books/1/
- req method: DELETE

# Adding the Authors app

1. Let's create the Authors App with the command `django-admin startapp authors`

```sh
django-admin startapp authors
```

2. Register the authors app in installed apps in `project/settings.py`

<div>
    <img src="./images/installed-authors.png" width="500px" />
</div>

3. Create the Author model in `authors/models.py`

```python
from django.db import models

# Create your models here.
class Author(models.Model):
    def __str__(self):
        return f'{self.name}'

    name = models.CharField(max_length=80, unique=True)
```

4. Register the model in `authors/admin.py`

```python
from django.contrib import admin

# Register your models here.
from .models import Author

admin.site.register(Author)
```

5. Update the Book model (`books/models.py`) to now use a ForeignKey for the author.

```python
from django.db import models

# Create your models here.
class Book(models.Model):
    def __str__(self):
        return f'{self.title} - {self.author}'

    # models.CharField is the data type and means "string"
    title = models.CharField(max_length=80, unique=True)
    author = models.ForeignKey(
        "authors.Author",
        related_name = "books",
        on_delete = models.CASCADE
    )
    genre = models.CharField(max_length=60)
    year = models.FloatField()
    owner = models.ForeignKey(
        "authentication.User",
        related_name = "books",
        on_delete = models.CASCADE
    )
```

6. Make migrations and migrate. MAKE SURE YOU DELETE ALL YOUR BOOKS BEFORE YOU DO THIS. YOU CAN DO THIS EASILY IN THE ADMIN APP.

```sh
python manage.py makemigrations &&
python manage.py migrate
```

6. Create the authors serializer - create the `serializers.py` file in the authors folder and put in this code:

```python
from rest_framework import serializers
from .models import Author

class AuthorSerializer(serializers.ModelSerializer):
  class Meta:
    model = Author
    fields = '__all__'
```

7. Create the views in `authors/views.py`

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound # This provides a default response for a not found

from .models import Author
from .serializers import AuthorSerializer

# Create your views here.

class AuthorListView(APIView):

    # handle a GET request in the BookListView
    def get(self, _request):
        # go to the database and get all the authors
        authors = Author.objects.all()
        # translate the books from the database to a usable form
        serialized_authors = AuthorSerializer(authors, many=True)
        # return the serialized data and a 200 status code
        return Response(serialized_authors.data, status=status.HTTP_200_OK)

    def post(self, request):
        author_to_add = AuthorSerializer(data=request.data)
        try:
           author_to_add.is_valid()
           author_to_add.save()
           return Response(author_to_add.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Error")
            # the below is necessary because two different formats of errors are possible. string or object format.
            # if it's string then e.__dict__ returns an empty dict {}
            # so we'll check it's a dict first, and if it's empty (falsey) then we'll use str() to convert to a string
            return Response(e.__dict__ if e.__dict__ else str(e), status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class AuthorDetailView(APIView):

    def get_author(self, pk):
        try:
            return Author.objects.get(pk=pk)
        except Author.DoesNotExist:
            raise NotFound(detail="Can't find that author")

    def get(self, request, pk):
        author = self.get_author(pk=pk)
        serialized_author = AuthorSerializer(author)
        return Response(serialized_author.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        author_to_update = self.get_author(pk=pk)
        updated_author = AuthorSerializer(author_to_update, data=request.data)

        if updated_author.is_valid():
            updated_author.save()
            return Response(updated_author.data, status=status.HTTP_202_ACCEPTED)
        return Response(updated_author.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def delete(self, _request, pk):
        author_to_delete = self.get_author(pk=pk)
        author_to_delete.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

8. Create the `urls.py` file in the authors folder, then add the urls code:

```python
from django.urls import path
from .views import AuthorListView, AuthorDetailView

urlpatterns = [
  path('', AuthorListView.as_view()),
  path('<int:pk>/', AuthorDetailView.as_view()),
]
```

9. Add the `authors/urls.py` to the `project/urls.py`.

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('books/', include('books.urls')),
    path('authors/', include('authors.urls')),
]
```

10. With the app running, test the endpoints with a tool such as postman:

Start with creating an author:

- endpoint: http://localhost:8000/auth/authors/
- req method: POST
- req body:

```json
{
  "name": "test author"
}
```

if everything is working, you should see the new author returned with their ID.

Now test the GET method:

- endpoint: http://localhost:8000/auth/authors/
- req method: GET

if everything is working, you should see the list of authors returned (it should only contain the one you created in the previos step at this point).

Now test creating the book, using the newly created authors ID as the author key for the book data:

- endpoint: http://localhost:8000/auth/books/
- req method: POST
- req body:

```json
{
  "title": "test_title",
  "author": 1,
  "genre": "test_genre",
  "year": 2025
}
```

If everything is working, you should see the new book returned and it should look something like this:

```json
{
  "id": 1,
  "title": "test_title",
  "genre": "test_genre",
  "year": 2025.0,
  "author": 1,
  "owner": 1
}
```

Now test the "get by id" endpoint:

- endpoint: http://localhost:8000/auth/authors/1/
- req method: GET

Now test the update author endpoint:

- endpoint: http://localhost:8000/auth/authors/1/
- req method: PUT
- req body:

```json
{
  "name": "updated author"
}
```

And finally, test the delete method.

- endpoint: http://localhost:8000/auth/authors/1/
- req method: DELETE

You should notice that the books associated with the author have been deleted, due to the models.CASCADE in the model.

You'll want to create a new author and book so you have some data to play around with going forward with the next steps.

# Populating the author key when retrieving books

1. Before we start this, let's organize our serializers into separate files. This is important because when we want to populate fields with nested data (like showing the full author object when retrieving a book), we can run into circular import dependencies. By separating our serializers into different files, we can:

- Keep our base/common serializers separate from populated serializers
- Avoid circular imports where serializers depend on each other
- Make our code more modular and maintainable
- Enable different serialization formats for different use cases

Let's start by restructuring our serializers:

- create a serializers folder inside the books folder
- create a file called `common.py` inside the serializers folder
- copy the existing code from `books/serializers.py` into `common.py` - you'll need to update the import of the model to `from ..models import Book`
- In `books/views.py`, update the import of the serializer to this: `from .serializers.common import BookSerializer`
- delete `books/serializers.py`

Now Recreate this folder/file structure for the authors serializers. We will do this now to make our lives easier in the coming steps.

- create a serializers folder inside the authors folder
- create a file called `common.py` inside the serializers folder
- copy the existing code from `authors/serializers.py` into `common.py` - you'll need to update the import of the model to `from ..models import Book`
- In `authors/views.py`, update the import of the serializer to this: `from .serializers.common import AuthorSerializer`
- delete `authors/serializers.py`

We won't need a populated serializer for users, so we can leave the users serializers as they are.

2. Now we can safely start using populated serializers. Create a file called `populated.py` in the books/serializers folder. Put this code inside it:

```python
from .common import BookSerializer
from authors.serializers.common import AuthorSerializer
from authentication.serializers import UserSerializer

class PopulatedBookSerializer(BookSerializer):
    author = AuthorSerializer()
    owner = UserSerializer()
```

3. Now we can update the BookDetailView to use the PopulatedBookSerializer, which will populate the author and owner data when we call it. Update the `books/views.py` to import the populated serializer and use it when we call the get function in the BookDetailView:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound

from .models import Book
from .serializers.common import BookSerializer
from .serializers.populated import PopulatedBookSerializer # <-- add this import
from rest_framework.permissions import IsAuthenticatedOrReadOnly

# Create your views here.

class BookListView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    def get(self, _request):
        books = Book.objects.all()
        serialized_books = BookSerializer(books, many=True)
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
            return Response(e.__dict__ if e.__dict__ else str(e), status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class BookDetailView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get_book(self, pk):
        try:
            return Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            raise NotFound(detail="Can't find that book")

    def get(self, _request, pk):
        try:
            book = Book.objects.get(pk=pk)
            serialized_book = PopulatedBookSerializer(book) # <-- use the populate serializer here
            return Response(serialized_book.data, status=status.HTTP_200_OK)
        except Book.DoesNotExist:
            raise NotFound(detail="Can't find that book")

    def put(self, request, pk):
        book_to_update = self.get_book(pk=pk)
        if book_to_update.owner != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        updated_book = BookSerializer(book_to_update, data=request.data)
        if updated_book.is_valid():
            updated_book.save()
            return Response(updated_book.data, status=status.HTTP_202_ACCEPTED)

        return Response(updated_book.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def delete(self, request, pk):
        book_to_delete = self.get_book(pk=pk)

        if book_to_delete.owner != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        book_to_delete.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

# Populating the books key when retrieving authors

1. Create a file called `populated.py` in the authors/serializers folder. Put this code inside it:

```python
from .common import AuthorSerializer
from books.serializers.common import BookSerializer

class PopulatedAuthorSerializer(AuthorSerializer):
    books = BookSerializer(many=True)
```

3. Now we can update the AuthorDetailView to use the PopulatedAuthorSerializer, which will populate the booksdata when we call it. Update the `authors/views.py` to import the populated serializer and use it when we call the get function in the AuthorDetailView:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound

from .models import Author
from .serializers.common import AuthorSerializer
from .serializers.populated import PopulatedAuthorSerializer # <-- import the populated serializer

# Create your views here.

class AuthorListView(APIView):

    def get(self, _request):
        authors = Author.objects.all()
        serialized_authors = AuthorSerializer(authors, many=True)
        return Response(serialized_authors.data, status=status.HTTP_200_OK)

    def post(self, request):
        author_to_add = AuthorSerializer(data=request.data)
        try:
           author_to_add.is_valid()
           author_to_add.save()
           return Response(author_to_add.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Error")
            return Response(e.__dict__ if e.__dict__ else str(e), status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class AuthorDetailView(APIView):

    def get_author(self, pk):
        try:
            return Author.objects.get(pk=pk)
        except Author.DoesNotExist:
            raise NotFound(detail="Can't find that author")

    def get(self, request, pk):
        author = self.get_author(pk=pk)
        serialized_author = PopulatedAuthorSerializer(author) # <-- use the populated serializer here
        return Response(serialized_author.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        author_to_update = self.get_author(pk=pk)
        updated_author = AuthorSerializer(author_to_update, data=request.data)

        if updated_author.is_valid():
            updated_author.save()
            return Response(updated_author.data, status=status.HTTP_202_ACCEPTED)
        return Response(updated_author.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def delete(self, _request, pk):
        author_to_delete = self.get_author(pk=pk)
        author_to_delete.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

4. With the app running, test the endpoint with a tool such as postman:

- endpoint: http://localhost:8000/auth/authors/2/
- req method: GET

If everything is working, you should see the author returned and this time, there should also be the books that the author has authored.

# Adding the Comments app

1. Let's create the comments app with the command `django-admin startapp comments`

```sh
django-admin startapp comments
```

2. Register the comments app in installed apps in `project/settings.py`

<div>
    <img src="./images/installed-comments.png" width="500px" />
</div>

3. Create the Comment model in `comments/models.py`

```python
from django.db import models

# Create your models here.

class Comment(models.Model):
    def __str__(self):
        return f'{self.text} - {self.book}'

    text = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    book = models.ForeignKey(
        "books.Book",
        related_name = "comments",
        on_delete=models.CASCADE
    )
    owner = models.ForeignKey( # if you call it user, I think it can clash with django fields so I tend to use owner
        "authentication.User",
        related_name="comments",
        on_delete=models.CASCADE,
    )
```

4. Register the model in `comments/admin.py`

```python
from django.contrib import admin

# Register your models here.
from .models import Comment

admin.site.register(Comment)
```

6. Make migrations and migrate.

```sh
python manage.py makemigrations &&
python manage.py migrate
```

6. Create the comments serializers folder and inside it, create a `common.py` and a `populated.py`.

in the `common.py`, put this code:

```python
from rest_framework import serializers
from ..models import Comment

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
```

in the `populated.py` put this code:

```python
from .common import CommentSerializer
from authentication.serializers import UserSerializer

class PopulatedCommentSerializer(CommentSerializer):
    owner = UserSerializer()
```

7. Create the views in `comments/views.py`

```python
from rest_framework.views import APIView # this imports rest_frameworks APIView that we'll use to extend to our custom view
from rest_framework.response import Response # Response gives us a way of sending a http response to the user making the request, passing back data and other information
from rest_framework.exceptions import NotFound
from rest_framework import status # status gives us a list of official/possible response codes

from .models import Comment
from .serializers.common import CommentSerializer
from rest_framework.permissions import IsAuthenticated

class CommentListView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        print("CREATING COMMMENT USER ID", request.user.id)
        request.data["owner"] = request.user.id
        comment_to_add = CommentSerializer(data=request.data)
        try:
            comment_to_add.is_valid()
            comment_to_add.save()
            return Response(comment_to_add.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Error")
            return Response(e.__dict__ if e.__dict__ else str(e), status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class CommentDetailView(APIView):
    permission_classes = (IsAuthenticated,) # only get here if you are signed in

    def get_comment(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            raise NotFound(detail="Can't find that Comment")

    def get(self, request, pk):
        comment = self.get_comment(pk=pk)
        serialized_comment = CommentSerializer(comment)
        return Response(serialized_comment.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        comment_to_update = self.get_comment(pk=pk)

        # request has been through the authentication process. It started as request.
        # request was sent with a token.
        #  token was checked, and the user was found.
        #  user was added to the request.
        if comment_to_update.owner != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        updated_comment = CommentSerializer(comment_to_update, data=request.data)

        if updated_comment.is_valid():
            updated_comment.save()
            return Response(updated_comment.data, status=status.HTTP_202_ACCEPTED)

        return Response(updated_comment.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


    def delete(self, request, pk):
        comment_to_delete = self.get_comment(pk=pk)

        if comment_to_delete.owner != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        comment_to_delete.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

8. Create the `urls.py` file in the comments folder, then add the urls code:

```python
from django.urls import path
from .views import CommentListView, CommentDetailView

urlpatterns = [
  path('', CommentListView.as_view()),
  path('<int:pk>/', CommentDetailView.as_view()),
]
```

9. Add the `comments/urls.py` to the `project/urls.py`.

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('books/', include('books.urls')),
    path('authors/', include('authors.urls')),
    path('comments/', include('comments.urls')),
]
```

10. With the app running, test the endpoints with a tool such as postman:

Start with creating a comment:

- endpoint: http://localhost:8000/comments/
- req method: POST
- req body:

```json
{
  "text": "test comment",
  "book": 2,
  "owner": 1
}
```

You can test the other comments endpoints with postman, such as the "get by id", update, and delete methods.

# Populating comments on books

1. Let's add the comments to books when we retrieve them. Update the `books/serializers/populated.py` to this:

```python
from .common import BookSerializer
from authors.serializers.common import AuthorSerializer
from authentication.serializers import UserSerializer
from comments.serializers.populated import PopulatedCommentSerializer

class PopulatedBookSerializer(BookSerializer):
    author = AuthorSerializer()
    owner = UserSerializer()
    comments = PopulatedCommentSerializer(many=True)
```

Now when you make a GET request to get a book by its ID, you should also see the comments. As it uses the populated comment serializer, you also get to see the user that created the comment populated within the comment data.

# Controlling what we expose on the user

1. You'll notice that anywhere we have been populating the user, we are able to see all the user data. We prefer to explicitly define which fields we want to expose in our serializers rather than using fields="**all**". This gives us precise control over what user data gets sent back in responses. For example, we don't want to expose sensitive information like password hashes, security questions, or other private user data that could pose security risks if exposed. By listing out exactly which fields we want (id, email, username, etc.), we ensure only the necessary user information is shared.

```python
from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation # function runs when creating superuser
from django.contrib.auth.hashers import make_password # hashes password for us
from django.core.exceptions import ValidationError

User = get_user_model()

class UserSerializer(serializers.ModelSerializer): # never converted to json and returned in response
    password = serializers.CharField(write_only=True) # write_only=True ensures never sent back in JSON
    password_confirmation = serializers.CharField(write_only=True)

    # validate function is going to:
    # check our passwords match
    # hash our passwords
    # add back to database
    def validate(self, data): # data comes from the request body
        print('DATA',data)
        # remove fields from request body and save to vars
        password = data.pop('password')
        password_confirmation = data.pop('password_confirmation')

        # check if they match
        if password != password_confirmation:
            raise ValidationError({'password_confirmation': 'do not match'})

        # checks if password is valid, comment this out so it works
        try:
            password_validation.validate_password(password=password)
        except ValidationError as err:
            print('VALIDATION ERROR')
            raise ValidationError({ 'password': err.messages })

        # hash the password, reassigning value on dict
        data['password'] = make_password(password)

        print('DATA ->', data)
        return data

    class Meta:
        model = User
        # We explicitly define fields rather than using fields="__all__" to control exactly what user data is exposed
        # This prevents accidentally exposing sensitive fields like password hash or security questions
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'profile_image', 'password', 'password_confirmation')
```

# Handling CORS in Django

Currently our api works and we can make request from postman. Postman is different to a browser. Browsers need to contend with something called CORS (Cross Origin Resource Sharing). Essentially, apis by default want the incoming requests to come from the server that the API is hosted on, or at least another back end server. Browsers are less safe, so there's extra steps put in place to lock them out. Postman mocks this behaviour, which is why you'll sometimes be able to call a 3rd party api from postman, but not from a browser.

We need to tell our Django app that it's ok to accept incoming requests from other servers. This is how we do it:

1. Let's install a package called `django-cors-headers`:

```sh
pipenv install django-cors-headers
```

2. Add it to your installed apps in `project/settings.py`

<div>
    <img src="./images/installed-corsheaders.png" width="500px" />
</div>

Add these lines to the middleware list in `project/settings.py`:

```python
MIDDLEWARE = [
    ...,
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    ...,
]
```

Finally, let's set where the requests can come from. We are going to allow requests to come from anywhere, so let's add this into our `project/settings.py` file:

```python
CORS_ALLOW_ALL_ORIGINS = True
```

Go to the `project/urls.py` and add /api to the beginning of all your routes (except the admin routes):

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/books/', include('books.urls')),
    path('api/authors/', include('authors.urls')),
    path('api/comments/', include('comments.urls')),
]
```

Congratulations, you've created a Django/Python API using Django Rest Framework (DRF), with 4 data entities (users, books, authors & comments) and exposes it's endpoints so it can be consumed from any front end application (like react.js)

Next up, create a front end to complete building your full stack application!
