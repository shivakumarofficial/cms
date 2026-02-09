from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import TimeOffRequest, Holiday, User

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'location', 'country', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location (e.g., SCV, USA)'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

class TimeOffRequestForm(forms.ModelForm):
    class Meta:
        model = TimeOffRequest
        fields = ['type', 'start_date', 'end_date', 'reason']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter reason for time-off request'}),
        }

class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = ['country', 'location', 'name', 'date']
        widgets = {
            'country': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('USA', 'USA'),
                ('UK', 'UK'),
                ('India', 'India'),
                ('Canada', 'Canada'),
            ]),
            'location': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('ALL', 'ALL'),
                ('AUS', 'AUS'),
                ('IST', 'IST'),
            ]),
            'name': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter holiday name...'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }