from django.apps import AppConfig

from django.db.models.signals import post_save

from user.signals import send_confirmation_email


class UserConfig(AppConfig):
    name = 'user'

    def ready(self):
        post_save.connect(send_confirmation_email, sender='user.User')
