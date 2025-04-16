from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, "index.html")
    
def find_bloodbanks(request):
    return render(request, "find-bloodbanks.html")

def login(request):
    return render(request, "login.html")

def eligibility(request):
    return render(request, "eligibility.html")


def donor_dash(request):
    return render(request, "donor/dashboard.html")

def donor_appt(request):
    return render(request, "donor/appointments.html")

def donor_hist(request):
    return render(request, "donor/history.html")

def donor_profile(request):
    return render(request, "donor/profile.html")


def bbworker_dash(request):
    return render(request, "bbworker/dashboard.html")

def bbworker_donors(request):
    return render(request, "bbworker/donors.html")

def bbworker_profile(request):
    return render(request, "bbworker/profile.html")

def bbworker_reg_donor(request):
    return render(request, "bbworker/register-donor.html")

def bbworker_reg_worker(request):
    return render(request, "bbworker/register-worker.html")


def hcworker_dash(request):
    return render(request, "hcworker/dashboard.html")

def hcworker_bloodsupply(request):
    return render(request, "hcworker/bloodsupply.html")

def hcworker_profile(request):
    return render(request, "hcworker/profile.html")

def hcworker_reg_worker(request):
    return render(request, "hcworker/register-worker.html")


