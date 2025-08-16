from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token, rotate_token
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django import forms
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.middleware.csrf import get_token
from django.core.exceptions import PermissionDenied
from .models import (
    Profile, Doctor, Appointment, MedicalRecord, 
    Prescription, HealthArticle
)
from .forms import (
    UserRegistrationForm, ProfileUpdateForm, UserUpdateForm,
    AppointmentForm, MedicalRecordForm, EmergencyContactForm, PrescriptionForm
)

def home(request):
    """Render the home page of the Online Health Consultation System."""
    articles = HealthArticle.objects.filter(featured=True)[:3]
    return render(request, 'online_health_consultation/home.html', {'featured_articles': articles})

@login_required
def change_profile_photo(request):
    """Handle profile photo updates."""
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        profile = request.user.profile
        profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        messages.success(request, 'Profile photo updated successfully!')
    return redirect('profile')

@login_required
def delete_profile_photo(request):
    """Handle profile photo deletion."""
    if request.method == 'POST':
        profile = request.user.profile
        if profile.profile_picture:
            profile.profile_picture.delete()  # Delete the actual file
            profile.profile_picture = None    # Clear the field
            profile.save()
            messages.success(request, 'Profile photo deleted successfully!')
    return redirect('profile')

@login_required
def profile(request):
    """Display user profile information."""
    user = request.user
    context = {
        'user': user,
        'appointments': user.patient_appointments.all()[:5] if hasattr(user, 'patient_appointments') else None
    }
    return render(request, 'online_health_consultation/profile.html', context)

class CombinedProfileForm(forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    phone_number = forms.CharField(max_length=15)
    emergency_contact_name = forms.CharField(max_length=100, required=False)
    emergency_contact_phone = forms.CharField(max_length=15, required=False)
    blood_group = forms.ChoiceField(
        choices=[
            ('', 'Select Blood Group'),
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('O+', 'O+'), ('O-', 'O-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
        ],
        required=False
    )

from django.views.decorators.csrf import ensure_csrf_cookie

@login_required
@ensure_csrf_cookie
@csrf_protect
def profile_edit(request):
    """Handle user profile updates with enhanced CSRF protection."""
    # Force CSRF cookie to be set
    get_token(request)
    
    if request.method == 'POST':
        if not request.POST.get('csrfmiddlewaretoken'):
            raise PermissionDenied('CSRF token missing')
        if request.user.profile.is_doctor:
            form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
            profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
            if form.is_valid() and profile_form.is_valid():
                form.save()
                profile_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('profile')
        else:
            form = CombinedProfileForm(request.POST, request.FILES)
            if form.is_valid():
                request.user.first_name = form.cleaned_data['first_name']
                request.user.last_name = form.cleaned_data['last_name']
                request.user.email = form.cleaned_data['email']
                request.user.save()
                
                profile = request.user.profile
                if request.FILES.get('profile_picture'):
                    profile.profile_picture = request.FILES['profile_picture']
                profile.date_of_birth = form.cleaned_data['date_of_birth']
                profile.phone_number = form.cleaned_data['phone_number']
                profile.emergency_contact_name = form.cleaned_data.get('emergency_contact_name', '')
                profile.emergency_contact_phone = form.cleaned_data.get('emergency_contact_phone', '')
                profile.blood_group = form.cleaned_data.get('blood_group', '')
                profile.save()
                
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('profile')
    else:
        if request.user.profile.is_doctor:
            form = UserUpdateForm(instance=request.user)
        else:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'date_of_birth': request.user.profile.date_of_birth,
                'phone_number': request.user.profile.phone_number,
                'emergency_contact_name': request.user.profile.emergency_contact_name,
                'emergency_contact_phone': request.user.profile.emergency_contact_phone,
                'blood_group': request.user.profile.blood_group,
            }
            form = CombinedProfileForm(initial=initial_data)
                
    return render(request, 'online_health_consultation/profile_edit.html', {'form': form})

# Authentication Views
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def user_logout(request):
    logout(request)
    # Ensure the session is cleared
    request.session.flush()
    # Clear any cookies
    response = redirect('home')
    response.delete_cookie('sessionid')
    messages.success(request, 'You have been successfully logged out.')
    return response

from django.views.decorators.csrf import csrf_protect

from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

@requires_csrf_token
def user_login(request):
    """Handle user login."""
    # Debug logging
    logger.info(f'Method: {request.method}')
    logger.info(f'CSRF Cookie: {request.COOKIES.get("csrftoken")}')
    if request.method == 'POST':
        logger.info(f'CSRF Token from POST: {request.POST.get("csrfmiddlewaretoken")}')
    
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile') and request.user.profile.is_doctor:
            return redirect('doctor_dashboard')
        return redirect('dashboard')

    # Set cookie and token explicitly for both GET and POST
    token = get_token(request)
    form = AuthenticationForm()
    if request.method == 'POST':
            
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Rotate CSRF token on successful login
                rotate_token(request)
                if hasattr(user, 'profile') and user.profile.is_doctor:
                    messages.success(request, f'Welcome back, Dr. {user.get_full_name() or username}!')
                    next_url = request.GET.get('next', 'doctor_dashboard')
                else:
                    messages.success(request, f'Welcome back, {username}!')
                    next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        # GET request
        form = AuthenticationForm()
    
    response = render(request, 'online_health_consultation/login.html', {'form': form})
    response.set_cookie(
        'csrftoken',
        token,
        max_age=60 * 60 * 24 * 7,  # 7 days
        domain=None,
        path='/',
        secure=False,
        httponly=False,
        samesite='Lax'
    )
    return response

def register(request):
    """Handle user registration with role selection."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Create user first
                user = form.save(commit=False)
                user.email = form.cleaned_data.get('email')
                user.first_name = form.cleaned_data.get('first_name')
                user.last_name = form.cleaned_data.get('last_name')
                user.save()

                # Create or update profile
                try:
                    profile = Profile.objects.get(user=user)
                except Profile.DoesNotExist:
                    profile = Profile(user=user)

                user_type = form.cleaned_data.get('user_type')
                profile.is_doctor = (user_type == 'doctor')
                
                # Handle profile fields based on user type
                if user_type == 'patient':
                    # Set patient-specific fields
                    profile.date_of_birth = form.cleaned_data.get('date_of_birth')
                    profile.phone_number = form.cleaned_data.get('phone_number')
                    profile.blood_group = form.cleaned_data.get('blood_group')
                    profile.emergency_contact_name = form.cleaned_data.get('emergency_contact_name')
                    profile.emergency_contact_phone = form.cleaned_data.get('emergency_contact_phone')
                else:
                    # For doctors, set these fields to None/empty
                    profile.date_of_birth = None
                    profile.phone_number = ''
                    profile.blood_group = ''
                    profile.emergency_contact_name = ''
                    profile.emergency_contact_phone = ''
                profile.save()

                # If registering as a doctor, create doctor profile
                if form.cleaned_data.get('user_type') == 'doctor':
                    Doctor.objects.create(
                        user=user,
                        specialization=form.cleaned_data.get('specialization'),
                        license_number=form.cleaned_data.get('license_number'),
                        experience_years=form.cleaned_data.get('experience_years'),
                        consultation_fee=form.cleaned_data.get('consultation_fee'),
                        available_from='09:00',  # Default availability
                        available_to='17:00'
                    )

                messages.success(request, 'Your account has been created successfully! You can now log in.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'An error occurred while creating your account: {str(e)}')
                if 'user' in locals() and user.id:
                    user.delete()  # Rollback user creation
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'online_health_consultation/register.html', {'form': form})

@login_required
def user_logout(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def dashboard(request):
    """Render the user's dashboard with all relevant information."""
    user = request.user
    is_doctor = user.profile.is_doctor

    # Get appointments queryset
    if is_doctor:
        appointments = Appointment.objects.filter(
            doctor__user=user,
            status__in=['Scheduled', 'Confirmed']
        ).order_by('datetime')
        appointments_count = appointments.count()
        upcoming_appointments = appointments[:5]
        consultations_count = appointments.filter(appointment_type='Consultation').count()
    else:
        appointments = Appointment.objects.filter(
            user=user,
            status__in=['Scheduled', 'Confirmed']
        ).order_by('datetime')
        appointments_count = appointments.count()
        upcoming_appointments = appointments[:5]
        consultations_count = appointments.filter(appointment_type='Consultation').count()

    # Get other counts
    records_count = MedicalRecord.objects.filter(user=user).count()
    prescriptions_count = Prescription.objects.filter(user=user).count()

    # Get recent articles
    recent_articles = HealthArticle.objects.order_by('-created_at')[:3] if HealthArticle.objects.exists() else []

    # Get recent activities
    activities = []  # Placeholder for activity feed

    context = {
        'upcoming_appointments': upcoming_appointments,
        'appointments_count': appointments_count,
        'consultations_count': consultations_count,
        'records_count': records_count,
        'prescriptions_count': prescriptions_count,
        'recent_articles': recent_articles,
        'activities': activities,
    }

    return render(request, 'online_health_consultation/dashboard.html', context)

# Consultation & Appointments
@login_required
def book_consultation(request):
    """Handle booking new consultations."""
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.appointment_type = 'Consultation'
            appointment.save()
            messages.success(request, 'Consultation booked successfully!')
            return redirect('dashboard')
    else:
        form = AppointmentForm()
    
    return render(request, 'online_health_consultation/book_consultation.html', {'form': form})

@login_required
def appointments(request):
    """View all appointments."""
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'online_health_consultation/appointments.html', {'appointments': appointments})

@login_required
def book_appointment(request):
    """Book a new appointment."""
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()
            messages.success(request, 'Appointment booked successfully!')
            return redirect('appointments')
    else:
        form = AppointmentForm()
    return render(request, 'online_health_consultation/book_appointment.html', {'form': form})

@login_required
def cancel_appointment(request, appointment_id):
    """Cancel an existing appointment."""
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    appointment.status = 'cancelled'
    appointment.save()
    messages.success(request, 'Appointment cancelled successfully!')
    return redirect('appointments')

# Medical Records & Prescriptions
@login_required
def medical_records(request):
    """View all medical records."""
    records = MedicalRecord.objects.filter(user=request.user)
    return render(request, 'online_health_consultation/records.html', {'records': records})

@login_required
def upload_record(request):
    """Upload a new medical record."""
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, request.FILES)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.save()
            return redirect('records')
    else:
        form = MedicalRecordForm()
    return render(request, 'online_health_consultation/upload_record.html', {'form': form})

@login_required
def prescriptions(request):
    """View all prescriptions."""
    prescriptions = Prescription.objects.filter(user=request.user)
    return render(request, 'online_health_consultation/prescriptions.html', {'prescriptions': prescriptions})

@login_required
def prescription_detail(request, prescription_id):
    """View detailed prescription information."""
    prescription = get_object_or_404(Prescription, id=prescription_id, user=request.user)
    return render(request, 'online_health_consultation/prescription_detail.html', {'prescription': prescription})

# Health Resources
def health_articles(request):
    """View health articles and resources."""
    articles = HealthArticle.objects.all()
    return render(request, 'online_health_consultation/articles.html', {'articles': articles})

def article_detail(request, article_slug):
    """View detailed article information."""
    article = get_object_or_404(HealthArticle, slug=article_slug)
    return render(request, 'online_health_consultation/article_detail.html', {'article': article})

# Emergency Services
def emergency(request):
    """Emergency services information page."""
    from django.conf import settings
    
    # Check if Google Maps API key is configured
    google_maps_api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
    if not google_maps_api_key:
        messages.warning(request, 'Google Maps API key is not configured. Nearby hospitals feature will not work.')
    
    context = {
        'google_maps_api_key': google_maps_api_key,
        'debug': settings.DEBUG,  # Pass debug status to template
    }
    return render(request, 'online_health_consultation/emergency.html', context)

def emergency_contact(request):
    """Emergency contact form."""
    if request.method == 'POST':
        form = EmergencyContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Emergency request sent successfully!')
            return redirect('emergency')
    else:
        form = EmergencyContactForm()
    return render(request, 'online_health_consultation/emergency_contact.html', {'form': form})

# User Profile & Settings
@login_required
def profile(request):
    """View user profile."""
    return render(request, 'online_health_consultation/profile.html')

@login_required
def profile_settings(request):
    """Update user profile settings."""
    return render(request, 'online_health_consultation/profile_settings.html')

# Doctor Views
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import datetime, timedelta

def is_doctor(user):
    return user.profile.is_doctor if hasattr(user, 'profile') else False

@login_required
@user_passes_test(is_doctor)
def doctor_dashboard(request):
    """Doctor's dashboard view."""
    today = timezone.now().date()
    doctor = request.user.doctor
    
    # Get today's appointments
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        datetime__date=today
    ).order_by('datetime')
    
    # Get pending consultations
    pending_consultations = Appointment.objects.filter(
        doctor=doctor,
        status='Scheduled',
        appointment_type='Consultation'
    ).count()
    
    # Get total unique patients
    total_patients = Appointment.objects.filter(
        doctor=doctor
    ).values('user').distinct().count()
    
    # Get completed sessions
    completed_sessions = Appointment.objects.filter(
        doctor=doctor,
        status='Completed'
    ).count()
    
    # Get recent activities
    recent_activities = []  # You can implement activity tracking here
    
    context = {
        'today_appointments': today_appointments[:5],  # Show only first 5
        'today_appointments_count': today_appointments.count(),
        'pending_consultations_count': pending_consultations,
        'total_patients_count': total_patients,
        'completed_sessions_count': completed_sessions,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'online_health_consultation/doctor_dashboard.html', context)

@login_required
@user_passes_test(is_doctor)
def doctor_appointments(request):
    """View doctor's appointments."""
    doctor = request.user.doctor
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-datetime')
    return render(request, 'online_health_consultation/doctor_appointments.html', {'appointments': appointments})

@login_required
@user_passes_test(is_doctor)
def doctor_consultations(request):
    """View doctor's consultations."""
    doctor = request.user.doctor
    
    # Get filter parameters
    date = request.GET.get('date')
    status = request.GET.get('status')
    
    # Base queryset
    consultations = Appointment.objects.filter(
        doctor=doctor,
        appointment_type='Consultation'
    ).order_by('-datetime')
    
    # Apply filters
    if date:
        try:
            filter_date = datetime.strptime(date, '%Y-%m-%d').date()
            consultations = consultations.filter(datetime__date=filter_date)
        except ValueError:
            messages.error(request, 'Invalid date format')
    
    if status:
        consultations = consultations.filter(status=status)
    
    return render(request, 'online_health_consultation/doctor_consultations.html', {'consultations': consultations})

@login_required
@user_passes_test(is_doctor)
def doctor_availability(request):
    """Update doctor's availability."""
    doctor = request.user.doctor
    if request.method == 'POST':
        # Handle availability update
        pass
    return render(request, 'online_health_consultation/doctor_availability.html', {'doctor': doctor})

@login_required
@user_passes_test(is_doctor)
def doctor_patients(request):
    """View doctor's patient list."""
    doctor = request.user.doctor
    patients = User.objects.filter(
        patient_appointments__doctor=doctor
    ).distinct()
    return render(request, 'online_health_consultation/doctor_patients.html', {'patients': patients})

@login_required
@user_passes_test(is_doctor)
def doctor_availability(request):
    """Update doctor's availability."""
    doctor = request.user.doctor
    if request.method == 'POST':
        doctor.is_available = request.POST.get('is_available') == 'on'
        doctor.available_from = request.POST.get('available_from')
        doctor.available_to = request.POST.get('available_to')
        
        try:
            doctor.consultation_fee = float(request.POST.get('consultation_fee', 0))
        except ValueError:
            messages.error(request, 'Invalid consultation fee value')
            return render(request, 'online_health_consultation/doctor_availability.html', {'doctor': doctor})
            
        doctor.save()
        messages.success(request, 'Availability settings updated successfully.')
        return redirect('doctor_dashboard')
    
    return render(request, 'online_health_consultation/doctor_availability.html', {'doctor': doctor})

@login_required
@user_passes_test(is_doctor)
def doctor_prescriptions(request):
    """Write new prescriptions."""
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.doctor = request.user.doctor
            prescription.save()
            messages.success(request, f'Prescription created successfully for {prescription.user.get_full_name() or prescription.user.username}.')
            return redirect('doctor_appointments')
    else:
        form = PrescriptionForm()
        # This ensures only patients appear in the dropdown
        form.fields['user'].queryset = User.objects.filter(profile__is_doctor=False).order_by('first_name', 'last_name')
    return render(request, 'online_health_consultation/doctor_prescriptions.html', {'form': form})

@login_required
@user_passes_test(is_doctor)
def complete_appointment(request, appointment_id):
    """Mark an appointment as completed."""
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor)
    if appointment.status != 'completed':
        appointment.status = 'completed'
        appointment.save()
        messages.success(request, 'Appointment marked as completed.')
    return redirect('doctor_appointments')

@login_required
@user_passes_test(is_doctor)
def write_prescription(request, appointment_id):
    """Write a prescription for a completed appointment."""
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor, status='completed')
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.doctor = request.user.doctor
            prescription.user = appointment.user
            prescription.appointment = appointment
            prescription.save()
            messages.success(request, f'Prescription created successfully for {prescription.user.get_full_name() or prescription.user.username}.')
            return redirect('doctor_appointments')
    else:
        # Initialize form with the appointment's patient and disable the field
        form = PrescriptionForm(initial={'user': appointment.user})
        form.fields['user'].disabled = True  # Make the user field read-only since it's from an appointment
        form.fields['user'].widget.attrs['class'] = 'form-control disabled'  # Add disabled styling
    
    context = {
        'form': form,
        'appointment': appointment,
        'patient_name': appointment.user.get_full_name() or appointment.user.username
    }
    return render(request, 'online_health_consultation/doctor_prescriptions.html', context)

def health_articles(request):
    """Display list of health articles."""
    # Get query parameters for filtering
    category = request.GET.get('category')
    
    # Query articles
    articles = HealthArticle.objects.all().order_by('-created_at')
    
    # Get popular articles
    popular_articles = HealthArticle.objects.all().order_by('-views')[:5]  # Get top 5 most viewed articles
    if category:
        articles = articles.filter(category__slug=category)
        
    # Get featured articles
    featured_articles = HealthArticle.objects.filter(featured=True)[:3]
    
    # Get popular articles
    popular_articles = HealthArticle.objects.order_by('-views')[:5]
    
    # Get all categories with article count
    categories = []
    # You would implement this based on your category model
    
    # Prepare context
    context = {
        'articles': articles,
        'featured_articles': featured_articles,
        'popular_articles': popular_articles,
        'categories': categories,
    }
    
    return render(request, 'online_health_consultation/articles.html', context)

def article_detail(request, slug):
    """Display a single article."""
    article = get_object_or_404(HealthArticle, slug=slug)
    
    # Increment view count
    article.views += 1
    article.save()
    
    return render(request, 'online_health_consultation/article_detail.html', {'article': article})