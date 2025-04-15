from django.db import models
from django.utils import timezone

# Create your models here.
class Donor(models.Model):
    donor_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=512)
    phone = models.CharField(max_length=10)
    birth_date = models.DateField()
    blood_type = models.CharField(max_length=5)
    password = models.CharField(max_length=25)
    email = models.CharField(max_length=30)

    class Meta:
        unique_together = ('phone', 'email')

    class Meta:
        unique_together = ('name', 'email')


class HealthCenter(models.Model):
    hc_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=50, default="Health Center")
    address = models.CharField(max_length=512)
    
    class Meta:
        unique_together = ('address',)


class HealthcareWorker(models.Model):
    hc_worker_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=50)
    health_center = models.ForeignKey(HealthCenter, on_delete=models.CASCADE, default=1)


class BloodBank(models.Model):
    bb_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, default="Blood Bank")
    phone = models.CharField(max_length=10,  default="9999999999")
    address = models.CharField(max_length=512, unique=True)    


class BloodbankWorker(models.Model):
    bb_worker_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=50)
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.CASCADE, default=1)


class Donation(models.Model):
    dono_id = models.BigAutoField(primary_key=True)
    blood_type = models.CharField(max_length=5, default="n/a")
    donation_date = models.DateField()
    sent_at = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10)
    transaction_date = models.DateField(null=True, blank=True)
    health_center = models.OneToOneField(HealthCenter, on_delete=models.CASCADE)  # due to unique constraint
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.CASCADE)
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)


class Message(models.Model):
    message_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=50)
    body = models.TextField()


class DonorMessage(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('donor', 'message')


class Appointment(models.Model):
    appt_id = models.BigAutoField(primary_key=True)
    appt_date = models.DateField(default=timezone.now)
    appt_time = models.DateTimeField(default=timezone.now)
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.CASCADE)