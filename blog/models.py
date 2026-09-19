
from django.db import models

from django.utils import timezone

from django.conf import settings

from django.urls import reverse

from taggit.managers import TaggableManager

from django.utils.text import slugify

from markdownx.models import MarkdownxField

import markdown





class PublishedManager(models.Manager):
    """
    Custom model manager that filters querysets to return only published posts.

    This manager is used as `Post.published` and automatically excludes draft posts.
    It provides a clean way to get published content without repeating filter logic.

    Usage: Post.published.all() instead of Post.objects.filter(status='PB')
    """

    def get_queryset(self):
        """
        Override the base manager's get_queryset method.

        Returns only posts with status equal to PUBLISHED.
        The super().get_queryset() call gets all objects, then we filter.

        :return: QuerySet containing only published posts
        """
        return (
            super().get_queryset().filter(status=Post.Status.PUBLISHED)
        )



class Post(models.Model):
    """
    Blog post model representing articles written by users.

    This model stores all blog post content, metadata, and provides
    methods for URL generation and Markdown rendering.

    Features:
    - Draft/Published status with TextChoices enum
    - Automatic slug generation from title
    - Markdown support for rich content
    - Tagging capability via django-taggit
    - Publication date for scheduled publishing
    - Auto-updated timestamps for created/updated
    """

    class Status(models.TextChoices):
        """
        Enum class defining possible post statuses.

        Values:
            DRAFT ('DF'): Post is not yet published (saved as 'DF' in database)
            PUBLISHED ('PB'): Post is publicly visible (saved as 'PB' in database)

        The display labels ('Draft', 'Published') appear in forms and admin.
        """
        DRAFT = 'DF', 'Draft'  # First value: DB storage, Second: Human-readable label
        PUBLISHED = 'PB', 'Published'


    title = models.CharField(max_length=250)
    cover_image = models.ImageField(upload_to='posts/%Y/%m/%d/', blank=True, null=True)

    slug = models.SlugField(
        max_length=250,
        unique_for_date='publish'
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts'
    )

    body = MarkdownxField()


    publish = models.DateTimeField(default=timezone.now)

    created = models.DateTimeField(auto_now_add=True)

    updated = models.DateTimeField(auto_now=True)

    status = models.CharField(
        max_length=10,
        choices=Status,
        default=Status.DRAFT
    )


    tags = TaggableManager()


    objects = models.Manager()

    published = PublishedManager()



    class Meta:
        """
        Model metadata configuration.

        ordering: Default sort order for queries (newest first)
        indexes: Database indexes for performance optimization
        """
        ordering = ['-publish']

        indexes = [
            models.Index(fields=['-publish']),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=['slug', 'publish'],
                name='unique_slug_per_date'
            )
        ]


    def __str__(self):
        """
        Returns a human-readable string representation of the post.

        Used in:
        - Django admin interface (list display, dropdowns)
        - Debugging and logging
        - Shell output when printing Post objects

        :return: Post title string
        """
        return self.title


    def get_absolute_url(self):
        """
        Returns the canonical URL for the post detail page.

        Used by:
        - Django admin "View on site" link
        - Redirect after post creation
        - Template links: <a href="{{ post.get_absolute_url }}">

        URL pattern requires: year, month, day, and slug.
        Example URL: /blog/2024/01/15/my-post-slug/

        :return: Absolute URL path to the post detail view
        """
        return reverse(
            'blog:post_detail',
            args=[
                self.publish.year,  # 4-digit year (2024)
                self.publish.month,  # Month number (1-12)
                self.publish.day,  # Day number (1-31)
                self.slug  # URL-friendly slug
            ]
        )



    def save(self, *args, **kwargs):
        """
        Override the save method to auto-populate slug from title.

        When a new post is created without a slug, this method automatically
        generates a slug based on the title using Django's slugify() function.

        Example: title = "My Amazing Post" → slug = "my-amazing-post"

        :param args: Variable positional arguments passed to parent save()
        :param kwargs: Variable keyword arguments passed to parent save()
        """
        if not self.slug:
            self.slug = slugify(self.title)
        self.clean()
        super().save(*args, **kwargs)


    def get_markdown_body(self):
        """
        Converts Markdown body content to HTML.

        This method is called in templates to render Markdown:
            {{ post.get_markdown_body|safe }}

        The |safe filter is required because the output contains HTML tags.

        Example:
            Input: "# Hello\n\nThis is **bold** text."
            Output: '<h1>Hello</h1>\n<p>This is <strong>bold</strong> text.</p>'

        :return: HTML string converted from Markdown
        """
        return markdown.markdown(self.body)



class Comment(models.Model):
    """
    Comment model representing user comments on blog posts.

    This model stores comment content, author information, and moderation status.
    Each comment belongs to exactly one Post (many-to-one relationship).

    Features:
    - Active flag for comment moderation (approve/hide)
    - Auto-timestamps for creation and update
    - Email field for gravatar support or reply notifications
    - Ordered by creation date (oldest first by default)
    """


    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )


    name = models.CharField(max_length=80)

    email = models.EmailField()


    body = models.TextField(max_length=200)

    image = models.ImageField(upload_to='comments/%Y/%m/%d/', blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)

    updated = models.DateTimeField(auto_now=True)


    active = models.BooleanField(default=True)



    class Meta:
        """
        Model metadata configuration for Comment model.

        ordering: Show oldest comments first (chronological conversation flow)
        indexes: Database index on created field for faster date-based queries
        """
        ordering = ['created']

        indexes = [
            models.Index(fields=['created']),
        ]


    def __str__(self):
        """
        Returns a human-readable string representation of the comment.

        Example output: "Comment by JohnDoe on My Blog Post"

        Used in:
        - Django admin interface
        - Debugging and logging
        - Shell output

        :return: Descriptive string with commenter name and associated post
        """
        return f"Comment by {self.name} on {self.post}"
