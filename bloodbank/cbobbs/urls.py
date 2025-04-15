from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("find-bloodbanks/", views.find_bloodbanks, name="find-bloodbanks"),
    path("login/", views.login, name="login")
]