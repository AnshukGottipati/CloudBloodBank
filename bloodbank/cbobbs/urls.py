from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("find-centers/", views.find_centers, name="find-centers"),
    path("login/", views.login, name="login")
]