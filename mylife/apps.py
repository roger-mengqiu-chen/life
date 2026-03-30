from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mylife'

    def ready(self):
        # Import plotly_app after Django is fully loaded
        from . import plotly_app  # noqa

