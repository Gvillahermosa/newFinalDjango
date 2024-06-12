from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from custom_user.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from studentLife_system.models import studentInfo

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))
    student_id = forms.IntegerField(label='Student ID', required=True, widget=forms.NumberInput(attrs={'placeholder': 'Student ID'}))

    class Meta:
        model = User
        fields = ["email", "password1", "password2", "student_id"]

    def save(self, commit=True):
        user = super().save(commit=False)
        student_id = self.cleaned_data['student_id']

        try:
            student_info = studentInfo.objects.get(studID=student_id)
            user.student_id = student_info  # Assign the studentInfo instance to the user
            user.first_name = student_info.firstname
            user.last_name = student_info.lastname
        except studentInfo.DoesNotExist:
            raise forms.ValidationError("The provided student ID does not exist in our records.")

        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Invalid email or password")
            elif not user.is_active:
                raise forms.ValidationError("This account is inactive.")
        return self.cleaned_data

class LoginAdminForm(AuthenticationForm):
    user_type = forms.ChoiceField(choices=[('sao admin', 'Sao Admin'), ('medical admin', 'Medical Admin')], required=True, widget=forms.Select(attrs={'class': 'dropdown'}))
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    def clean(self):
        cleaned_data = super().clean()  # Call the parent clean method which handles authentication
        return cleaned_data
