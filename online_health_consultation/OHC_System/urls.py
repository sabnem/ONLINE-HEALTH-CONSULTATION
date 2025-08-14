from django.urls import path, include
from . import views

urlpatterns = [
    # Authentication & Main Pages
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/change-photo/', views.change_profile_photo, name='change_profile_photo'),
    
    # Consultation & Appointments
    path('consultation/', views.book_consultation, name='book_consultation'),
    path('appointments/', views.appointments, name='appointments'),
    path('appointments/book/', views.book_appointment, name='book_appointment'),
    path('appointments/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    
    # Medical Records & Prescriptions
    
    # Articles & Resources
    path('articles/', views.health_articles, name='articles'),
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),
    path('records/', views.medical_records, name='records'),
    path('records/upload/', views.upload_record, name='upload_record'),
    path('prescriptions/', views.prescriptions, name='prescriptions'),
    path('prescriptions/<int:prescription_id>/', views.prescription_detail, name='prescription_detail'),
    
    # Emergency Services
    path('emergency/', views.emergency, name='emergency'),
    path('emergency/contact/', views.emergency_contact, name='emergency_contact'),
    
    # Doctor URLs
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor/availability/', views.doctor_availability, name='doctor_availability'),
    path('doctor/prescriptions/', views.doctor_prescriptions, name='doctor_prescriptions'),
    path('doctor/appointments/complete/<int:appointment_id>/', views.complete_appointment, name='complete_appointment'),
    path('doctor/prescriptions/<int:appointment_id>/write/', views.write_prescription, name='write_prescription'),
    path('doctor/consultations/', views.doctor_consultations, name='doctor_consultations'),
    path('doctor/patients/', views.doctor_patients, name='doctor_patients'),
    
    # User Profile & Settings
    path('profile/settings/', views.profile_settings, name='profile_settings'),
]
