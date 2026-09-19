

from django.apps import AppConfig

from django.db import connection


class BlogConfig(AppConfig):
    """
    Application configuration for the 'blog' app.

    This class configures the blog application when Django starts.
    It defines application metadata and initializes app-specific components.

    Key responsibilities:
    - Set default primary key type for models
    - Define application name
    - Execute startup code via ready() method
    - Register signals
    - Verify database connectivity
    """


    default_auto_field = 'django.db.models.BigAutoField'


    name = 'blog'


    def ready(self):
        """
        Application startup method called when Django initializes this app.

        This method is automatically called once when the Django application
        starts (specifically when the app registry is fully populated).

        Execution timing:
        - Called after all models are loaded
        - Called before the request/response cycle begins
        - Only called once during server startup

        Typical use cases for ready() method:
        - Registering signal handlers
        - Starting background threads
        - Validating configuration
        - Pre-loading caches
        - Running startup checks
        - Connecting to external services

        ⚠️ IMPORTANT WARNINGS:
        - Avoid accessing models in module-level code (use ready() instead)
        - Keep ready() methods fast (they block startup)
        - Avoid database queries that may fail (use try/except)
        - Only use for side effects, not for returning values

        This implementation performs two checks:
        1. Database connection verification
        2. Signals module import (optional)
        """


        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")

            print(f"[OK] {self.name} database connection is healthy")

        except Exception as e:
            print(f"[WARNING] {self.name} database connection failed: {e}")


        try:
            from . import signals

            print(f"[OK] {self.name} signals registered")

        except ImportError:
            print(f"[INFO] {self.name} has no signals.py; skipping signal registration")
