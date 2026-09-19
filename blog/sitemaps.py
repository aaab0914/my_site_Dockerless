from django.contrib.sitemaps import Sitemap
from .models import Post

class PostSitemap(Sitemap):
    """
    Sitemap configuration for the Post model.
    """
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        """
        Return the queryset of published posts.
        """
        return Post.published.all()

    def lastmod(self, obj):
        """
        Return the last modified date of the post.
        """
        return obj.updated
