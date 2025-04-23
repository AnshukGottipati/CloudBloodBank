from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import BloodBankWorkerRegistrationForm, HealthCareWorkerRegistrationForm, DonorRegistrationForm
from django.db import transaction 
from .decorators import donor_required, hcworker_required, hcworker_admin_required, bbworker_required, bbworker_admin_required

from .models import BloodbankWorker, BloodBank, HealthcareWorker, Donor, Appointment, Donation
from datetime import timedelta, datetime
from django.utils import timezone



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
                return redirect('bbworker-registration')
            elif(hasattr(user,'bbworker') and user.bbworker.role == "employee"):
                return redirect('bb-dash')
            
            elif hasattr(user, 'hcworker') and user.hcworker.role == "admin":
                return redirect('hcworker-registration')
            elif(hasattr(user,'hcworker') and user.hcworker.role == "employee"):
                return redirect('hc-dash')

            elif(hasattr(user,'donor')):
                return redirect('donor-dash')
            else:
                messages.error(request,"Why are you here")
        else:
            messages.error(request,"Invalid email or password.")
    return render(request, "login.html")

def logout_user(request):
    logout(request)
    messages.success(request,"You have been Logged out!")
    return redirect("home")

def eligibility(request):
    return render(request, "eligibility.html")

#@donor_required
def donor_dash(request):
    donor = request.user.donor 
    donation_history = Donation.objects.filter(donor=donor).order_by('-donation_date')
    appointments = Appointment.objects.filter(donor=donor).order_by('-appt_date', '-appt_time')

    total_donations = donation_history.count()
    last_donation = donation_history.first()

    next_eligible_date = None
    if last_donation:
        next_eligible_date = last_donation.date + timedelta(days=56)

    context = {
        'donor': donor,
        'donation_history': donation_history,
        'appointments': appointments,
        'total_donations': total_donations,
        'last_donation': last_donation,
        'next_eligible_date': next_eligible_date,
        'lives_saved': total_donations * 3,
    }
    return render(request, 'donor/dashboard.html', context)

#@donor_required
def donor_appt(request):
    donor = request.user.donor

    if request.method == 'POST':
        appt_id = request.POST.get('appt_id')
        try:
            appt = Appointment.objects.get(appt_id=appt_id, donor=donor)
            appt.delete()
            messages.success(request, "Appointment canceled successfully.")
        except Appointment.DoesNotExist:
            messages.error(request, "Appointment could not be found.")
        return redirect('donor-appt')

    # Get current date and time
    now = timezone.now()

    # Generate the available time slots (8 AM to 5 PM, excluding 1-2 PM)
    time_slots = []
    start_time = datetime.strptime("08:00", "%H:%M")
    end_time = datetime.strptime("17:00", "%H:%M")

    # Iterate through the time slots
    while start_time < end_time:
        if start_time.hour == 13:  # Skip the 1-2 PM time slot
            start_time = start_time + timedelta(hours=1)
            continue
        
        time_slots.append(start_time.strftime("%I:%M %p"))
        start_time = start_time + timedelta(minutes=30)

    appointments = Appointment.objects.filter(donor=donor).order_by('-appt_date', '-appt_time')

    for appt in appointments:
        appt.is_future = appt.appt_time > now

    return render(request, 'donor/appointments.html', {
        'appointments': appointments,
        'time_slots': time_slots,  # Pass the time slots to the template
        'today': now,
    })

#@donor_required
def donor_hist(request):
    donor = request.user.donor 

    donations = Donation.objects.filter(donor=donor)
    
    if 'year' in request.GET and request.GET['year']:
        donations = donations.filter(donation_date__year=request.GET['year'])
    
    if 'location' in request.GET and request.GET['location']:
        donations = donations.filter(blood_bank_id=request.GET['location'])
        
    years = donations.values_list('donation_date__year', flat=True).distinct()
    
    bloodbanks = BloodBank.objects.all()

    # Pass the context to the template
    return render(request, 'donor/history.html', {
        'donations': donations,
        'years': years,
        'bloodbanks': bloodbanks
    })

#@donor_required
def donor_profile(request):
    donor = request.user.donor  # Assuming the Donor model is related to the user

    # Fetch the donor's appointments
    appointments = Appointment.objects.filter(donor=donor).order_by('appt_date', 'appt_time')

    if request.method == 'POST':
        donor.email = request.POST.get('email')
        donor.phone_number = request.POST.get('phone_number')
        donor.address = request.POST.get('address')
        donor.save() 
        
        return redirect('donor-profile')  
    
    return render(request, 'donor/profile.html', {
        'donor': donor,
        'appointments': appointments
    })

#@bbworker_required
def bbworker_dash(request):
    return render(request, "bbworker/dashboard.html")

#@bbworker_required
def bbworker_donors(request):
    donations = Donation.objects.select_related('donor').all() 
     
    return render(request, 'bbworker/donors.html', {'donations': donations})


#@bbworker_required
def bbworker_donation(request):
    if request.method == "POST":
        # Grab data from POST
        blood_type = request.POST.get("blood_type")
        donation_date = request.POST.get("donation_date")
        sent_at = request.POST.get("sent_at") or None
        status = request.POST.get("status")
        transaction_date = request.POST.get("transaction_date") or None
        blood_bank_id = request.POST.get("blood_bank")
        donor_email = request.POST.get("donor_email")

        try:
            blood_bank = BloodBank.objects.get(bb_id=blood_bank_id)
        except BloodBank.DoesNotExist:
            messages.error(request, "Blood Bank not found.")
            return redirect("bbworker-donation")

        try:
            donor = Donor.objects.get(email=donor_email)
        except Donor.DoesNotExist:
            messages.error(request, "Donor with that email does not exist.")
            return redirect("bbworker-donation")

        # Save the donation
        Donation.objects.create(
            blood_type=blood_type,
            donation_date=donation_date,
            sent_at=sent_at,
            status=status,
            transaction_date=transaction_date,
            blood_bank=blood_bank,
            donor=donor
        )

        messages.success(request, "Donation entry added successfully!")
        return redirect("bbworker-donation")

    # GET request
    blood_banks = BloodBank.objects.all()
    return render(request, "bbworker/donation.html", {"blood_banks": blood_banks})

#@bbworker_required
def bbworker_appt(request):
    bbworker = request.user.bbworker
    appointments = Appointment.objects.filter(blood_bank=bbworker.blood_bank).order_by('-appt_date', '-appt_time')
    return render(request, 'bbworker/appointments.html', {'appointments': appointments})

#@hcworker_required
def hcworker_dash(request):
    return render(request, "hcworker/dashboard.html")

#@hcworker_required
def hcworker_bloodsupply(request):
    return render(request, "hcworker/bloodsupply.html")

#@bbworker_required
def register_donor(request):
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=True)  
                messages.success(request, f"Donor account created for {user.email}")
                return redirect(request.path) 
    else:
        form = DonorRegistrationForm()
    
    return render(request, 'bbworker/register-donor.html', {'form': form})
    
#@bbworker_admin_required
def register_bbworker(request):
    if request.method == 'POST':
        form = BloodBankWorkerRegistrationForm(request.POST, request=request)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                messages.success(request, f"Worker account created. Username: {user.username}")
                return redirect(request.path)
    else:
        form = BloodBankWorkerRegistrationForm(request=request)

    return render(request, 'bbworker/register-bbworker.html', {'form': form})

#@hcworker_admin_required
def register_hcworker(request):
    if request.method == 'POST':
        form = HealthCareWorkerRegistrationForm(request.POST, request=request)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                messages.success(request, f"Healthcare Worker created. Username: {user.username}")
                return redirect(request.path)
    else:
        form = HealthCareWorkerRegistrationForm(request=request)

    return render(request, 'hcworker/register-hcworker.html', {'form': form})
