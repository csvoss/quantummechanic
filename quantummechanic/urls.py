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
    url(r'^sandbox/', circuits.views.main, name='main'),
    url(r'^addgate/', circuits.views.addgate, name='addgate'),
    url(r'^undo/', circuits.views.undo, name='undo'),
    url(r'^clear/', circuits.views.undo, name='clear'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
