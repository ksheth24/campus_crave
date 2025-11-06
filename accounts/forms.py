from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import SellerVerificationApplication, Meal


class VerificationForm(forms.ModelForm):
    class Meta:
        model = SellerVerificationApplication
        fields = ['full_name', 'email', 'student_id_number', 'student_id_file', 'agree_meal_safety']
        widgets = {
            'agree_meal_safety': forms.CheckboxInput(),
        }

    def clean_agree_meal_safety(self):
        agree = self.cleaned_data.get('agree_meal_safety')
        if not agree:
            raise forms.ValidationError('You must agree to the meal safety agreement to apply.')
        return agree
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Pre-fill email if user is logged in
        if self.user and self.user.is_authenticated:
            self.fields['email'].initial = self.user.email
            if self.user.first_name or self.user.last_name:
                self.fields['full_name'].initial = f"{self.user.first_name} {self.user.last_name}".strip()
    
    def save(self, commit=True):
        application = super().save(commit=False)
        if self.user and self.user.is_authenticated:
            application.user = self.user
        if commit:
            application.save()
        return application


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['title', 'description', 'ingredients', 'photo', 'price', 
                  'pickup_location', 'pickup_latitude', 'pickup_longitude', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'ingredients': forms.Textarea(attrs={'rows': 3}),
            'pickup_latitude': forms.HiddenInput(),
            'pickup_longitude': forms.HiddenInput(),
        }
        help_texts = {
            'pickup_location': 'Enter a descriptive location (e.g., "Main Library, 2nd Floor")',
            'price': 'Price in USD',
        }
