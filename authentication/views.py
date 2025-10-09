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

