from datetime import timedelta, datetime
from collections import defaultdict
from math import radians, sin, cos, sqrt, atan2
import requests
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import transaction 
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import BloodBankWorkerRegistrationForm, HealthCareWorkerRegistrationForm, DonorRegistrationForm, LogDonationForm, LogTransactionForm, UpdateStatusForm, TransportForm
from .models import BloodbankWorker, BloodBank, HealthcareWorker, Donor, Appointment, Donation, Message, MessageRecipient
from .decorators import donor_required, hcworker_required, hcworker_admin_required, bbworker_required, bbworker_admin_required


GOOGLE_MAPS_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"
GOOGLE_MAPS_API_KEY= getattr(settings, "GOOGLE_API_KEY", "")

# Function to geocode an address using Google Maps Geocoding API
def geocode_address(address):
    params = {
        "address": address,
        "key": GOOGLE_MAPS_API_KEY
    }

    response = requests.get(GOOGLE_MAPS_API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]

    return None, None

# Haversine formula to calculate distance between two coordinates (in kilometers)
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# View to find the closest blood banks
def find_bloodbanks(request):
    if request.method == "POST":
        user_address = request.POST.get('address')
        user_lat, user_lon = geocode_address(user_address)

        if user_lat is None or user_lon is None:
            return JsonResponse({
                "error": "Unable to geocode address. Please check the address."
            }, status=400)

        bloodbanks = BloodBank.objects.all()

        distances = []
        for bloodbank in bloodbanks:
            bb_lat = bloodbank.latitude
            bb_lon = bloodbank.longitude
            distance = haversine_distance(user_lat, user_lon, bb_lat, bb_lon)
            distances.append((bloodbank, distance))

        distances.sort(key=lambda x: x[1])
        MAX_DISTANCE_KM = 50

        # Take up to 3 within range, but keep the distance for each
        closest_pairs = [pair for pair in distances[:3] if pair[1] <= MAX_DISTANCE_KM]

        if not closest_pairs:
            return JsonResponse({
                "message": "No nearby blood banks found within a reasonable distance."
            }, status=404)

        result = [{
            "name": bb.name,
            "address": bb.address,
            "city": bb.city,
            "state": bb.state,
            "zipcode": bb.zipcode,
            "phone": bb.phone,
            "latitude": bb.latitude,
            "longitude": bb.longitude,
            "distance": round(distance, 2),
        } for bb, distance in closest_pairs]

        return JsonResponse({"bloodbanks": result})

    # GET: Render template and pass Maps API key securely in context
    return render(request, "find-bloodbanks.html", {
        "GOOGLE_MAPS_API_KEY": settings.GOOGLE_API_KEY
    })

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

# Login User
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

# Logout user
def logout_user(request):
    logout(request)
    messages.success(request,"You have been Logged out!")
    return redirect("home")

# Elibigibility form
def eligibility(request):
    return render(request, "eligibility.html")

# Donor's dash
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
def bbworker_donors(request):    
    bbworker = request.user.bbworker 
    blood_bank = bbworker.blood_bank

    bb_donations = Donation.objects.filter(blood_bank=bbworker.blood_bank)
    donations = bb_donations.order_by('-donation_date')
     
    return render(request, 'bbworker/donors.html', {
        'blood_bank':blood_bank, 
        'donations': donations
        })

@bbworker_required
def bbworker_donor_notes(request): 
    blood_bank = request.user.bbworker.blood_bank
    donor = None
    email = request.GET.get('email')
    
    if email:
        donor = Donor.objects.filter(email=email).first()

    if request.method == 'POST' and donor:
        donor.medical_notes = request.POST.get('notes')
        donor.save()
        
        title = "Medical Notes Updated"
        body = (
            f"Dear {donor.name},\n\n"
            "Your medical notes have been updated in our system. "
            "Please check your profile for more details or reach out to us if you have any questions.\n\n"
            "Thank you for being a valued donor."
        )
        
        send_donor_message(donor, title, body)

        messages.success(request, "Note saved and donor notified.")
        
    return render(request, 'bbworker/donor-notes.html', {
        'blood_bank': blood_bank, 
        'donor': donor, 
        'email': email})

@bbworker_required
def bbworker_donation(request):
    log_form = LogDonationForm()
    status_form = UpdateStatusForm()
    transaction_form = LogTransactionForm()
    transport_form = TransportForm()    
    blood_bank = request.user.bbworker.blood_bank

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
                    send_donor_message(
                        donor,
                        "Thank You for Donating!",
                        f"Your donation on {d_date} at {bb.name} has been logged and is now being processed. Thank you!"
                    )
                    messages.success(request, "Donation logged.")
                except Donor.DoesNotExist:
                    messages.error(request, "Donor not found.")
            
        elif form_type == 'status':
            status_form = UpdateStatusForm(request.POST)
            if status_form.is_valid():
                try:
                    donor = Donor.objects.get(email=status_form.cleaned_data['donor_email'])
                    donation = Donation.objects.get(donor=donor, donation_date=status_form.cleaned_data['donation_date'], blood_bank=bb)
                    donation.status = status_form.cleaned_data['status']
                    donation.save()
                    send_donor_message(
                        donor,
                        "Donation Status Updated",
                        f"The status of your donation on {donation.donation_date} is now: {donation.status}."
                    )
                    messages.success(request, "Status updated.")
                except (Donor.DoesNotExist, Donation.DoesNotExist):
                    messages.error(request, "Donation not found.")

        elif form_type == 'transaction':
            transaction_form = LogTransactionForm(request.POST)
            if transaction_form.is_valid():
                try:
                    donor = Donor.objects.get(email=transaction_form.cleaned_data['donor_email'])
                    donation = Donation.objects.get(donor=donor, donation_date=transaction_form.cleaned_data['donation_date'], blood_bank=bb)
                    donation.transaction_date = transaction_form.cleaned_data['transaction_date']
                    donation.save()
                    send_donor_message(
                        donor,
                        "Donation Transaction Date Recorded",
                        f"Your donation on {donation.donation_date} a recorded transaction date of {donation.transaction_date}."
                    )
                    messages.success(request, "Transaction date logged.")
                except (Donor.DoesNotExist, Donation.DoesNotExist):
                    messages.error(request, "Donation not found.")
    
        elif form_type == 'transport':
            transport_form = TransportForm(request.POST)
            if transport_form.is_valid():
                blood_type = transport_form.cleaned_data['blood_type']
                transfer_date = transport_form.cleaned_data['transfer_date']
                health_center = transport_form.cleaned_data['health_center']

                donations = Donation.objects.filter(
                    blood_type=blood_type,
                    blood_bank=bb,                    
                    health_center__isnull=True
                )

                for donation in donations:
                    donation.transfer_date = transfer_date
                    donation.health_center = health_center
                    donation.status = 'delivered'
                    donation.save()

                count = donations.count()
                messages.success(request, f"Transported {count} donations.")
               
                send_donor_message(
                    donation.donor,
                    "Your Donation Was Delivered",
                    f"Your donation (blood type {donation.blood_type}) has been delivered to a healthcare center."
                )

                title = f"Incoming {blood_type} Donations"
                body = (
                    f"{count} units of {blood_type} blood have been dispatched to your health center "
                    f"({health_center.name}) and are marked as delivered.\n\n"
                    f"Transfer Date: {transfer_date.strftime('%Y-%m-%d')}"
                )

                hc_workers = HealthcareWorker.objects.filter(health_center=health_center)
                for hc_worker in hc_workers:
                    MessageRecipient.objects.create(
                        message=Message.objects.create(title=title, body=body),
                        user=hc_worker.hc_worker_id,
                        recipient_type='hc_worker'
                    )

    context = {
        'blood_bank': blood_bank,
        'log_form': log_form,
        'status_form': status_form,
        'transaction_form': transaction_form,
        'transport_form': transport_form
    }
    return render(request, 'bbworker/donation.html', context)

@bbworker_required
def bbworker_appt(request):
    bbworker = request.user.bbworker
    blood_bank = bbworker.blood_bank
    appointments = Appointment.objects.filter(blood_bank=blood_bank).order_by('-appt_date', '-appt_time')
    now = timezone.now()

    if request.method == 'POST':
  
        donor_email = request.POST.get('donor_email')
        date_str = request.POST.get('appt_date')  # format: 'YYYY-MM-DD'
        time_str = request.POST.get('appt_time')  # format: 'HH:MM AM/PM'

        if donor_email and date_str and time_str:
            try:
                donor = Donor.objects.get(email=donor_email)
                appt_date = parse_date(date_str)
                appt_time_obj = datetime.strptime(time_str, "%I:%M %p")

                appt_datetime = datetime.combine(appt_date, appt_time_obj.time())              
    
                Appointment.objects.create(
                    appt_date=appt_date,
                    appt_time=appt_datetime,
                    donor=donor,
                    blood_bank=blood_bank
                )

                messages.success(request, f"Appointment created successfully.")
            except Exception as e:
                messages.error(request, f"Error creating appointment: {e}")
        else:
            messages.error(request, "Please fill out all fields to create an appointment.")

        return redirect('bb-appt')

    time_slots = []
    start_time = datetime.strptime("08:00", "%H:%M")
    end_time = datetime.strptime("17:00", "%H:%M")

    while start_time < end_time:
        if start_time.hour == 13:
            start_time += timedelta(hours=1)
            continue
        time_slots.append(start_time.strftime("%I:%M %p"))
        start_time += timedelta(minutes=30)

    appointments = Appointment.objects.filter(blood_bank=blood_bank).order_by('-appt_date', '-appt_time')
    for appt in appointments:
        appt.is_future = appt.appt_time > now

    return render(request, 'bbworker/appointments.html', {
        'appointments': appointments,
        'time_slots': time_slots,
        'today': now,
        'blood_banks': blood_bank
    })

@bbworker_admin_required
def bbworker_workers(request):
    blood_bank = request.user.bbworker.blood_bank
    workers = BloodbankWorker.objects.filter(blood_bank=blood_bank)
    return render(request, 'bbworker/workers.html', {
        'workers': workers,
        'blood_bank': blood_bank
        })

@hcworker_required
def hcworker_bloodsupply(request):
    worker = HealthcareWorker.objects.select_related('health_center').get(hc_worker_id=request.user)
    health_center = worker.health_center

    if request.method == "POST":
        blood_type_used = request.POST.get("blood_type")
        donation = Donation.objects.filter(
            health_center=health_center,
            blood_type=blood_type_used,
            status="delivered"
        ).order_by("donation_date").first()

        if donation:
            donation.status = "used"
            donation.save()
            return redirect("hc-bloodsupply")
        else:
            messages.error(request, f"No available units of blood type {blood_type_used} at your health center.")

    BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    bloodbank_stats = defaultdict(lambda: {bt: 0 for bt in BLOOD_TYPES})
    healthcenter_stats = {health_center.name: {bt: 0 for bt in BLOOD_TYPES}}

    for bank in BloodBank.objects.all():
        bloodbank_stats[bank.name] = {bt: 0 for bt in BLOOD_TYPES}

    donations = Donation.objects.select_related('blood_bank', 'health_center').all()

    for d in donations: 
        if d.health_center == health_center and d.status == 'delivered':
            healthcenter_stats[health_center.name][d.blood_type] += 1
            
        elif d.health_center is None and d.blood_bank:
            bloodbank_stats[d.blood_bank.name][d.blood_type] += 1


    return render(request, "hcworker/bloodsupply.html", {
        "health_center": health_center,
        "bloodbank_stats": dict(bloodbank_stats),
        "healthcenter_stats": healthcenter_stats,
        "blood_types": BLOOD_TYPES
    })

@hcworker_required
def hcworker_request_blood(request):  
    
    hc_worker = HealthcareWorker.objects.get(hc_worker_id=request.user)
    health_center = hc_worker.health_center

    if request.method == "POST":
        priority = request.POST.get('priority')
        blood_types = request.POST.getlist('blood-types[]')
        
        if not priority or not blood_types:
            messages.error(request, "Priority and blood types are required.")
            return redirect('hcworker:send_message')
        
        title = f"{priority.capitalize()} - {', '.join(blood_types)} requested"        
       
        hc_worker = HealthcareWorker.objects.get(hc_worker_id=request.user)
        health_center = hc_worker.health_center
        body = (
            f"Blood types needed: {', '.join(blood_types)}\n\n"
            f"Health Center Details:\n"
            f"Name: {health_center.name}\n"
            f"Address: {health_center.address}\n"
            f"Phone: {health_center.phone}"
        )  

        bb_message = Message.objects.create(title=title, body=body)
        for bb_worker in BloodbankWorker.objects.all():
            MessageRecipient.objects.create(
                message=bb_message,
                user=bb_worker.bb_worker_id,
                recipient_type='blood_bank_worker'
            )

        donor_title = "Urgent Need for Your Blood Type"
        donor_body = (
            f"Dear Donor, "
            f"We are currently experiencing a {priority} need for blood donations of your blood type "
            f"at {health_center.name}. Please consider donating soon to help save lives. "
            f"Location: {health_center.address} || Phone: {health_center.phone}"
        )
        donor_message = Message.objects.create(title=donor_title, body=donor_body)
        for donor in Donor.objects.filter(blood_type__in=blood_types):
            MessageRecipient.objects.create(
                message=donor_message,
                user=donor.donor_id, 
                recipient_type='donor'
            )

        messages.success(request, "Messages successfully sent to blood banks and eligible donors.")
    
    return render(request, 'hcworker/send-message.html', {"health_center": health_center})

@hcworker_admin_required
def hcworker_workers(request):
    health_center = request.user.hcworker.health_center
    workers = HealthcareWorker.objects.filter(health_center=health_center)
    return render(request, 'hcworker/workers.html', {
        "health_center": health_center,
        'workers': workers}
        )

@bbworker_required
def register_donor(request):    
    blood_bank = request.user.bbworker.blood_bank

    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=True)  
                messages.success(request, f"Donor account created for {user.email}")
                return redirect(request.path) 
    else:
        form = DonorRegistrationForm()
    
    return render(request, 'bbworker/register-donor.html', {
        'blood_bank': blood_bank, 
        'form': form
        })
    
@bbworker_admin_required
def register_bbworker(request):    
    blood_bank = request.user.bbworker.blood_bank

    if request.method == 'POST':
        form = BloodBankWorkerRegistrationForm(request.POST, request=request)
        if form.is_valid():
            
            with transaction.atomic():
                user = form.save()
                messages.success(request, f"Worker account created. Username: {user.username}")
                return redirect(request.path)
    else:
        form = BloodBankWorkerRegistrationForm(request=request)

    return render(request, 'bbworker/register-bbworker.html', {
        'blood_bank': blood_bank, 
        'form': form})

@hcworker_admin_required
def register_hcworker(request):    
    health_center = request.user.hcworker.health_center
    if request.method == 'POST':
        form = HealthCareWorkerRegistrationForm(request.POST, request=request)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                messages.success(request, f"Healthcare Worker created. Username: {user.username}")
                return redirect(request.path)
    else:
        form = HealthCareWorkerRegistrationForm(request=request)

    return render(request, 'hcworker/register-hcworker.html', {        
        "health_center": health_center,
        'form': form
        })

# User inbox
@login_required
def inbox(request):  
    if hasattr(request.user, 'hcworker'):
        title = request.user.hcworker.health_center
    elif hasattr(request.user, 'bbworker'):
        title = request.user.bbworker.blood_bank
    elif hasattr(request.user, 'donor'):
        title = request.user.donor
    else:
        return render(request, 'access-denied.html')
    
    user_messages = MessageRecipient.objects.filter(user=request.user).order_by('-send_date')
    
    return render(request, 'inbox.html', {      
        "title": title,
        'message_list': user_messages
        })

# Simplifying sending messages to a donor
def send_donor_message(donor, title, body):
    message = Message.objects.create(
        title=title,
        body=body
    )
    MessageRecipient.objects.create(
        message=message,
        user=donor.donor_id,  
        recipient_type='donor'
    )
