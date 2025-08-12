from django.apps import AppConfig


class OhcSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'OHC_System'

    def ready(self):
        """Import and connect signal handlers."""
        import OHC_System.signals
