from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import BloodBankWorkerRegistrationForm, HealthCareWorkerRegistrationForm, DonorRegistrationForm, LogDonationForm, LogTransactionForm, UpdateStatusForm, TransportForm
from django.db import transaction 
from .decorators import donor_required, hcworker_required, hcworker_admin_required, bbworker_required, bbworker_admin_required

from .models import BloodbankWorker, BloodBank, HealthcareWorker, Donor, Appointment, Donation
from datetime import timedelta, datetime
from django.utils import timezone
from django.utils.dateparse import parse_date
from collections import defaultdict

# Create your views here.
def home(request):
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
                return redirect('bb-appt')
            
            elif hasattr(user, 'hcworker') and user.hcworker.role == "admin":
                return redirect('hcworker-registration')
            elif(hasattr(user,'hcworker') and user.hcworker.role == "employee"):
                return redirect('hc-bloodsupply')

            elif(hasattr(user,'donor')):
                return redirect('donor-dash')
            else:
                messages.error(request,"Why are you here")
        else:
            messages.error(request,"Invalid email or password.")
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
                return redirect('bb-appt')
            
            elif hasattr(user, 'hcworker') and user.hcworker.role == "admin":
                return redirect('hcworker-registration')
            elif(hasattr(user,'hcworker') and user.hcworker.role == "employee"):
                return redirect('hc-bloodsupply')

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

@donor_required
def donor_dash(request):
    donor = request.user.donor 
    donation_history = Donation.objects.filter(donor=donor).order_by('-donation_date')
    appointments = Appointment.objects.filter(donor=donor).order_by('-appt_date', '-appt_time')

    total_donations = donation_history.count()
    last_donation = donation_history.first()

    next_eligible_date = None
    if last_donation:
        next_eligible_date = last_donation.donation_date + timedelta(days=56)

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

@donor_required
def donor_appt(request):
    donor = request.user.donor
    blood_banks = BloodBank.objects.all()
    now = timezone.now()

    if request.method == 'POST':
  
        bank_id = request.POST.get('blood_bank_id')
        date_str = request.POST.get('appt_date')  # format: 'YYYY-MM-DD'
        time_str = request.POST.get('appt_time')  # format: 'HH:MM AM/PM'

        if bank_id and date_str and time_str:
            try:
                blood_bank = BloodBank.objects.get(pk=bank_id)
                appt_date = parse_date(date_str)
                appt_time_obj = datetime.strptime(time_str, "%I:%M %p")

                appt_datetime = datetime.combine(appt_date, appt_time_obj.time())

                last_appt = Appointment.objects.filter(donor=donor).order_by('-appt_time').first()

                if timezone.is_naive(appt_datetime):
                    appt_datetime = timezone.make_aware(appt_datetime, timezone.get_current_timezone())

                if last_appt:
                    min_eligible_date = last_appt.appt_time + timedelta(days=56)
                    if appt_datetime < min_eligible_date:
                        messages.error(request, f"You must wait 56 days between appointments. Next eligible date: {min_eligible_date.date()}")
                        return redirect('donor-appt')
    
                    Appointment.objects.create(
                        appt_date=appt_date,
                        appt_time=appt_datetime,
                        donor=donor,
                        blood_bank=blood_bank
                    )
                    messages.success(request, "Appointment created successfully.")
            except Exception as e:
                messages.error(request, f"Error creating appointment: {e}")
        else:
            messages.error(request, "Please fill out all fields to create an appointment.")

        return redirect('donor-appt')

    time_slots = []
    start_time = datetime.strptime("08:00", "%H:%M")
    end_time = datetime.strptime("17:00", "%H:%M")

    while start_time < end_time:
        if start_time.hour == 13:
            start_time += timedelta(hours=1)
            continue
        time_slots.append(start_time.strftime("%I:%M %p"))
        start_time += timedelta(minutes=30)

    appointments = Appointment.objects.filter(donor=donor).order_by('-appt_date', '-appt_time')
    for appt in appointments:
        appt.is_future = appt.appt_time > now

    return render(request, 'donor/appointments.html', {
        'appointments': appointments,
        'time_slots': time_slots,
        'today': now,
        'blood_banks': blood_banks
    })

@donor_required
def donor_hist(request):
    donor = request.user.donor 
    
    all_donations = Donation.objects.filter(donor=donor)

    donations = all_donations.order_by('-donation_date')

    bloodbanks = BloodBank.objects.all()

    return render(request, 'donor/history.html', {
        'donations': donations,
        'bloodbanks': bloodbanks,
    })

@donor_required
def donor_profile(request):
    donor = request.user.donor
    user = request.user
    
    appointments = Appointment.objects.filter(donor=donor).order_by('appt_date', 'appt_time')

    if request.method == 'POST':
        new_email = request.POST.get('email')  
        new_phone = request.POST.get('phone_number')
        new_address = request.POST.get('address')
        
        if new_email:
            user.username = new_email
            user.save()
            
        if new_email:
            donor.email = new_email
        if new_phone:
            donor.phone = new_phone
        if new_address:
            donor.address = new_address
        donor.save()

        return redirect('donor-profile')
    
    return render(request, 'donor/profile.html', {
        'donor': donor,
        'appointments': appointments
    })

@bbworker_required
def bbworker_dash(request):
    return render(request, "bbworker/dashboard.html")

@bbworker_required
def bbworker_donors(request):    
    bbworker = request.user.bbworker 

    bb_donations = Donation.objects.filter(blood_bank=bbworker.blood_bank)
    donations = bb_donations.order_by('-donation_date')
     
    return render(request, 'bbworker/donors.html', {'donations': donations})

@bbworker_required
def bbworker_donor_notes(request): 
    donor = None
    email = request.GET.get('email')
    
    if email:
        donor = Donor.objects.filter(email=email).first()

    if request.method == 'POST' and donor:
        donor.medical_notes = request.POST.get('notes')
        donor.save()
        messages.success(request, "Note saved")
        
    return render(request, 'bbworker/donor-notes.html', {'donor': donor, 'email': email})

@bbworker_required
def bbworker_donation(request):
    log_form = LogDonationForm()
    status_form = UpdateStatusForm()
    transaction_form = LogTransactionForm()
    transport_form = TransportForm()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        user = request.user

        if not hasattr(user, 'bbworker'):
            messages.error(request, "You are not authorized.")
            return redirect('bb-donors')

        bb = user.bbworker.blood_bank
        
        if form_type == 'log':
            log_form = LogDonationForm(request.POST)
            if log_form.is_valid():
                email = log_form.cleaned_data['donor_email']
                d_date = log_form.cleaned_data['donation_date']
                try:
                    donor = Donor.objects.get(email=email)
                    Donation.objects.create(
                        blood_type=donor.blood_type,
                        donation_date=d_date,
                        status='processing',
                        donor=donor,
                        blood_bank=bb
                    )
                    messages.success(request, "Donation logged.")
                except Donor.DoesNotExist:
                    messages.error(request, "Donor not found.")

        # Handle Status Update
        elif form_type == 'status':
            status_form = UpdateStatusForm(request.POST)
            if status_form.is_valid():
                try:
                    donor = Donor.objects.get(email=status_form.cleaned_data['donor_email'])
                    donation = Donation.objects.get(donor=donor, donation_date=status_form.cleaned_data['donation_date'], blood_bank=bb)
                    donation.status = status_form.cleaned_data['status']
                    donation.save()
                    messages.success(request, "Status updated.")
                except (Donor.DoesNotExist, Donation.DoesNotExist):
                    messages.error(request, "Donation not found.")

        # Handle Transaction Logging
        elif form_type == 'transaction':
            transaction_form = LogTransactionForm(request.POST)
            if transaction_form.is_valid():
                try:
                    donor = Donor.objects.get(email=transaction_form.cleaned_data['donor_email'])
                    donation = Donation.objects.get(donor=donor, donation_date=transaction_form.cleaned_data['donation_date'], blood_bank=bb)
                    donation.transaction_date = transaction_form.cleaned_data['transaction_date']
                    donation.save()
                    messages.success(request, "Transaction date logged.")
                except (Donor.DoesNotExist, Donation.DoesNotExist):
                    messages.error(request, "Donation not found.")

        # Handle Transport
        elif form_type == 'transport':
            transport_form = TransportForm(request.POST)
            if transport_form.is_valid():
                donations = Donation.objects.filter(blood_type=transport_form.cleaned_data['blood_type'], blood_bank=bb)
                for donation in donations:
                    donation.transfer_date = transport_form.cleaned_data['transfer_date']
                    donation.health_center = transport_form.cleaned_data['health_center']
                    donation.status = 'delivered'
                    donation.save()
                messages.success(request, f"Transported {donations.count()} donations.")

    context = {
        'log_form': log_form,
        'status_form': status_form,
        'transaction_form': transaction_form,
        'transport_form': transport_form
    }
    return render(request, 'bbworker/donation.html', context)

@bbworker_required
def bbworker_appt(request):
    bbworker = request.user.bbworker
    appointments = Appointment.objects.filter(blood_bank=bbworker.blood_bank).order_by('-appt_date', '-appt_time')
    return render(request, 'bbworker/appointments.html', {'appointments': appointments})

@bbworker_admin_required
def bbworker_workers(request):
    bloodbank = request.user.bbworker.blood_bank
    workers = BloodbankWorker.objects.filter(blood_bank=bloodbank)
    return render(request, 'bbworker/workers.html', {'workers': workers})

@hcworker_required
def hcworker_bloodsupply(request):
    user = request.user
    try:
        worker = HealthcareWorker.objects.select_related('health_center').get(hc_worker_id=user)
        user_center = worker.health_center
    except HealthcareWorker.DoesNotExist:
        return render(request, "hcworker/bloodsupply.html", {
            "bloodbank_stats": {},
            "healthcenter_stats": {},
        })

    BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    bloodbank_stats = defaultdict(lambda: {bt: 0 for bt in BLOOD_TYPES})
    healthcenter_stats = {user_center.name: {bt: 0 for bt in BLOOD_TYPES}}

    donations = Donation.objects.select_related('blood_bank', 'health_center').all()

    for d in donations:
        if d.status != 'delivered':
            bloodbank_stats[d.blood_bank.name][d.blood_type] += 1

        if d.health_center == user_center and d.status != 'used':
            healthcenter_stats[user_center.name][d.blood_type] += 1

    return render(request, "hcworker/bloodsupply.html", {
        "bloodbank_stats": dict(bloodbank_stats),
        "healthcenter_stats": healthcenter_stats
    })

@bbworker_required
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
    
@bbworker_admin_required
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

@hcworker_admin_required
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
