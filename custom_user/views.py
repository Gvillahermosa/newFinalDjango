from django.contrib.sites.shortcuts import get_current_site
from django.db import IntegrityError
from django.forms import ValidationError
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, authenticate
from .forms import RegistrationForm, LoginForm, LoginAdminForm
from .tokens import account_activation_token
from .models import User
from studentLife_system.models import studentInfo
from django.contrib.auth import logout



def index(request):
    form = RegistrationForm()
    form2 = LoginForm()
    return render(request, "application/signin.html", { "form":form, "form2":form2})

def login_user(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            try:
                email = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password")
                user = authenticate(email=email, password=password)
                if user is not None:
                    if not user.is_active:
                        messages.error(request, "Your account is not activated. Please check your email and activate your account.")
                    else:
                        login(request, user)
                       
                        if user.is_staff:
                            return redirect('admin_dashboard')
                        else:
                            return redirect('studentLife_system:homepage')
                else:
                    messages.error(request, "Invalid email or password.")
            except ValidationError as e:
                messages.error(request, "Invalid email or password.")
            except Exception as e:
                messages.error(request, "An error occurred during login: {}".format(str(e)))
                # Log the exception or handle it in some other way
        else: 
            try:
                email = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password")
                user = authenticate(email=email, password=password)
                if user is not None:
                    if not user.is_active:
                        messages.error(request, "Your account is not activated. Please check your email and activate your account.")
                    else:
                        login(request, user)
                        
                        if user.is_staff:
                            return redirect('admin_dashboard')
                        else:
                            return redirect('studentLife_system:homepage')
                else:
                    messages.error(request, "Invalid email or password.")
            except ValidationError as e:
                messages.error(request, "Invalid email or password.")
            except Exception as e:
                messages.error(request, "An error occurred during login: {}".format(str(e)))
    else:
        form = LoginForm()

    return render(request, "application/signin.html", {"form2": form})

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        
        if form.is_valid():
            # Get the student_id from the form
            student_id = form.cleaned_data.get('student_id')

            try:
                # Check if the student_id exists in the studentInfo model
                student_info = studentInfo.objects.get(studID=student_id)
            except studentInfo.DoesNotExist:
                messages.error(request, "The provided student ID does not exist in our records.")
                return redirect('custom_user:register')
            except Exception as e:
                messages.error(request, f"An error occurred while checking the student ID: {e}")
                return redirect('custom_user:register')
            
            try:
                if User.objects.filter(email=form.cleaned_data.get('email')).exists():
                    messages.error(request, "The email is already in use.")
                    return redirect('custom_user:register')

                # Check if the passwords match
                if form.cleaned_data.get('password1') != form.cleaned_data.get('password2'):
                    messages.error(request, "The passwords do not match.")
                    return redirect('custom_user:register')
                
                # Create the user and save it
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                # Continue with the account activation process
                current_site = get_current_site(request)
                mail_subject = "Activate your account"
                message = render_to_string(
                    "application/account_activation_email.html",
                    {
                        "user": user,
                        "domain": current_site.domain,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": account_activation_token.make_token(user),
                    },
                )
                to_email = form.cleaned_data.get("email")
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()
                messages.success(request, "Please check your email to complete the registration")
                return redirect("index")
            except Exception as e:
                messages.error(request, f"An error occurred while creating the user: {e}")
                return redirect('custom_user:register')
        else:
            # Add form errors to messages
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = RegistrationForm()
    
    return render(request, "application/signup.html", {"form": form})



def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Your account has been successfully activated!")
        return redirect(reverse("custom_user:index"))
    else:
        messages.error(request, "Activation link is invalid or expired")
        return redirect("custom_user:index")
    
import logging

def login_admin(request):
    if request.method == "POST":
        form = LoginAdminForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user_type = form.cleaned_data.get('user_type')
            user = authenticate(email=email, password=password)
            
            if user is not None:
                if not user.is_active:
                    messages.error(request, "Your account is not activated. Please check your email and activate your account.")
                else:
                    if user.user_type == user_type:
                        login(request, user)
                        if user_type == 'sao admin':
                            return redirect('studentLife_system:equipmentTrackerAdmin')
                        elif user_type == 'medical admin':
                            return redirect('medical:patient_profile')
                    else:
                        messages.error(request, "The provided user type does not match the user's account type.")
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid login form submission.")
            logging.debug("Form errors: %s", form.errors)
    else:
        form = LoginAdminForm()

    return render(request, "application/signin_admin.html", {"form": form})




def logout_user(request):
    logout(request)
    return redirect('studentLife_system:homepage')