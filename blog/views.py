from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic.edit import DeleteView

from taggit.models import Tag

from .forms import CommentForm, EmailPostForm, PostCreateForm, SearchForm
from .models import Comment, Post


def _redirect_to_post(post):
    return redirect(
        "blog:post_detail",
        year=post.publish.year,
        month=post.publish.month,
        day=post.publish.day,
        post_slug=post.slug,
    )


def _display_name(user):
    return getattr(user, "display_name", "") or user.username


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)

    if request.method == "POST":
        form = EmailPostForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            send_mail(
                subject=f"{cd['name']} recommends {post.title}",
                message=f"{cd['comment']}\n\nRead the post: {post_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[cd["to"]],
                reply_to=[cd["email"]],
            )
            messages.success(request, "The post was shared successfully.")

            return _redirect_to_post(post)
    else:
        form = EmailPostForm()

    return render(request, "blog/post/share.html", {"post": post, "form": form})


def post_list(request, tag_slug=None):
    posts_qs = Post.published.all()

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts_qs = posts_qs.filter(tags__in=[tag])

    paginator = Paginator(posts_qs, 10)
    page_number = request.GET.get("page", 1)
    posts = paginator.get_page(page_number)

    return render(
        request,
        "blog/post/all_posts_list.html",
        {"posts": posts, "tag": tag},
    )


def post_detail(request, year, month, day, post_slug):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post_slug,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    comments = post.comments.filter(active=True)
    form = CommentForm()

    post_tags_ids = post.tags.values_list("id", flat=True)

    similar_posts = (
        Post.published.filter(
            Q(tags__in=post_tags_ids) | Q(title__icontains=post.title)
        )
        .exclude(id=post.id)
        .annotate(
            same_tags=Count("tags", filter=Q(tags__in=post_tags_ids))
        )
        .distinct()
        .order_by("-same_tags", "-publish")[:4]
    )

    return render(
        request,
        "blog/post/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "form": form,
            "similar_posts": similar_posts,
        },
    )


def post_search(request):
    form = SearchForm(request.GET or None)
    query = None
    results = Post.published.none()

    if form.is_valid():
        query = form.cleaned_data["query"]
        results = Post.published.filter(
            Q(title__icontains=query) | Q(body__icontains=query)
        ).order_by("-publish")

    paginator = Paginator(results, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/post/search_post.html",
        {
            "form": form,
            "query": query,
            "results": page_obj,
        },
    )


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostCreateForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, "Post created successfully.")
            return redirect(post.get_absolute_url())
    else:
        form = PostCreateForm()

    return render(request, "blog/post/create_post.html", {"form": form})


@login_required
def post_delete_success(request):
    return render(request, "blog/post/post_delete_success.html")


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/post/post_delete.html"
    success_url = reverse_lazy("blog:post_delete_success")
    context_object_name = "post"
    pk_url_kwarg = "pk"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(author=self.request.user)


@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    form = CommentForm(request.POST, request.FILES)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.user = request.user
        comment.name = _display_name(request.user)
        comment.save()
        messages.success(request, "Comment added successfully.")
        return _redirect_to_post(post)

    return render(
        request,
        "blog/comment/add_comment.html",
        {"post": post, "form": form},
    )


@login_required
def edit_comment(request, post_slug, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.post.slug != post_slug:
        return redirect("blog:all_posts_list")

    if comment.user != request.user and not request.user.is_superuser:
        return _redirect_to_post(comment.post)

    if request.method == "POST":
        form = CommentForm(
            data=request.POST,
            files=request.FILES,
            instance=comment,
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated successfully.")
            return _redirect_to_post(comment.post)
    else:
        form = CommentForm(instance=comment)

    return render(
        request,
        "blog/comment/edit_comment.html",
        {"form": form, "comment": comment, "post": comment.post},
    )


@login_required
def comment_delete(request, post_slug, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.post.slug != post_slug:
        return redirect("blog:all_posts_list")

    if comment.user != request.user and not request.user.is_superuser:
        messages.error(request, "You are not allowed to delete this comment.")
        return _redirect_to_post(comment.post)

    if request.method == "POST":
        post = comment.post
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
        return _redirect_to_post(post)

    return render(request, "blog/comment/delete_comment.html", {"comment": comment})