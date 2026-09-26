import re

import markdown
from better_profanity import profanity
from django.conf import settings
from django.core.exceptions import ValidationError

# from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from markdownx.models import MarkdownxField
from taggit.managers import TaggableManager

profanity.load_censor_words()

def validate_no_profanity(value):
    """ Validator to check for profanity. """
    if profanity.contains_profanity(value):
        raise ValidationError(
            'Content contains inappropriate or offensive language.',
            code='profanity',
        )

def validate_stripped_length(value):
    if len(value.strip()) < 5:
        raise ValidationError(
            'Content must be at least 5 characters after trimming.',
            code='min_length',
        )

def validate_meaningful_content(value):
    """ Reject content that is only numbers or only symbols. """
    stripped = value.strip()
    if stripped.isdigit():
        raise ValidationError(
            'Content cannot be only numbers.',
            code='Only_numbers',
        )
    if not re.search(r'[a-zA-Z\u4e00-\u9fff]', stripped):
        raise

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"

    title = models.CharField(max_length=250)
    cover_image = models.ImageField(upload_to="posts/%Y/%m/%d/", blank=True, null=True)
    slug = models.SlugField(max_length=250, unique_for_date="publish")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blog_posts"
    )
    body = MarkdownxField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=Status, default=Status.DRAFT)
    tags = TaggableManager()
    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ["-publish"]
        indexes = [models.Index(fields=["-publish"])]
        constraints = [
            models.UniqueConstraint(fields=["slug", "publish"], name="unique_slug_per_date")
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "blog:post_detail",
            args=[self.publish.year, self.publish.month, self.publish.day, self.slug],
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        self.clean()
        super().save(*args, **kwargs)

    def get_markdown_body(self):
        return markdown.markdown(self.body)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField(max_length=200)
    image = models.ImageField(upload_to="comments/%Y/%m/%d/", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["created"]
        indexes = [models.Index(fields=["created"])]

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"
