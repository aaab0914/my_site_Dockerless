import re

from better_profanity import profanity
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from taggit.managers import TaggableManager

profanity.load_censor_words()


def validate_no_profanity(value):
    """Validator to check for profanity."""
    if profanity.contains_profanity(value):
        raise ValidationError(
            "Content contains inappropriate or offensive language.",
            code="profanity",
        )


def validate_stripped_length(value):
    """Reject content shorter than 5 characters after trimming."""
    if len(value.strip()) < 5:
        raise ValidationError(
            "Content must be at least 5 characters after trimming.",
            code="min_length",
        )


def validate_meaningful_content(value):
    """Reject content that is only numbers or only symbols."""
    stripped = value.strip()
    if stripped.isdigit():
        raise ValidationError(
            "Content cannot be only numbers.",
            code="only_numbers",
        )
    if not re.search(r"[a-zA-Z\u4e00-\u9fff]", stripped):
        raise ValidationError(
            "Content must contain at least one letter.",
            code="no_letters",
        )


text_validator = RegexValidator(
    regex=r"^[a-zA-Z0-9\u4e00-\u9fff\s.,!?'\"():/\n\r-]+$",
    message="Only letters, numbers, spaces, and basic punctuation are allowed.",
)


def validate_no_excessive_whitespace(value):
    """Reject content with excessive whitespace."""
    if re.search(r"\s{5,}", value):
        raise ValidationError(
            "Content contains excessive whitespace.",
            code="excessive_whitespace",
        )


def validate_no_repeated_chars(value):
    """Reject content with too many repeated characters."""
    if re.search(r"(.)\1{4,}", value):
        raise ValidationError(
            "Content contains too many repeated characters.",
            code="repeated_chars",
        )


def validate_no_html(value):
    """Reject content containing HTML tags."""
    if re.search(r"<[^>]+>", value):
        raise ValidationError(
            "HTML tags are not allowed.",
            code="html_not_allowed",
        )


class PublishedManager(models.Manager):
    """Manager that returns only published posts."""

    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"

    title = models.CharField(
        max_length=200,
        validators=[
            MaxLengthValidator(200, message="Title must not exceed 200 characters."),
            validate_stripped_length,
            validate_meaningful_content,
            text_validator,
            validate_no_profanity,
        ],
    )
    cover_image = models.ImageField(upload_to="posts/%Y/%m/%d/", blank=True, null=True)
    slug = models.SlugField(max_length=250, unique_for_date="publish")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_posts",
    )
    body = models.TextField(
        validators=[
            MaxLengthValidator(5000, message="Body must not exceed 5000 characters."),
            validate_stripped_length,
            validate_meaningful_content,
            text_validator,
            validate_no_profanity,
        ],
    )
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
            models.UniqueConstraint(
                fields=["slug", "publish"],
                name="unique_slug_per_date",
            )
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
        super().save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField(
        validators=[
            MaxLengthValidator(5000, message="Body must not exceed 5000 characters."),
            validate_stripped_length,
            validate_meaningful_content,
            text_validator,
            validate_no_profanity,
        ],
    )
    image = models.ImageField(upload_to="comments/%Y/%m/%d/", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["created"]
        indexes = [models.Index(fields=["created"])]

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"