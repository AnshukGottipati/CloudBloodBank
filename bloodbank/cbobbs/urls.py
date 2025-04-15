from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("find-bloodbanks/", views.find_bloodbanks, name="find-bloodbanks"),
    path("login/", views.login, name="login"),
    path("eligibility/", views.eligibility, name="eligibility"),
    path("donor/dash/", views.donor_dash, name="donor-dash"),
    path("donor/appt/", views.donor_appt, name="donor-appt"),
    path("donor/hist/", views.donor_hist, name="donor-hist"),
    path("donor/profile/", views.donor_profile, name="donor-profile"),
]