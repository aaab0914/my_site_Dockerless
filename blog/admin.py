
from django.contrib import admin

from django.utils.html import format_html

from .models import Post, Comment





@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Post model.

    This class customizes how Post objects are displayed, filtered, searched,
    and edited in the Django admin interface.

    The @admin.register decorator automatically registers this admin class
    with the Django admin site for the Post model.

    Features configured:
    - List view columns and filters
    - Search functionality
    - Auto-populated slug field
    - Author selection via raw_id_fields (efficient for many users)
    - Date hierarchy navigation
    - Facet counts for better filtering UX
    - Custom CSS for MarkdownX widget
    """


    list_display = [
        'title',  # Post title (clickable by default)
        'slug',  # URL-friendly identifier
        'author',  # User who wrote the post (ForeignKey)
        'publish',  # Publication date/time
        'status'  # Draft or Published (from Status enum)
    ]


    list_filter = [
        'status',  # Filter by Draft/Published status
        'created',  # Filter by creation date (Today, Past 7 days, This month, etc.)
        'publish',  # Filter by publication date
        'author'  # Filter by author (requires select widget)
    ]


    search_fields = [
        'title',  # Search by post title (partial match, case-insensitive)
        'body'  # Search by post content (partial match, case-insensitive)
    ]


    prepopulated_fields = {
        'slug': ('title',)  # Auto-generate slug from title field when typing
    }


    raw_id_fields = ['author']


    date_hierarchy = 'publish'


    ordering = ['status', 'publish']


    show_facets = admin.ShowFacets.ALWAYS



    class Media:
        """
        Custom CSS and JavaScript for the admin interface.

        This class is automatically detected by Django and the media files
        are included in the admin change form for Post.
        """

        css = {
            'all': ('admin/css/markdownx_admin.css',)
        }




@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Comment model.

    This class customizes how Comment objects are displayed and managed
    in the Django admin interface.

    The @admin.register decorator automatically registers this admin class
    with the Django admin site for the Comment model.

    Features configured:
    - List view columns (with moderation actions)
    - Filter by active status and dates
    - Search by author name, email, and content
    - Custom actions can be added for bulk moderation
    """


    list_display = [
        'name',  # Commenter's name (displayed with the comment)
        'email',  # Commenter's email (for gravatar or moderation/replies)
        'post',  # Parent post this comment belongs to (ForeignKey)
        'created',  # When the comment was submitted
        'active'  # Boolean: whether comment is visible (True) or hidden (False)
    ]


    list_filter = [
        'active',  # Filter by Active/Inactive (approved vs pending)
        'created',  # Filter by creation date
        'updated'  # Filter by last modification date
    ]


    search_fields = [
        'name',  # Search by commenter name (partial match)
        'email',  # Search by email address
        'body'  # Search by comment content (partial match)
    ]
