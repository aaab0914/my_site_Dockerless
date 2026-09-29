import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class BlogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "blog"

    def ready(self):
        import blog.signals  # noqa: F401
        logger.info("blog signals registered")