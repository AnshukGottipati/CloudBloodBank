from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import BloodbankWorker, HealthcareWorker, Donor
from django.utils.translation import gettext_lazy as _

ROLE_CHOICES = [
    ('employee', 'Employee'),
    ('admin', 'Admin'),
]

class BloodBankWorkerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, max_length=254)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # get request for access to logged-in user
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        if BloodbankWorker.objects.filter(email=email).exists():
            raise ValidationError("A blood bank worker with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email']
        user.username = email
        if commit:
            user.save()

        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        full_name = f"{first_name} {last_name}"
        role = self.cleaned_data['role']

        # Safely get the blood_bank from the logged-in user
        if hasattr(self.request.user, 'bbworker'):
            blood_bank = self.request.user.bbworker.blood_bank
        else:
            raise ValidationError("Your account is not linked to a blood bank.")

        BloodbankWorker.objects.create(
            bb_worker_id=user,
            name=full_name,
            email=email,
            blood_bank=blood_bank,
            role=role
        )

        return user
    
class HealthCareWorkerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, max_length=254)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        if HealthcareWorker.objects.filter(email=email).exists():
            raise ValidationError("A healthcare worker with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()

        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        full_name = f"{first_name} {last_name}"
        email = self.cleaned_data['email']
        role = self.cleaned_data['role']

        try:
            health_center = self.request.user.hcworker.health_center.first()
        except AttributeError:
            raise ValidationError("Your account is not linked to a health center.")

        HealthcareWorker.objects.create(
            hc_worker_id=user,
            name=full_name,
            email=email,
            health_center=health_center,
            role=role
        )

        return user
    
class DonorRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, max_length=254)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)

    address = forms.CharField(max_length=512, required=False)
    phone = forms.CharField(max_length=10, required=False)
    birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    
    blood_type = forms.ChoiceField(choices=Donor.BLOOD_TYPE_CHOICES, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2',
                  'address', 'phone', 'birth_date', 'blood_type']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("A user with this email already exists in the system."))
        if Donor.objects.filter(email=email).exists():
            raise ValidationError(_("A donor with this email already exists."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email'] 
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()

            donor = Donor.objects.create(
                donor_id=user,
                name=f"{user.first_name} {user.last_name}",
                address=self.cleaned_data['address'],
                phone=self.cleaned_data['phone'],
                birth_date=self.cleaned_data['birth_date'],
                email=self.cleaned_data['email'],
                blood_type=self.cleaned_data['blood_type'],
            )

        return user