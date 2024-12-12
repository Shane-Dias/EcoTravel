from django import forms
from .models import Trip
from .models import User
from .models import Profile, Transportation, Accommodation

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class TripForm(forms.ModelForm):
    transportation = forms.ModelChoiceField(queryset=Transportation.objects.all(), required=True)
    hotel = forms.ModelChoiceField(queryset=Accommodation.objects.all(), required=False)  # Optional field
    class Meta:
        model = Trip
        fields = ['start_date', 'end_date', 'accommodation', 'transportation', 'people', 'hotel']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'preferences', 'profile_pic']

class DestinationSearchForm(forms.Form):
    destination = forms.CharField(label="Search Destination", max_length=100)
    transport_mode = forms.ChoiceField(
        label="Transport Mode", 
        choices=[('driving', 'Electric Car'), 
                 ('transit', 'Public Transport'), 
                 ('walking', 'Walking'), 
                 ('bicycling', 'Cycling')]
    )

from django import forms
from .models import UploadedPlanTrip

class UploadedPlanTripForm(forms.ModelForm):
    class Meta:
        model = UploadedPlanTrip
        fields = ['image']