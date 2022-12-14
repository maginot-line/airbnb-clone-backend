from django.urls import path
from . import views

urlpatterns = [
    path("", views.Users.as_view()),
    path("me", views.Me.as_view()),
    path("change-password", views.ChangePassword.as_view()),
    path("log-in", views.LogIn.as_view()),
    path("log-out", views.LogOut.as_view()),
    path("github", views.GithubLogin.as_view()),
    path("kakao", views.KakaoLogin.as_view()),
    path("sign-in", views.SignIn.as_view()),
    path("@<str:username>", views.PublicUser.as_view()),
]
