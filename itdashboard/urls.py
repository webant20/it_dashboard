"""
URL configuration for itdashboard project.
"""
from django.conf import settings  
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from AssetApp import views  # Existing views for AssetApp

urlpatterns = [
    path("", include("DashboardApp.urls")),  # Dashboard App as home page
    path('admin/', admin.site.urls),

    # Existing file upload routes
    path('upload/', views.upload_file_page, name='upload_file_page'),  
    path('upload/parse/', views.parse_file, name='parse_file'),       

    # ✅ Include DMS URLs
    # path('dms/', include('dms.urls')),   # New DMS URLs included here
]

# ✅ Handle Media URL for File Uploads
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
