from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from apps.crypto.base import BaseEncryptedObject        

class EncryptedPassword(BaseEncryptedObject):
    """
    Simple password encrypted model
    """
    password = models.TextField(_('Encrypted password'))

    def get_absolute_url(self):
        return reverse('crypto:edit_pass', kwargs={'pk' : self.pk})

    def get_delete_url(self):
        return reverse('crypto:delete_pass', kwargs={'pk' : self.pk})

    class Meta:
        verbose_name = "Password"
        verbose_name_plural = "Passwords"
        ordering = ['-date_created']

class EncryptedSocialAccount(BaseEncryptedObject):
    """
    Social account encrypted model
    """
    login = models.CharField(_('Login'), max_length=250)
    password = models.TextField(_('Encrypted password'))

    def get_absolute_url(self):
        return reverse('crypto:edit_social', kwargs={'pk' : self.pk})

    def get_delete_url(self):
        return reverse('crypto:delete_social', kwargs={'pk' : self.pk})

    class Meta:
        verbose_name = "Social Account"
        verbose_name_plural = "Social Accounts"
        ordering = ['-date_created']

class EncryptedSSHKeypair(BaseEncryptedObject):
    """
    SSH Key pair encrypted model
    """
    public_key = models.TextField(_('Public key'))
    private_key = models.TextField(_('Encrypted Private key'))

    def get_absolute_url(self):
        return reverse('crypto:edit_ssh', kwargs={'pk' : self.pk})

    def get_delete_url(self):
        return reverse('crypto:delete_ssh', kwargs={'pk' : self.pk})

    class Meta:
        verbose_name = "SSH key pair"
        verbose_name_plural = "SSH key pairs"
        ordering = ['-date_created']