from django.shortcuts import render

def home(request):
    #Render the home page of the Online Health Consultation System.
    return render(request, 'online_health_consultation/home.html')

def consult(request):
    #Render the consultation page where users can ask questions.
    return render(request, 'online_health_consultation/consult.html')

def tips(request):
    #Render the tips page where users can read health tips provided by doctors.
    return render(request, 'online_health_consultation/tips.html')

def profile(request):
    #Render the user profile page where users can view and edit their profile information.
    return render(request, 'online_health_consultation/profile.html')

def appointments(request):
    #Render the appointments page where users can view their scheduled appointments with doctors.
    return render(request, 'online_health_consultation/appointments.html')
def dashboard(request):
    return render(request, 'online_health_consultation/dashboard.html')

def register(request):
    return render(request, 'online_health_consultation/register.html')

def user_login(request):
    #Render the login page for users to authenticate themselves.
    return render(request, 'online_health_consultation/login.html')

def user_logout(request):
    return render(request, 'online_health_consultation/logout.html')