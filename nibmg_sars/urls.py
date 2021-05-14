"""nibmg_sars URL Configuration

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
import os
from django.urls import path
from dotenv import load_dotenv
from django.contrib import admin
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from rest_framework.documentation import include_docs_urls

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

urlpatterns = [
	url(os.getenv('BASE_URL'), include([
		url(r'^admin/', admin.site.urls),
		url(r'^api/', include_docs_urls(title='API Documentation')),
		url(r'^api/auth/', include(('accounts.api.urls', 'accounts'), namespace='api-auth')),
		url(r'^api/files/', include(('sequences.api.urls', 'sequences'), namespace='api-upload')),
	])),
]

if settings.DEBUG :
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
