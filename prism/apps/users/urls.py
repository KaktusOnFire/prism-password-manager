from django.urls import path

from .views import CreateUserView, ResetUserView, \
    PasswordView, EncryptionKeyView, \
    ProfileView, UsersView

app_name = 'users'
urlpatterns = [
    #Common urls
    path('profile', ProfileView.as_view(), name="profile"),
    path('password', PasswordView.as_view(), name="password"),
    path('key/', EncryptionKeyView.as_view(), name="key"),

    #Admin urls
    path('manager', UsersView.as_view(), name="manager"),
    path('create', CreateUserView.as_view(), name="create"),
    path('edit/<uuid:pk>', ResetUserView.as_view(), name="edit"),
]