from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Post
from .models import Comment
from django.contrib.auth.models import User
import re

@receiver(post_save, sender=Post)
def post_saved_handler(sender, instance, created, **kwargs):
    if created:
        print(f"New post '{instance.title}' created by {instance.author.username}")
    else:
        print(f"Post '{instance.title}' updated. Status: {instance.status}")

@receiver(pre_delete, sender=Post)
def post_deleted_handler(sender, instance, **kwargs):
    print(f"Post '{instance.title}' is being deleted by {instance.author.username}")


@receiver(pre_save, sender=User)
def validate_user_chars(sender, instance, **kwargs):
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')

    if chinese_pattern.search(instance.username):
        raise ValidationError('Username cannot contain Chinese characters.')
