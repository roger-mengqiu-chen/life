import logging
import os
from pathlib import Path
from django.apps import AppConfig
from django.db.backends.signals import connection_created

logger = logging.getLogger(__name__)


def load_sqlite_extension(connection, **kwargs):
    if connection.vendor != 'sqlite':
        return

    base_dir = os.path.dirname(os.path.dirname(Path(__file__).resolve()))
    extension_path = os.path.join(base_dir, 'sqlite_extensions', 'vec1.so')

    raw_connection = connection.connection
    if hasattr(raw_connection, 'enable_load_extension'):
        try:
            raw_connection.enable_load_extension(True)
            raw_connection.load_extension(extension_path)
            raw_connection.enable_load_extension(False)  # Turn off after loading for security
        except Exception as e:
            logger.warning(f"Could not load SQLite extension '{extension_path}': {e}")
    else:
        logger.warning(
            "SQLite load extension is not enabled in this Python's sqlite3 build. "
            "Install pysqlite3-binary or rebuild Python with --enable-loadable-sqlite-extensions."
        )


class MyLifeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mylife'

    def ready(self):
        connection_created.connect(load_sqlite_extension)

        # Fix compatibility between django-plotly-dash's PseudoFlask and Dash >= 2.16
        try:
            from django_plotly_dash.dash_wrapper import PseudoFlask
            PseudoFlask.secret_key = None
        except ImportError:
            pass

        # Load dash apps so they are registered in django-plotly-dash
        try:
            import mylife.dashboard.dashboard  # noqa: F401
        except ImportError:
            pass
