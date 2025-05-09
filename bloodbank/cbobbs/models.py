from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import requests
from django.conf import settings

# Create your models here.
class Donor(models.Model):
    donor_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="donor") # required
    name = models.CharField(max_length=50) 
    address = models.CharField(max_length=512, blank=True) 
    phone = models.CharField(max_length=10, blank=True) 
    birth_date = models.DateField(null=True, blank=True)  
    email = models.CharField(max_length=50) 
    medical_notes = models.TextField(blank=True, null=True)
    
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)

    class Meta:
        unique_together = [
            ('phone', 'email')
        ]
        

class HealthCenter(models.Model):
    hc_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, default="Health Center")
    phone = models.CharField(max_length=10,  default="9999999999")
    address = models.CharField(max_length=512)
    admin_key = models.CharField(max_length=5, default="admin")
    
    class Meta:
        unique_together = ('address',)


class HealthcareWorker(models.Model):
    hc_worker_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,related_name="hcworker")
    name = models.CharField(max_length=310)
    email = models.CharField(max_length=254)
    health_center = models.ForeignKey(HealthCenter, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=50,
        choices=[('admin', 'Admin'), ('employee', 'Employee')],
        default='employee',
    )


class BloodBank(models.Model):
    bb_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, default="Blood Bank")
    phone = models.CharField(max_length=10, default="9999999999")
    address = models.CharField(max_length=512, unique=True)
    zipcode = models.CharField(max_length=10, default="28277")
    city = models.CharField(max_length=100, default="Charlotte")
    state = models.CharField(max_length=100, default="North Carolina")
    admin_key = models.CharField(max_length=5, default="admin")

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    
    def save(self, *args, **kwargs):
        
        if not self.latitude or not self.longitude:
            full_address = f"{self.address}, {self.city}, {self.state} {self.zipcode}"
            geocoded = self.geocode_address(full_address)
            if geocoded:
                self.latitude = geocoded['lat']
                self.longitude = geocoded['lng']
        super().save(*args, **kwargs)

    def geocode_address(self, address):
        api_key = settings.GOOGLE_API_KEY 
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {'address': address, 'key': api_key}
        response = requests.get(url, params=params).json()
        if response['status'] == 'OK':
            loc = response['results'][0]['geometry']['location']
            return {'lat': loc['lat'], 'lng': loc['lng']}
        return None

    def __str__(self):
        return self.name



class BloodbankWorker(models.Model):
    bb_worker_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,related_name="bbworker")
    name = models.CharField(max_length=310)
    email = models.CharField(max_length=254, unique=True,)
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=50,
        choices=[('admin', 'Admin'), ('employee', 'Employee')],
        default='employee',
    )


class Donation(models.Model):
    dono_id = models.BigAutoField(primary_key=True)
    blood_type = models.CharField(max_length=5, default="n/a")
    donation_date = models.DateField()
    transfer_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10)
    transaction_date = models.DateField(null=True, blank=True)
    health_center = models.ForeignKey(HealthCenter, null=True, on_delete=models.CASCADE) 
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.CASCADE)
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)


class Appointment(models.Model):
    appt_id = models.BigAutoField(primary_key=True)
    appt_date = models.DateField(default=timezone.now)
    appt_time = models.DateTimeField(default=timezone.now)
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.CASCADE)


class Message(models.Model):
    message_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=50)
    body = models.TextField()
    
    def __str__(self):
        return self.title
    

class MessageRecipient(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipient_type = models.CharField(max_length=20, choices=[('donor', 'Donor'), ('blood_bank_worker', 'Blood Bank Worker'), ('hc_worker', 'Healthcare Worker')])
    send_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message to {self.user.username}"

