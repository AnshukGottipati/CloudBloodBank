from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import BloodbankWorker, HealthcareWorker, Donor, BloodBank, HealthCenter, Donation
from django.utils.translation import gettext_lazy as _

ROLE_CHOICES = [
    ('employee', 'Employee'),
    ('admin', 'Admin'),
]

STATUS_CHOICES = [
    ('processing', 'Processing'),
    ('testing', 'Testing'),
    ('processed', 'Processed'),
    ('delivered', 'Delivered'),
    ('used', 'Used'),
]

BLOOD_TYPE_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-'),
]

class BloodBankWorkerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, max_length=254)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)
    blood_bank = forms.ModelChoiceField(queryset=BloodBank.objects.all(), required=True)
    admin_key = forms.CharField(max_length=5, required=False, help_text="Required if registering for a different blood bank.")

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'blood_bank', 'admin_key', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        if BloodbankWorker.objects.filter(email=email).exists():
            raise ValidationError("A blood bank worker with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        selected_bank = cleaned_data.get('blood_bank')
        entered_key = cleaned_data.get('admin_key')

        if selected_bank and selected_bank:
            if selected_bank.admin_key != entered_key:
                self.add_error('admin_key', "Invalid admin key for selected blood bank.")


        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email']
        user.username = email
        if commit:
            user.save()

        full_name = f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}"
        role = self.cleaned_data['role']
        blood_bank = self.cleaned_data['blood_bank']

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
            #raise ValidationError("Your account is not linked to a health center.")
            health_center = HealthCenter.objects.first()  # Gets the first BloodBank entry
            if not health_center:
                raise ValidationError("No blood bank available to assign to this worker.")

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
    
class LogDonationForm(forms.Form):
    donor_email = forms.EmailField()
    donation_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )

class UpdateStatusForm(forms.Form):
    donor_email = forms.EmailField()
    donation_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    status = forms.ChoiceField(choices=STATUS_CHOICES)

class LogTransactionForm(forms.Form):
    donor_email = forms.EmailField()
    donation_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    transaction_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )

class TransportForm(forms.Form):
    BLOOD_TYPE_CHOICES = Donor.BLOOD_TYPE_CHOICES

    blood_type = forms.ChoiceField(choices=BLOOD_TYPE_CHOICES)
    transfer_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    health_center = forms.ModelChoiceField(queryset=HealthCenter.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize label for dropdown
        self.fields['health_center'].label_from_instance = lambda obj: obj.name