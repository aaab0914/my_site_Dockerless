# blog/templatetags/user_tags.py
from django import template

register = template.Library()


@register.simple_tag
def is_superuser(user):
    """
    Return the appropriate HTML label for a superuser.
    """
    if user.is_authenticated and user.is_superuser:
        return '<span style="color: #cc0000; font-weight: bold; font-size: 0.8em;">Superuser</span>'
    return ""
