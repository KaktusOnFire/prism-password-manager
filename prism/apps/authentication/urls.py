from django.urls import path
from django.conf import settings

from .views import LoginView, LogoutView, SignUpView

app_name = 'authentication'
urlpatterns = [
    #Common urls
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
]

if settings.REGISTRATION_ENABLED:
    urlpatterns += path('register/', SignUpView.as_view(), name="register"),