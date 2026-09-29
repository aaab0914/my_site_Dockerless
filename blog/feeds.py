from django.contrib.auth import get_user_model
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import truncatewords
from django.urls import reverse

from .models import Post

User = get_user_model()


class BasePostFeed(Feed):
    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords(item.body, 30) + "..."

    def item_pubdate(self, item):
        return item.publish


class LatestPostsFeed(BasePostFeed):
    title = "My Blog"
    description = "New Posts of My Blog."

    def link(self):
        return reverse("blog:all_posts_list")

    def items(self):
        return Post.published.all()[:5]


class UserPostsFeed(BasePostFeed):
    def get_object(self, request, username):
        return get_object_or_404(User, username=username)

    def title(self, obj):
        return f"{obj.username}'s Posts"

    def link(self, obj):
        return reverse("blog:user_posts", args=[obj.username])

    def description(self, obj):
        return f"Latest posts from {obj.username}"

    def items(self, obj):
        return Post.published.filter(author=obj).order_by("-publish")[:5]