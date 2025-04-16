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
    
    
    path("bbworker/login/", views.bbworker_login, name="bb-login"),
    path("bbworker/dash/", views.bbworker_dash, name="bb-dash"),
    path("bbworker/donors/", views.bbworker_donors, name="bb-donors"),
    path("bbworker/donation/", views.bbworker_donation, name="bb-donation"),
    path("bbworker/profile/", views.bbworker_profile, name="bb-profile"),
    path("bbworker/reg/donor/", views.bbworker_reg_donor, name="bb-reg-donor"),
    path("bbworker/reg/worker/", views.bbworker_reg_worker, name="bb-reg-worker"),
    

    path("hcworker/login/", views.hcworker_login, name="hc-login"),
    path("hcworker/dash/", views.hcworker_dash, name="hc-dash"),
    path("hcworker/bloodsupply/", views.hcworker_bloodsupply, name="hc-bloodsupply"),
    path("hcworker/profile/", views.hcworker_profile, name="hc-profile"),
    path("hcworker/reg/worker/", views.hcworker_reg_worker, name="hc-reg-worker"),
]