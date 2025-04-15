from django.contrib import admin
from .models import Donor, HealthcareWorker, HealthCenter, BloodbankWorker, BloodBank, Donation, Message, DonorMessage

# Register your models here.
admin.site.register(Donor)
admin.site.register(HealthcareWorker)
admin.site.register(HealthCenter)
admin.site.register(BloodbankWorker)
admin.site.register(BloodBank)
admin.site.register(Donation)
admin.site.register(Message)
admin.site.register(DonorMessage)
