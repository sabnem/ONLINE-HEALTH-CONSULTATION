from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_doctor = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg', blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)  # Making it nullable for existing records
    blood_group = models.CharField(max_length=3, blank=True)
    emergency_contact_name = models.CharField(max_length=100, null=True, blank=True)  # Making it nullable for existing records
    emergency_contact_phone = models.CharField(max_length=15, null=True, blank=True)  # Making it nullable for existing records

    def __str__(self):
        return f"{self.user.username} - {'Doctor' if self.is_doctor else 'Patient'}"

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    is_available = models.BooleanField(default=True)
    available_from = models.TimeField(null=True, blank=True)
    available_to = models.TimeField(null=True, blank=True)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    experience_years = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"

    def get_display_name(self):
        full_name = self.user.get_full_name()
        return f"Dr. {full_name} ({self.specialization})" if full_name else f"Dr. {self.user.username} ({self.specialization})"

class Prescription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_prescriptions')
    appointment = models.OneToOneField('Appointment', on_delete=models.SET_NULL, null=True, blank=True)
    diagnosis = models.TextField()
    medications = models.TextField()
    instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.user.username} by Dr. {self.doctor.user.username}"

    class Meta:
        ordering = ['-date']

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'

class HealthArticle(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    summary = models.TextField()
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='article_images/', null=True, blank=True)
    featured = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_related_articles(self):
        return HealthArticle.objects.filter(
            category=self.category
        ).exclude(id=self.id).order_by('-views')[:5]

    def __str__(self):
        return self.title
    experience_years = models.IntegerField()
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    available_from = models.TimeField()
    available_to = models.TimeField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"

class Appointment(models.Model):
    APPOINTMENT_TYPE_CHOICES = [
        ('Consultation', 'Consultation'),
        ('Follow-up', 'Follow-up'),
        ('Test', 'Test'),
        ('Procedure', 'Procedure')
    ]
    
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('No-show', 'No-show')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    datetime = models.DateTimeField(null=True, blank=True)
    appointment_type = models.CharField(
        max_length=20,
        choices=APPOINTMENT_TYPE_CHOICES,
        default='Consultation'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Scheduled'
    )
    symptoms = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-datetime']

    def __str__(self):
        return f"{self.appointment_type} with Dr. {self.doctor} on {self.datetime}"

class Question(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    answered = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Answer(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    response = models.TextField()
    date_answered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer to: {self.question.title}"

class Tip(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class MedicalRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    date = models.DateField()
    record_type = models.CharField(max_length=50)
    file = models.FileField(upload_to='medical_records/')
    notes = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class Prescription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    diagnosis = models.TextField()
    medications = models.TextField()
    instructions = models.TextField()
    next_visit = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Prescription for {self.user.username} by {self.doctor}"

class HealthArticle(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    featured = models.BooleanField(default=False)
    image = models.ImageField(upload_to='article_images/', null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class EmergencyContact(models.Model):
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    location = models.TextField()
    emergency_type = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Emergency - {self.name} - {self.emergency_type}"
