import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodbank.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.management import call_command
from cbobbs.models import HealthCenter, HealthcareWorker, BloodBank, BloodbankWorker

def create_data():
    
    create_hc(name="Atrium Health University City",
              address="8800 N Tryon St, Charlotte, NC 28262",
              phone="7048636000")
    
    create_hc(name="Sugar Creek Health Center",
              address="721 W Sugar Creek Rd, Charlotte, NC 28213",
              phone="7048599544")
    
    create_bb(name="American Red Cross - Charlotte",
              address="2425 Park Rd",
              city="Charlotte", 
              state="North Carolina", 
              zipcode="28203",
              phone="7043761661")
    
    create_bb(name="BioLife Plasma Services",
              address="5300 South Blvd", 
              city="Charlotte",
              state="North Carolina", 
              zipcode="28217",
              phone="7042641948")
    
    create_bb(name="CSL Plasma",  
              address="8404 N Tryon St",
              city="Charlotte",
              state="North Carolina",
              zipcode="28262",
              phone="9802653288")
    
    create_bb(name="Octapharma Plasma",
              address="3120 Milton Rd", 
              city="Charlotte",
              state="North Carolina",
              zipcode="28215",
              phone="7045373880")
    
    create_bb(name="Grifols Talecris - Plasma Donation Center",
              address="2901-A Freedom Dr",
              city="Charlotte",
              state="North Carolina",
              zipcode="28208",
              phone="7043926500") 
    
    call_command('populate_lat_lng')
    
    print("DB Populated ^-^")

def create_bb(name, phone, address, zipcode, city, state):
    bb = BloodBank.objects.create(name=name, 
                                   address=address, 
                                   city=city, 
                                   state=state, 
                                   zipcode=zipcode,
                                   phone=phone)
    
    email= f"admin@{name.split()[0].lower()}.com"
    
    user = User.objects.create_user(username=email, 
                                    password="pass123")
    
    BloodbankWorker.objects.create(
        bb_worker_id=user,
        name="admin",
        email=email,
        blood_bank=bb,
        role='admin')

def create_hc(name, phone, address):
    hc = HealthCenter.objects.create(name=name, 
                                      address=address, 
                                      phone=phone)
    
    email= f"admin@{name.split()[0].lower()}.com"

    user = User.objects.create_user(username=email,
                                    password="pass123")
    HealthcareWorker.objects.create(
            hc_worker_id=user,
            name="admin",
            email=email,
            health_center=hc,
            role="admin"
    )
    
create_data()
