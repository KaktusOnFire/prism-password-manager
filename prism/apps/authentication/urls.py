from django.urls import path
from django.conf import settings

from .views import LoginView, LogoutView, SignUpView, AccountActivateView

app_name = 'authentication'
urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
]

if settings.REGISTRATION_ENABLED:
    urlpatterns += path('register/', SignUpView.as_view(), name="register"),
    urlpatterns += path('activate/<slug:uidb64>/<slug:token>/', AccountActivateView.as_view(), name='activate'),