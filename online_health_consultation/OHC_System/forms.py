from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Appointment, MedicalRecord, EmergencyContact

class UserRegistrationForm(UserCreationForm):
    USER_TYPE_CHOICES = [
        ('patient', 'Register as Patient'),
        ('doctor', 'Register as Doctor'),
    ]
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'btn-check'}),
        label='Register as',
        required=True
    )
    
    # Additional fields for doctors
    specialization = forms.CharField(required=False)
    license_number = forms.CharField(required=False)
    experience_years = forms.IntegerField(required=False)
    consultation_fee = forms.DecimalField(required=False, decimal_places=2)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        
        if user_type == 'doctor':
            # Make doctor fields required when registering as a doctor
            required_fields = ['specialization', 'license_number', 'experience_years', 'consultation_fee']
            for field in required_fields:
                value = cleaned_data.get(field)
                if not value:
                    self.add_error(field, 'This field is required')
        
        return cleaned_data

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'date_of_birth', 'blood_group', 'emergency_contact']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'datetime', 'appointment_type']
        widgets = {
            'datetime': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        doctor = cleaned_data.get('doctor')

        if date and time and doctor:
            # Check if the doctor is available at this time
            existing_appointments = Appointment.objects.filter(
                doctor=doctor,
                date=date,
                time=time,
                status='scheduled'
            )
            if existing_appointments.exists():
                raise forms.ValidationError('This time slot is already booked.')
        return cleaned_data

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['title', 'date', 'record_type', 'file', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'contact_number', 'location', 'emergency_type', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'location': forms.Textarea(attrs={'rows': 2}),
        }

class SearchDoctorForm(forms.Form):
    specialization = forms.CharField(required=False)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=False)
