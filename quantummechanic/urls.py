from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
import settings
import circuits.views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'quantummechanic.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
                       
    url(r'^$', circuits.views.index, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^sandbox/(?P<n>\d{0,10})', circuits.views.sandbox, name='sandbox'),
    url(r'^sandbox/', circuits.views.sandbox_default, name='sandbox_default'),
    url(r'^addgate/', circuits.views.addgate, name='addgate'),
    url(r'^undo/', circuits.views.undo, name='undo'),
    url(r'^clear/', circuits.views.clear, name='clear'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
