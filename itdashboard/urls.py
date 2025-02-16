"""
URL configuration for itdashboard project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf import settings  # Import settings
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from AssetApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload/', views.upload_file_page, name='upload_file_page'),  # New file upload page
    path('upload/parse/', views.parse_file, name='parse_file'),        # Parsing logic endpoint
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
