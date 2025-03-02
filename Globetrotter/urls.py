from django.conf.urls import include
from django.contrib import admin
from django.urls import path,re_path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    path('api/v1/',include('quiz.urls')),
    re_path(r'^.*$', views.error), 
]
