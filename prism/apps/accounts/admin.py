from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import PrismUserCreationForm, PrismUserChangeForm
from .models import PrismUser

class PrismUserAdmin(UserAdmin):
    add_form = PrismUserCreationForm
    form = PrismUserChangeForm
    model = PrismUser
    list_display = ['username', 'email',]

admin.site.register(PrismUser, PrismUserAdmin)