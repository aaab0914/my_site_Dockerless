from django.urls import include, path

from . import api_views, views
from .feeds import LatestPostsFeed, UserPostsFeed
from .views import PostDeleteView

app_name = "blog"

urlpatterns = [
    path(
        "<int:year>/<int:month>/<int:day>/<slug:post_slug>/",
        views.post_detail,
        name="post_detail",
    ),
    path("<int:post_id>/share/", views.post_share, name="post_share"),
    path("<int:post_id>/comment/", views.add_comment, name="post_comment"),
    path("tag/<slug:tag_slug>/", views.post_list, name="post_list_by_tag"),
    path("", views.post_list, name="all_posts_list"),
    path("feed/", LatestPostsFeed(), name="post_feed"),
    path("search/", views.post_search, name="post_search"),
    path("create/", views.post_create, name="post_create"),
    path("<int:pk>/delete/", PostDeleteView.as_view(), name="post_delete"),
    path(
        "post_delete_success/",
        views.post_delete_success,
        name="post_delete_success",
    ),
    path(
        "<slug:post_slug>/<int:comment_id>/edit/",
        views.edit_comment,
        name="edit_comment",
    ),
    path(
        "<slug:post_slug>/<int:comment_id>/delete/",
        views.comment_delete,
        name="comment_delete",
    ),
    path("users/", include("users.urls")),
    path("feed/<str:username>/", UserPostsFeed(), name="user_feed"),
    path(
        "api/posts/",
        api_views.PostListAPIView.as_view(),
        name="api_post_list",
    ),
    path(
        "api/posts/<int:pk>/",
        api_views.PostDetailAPIView.as_view(),
        name="api_post_detail",
    ),
    path(
        "api/comments/",
        api_views.CommentListAPIView.as_view(),
        name="api_comment_list",
    ),
    path(
        "api/comments/<int:pk>/",
        api_views.CommentDetailAPIView.as_view(),
        name="api_comment_detail",
    ),
    path("api/tags/", api_views.tag_list_api, name="api_tag_list"),
    path(
        "api/tags/<slug:slug>/",
        api_views.tag_detail_api,
        name="api_tag_detail",
    ),
]
