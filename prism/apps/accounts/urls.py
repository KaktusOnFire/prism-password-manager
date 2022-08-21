from django.urls import path, include
from .views import LoginView, LogoutView, EncryptionKeyView

app_name = 'accounts'
urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('key/', EncryptionKeyView.as_view(), name="key"),
]
