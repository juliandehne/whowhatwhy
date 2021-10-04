from django.apps import AppConfig


class TwitterConfig(AppConfig):
    name = 'twitter'

    # this is so magic...
    def ready(self):
        pass
