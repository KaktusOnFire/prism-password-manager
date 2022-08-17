from django.contrib import admin
from .models import EncryptedPassword, EncryptedSocialAccount, EncryptedSSHKeypair
# Register your models here.

admin.site.register(EncryptedPassword)
admin.site.register(EncryptedSocialAccount)
admin.site.register(EncryptedSSHKeypair)