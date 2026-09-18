# blog/apps.py

# =====================
# IMPORTS
# =====================

from django.apps import AppConfig
# AppConfig: Base class for application configuration
# Allows customization of app behavior (ready() method, labels, etc.)

from django.db import connection


# connection: Django's database connection wrapper
# Used to execute raw SQL queries for connection testing


# =====================
# BLOG APPLICATION CONFIGURATION
# =====================

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

    # ----- DEFAULT PRIMARY KEY CONFIGURATION -----

    default_auto_field = 'django.db.models.BigAutoField'
    # Specifies the default primary key type for all models in this app
    # 'BigAutoField': 64-bit integer ID (range: up to 9 quintillion)
    # Benefits over default AutoField (32-bit):
    #   - Supports larger tables (more than 2 billion rows)
    #   - Future-proof for scaling
    #   - Django 3.2+ recommended default
    # Alternative values: 'django.db.models.AutoField' (legacy)

    # ----- APPLICATION IDENTIFIER -----

    name = 'blog'

    # The full Python path to the application
    # Django uses this to locate models, templates, static files, etc.
    # MUST match the app name in INSTALLED_APPS in settings.py
    # Example: INSTALLED_APPS = ['blog', ...]

    # ----- VERBOSE NAME (OPTIONAL) -----
    # Can be set for human-readable label in admin:
    # verbose_name = 'Blog'

    # =====================
    # APPLICATION STARTUP HOOK
    # =====================

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

        # ----- DATABASE CONNECTION CHECK -----
        # Verifies that the database is reachable
        # Useful for catching configuration issues early

        try:
            # Open a database cursor to test connectivity
            with connection.cursor() as cursor:
                # Execute a simple, harmless query that should always succeed
                # 'SELECT 1' works on all database backends (PostgreSQL, MySQL, SQLite)
                cursor.execute("SELECT 1")

            # Connection successful - log success message
            # f"{self.name}" is 'blog' (the application name)
            print(f"[OK] {self.name} 数据库连接正常")

        except Exception as e:
            # Connection failed - log warning but don't crash
            # This allows the app to start even if database is temporarily unavailable
            # (e.g., during Docker container startup where DB may not be ready yet)
            print(f"[WARNING] {self.name} 数据库连接异常: {e}")

        # ----- SIGNAL REGISTRATION -----
        # Attempts to import the signals module to register signal handlers
        # This is the standard Django pattern for signal registration

        try:
            # Import the signals module (relative import)
            # The 'from . import signals' line registers signals when the module loads
            # Signal handlers are typically defined in blog/signals.py
            from . import signals

            # Signal registration successful
            print(f"[OK] {self.name} 信号已注册")

        except ImportError:
            # No signals.py file exists - skip signal registration
            # This is not an error; many apps don't need signals
            # ℹ️ (information) icon indicates this is informational, not an error
            print(f"ℹ️ {self.name} 没有 signals.py 文件，跳过信号注册")

# =====================
# SIGNAL MODULE EXAMPLE (signals.py)
# =====================
#
# If you create a signals.py file, typical content might be:
#
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Post
#
# @receiver(post_save, sender=Post)
# def post_saved_handler(sender, instance, created, **kwargs):
#     """Handle post-save events (e.g., send notifications, update caches)"""
#     if created:
#         print(f"New post created: {instance.title}")
#     else:
#         print(f"Post updated: {instance.title}")


# =====================
# NOTES ON APP CONFIG REGISTRATION
# =====================
#
# Method 1: Default (implicit) registration - Django auto-detects subclasses
#   INSTALLED_APPS = ['blog']  # Django finds BlogConfig automatically
#
# Method 2: Explicit registration (recommended for clarity)
#   INSTALLED_APPS = ['blog.apps.BlogConfig', ...]
#
# The explicit method is preferred because it clearly shows which config class
# Django should use, especially if you have custom ready() logic.
#
# To use explicit registration, change settings.py:
#   INSTALLED_APPS = [
#       'blog.apps.BlogConfig',  # Explicit
#       # 'blog',                 # Implicit (not needed if using explicit)
#   ]


# =====================
# READY() METHOD BEST PRACTICES
# =====================
#
# 1. Keep it Idempotent:
#    - Should be safe to call multiple times
#    - Django calls ready() only once, but tests may cause multiple calls
#
# 2. Avoid Circular Imports:
#    - Use local imports inside ready() (like `from . import signals`)
#    - Don't import models at module level if used in ready()
#
# 3. Handle Errors Gracefully:
#    - Use try/except for external dependencies
#    - Use logging instead of print() in production
#
# Example with logging:
#   import logging
#   logger = logging.getLogger(__name__)
#
#   def ready(self):
#       try:
#           with connection.cursor() as cursor:
#               cursor.execute("SELECT 1")
#           logger.info(f"{self.name} database connection OK")
#       except Exception as e:
#           logger.warning(f"{self.name} database connection failed: {e}")
#
# 4. Don't Perform Database Migrations Here:
#    - ready() runs on every startup, not just during migrations
#    - Use management commands for one-time setup


# =====================
# TROUBLESHOOTING
# =====================
#
# 1. ready() method not being called
#    → Ensure app config is correctly referenced in INSTALLED_APPS
#    → Use explicit path: 'blog.apps.BlogConfig' in settings.py
#    → Restart Django server (changes to apps.py require restart)
#
# 2. "App 'blog' doesn't have a 'BlogConfig' class"
#    → Check that class name exactly matches (case-sensitive)
#    → Verify class inherits from AppConfig
#    → Ensure __init__.py exists in blog directory
#
# 3. Database check runs too early (before database is ready)
#    → This is normal during Docker container startup
#    → The exception catch prevents crashes
#    → Consider using connection.ensure_connection() with timeout
#
# 4. Signals not being registered
#    → Verify signals.py exists in the app directory
#    → Check for syntax errors in signals.py
#    → Ensure signal handlers are decorated with @receiver
#
# 5. print() statements not showing in console
#    → Use logging instead: import logging; logger = logging.getLogger(__name__)
#    → Check that runserver is capturing stdout
#    → Use --verbosity 3 for more output
#
# 6. Module-level database queries causing errors
#    → Move queries into ready() method
#    → Use connection instead of model imports
#    → Wrap in try/except to prevent startup crashes


# =====================
# ALTERNATIVE CONFIGURATION EXAMPLE
# =====================
#
# class BlogConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'blog'
#     verbose_name = 'Blog Management'
#
#     def ready(self):
#         # Only register signals in production to avoid test noise
#         import os
#         if os.environ.get('DJANGO_SETTINGS_MODULE') != 'config.settings.test':
#             from . import signals
#
#         # Set up cache warming (optional)
#         from django.core.cache import cache
#         cache.set('blog_app_ready', True, timeout=60)
