from django.db import models
from django.utils.translation import gettext_lazy as _

import uuid

from cryptography.fernet import Fernet, MultiFernet

from apps.users.models import PrismUser

class CryptoManager:
    
    @staticmethod
    def create_pkey():
        return Fernet.generate_key()

    @staticmethod
    def change_pkey(pkey_new, pkey_old, tokens):
        fr = MultiFernet([Fernet(pkey_new), Fernet(pkey_old)])
        rotated = map(fr.rotate, tokens)

        fr = MultiFernet([Fernet(pkey_new)])
        rotated = map(fr.rotate, tokens)
        return rotated

    @staticmethod
    def encrypt(pkey, token):
        f = Fernet(pkey)
        return str(f.encrypt(bytes(token, 'utf-8')), encoding='utf-8')

    @staticmethod
    def decrypt(pkey, token):
        f = Fernet(pkey)
        return str(f.decrypt(bytes(token, 'utf-8')), encoding='utf-8')

class BaseEncryptedObject(models.Model):
    """
    Base class for all encrypted models
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("Title"), max_length=500)
    owner = models.ForeignKey(to=PrismUser, on_delete=models.CASCADE)
    date_created = models.DateTimeField(_('Date created'), auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def __repr__(self):
        return self.title
        
    class Meta:
        abstract = True
