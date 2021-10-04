from django.apps import AppConfig


class DelabConfig(AppConfig):
    name = 'delab'

    # def ready(self):
    #    import delab.signals
    def ready(self):
        print("at ready")
        import delab.signals
