from django.urls import path, include
from django.contrib.auth import views as authViews

from core.controllers import home

urlpatterns = [
    path('login/',authViews.LoginView.as_view(template_name="registration/login.html"),name="login"),
    path('logout/',authViews.LogoutView.as_view(),name='logout'),
    path('change_password/',authViews.PasswordChangeView.as_view(),name="change Password"),
    path('home/',home.home,name="home")
]