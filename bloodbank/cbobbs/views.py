from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login,logout
from django .contrib import messages
from .forms import BloodBankWorkerRegistrationForm, HealthCareWorkerRegistrationForm, DonorRegistrationForm
from django.db import transaction

from .models import BloodbankWorker, HealthcareWorker, Donor


# Create your views here.
def home(request):
    return render(request, "index.html")
    
def find_bloodbanks(request):
    return render(request, "find-bloodbanks.html")

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        #auth
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            messages.success(request,"You have Successfully Logged In!")
            
            if hasattr(user, 'bbworker') and user.bbworker.role == "admin":
                return redirect('bb-reg-worker')
            elif(hasattr(user,'bbworker') and user.bbworker.role == "employee"):
                return redirect('bb-dash')
            
            elif hasattr(user, 'hcworker') and user.hcworker.role == "admin":
                return redirect('hc-reg-worker')
            elif(hasattr(user,'hcworker') and user.hcworker.role == "employee"):
                return redirect('hc-dash')

            elif(hasattr(user,'donor')):
                return redirect('donor-dash')
            else:
                messages.error(request,"WHy are you here")
        else:
            messages.error(request,"Invalid email or password.")
    return render(request, "login.html")

def logout_user(request):
    logout(request)
    messages.success(request,"You have been Logged out!")
    return redirect("home")

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
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.save()  

               
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                generated_username = f"{first_name[0].lower()}{last_name.lower()}{user.id}"
                user.username = generated_username
                user.save()  

                email = form.cleaned_data['email']
                full_name = f"{first_name} {last_name}"

                
                Donor.objects.create(
                    donor_id = user,
                    name=full_name,
                    email=email
                )

                messages.success(request, f"Donor account created. Username: {generated_username}")
                return redirect(request.path)
    else:
        form = DonorRegistrationForm()
    return render(request, 'bbworker/register-donor.html', {'form': form})


def bbworker_reg_worker(request):
    if request.method == 'POST':
        form = BloodBankWorkerRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.save()  

               
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                generated_username = f"{first_name[0].lower()}{last_name.lower()}{user.id}"
                user.username = generated_username
                user.save()  

               
                role = form.cleaned_data['role']
                email = form.cleaned_data['email']
                full_name = f"{first_name} {last_name}"

                if hasattr(request.user, 'bbworker'):
                    blood_bank = request.user.bbworker.blood_bank
                else:
                    messages.error(request, "Your account is not linked to a blood bank.")
                    return redirect(request.path)

                
                BloodbankWorker.objects.create(
                    bb_worker_id=user,
                    name=full_name,
                    email=email,
                    blood_bank=blood_bank,
                    role=role
                )

                messages.success(request, f"Worker account created. Username: {generated_username}")
                return redirect(request.path)
    else:
        form = BloodBankWorkerRegistrationForm()
    return render(request, 'bbworker/register-worker.html', {'form': form})


def hcworker_dash(request):
    return render(request, "hcworker/dashboard.html")

def hcworker_bloodsupply(request):
    return render(request, "hcworker/bloodsupply.html")

def hcworker_profile(request):
    return render(request, "hcworker/profile.html")

def hcworker_reg_worker(request):
    if request.method == 'POST':
        form = HealthCareWorkerRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.save()  

               
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                generated_username = f"{first_name[0].lower()}{last_name.lower()}{user.id}"
                user.username = generated_username
                user.save()  

               
                role = form.cleaned_data['role']
                email = form.cleaned_data['email']
                full_name = f"{first_name} {last_name}"

                if hasattr(request.user, 'hcworker'):
                    health_center = request.user.hcworker.health_center
                else:
                    messages.error(request, "Your account is not linked to a blood bank.")
                    return redirect(request.path)

                
                HealthcareWorker.objects.create(
                    hc_worker_id=user,
                    name=full_name,
                    email=email,
                    health_center=health_center,
                    role=role
                )

                messages.success(request, f"Worker account created. Username: {generated_username}")
                return redirect(request.path)
    else:
        form = HealthCareWorkerRegistrationForm()
    return render(request, 'hcworker/register-worker.html', {'form': form})


