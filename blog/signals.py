import logging

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import Post

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Post, dispatch_uid="blog.post_saved_handler")
def post_saved_handler(sender, instance, created, **kwargs):
    if created:
        logger.info(
            "New post '%s' created by %s",
            instance.title,
            instance.author.username,
        )
    else:
        logger.info(
            "Post '%s' updated. Status: %s",
            instance.title,
            instance.status,
        )


@receiver(pre_delete, sender=Post, dispatch_uid="blog.post_deleted_handler")
def post_deleted_handler(sender, instance, **kwargs):
    author_name = getattr(instance.author, "username", "unknown")
    logger.info("Post '%s' is being deleted by %s", instance.title, author_name)