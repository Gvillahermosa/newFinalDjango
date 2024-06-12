from django.apps import AppConfig


class StudentlifeSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'studentLife_system'

    def ready(self):
        import studentLife_system.signals
