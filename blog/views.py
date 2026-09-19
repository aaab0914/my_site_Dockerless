from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from django.http import Http404

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.views.generic import ListView
from django.contrib import messages


from django.views.decorators.http import require_POST

from django.db.models import Count
from django.views.generic.detail import DetailView

from taggit.models import Tag

from .models import Post, Comment

from .forms import EmailPostForm, CommentForm, SearchForm, PostCreateForm


from django.db.models import Q

from django.contrib.auth.decorators import login_required

from django.utils.text import slugify
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView







def post_share(request, post_id):
    """
    View function for sharing a post via email.

    This view:
    - Retrieves a published post by its ID
    - Displays a form for entering recipient email and comments (GET request)
    - Processes the form and sends an email (POST request)

    Note: The actual email sending logic is omitted (commented out).

    :param request: HTTP request object
    :param post_id: Primary key of the post to share
    :return: Rendered share form or redirect after successful email
    """

    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )

    if request.method == 'POST':
        form = EmailPostForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data


    else:
        form = EmailPostForm()

    return render(
        request,
        'blog/post/share.html',
        {'post': post, 'form': form}
    )


def post_list(request, tag_slug=None):
    """
    View function for displaying a list of posts with optional tag filtering.

    Features:
    - Shows only published posts
    - Supports filtering by tag slug (optional URL parameter)
    - Paginates results (10 posts per page)
    - Handles invalid page numbers gracefully

    URL patterns:
        /blog/              - Shows all posts
        /blog/tag/django/   - Shows posts tagged with 'django'

    :param request: HTTP request object
    :param tag_slug: Optional slug of the tag to filter by (from URL)
    :return: Rendered list template with posts and optional tag
    """

    post_list = Post.published.all()

    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)

        post_list = post_list.filter(tags__in=[tag])

    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page', 1)

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(
        request,
        'blog/post/all_posts_list.html',
        {'posts': posts, 'tag': tag if tag_slug else None}
    )


def post_detail(request, year, month, day, post_slug):
    """
    View function for displaying a single post detail page.

    This view:
    - Retrieves a published post by slug and publication date
    - Displays active comments for the post
    - Provides a form for adding new comments
    - Shows similar posts based on tag overlap and title similarity

    URL pattern: /blog/2024/01/15/my-post-slug/

    :param request: HTTP request object
    :param year: Publication year (e.g., 2024)
    :param month: Publication month (e.g., 1 for January)
    :param day: Publication day (e.g., 15)
    :param post_slug: URL-friendly slug of the post (e.g., 'my-post-slug')
    :return: Rendered detail template with post, comments, form, and similar posts
    """

    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,  # Only published posts
        slug=post_slug,  # Match the slug
        publish__year=year,  # Match publication year
        publish__month=month,  # Match publication month
        publish__day=day  # Match publication day
    )

    comments = post.comments.filter(active=True)

    form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)

    tag_based_posts = Post.published.filter(
        tags__in=post_tags_ids
    ).exclude(id=post.id)  # Exclude the current post itself

    title_based_posts = Post.published.none()

    if tag_based_posts.count() < 4:
        title_based_posts = Post.published.annotate(
            similarity=TrigramSimilarity('title', post.title)
        ).filter(
            similarity__gt=0.1  # Only posts with >10% title similarity
        ).exclude(
            id=post.id
        ).order_by('-similarity')[:4 - tag_based_posts.count()]  # Take only what's needed

    similar_posts = (tag_based_posts | title_based_posts).distinct()

    similar_posts = similar_posts.annotate(
        same_tags=Count('tags')  # Count how many tags are shared
    ).order_by(
        '-same_tags',  # Posts with more shared tags come first
        '-publish'  # Then by newest publication date
    )[:4]  # Limit to maximum 4 similar posts

    return render(
        request,
        'blog/post/post_detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form,
            'similar_posts': similar_posts
        }
    )

def post_search(request):
    """
    View function for searching posts by keyword using PostgreSQL full-text search.

    This view implements hybrid search combining:
    1. PostgreSQL full-text search (ranked by relevance)
    2. Trigram similarity (fuzzy matching for typos)

    Features:
    - Searches both title (weight A) and body (weight B)
    - Combines full-text and trigram results
    - Orders results by final relevance rank

    URL pattern: /blog/search/?query=django

    :param request: HTTP request object (with optional 'query' GET parameter)
    :return: Rendered search template with form, query, and results
    """

    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)

        if form.is_valid():
            query = form.cleaned_data['query']

            results = Post.published.filter(
                Q(title__icontains=query) | Q(body__icontains=query)
            ).order_by('-publish')

    return render(
        request,
        'blog/post/search_post.html',
        {'form': form, 'query': query, 'results': results}
    )


@login_required
def post_create(request):
    """
    View function for creating a new post (authenticated users only).

    This view:
    - Requires user to be logged in (@login_required decorator)
    - Displays an empty form for GET requests
    - Processes form submission for POST requests
    - Automatically sets the author to the current logged-in user
    - Automatically publishes the post (status set to PUBLISHED)

    Note: This is an admin/create view, not part of the public blog.

    :param request: HTTP request object
    :return: Rendered create form or redirect to the new post's detail page
    """

    if request.method == 'POST':
        form = PostCreateForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)

            post.author = request.user

            post.status = Post.Status.PUBLISHED

            post.save()

            form.save_m2m()

            return redirect(post.get_absolute_url())

    else:
        form = PostCreateForm()

    return render(request, 'blog/post/create_post.html', {'form': form})


def post_delete_success(request):
    """
    View function for the post deletion success page.

    This view renders a confirmation page that is shown to the user
    after a post has been successfully deleted. It does not perform
    any database operations and simply displays a success message.

    Args:
        request: HTTP request object
    Returns:
        Rendered HTML template with success message
    """
    return render(request, 'blog/post/post_delete_success.html')


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """
    Class-based view for deleting a post.

    This view:
    - Requires the user to be logged in (LoginRequiredMixin)
    - Only allows the author of the post or a superuser to delete
    - Shows a confirmation page before deletion (GET request)
    - Deletes the post after confirmation (POST request)

    Attributes:
        model: The Post model to be deleted
        template_name: The template for the delete confirmation page
        success_url: The URL to redirect to after successful deletion
        context_object_name: The name of the object in the template context
        pk_url_kwarg: The URL parameter name for the primary key
    """

    model = Post

    template_name = 'blog/post/post_delete.html'

    success_url = reverse_lazy('blog:post_delete_success')

    context_object_name = 'post'

    pk_url_kwarg = 'pk'

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch method to add permission checks before processing.

        This method is called before any request processing occurs.
        It checks if the current user is the author of the post or a superuser.
        If not, a PermissionDenied exception is raised.

        Args:
            request: HTTP request object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        Returns:
            Response from parent dispatch method or raises PermissionDenied
        """
        obj = self.get_object()

        if obj.author != request.user and not request.user.is_superuser:
            raise PermissionDenied("You are not allowed to delete this post.")

        return super().dispatch(request, *args, **kwargs)

@login_required
@require_POST
def add_comment(request, post_id):
    """
    View function for handling comment submission (POST only).

    This view:
    - Accepts only POST requests (decorated with @require_POST)
    - Creates a new comment for the specified post
    - Associates the comment with the post (foreign key)
    - Comments are created with active=False by default (requires moderation)

    :param request: HTTP request object (must be POST)
    :param post_id: Primary key of the post to comment on
    :return: Rendered comment template with post, form, and new comment
    """

    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )

    comment = None

    form = CommentForm(request.POST, request.FILES)

    if form.is_valid():
        comment = form.save(commit=False)

        comment.post = post
        comment.name = request.user.username

        comment.save()

    return render(
        request,
        'blog/comment/add_comment_success.html',
        {
            'post': post,
            'form': form,
            'comment': comment
        }
    )


@login_required
def edit_comment(request, post_slug, comment_id):
    """
    View function for editing an existing comment.

    This view:
    - Requires user to be logged in (@login_required)
    - Verifies the comment belongs to the specified post (slug check)
    - Only allows the comment author or superuser to edit
    - Displays a form for editing the comment body

    Args:
        request: HTTP request object
        post_slug: Slug of the post containing the comment
        comment_id: ID of the comment to edit
    Returns:
        Rendered edit form or redirect to post detail page
    """

    comment = get_object_or_404(Comment, id=comment_id)

    if comment.post.slug != post_slug:
        return redirect('blog:post_list')

    if comment.name != request.user.username and not request.user.is_superuser:
        return redirect(
            'blog:post_detail',
            year=comment.post.publish.year,
            month=comment.post.publish.month,
            day=comment.post.publish.day,
            post_slug=comment.post.slug,
        )

    if request.method == 'POST':
        form = CommentForm(data=request.POST, instance=comment)

        if form.is_valid():
            form.save()
            return redirect(
                'blog:post_detail',
                year=comment.post.publish.year,
                month=comment.post.publish.month,
                day=comment.post.publish.day,
                post_slug=comment.post.slug,
            )

    else:
        form = CommentForm(instance=comment)

    return render(
        request,
        'blog/comment/edit_comment.html',
        {
            'form': form,
            'comment': comment,
            'post': comment.post,
        }
    )


@login_required
def comment_delete(request, post_slug, comment_id):
    """
    View function for deleting a comment.

    This view:
    - Requires user to be logged in (@login_required)
    - Only allows the comment author or superuser to delete
    - Redirects back to the post detail page after deletion

    Args:
        request: HTTP request object
        post_slug: Slug of the post containing the comment
        comment_id: ID of the comment to delete
    Returns:
        Redirect to post detail page or rendered confirmation template
    """

    comment = get_object_or_404(Comment, id=comment_id)

    if request.user.username != comment.name and not request.user.is_superuser:
        messages.error(request, 'You are not allowed to delete this comment.')
        return redirect(
            'blog:post_detail',
            year=comment.post.publish.year,
            month=comment.post.publish.month,
            day=comment.post.publish.day,
            post_slug=comment.post.slug,
        )

    if request.method == 'POST':
        post = comment.post
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
        return redirect(
            'blog:post_detail',
            year=post.publish.year,
            month=post.publish.month,
            day=post.publish.day,
            post_slug=post.slug,
        )

    return render(request, 'blog/comment/delete_comment.html', {'comment': comment})
