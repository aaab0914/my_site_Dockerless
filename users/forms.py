
from django import forms

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from django.contrib.auth.models import User

from .models import Profile



class UserRegisterForm(UserCreationForm):
    """
    Form for user registration.

    Extends Django's built-in UserCreationForm to add an email field
    and custom CSS classes for better styling.

    Attributes:
        email: Custom EmailField with styling and validation
    """

    email = forms.EmailField(
        required=True,  # Email is mandatory for registration
        widget=forms.EmailInput(attrs={
            "class": "form-control",  # Bootstrap-like CSS class for styling
            "placeholder": "Email",  # Placeholder text shown in the input
        }),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            'password1',  # First password input
            'password2',  # Confirmation password input
        )
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Username",
            }),
            'password1': forms.PasswordInput(attrs={
                "class": "form-control",
                "placeholder": "Password",
            }),
            "password2": forms.PasswordInput(attrs={
                "class": "form-control",
                "placeholder": "Confirm Password",
            })
        }



class UserLoginForm(AuthenticationForm):
    """
    Form for user login.

    Extends Django's built-in AuthenticationForm to add custom CSS classes
    for username and password fields.

    Attributes:
        username: Custom CharField with styling
        password: Custom CharField with styling
    """

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Username",
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password",
        })
    )



class UserProfileForm(forms.ModelForm):
    """
    Form for editing user profile information.

    Allows users to update their bio, location, birth date, and avatar.

    Attributes:
        Meta: Inner class that defines model and field configuration
    """

    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birth_date', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4  # Number of rows for the textarea
            }),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'  # HTML5 date picker
            }),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
