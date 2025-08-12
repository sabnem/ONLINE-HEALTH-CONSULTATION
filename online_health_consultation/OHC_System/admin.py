from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib import messages
from .models import (
    Profile, Doctor, Appointment, MedicalRecord, Prescription, 
    HealthArticle, Question, Answer, Tip, EmergencyContact
)

# Define inline admin for Profile
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

# Extend User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_is_doctor')
    list_filter = BaseUserAdmin.list_filter + ('profile__is_doctor',)
    
    def get_is_doctor(self, obj):
        return obj.profile.is_doctor if hasattr(obj, 'profile') else False
    get_is_doctor.short_description = 'Is Doctor'
    get_is_doctor.boolean = True

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'doctor', 'datetime', 'appointment_type', 'status')
    list_filter = ('status', 'appointment_type', 'doctor')
    search_fields = ('user__username', 'doctor__user__username', 'symptoms')
    date_hierarchy = 'datetime'
    list_per_page = 20
    ordering = ('-datetime',)
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new appointment
            messages.add_message(request, messages.INFO, f'New appointment created for {obj.user} with Dr. {obj.doctor}')
        super().save_model(request, obj, form, change)

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'record_type', 'date', 'uploaded_at')
    list_filter = ('record_type', 'date')
    search_fields = ('user__username', 'title', 'notes')
    readonly_fields = ('uploaded_at',)
    list_per_page = 20
    ordering = ('-uploaded_at',)

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'doctor', 'date', 'get_medications', 'is_active')
    list_filter = ('is_active', 'date', 'doctor')
    search_fields = ('user__username', 'doctor__user__username', 'medications', 'diagnosis')
    readonly_fields = ('date',)
    list_per_page = 20
    ordering = ('-date',)

    def get_medications(self, obj):
        return obj.medications[:50] + '...' if len(obj.medications) > 50 else obj.medications
    get_medications.short_description = 'Medications'

@admin.register(HealthArticle)
class HealthArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'featured', 'get_excerpt')
    list_filter = ('featured', 'author')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    ordering = ('-created_at',)
    
    def get_excerpt(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    get_excerpt.short_description = 'Content Preview'

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'specialization', 'license_number', 'is_available', 'experience_years')
    list_filter = ('specialization', 'is_available', 'experience_years')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'license_number')
    readonly_fields = ('user',)
    list_per_page = 20
    
    def get_full_name(self, obj):
        return f"Dr. {obj.user.get_full_name() or obj.user.username}"
    get_full_name.short_description = 'Doctor Name'

    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'specialization', 'license_number', 'experience_years')
        }),
        ('Availability', {
            'fields': ('is_available', 'available_from', 'available_to')
        }),
        ('Financial', {
            'fields': ('consultation_fee',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient', 'date_posted', 'answered')
    list_filter = ('answered', 'date_posted')
    search_fields = ('title', 'description', 'patient__username')
    readonly_fields = ('date_posted',)
    list_per_page = 20
    ordering = ('-date_posted',)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'doctor', 'date_answered')
    search_fields = ('question__title', 'doctor__username', 'response')
    readonly_fields = ('date_answered',)
    list_per_page = 20
    ordering = ('-date_answered',)

@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = ('title', 'doctor', 'date_posted')
    search_fields = ('title', 'content', 'doctor__username')
    readonly_fields = ('date_posted',)
    list_per_page = 20
    ordering = ('-date_posted',)

@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'emergency_type', 'contact_number', 'created_at', 'is_resolved')
    list_filter = ('emergency_type', 'is_resolved')
    search_fields = ('name', 'contact_number', 'description', 'location')
    readonly_fields = ('created_at',)
    list_per_page = 20
    ordering = ('-created_at',)
