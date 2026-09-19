

from django import template

from django.db.models import Count

from django.utils.safestring import mark_safe

from ..models import Post

import markdown


register = template.Library()


@register.simple_tag
def total_posts():
    """
    Simple template tag that returns the total number of published posts.

    Usage in templates:
        {% load blog_tags %}
        {% total_posts %}

    Output example:
        12

    This tag requires no parameters and returns an integer.

    :return: Integer count of all published posts
    """
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    """
    Inclusion tag that renders a list of the most recent posts.

    This tag retrieves the latest posts and renders them using a specified template.
    Inclusion tags are more powerful than simple tags because they render a template.

    Usage in templates:
        {% load blog_tags %}
        {% show_latest_posts %}
        {% show_latest_posts 3 %}

    The template should be located at: blog/templates/blog/post/latest_posts.html

    Template variables available:
        - latest_posts: QuerySet of the most recent published posts

    Example template content (latest_posts.html):
        <ul>
            {% for post in latest_posts %}
                <li><a href="{{ post.get_absolute_url }}">{{ post.title }}</a></li>
            {% endfor %}
        </ul>

    :param count: Number of posts to display (default: 5)
    :return: Dictionary containing the latest_posts variable for the template
    """
    latest_posts = Post.published.order_by('-publish')[:count]

    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_commented_posts(count=5):
    """
    Simple template tag that returns the posts with the most comments.

    Uses Django aggregation to annotate each post with its comment count,
    then sorts by the highest count and returns the top N posts.

    Usage in templates:
        {% load blog_tags %}
        {% get_most_commented_posts %}
        {% get_most_commented_posts 3 %}

    Output example:
        [<Post: My Popular Post>, <Post: Another Post>, ...]

    Note: Returns a QuerySet (not rendered HTML). To display, iterate in template:
        {% for post in most_commented_posts %}
            <li><a href="{{ post.get_absolute_url }}">{{ post.title }}</a></li>
        {% endfor %}

    :param count: Number of posts to return (default: 5)
    :return: QuerySet of the most commented published posts
    """
    return Post.published.annotate(
        total_comments=Count('comments')  # Count comments via related_name='comments'
    ).filter(
        total_comments__gt=0  # Only posts with at least one comment
    ).order_by(
        '-total_comments'  # Descending order (highest first)
    )[:count]  # Limit to 'count' number of results


@register.filter(name='markdown')
def markdown_format(text):
    """
    Template filter that converts Markdown text to HTML.

    This filter allows you to write Markdown in your blog posts and have it
    automatically converted to HTML when rendered.

    Usage in templates:
        {% load blog_tags %}
        {{ post.body|markdown }}

    Example:
        Input: "# Hello\n\nThis is **bold** text."
        Output: <h1>Hello</h1>\n<p>This is <strong>bold</strong> text.</p>

    Important security considerations:
    - mark_safe() marks the output as safe HTML (prevents auto-escaping)
    - Without mark_safe(), Django would escape the HTML tags
    - Be cautious with user-generated content to prevent XSS attacks

    To install markdown library:
        pip install markdown

    :param text: Markdown text string to convert
    :return: HTML string marked as safe for rendering
    """
    return mark_safe(markdown.markdown(text))

@register.simple_tag
def user_posts_count(user):
    """
    Returns the number of posts written by the specified user.

    Usage:
        {% user_posts_count request.user %}

    Returns:
        int: Number of posts by the user
    :param user:
    :return:
    """
    if user.is_authenticated:
        return Post.objects.filter(author=user).count()
    return 0
