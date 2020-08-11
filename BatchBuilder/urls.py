from django.contrib import admin
from django.urls import path
from main_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/github', views.GithubView.as_view()),
    path('', views.home)
]
