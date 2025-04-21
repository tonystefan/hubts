from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import User

class UserRegisterForm(UserCreationForm):
    """
    Form for user registration.
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class UserLoginForm(forms.Form):
    """
    Form for user login.
    """
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError('Email ou senha inválidos.')
        
        return self.cleaned_data

class UserProfileForm(forms.ModelForm):
    """
    Form for user profile update.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'profile_image']
