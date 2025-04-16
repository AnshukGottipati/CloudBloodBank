from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta, datetime
from .models import BloodBank, Donor, HealthcareWorker, Donation, Appointment, BloodbankWorker, HealthCenter
from django.db.models.functions import ExtractYear
from django.contrib import messages

# Create your views here.
def home(request):
    return render(request, "index.html")
    
def find_bloodbanks(request):
    bloodbanks = BloodBank.objects.all()
    
    context = {
        'bloodbanks': bloodbanks,
    }
    
    return render(request, "find-bloodbanks.html", context)

def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        try:
            # Try to get the donor with the matching email and password
            donor = Donor.objects.get(email=email, password=password)
            # Redirect to the donor dashboard
            return redirect("donor-dash")
        except Donor.DoesNotExist:
            # If no match is found, show an error
            error_message = "Invalid email or password. Please try again."
            return render(request, "login.html", {"error": error_message})
    
    return render(request, "login.html")

def eligibility(request):
    return render(request, "eligibility.html")

def donor_dash(request):
    # Get the first donor (assuming donor_id=1 or first in the database)
    donor = Donor.objects.first()
    
    if not donor:
        return render(request, 'donor/dashboard.html', {'message': 'No donor found.'})
    
    # Fetch all donations related to this donor (donor_id = 1)
    donations = Donation.objects.filter(donor=donor)

    # Calculate total donations
    total_donations = donations.count()

    # Get the most recent donation (if any)
    last_donation = donations.order_by('-donation_date').first()

    # Calculate the estimated lives saved (each donation can save 3 lives)
    estimated_lives_saved = total_donations * 3

    # Pass the data to the template
    context = {
        'donor': donor,
        'total_donations': total_donations,
        'last_donation': last_donation,
        'donations': donations,
        'estimated_lives_saved': estimated_lives_saved,
    }
    return render(request, 'donor/dashboard.html', context)

def donor_appt(request):
    donor = Donor.objects.order_by('donor_id').first()

    if not donor:
        return render(request, 'donor/appointments.html', {
            'appointments': [],
            'blood_banks': [],
            'error': 'No donors found in the system.'
        })

    appointments = Appointment.objects.filter(donor=donor).order_by('-appt_date', '-appt_time')
    blood_banks = BloodBank.objects.all()

    # Only handle the form if it's a POST request
    if request.method == "POST":
        appt_date = request.POST.get("appt_date")
        appt_time = request.POST.get("appt_time")
        blood_bank_id = request.POST.get("blood_bank_id")

        if appt_date and appt_time and blood_bank_id:
            try:
                full_appt_datetime = datetime.strptime(f"{appt_date} {appt_time}", "%Y-%m-%d %H:%M")
                blood_bank = BloodBank.objects.get(bb_id=blood_bank_id)

                Appointment.objects.create(
                    donor=donor,
                    appt_date=appt_date,
                    appt_time=full_appt_datetime,
                    blood_bank=blood_bank
                )
                return redirect("donor-appt")
            except ValueError:
                return render(request, "donor/appointments.html", {
                    "appointments": appointments,
                    "blood_banks": blood_banks,
                    "error": "Invalid date or time format."
                })

    return render(request, "donor/appointments.html", {
        "appointments": appointments,
        "blood_banks": blood_banks
    })

def donor_hist(request):
    # Get first donor (or fallback to donor_id=1)
    donor = Donor.objects.first() or Donor.objects.get(id=1)

    # Base query
    donations = Donation.objects.filter(donor=donor)

    # Filter by year if provided
    year = request.GET.get('year')
    if year:
        donations = donations.filter(donation_date__year=year)

    # Filter by blood bank if provided
    location = request.GET.get('location')
    if location:
        donations = donations.filter(blood_bank_id=location)

    # Unique years for dropdown
    years = Donation.objects.filter(donor=donor).annotate(
        year=ExtractYear('donation_date')
    ).values_list('year', flat=True).distinct().order_by('-year')

    bloodbanks = BloodBank.objects.all()

    return render(request, "donor/history.html", {
        "donations": donations,
        "years": years,
        "bloodbanks": bloodbanks,
        "request": request,  # Needed to access GET in template
    })

def donor_profile(request):
    # Retrieve the first donor (donor_id=1) or change to another condition if needed
    donor = Donor.objects.first()  # Assuming the first donor is what you want
    donations = Donation.objects.filter(donor_id=donor.donor_id)  # Use 'donor_id' instead of 'id'

    # Gather summary info like total donations and last donation date
    total_donations = donations.count()
    last_donation = donations.order_by('-donation_date').first()

    if request.method == 'POST':
        # Manually update the donor fields based on POST data
        donor.name = request.POST.get('name', donor.name)
        donor.email = request.POST.get('email', donor.email)
        donor.phone = request.POST.get('phone', donor.phone)
        donor.address = request.POST.get('address', donor.address)
        donor.birth_date = request.POST.get('birth_date', donor.birth_date)
        donor.blood_type = request.POST.get('blood_type', donor.blood_type)

        donor.save()  # Save the updated donor instance

        # Redirect after form submission
        return redirect('donor-profile')

    # If it's a GET request, render the page with the current donor data
    context = {
        'donor': donor,
        'donations': donations,
        'total_donations': total_donations,
        'last_donation': last_donation,
    }

    return render(request, 'donor/profile.html', context)

def bbworker_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Try to get the donor with the matching email and password
            bbworker = BloodbankWorker.objects.get(email=email, password=password)
            # Redirect to the donor dashboard
            return redirect("bb-dash")
        except BloodbankWorker.DoesNotExist:
            # If no match is found, show an error
            error_message = "Invalid email or password. Please try again."
            return render(request, "login.html", {"error": error_message})
    
    return render(request, 'bbworker/login.html')

def bbworker_dash(request):
    # Retrieve the first BloodbankWorker
    bb_worker = BloodbankWorker.objects.first()
    
    # Pass the BloodbankWorker object to the template
    context = {
        'bb_worker': bb_worker,
    }
    
    return render(request, 'bbworker/dashboard.html', context)

def bbworker_donors(request):
    # Retrieve all donations and related donors
    donations = Donation.objects.select_related('donor').all()  # Using select_related for optimization

    # Pass the donations with related donor information to the template
    return render(request, 'bbworker/donors.html', {'donations': donations})

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

def bbworker_profile(request):
    return render(request, "bbworker/profile.html")

def bbworker_reg_donor(request):
    return render(request, "bbworker/register-donor.html")

def bbworker_reg_worker(request):
    return render(request, "bbworker/register-worker.html")

def hcworker_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Try to get the donor with the matching email and password
            hcworker = HealthcareWorker.objects.get(email=email, password=password)
            # Redirect to the donor dashboard
            return redirect("hc-dash")
        except HealthcareWorker.DoesNotExist:
            # If no match is found, show an error
            error_message = "Invalid email or password. Please try again."
            return render(request, "login.html", {"error": error_message})
    
    return render(request, 'bbworker/login.html')

def hcworker_dash(request):
    return render(request, "hcworker/dashboard.html")

def hcworker_bloodsupply(request):
    return render(request, "hcworker/bloodsupply.html")

def hcworker_profile(request):
    return render(request, "hcworker/profile.html")

def hcworker_reg_worker(request):
    return render(request, "hcworker/register-worker.html")


