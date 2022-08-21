from django.urls import path
from django.conf import settings

from .views import LoginView, LogoutView, PasswordView, SignUpView, EncryptionKeyView, ProfileView

import os

app_name = 'accounts'
urlpatterns = [
    path('user/profile', ProfileView.as_view(), name="profile"),
    path('user/password', PasswordView.as_view(), name="password"),
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('key/', EncryptionKeyView.as_view(), name="key"),
]

if settings.REGISTRATION_ENABLED:
    urlpatterns += path('register/', SignUpView.as_view(), name="register"),