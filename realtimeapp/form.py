
from .models import *

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms






class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username', 
            'first_name', 
            'last_name', 
            'email', 
         
        ]

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        
        fields = [
            'bio',
            'phone_number',
            'birth_date',
            'profile_image',
            'Gender',
            'city',
            'Landmark',
            'address',
            'pincode'
        ]


