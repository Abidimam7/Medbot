from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

def signup_page(request):
    """
    Handle user registration.
    """
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'chatbot/signup.html')

        try:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            messages.success(request, "Signup successful. Please log in.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return render(request, 'chatbot/signup.html')


def login_page(request):
    """
    Handle user login.
    """
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('chatbot_page')  # Redirect to chatbot page after login
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'chatbot/login.html')


def logout_user(request):
    """
    Log out the user and redirect to the login page.
    """
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    """
    Display the user's profile.
    """
    return render(request, 'chatbot/profile.html')


@login_required
def update_profile(request):
    """
    Handle profile updates.
    """
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile_settings')
    else:
        return redirect('profile_settings')
