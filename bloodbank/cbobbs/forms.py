# forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import BloodbankWorker, HealthcareWorker, Donor

ROLE_CHOICES = [
    ('employee', 'Employee'),
    ('admin', 'Admin'),
]

class BloodBankWorkerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True,max_length=254)
    first_name = forms.CharField(max_length=150,required=True)
    last_name = forms.CharField(max_length=150,required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES,required=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'password1', 'password2']

    def clean_email(self):
            email = self.cleaned_data.get('email')

            
            if User.objects.filter(email=email).exists():
                raise ValidationError("A user with this email already exists in the system.")
            if BloodbankWorker.objects.filter(email=email).exists():
                raise forms.ValidationError("A worker with this email already exists.")
        
            return email
    
class HealthCareWorkerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True,max_length=254)
    first_name = forms.CharField(max_length=150,required=True)
    last_name = forms.CharField(max_length=150,required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES,required=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'password1', 'password2']

    def clean_email(self):
            email = self.cleaned_data.get('email')

            
            if User.objects.filter(email=email).exists():
                raise ValidationError("A user with this email already exists in the system.")
            if HealthcareWorker.objects.filter(email=email).exists():
                raise forms.ValidationError("A worker with this email already exists.")
        
            return email
    
class DonorRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True,max_length=254)
    first_name = forms.CharField(max_length=150,required=True)
    last_name = forms.CharField(max_length=150,required=True)
    

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_email(self):
            email = self.cleaned_data.get('email')

            
            if User.objects.filter(email=email).exists():
                raise ValidationError("A user with this email already exists in the system.")
            if Donor.objects.filter(email=email).exists():
                raise forms.ValidationError("A user with this email already exists.")
        
            return email
