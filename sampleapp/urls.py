"""
URL configuration for sample project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from .views import base, register, custom_login, custom_logout, upload_file, upload_chunk, query_builder, user_list, count_records

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', base, name='base'),
    path('register/', register, name='register'),
    path('login/', custom_login, name='custom_login'),
    path('logout/', custom_logout, name='custom_logout'),
# ====================================================================
    path('upload/', upload_file, name='upload_file'),
    path('upload_chunk/', upload_chunk, name='upload_chunk'),
    path('query-builder/', query_builder, name='query_builder'),
    path('users/', user_list, name='user_list'),
# =====================================================================
    path('api/count_records/', count_records, name='count_records'),



# ======================================================================
]
