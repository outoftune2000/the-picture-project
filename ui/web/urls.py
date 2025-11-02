from __future__ import annotations

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from pathlib import Path

from webapp import views


BASE_DIR = Path(__file__).resolve().parents[1].parent

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('upload/', views.upload, name='upload'),
    path('recombine/', views.recombine, name='recombine'),
    path('delete/', views.delete_all, name='delete_all'),
]

# Serve images in development
if settings.DEBUG:
    urlpatterns += static('/images/', document_root=str(BASE_DIR / 'images'))


