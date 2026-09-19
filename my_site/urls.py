
from django.contrib import admin

from django.urls import path, include

from django.contrib.sitemaps.views import sitemap

from markdownx import urls as markdownx_urls

from blog.sitemaps import PostSitemap

from django.conf.urls.static import static

from django.conf import settings



sitemaps = {
    'posts': PostSitemap,
}



urlpatterns = [
    path("admin/", admin.site.urls),

    path('blog/', include('blog.urls', namespace='blog')),

    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemaps'
    ),

    path('markdownx/', include(markdownx_urls)),

    path('users/', include('users.urls', namespace='users')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
