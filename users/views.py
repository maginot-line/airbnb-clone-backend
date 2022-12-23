import jwt
import requests
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from users.models import User
from .serializers import PrivateUserSerializer

# Create your views here.
class Me(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):
    user = request.user
    serializer = PrivateUserSerializer(user)
    return Response(serializer.data)

  def put(self, request):
    user = request.user
    serializer = PrivateUserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
      user = serializer.save()
      serializer = PrivateUserSerializer(user)
      return Response(serializer.data)
    else:
      return Response(serializer.errors)


class Users(APIView):
  def post(self, request):
    password = request.data.get('password')
    if not password:
      raise ParseError
    serializer = PrivateUserSerializer(data=request.data)
    if serializer.is_valid():
      user = serializer.save()
      user.set_password(password)
      user.save()
      serializer = PrivateUserSerializer(user)
      return Response(serializer.data)
    else:
      return Response(serializer.errors)


class PublicUser(APIView):
  def get(self, request, username):
    try:
      user = User.objects.get(username=username)
    except User.DoesNotExist:
      raise NotFound
    serializer = PrivateUserSerializer(user)
    return Response(serializer.data)


class ChangePassword(APIView):
  permission_classes = [IsAuthenticated]

  def put(self, request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    if not old_password or not new_password:
      raise ParseError
    if user.check_password(old_password):
      user.set_password(new_password)
      user.save()
      return Response(status=HTTP_200_OK)
    else:
      raise ParseError


class LogIn(APIView):
  def post(self, request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
      raise ParseError
    user = authenticate(request, username=username, password=password)
    if user:
      login(request, user)
      return Response({'ok': 'Welcome'})
    else:
      return Response({'error': 'wrong password'}, status=HTTP_400_BAD_REQUEST)


class LogOut(APIView):
  permission_classes = [IsAuthenticated]

  def post(self, request):
    logout(request)
    return Response({'ok': 'bye!'})


class JWTLogIn(APIView):
  def post(self, request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
      raise ParseError
    user = authenticate(request, username=username, password=password)
    if user:
      token = jwt.encode({'pk': user.pk}, settings.SECRET_KEY, algorithm='HS256')
      return Response({'token': token})
    else:
      return Response({'error': 'wrong password'})


class GithubLogin(APIView):
  def post(self, request):
    try:
      code = request.data.get('code')
      access_token = requests.post(
          f'https://github.com/login/oauth/access_token?code={code}&client_id=edd37c5f10e12db8f49e&client_secret={settings.GH_SECRET}',
          headers={'Accept': 'application/json'},
          timeout=3,
      )
      access_token = access_token.json().get('access_token')
      user_data = requests.get(
          'https://api.github.com/user',
          headers={
              'Authorization': f'Bearer {access_token}',
              'Accept': 'application/json',
          },
          timeout=3,
      )
      user_data = user_data.json()
      user_emails = requests.get(
          'https://api.github.com/user/emails',
          headers={
              'Authorization': f'Bearer {access_token}',
              'Accept': 'application/json',
          },
          timeout=3,
      )
      user_emails = user_emails.json()
      try:
        user = User.objects.get(email=user_emails[0].get('email'))
        login(request, user)
        return Response(status=HTTP_200_OK)
      except User.DoesNotExist:
        user = User.objects.create(
            username=user_data.get('login'),
            email=user_emails[0].get('email'),
            name=user_data.get('name'),
            avatar=user_data.get('avatar_url'),
        )
        user.set_unusable_password()
        user.save()
        login(request, user)
        return Response(status=HTTP_200_OK)
    except Exception:
      return Response(status=HTTP_400_BAD_REQUEST)


class KakaoLogin(APIView):
  def post(self, request):
    try:
      code = request.data.get('code')
      access_token = requests.post(
          'https://kauth.kakao.com/oauth/token',
          headers={'Content-Type': 'application/x-www-form-urlencoded'},
          data={
              'grant_type': 'authorization_code',
              'client_id': '943aa3bb926e136c9fd9f59e6e3f00a1',
              'redirect_uri': 'http://127.0.0.1:3000/social/kakao',
              'code': code,
          },
          timeout=3,
      )
      access_token = access_token.json().get('access_token')
      user_data = requests.get(
          'https://kapi.kakao.com/v2/user/me',
          headers={
              'Authorization': f'Bearer {access_token}',
              'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
          },
          timeout=3,
      )
      user_data = user_data.json()
      kakao_account = user_data.get('kakao_account')
      profile = kakao_account.get('profile')
      try:
        user = User.objects.get(email=kakao_account.get('email'))
        login(request, user)
        return Response(status=HTTP_200_OK)
      except User.DoesNotExist:
        user = User.objects.create(
            email=kakao_account.get('email'),
            username=profile.get('nickname'),
            name=profile.get('nickname'),
            avatar=profile.get('profile_image_url'),
        )
        user.set_unusable_password()
        user.save()
        login(request, user)
        return Response(status=HTTP_200_OK)
    except Exception:
      return Response(status=HTTP_400_BAD_REQUEST)


class SignIn(APIView):
  def post(self, request):
    name = request.data.get('name')
    email = request.data.get('email')
    username = request.data.get('username')
    password = request.data.get('password')
    if not name or not email or not username or not password:
      raise ParseError
    try:
      User.objects.get(email=email)
      return Response(
          {'error': 'email already exists'}, status=HTTP_400_BAD_REQUEST
      )
    except User.DoesNotExist:
      try:
        User.objects.get(username=username)
        return Response(
            {'error': 'username already exists'}, status=HTTP_400_BAD_REQUEST
        )
      except User.DoesNotExist:
        user = User.objects.create_user(
            name=name,
            email=email,
            username=username,
            password=password,
        )
        login(request, user)
        return Response(status=HTTP_200_OK)
