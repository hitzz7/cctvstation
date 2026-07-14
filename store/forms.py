from django import forms
from django.contrib.auth.models import User
from .models import StartaProject, UserProfile

class ContactForm(forms.ModelForm):
    class Meta:
        model = StartaProject
        fields = ['name', 'email', 'mobile', 'description']


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    phone = forms.CharField(max_length=20, required=False)
    pickup_location = forms.CharField(widget=forms.Textarea, required=False, help_text='Your pickup address')
    city = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'pickup_location', 'city']