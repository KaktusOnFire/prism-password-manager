from django.urls import path
from .views import SecretsView, \
    CreatePasswordView, EditPasswordView, DeletePasswordView, \
    CreateSocialAccountView, EditSocialAccountView, DeleteSocialAccountView, \
    CreateSSHKeypairView, EditSSHKeypairView, DeleteSSHKeypairView
    

app_name = 'crypto'
urlpatterns = [
    path('create/password', CreatePasswordView.as_view(), name="create_pass"),
    path('create/social', CreateSocialAccountView.as_view(), name="create_social"),
    path('create/ssh', CreateSSHKeypairView.as_view(), name="create_ssh"),

    path('edit/password/<uuid:pk>', EditPasswordView.as_view(), name="edit_pass"),
    path('edit/social/<uuid:pk>', EditSocialAccountView.as_view(), name="edit_social"),
    path('edit/ssh/<uuid:pk>', EditSSHKeypairView.as_view(), name="edit_ssh"),

    path('delete/password/<uuid:pk>', DeletePasswordView.as_view(), name="delete_pass"),
    path('delete/social/<uuid:pk>', DeleteSocialAccountView.as_view(), name="delete_social"),
    path('delete/ssh/<uuid:pk>', DeleteSSHKeypairView.as_view(), name="delete_ssh"),

    path('home/', SecretsView.as_view(), name="home"),
]
