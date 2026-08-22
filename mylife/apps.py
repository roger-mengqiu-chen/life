from pathlib import Path
from django.conf import settings
from django.apps import AppConfig

from django.db.backends.signals import connection_created
import os


def load_sqlite_extension(connection, **kwargs):
    if connection.vendor != 'sqlite':
        return

    base_dir = os.path.dirname(os.path.dirname(Path(__file__).resolve()))
    extension_path = os.path.join(base_dir, 'sqlite_extensions', 'vec1.so')

    raw_connection = connection.connection
    raw_connection.enable_load_extension(True)
    raw_connection.load_extension(extension_path)
    raw_connection.enable_load_extension(False)  # Turn off after loading for security


class MyLifeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mylife'

    def ready(self):
        # Fix compatibility between django-plotly-dash's PseudoFlask and Dash >= 2.16
        try:
            from django_plotly_dash.dash_wrapper import PseudoFlask
            PseudoFlask.secret_key = None
        except ImportError:
            pass

        try:
            import mylife.dashboard.dashboard  # noqa: F401
        except ImportError:
            pass
