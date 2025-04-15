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