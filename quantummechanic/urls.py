from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
import settings
import circuits.views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'quantummechanic.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^circuits/', circuits.views.main, name='main')
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
