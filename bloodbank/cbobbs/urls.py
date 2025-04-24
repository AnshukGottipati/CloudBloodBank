from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("find-bloodbanks/", views.find_bloodbanks, name="find-bloodbanks"),
    path("eligibility/", views.eligibility, name="eligibility"),

    path("login/", views.login_user, name="login"),
    path("logout/",views.logout_user,name="logout"),

    path("donor/", views.donor_dash, name="donor-dash"),
    path("donor/appt/", views.donor_appt, name="donor-appt"),
    path("donor/hist/", views.donor_hist, name="donor-hist"),
    path("donor/profile/", views.donor_profile, name="donor-profile"),
    path("donor/inbox", views.donor_inbox, name="donor-inbox"),

    path("bbworker/donors/", views.bbworker_donors, name="bb-donors"),
    path("bbworker/donor-notes/", views.bbworker_donor_notes, name="bb-donor-notes"),
    path("bbworker/donation/", views.bbworker_donation, name="bb-donation"),
    path("bbworker/appt/", views.bbworker_appt, name="bb-appt"),
    path("bbworker/workers/", views.bbworker_workers, name="bb-workers"),
    path("bbworker/inbox", views.bbworker_inbox, name="bb-inbox"),
    
    path("hcworker/bloodsupply/", views.hcworker_bloodsupply, name="hc-bloodsupply"),
    path("hcworker/request-blood/", views.hcworker_request_blood, name="hc-request-blood"),
    path("hcworker/workers/", views.hcworker_workers, name="hc-workers"),
    path("hcworker/inbox", views.hcworker_inbox, name="hc-inbox"),

    path("register/donor/", views.register_donor, name="donor-registration"),
    path("register/bbworker/", views.register_bbworker, name="bbworker-registration"),
    path("register/hcworker/", views.register_hcworker, name="hcworker-registration")
]