from django.contrib import admin
from django.urls import include, path
from home.admin import custon_adm_site

urlpatterns = [
    # URLs for default admin
    path('primeadmin/', admin.site.urls),

    # URLs for custom admin
    path('admin/', custon_adm_site.urls),
    
    # URLs for allauth
    path('accounts/', include('allauth.urls')),
    
    # URLs for my apps
    path('', include('home.urls')),
    path('', include('portfolio.urls')),
	
]
