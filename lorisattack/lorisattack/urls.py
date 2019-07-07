"""callippus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.conf import settings

# update displayed header/title
admin.site.site_header = settings.SITE_HEADER
admin.site.site_title = settings.SITE_TITLE

urlpatterns = [
    url('', include('social_django.urls', namespace='social')),
    url(r'^$', RedirectView.as_view(url=f'{settings.URL_PREFIX}/admin')),
    url(r'^admin/', admin.site.urls)
]
