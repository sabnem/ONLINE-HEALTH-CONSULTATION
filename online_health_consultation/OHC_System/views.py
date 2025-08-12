from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Appointment, MedicalRecord, Prescription, HealthArticle
from .forms import AppointmentForm, MedicalRecordForm, EmergencyContactForm

def home(request):
    """Render the home page of the Online Health Consultation System."""
    articles = HealthArticle.objects.filter(featured=True)[:3]
    return render(request, 'online_health_consultation/home.html', {'featured_articles': articles})

# Authentication Views
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm, ProfileUpdateForm
from django.contrib import messages

def user_login(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'online_health_consultation/login.html', {'form': form})

def register(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create associated profile
            profile = user.profile  # Signal will create this
            profile.save()
            
            # Log the user in
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            
            messages.success(request, f'Account created successfully! Welcome, {username}!')
            return redirect('dashboard')
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
    return render(request, 'online_health_consultation/emergency.html')

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