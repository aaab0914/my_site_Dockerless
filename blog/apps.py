from django.apps import AppConfig
from django.db import connection

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    def ready(self):
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