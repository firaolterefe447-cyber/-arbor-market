"""
User Registration and Profile Forms.

This module defines the forms for registering different user types.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

# ==========================================
# 1. FARMER REGISTRATION
# ==========================================

class FarmerRegistrationForm(forms.ModelForm):
    location = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-emerald-500 focus:ring-emerald-500',
        'placeholder': 'e.g. Bishoftu'
    }))
    password = forms.CharField(label=_("PIN"), widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-emerald-500 focus:ring-emerald-500',
        'placeholder': '4-digit PIN',
        'maxlength': '4',
        'inputmode': 'numeric'
    }))
    confirm_password = forms.CharField(label=_("Confirm PIN"), widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-emerald-500 focus:ring-emerald-500',
        'placeholder': 'Confirm PIN',
        'maxlength': '4',
        'inputmode': 'numeric'
    }))

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number', 'location', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-emerald-500',
                'placeholder': 'Abebe'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-emerald-500',
                'placeholder': 'Kebede'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-emerald-500',
                'placeholder': '0911...'
            }),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone).exists():
            raise ValidationError("This phone number is already registered.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and len(password) != 4:
            self.add_error('password', "PIN must be exactly 4 digits.")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "PINs do not match!")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.user_type = 'farmer'
        user.location = self.cleaned_data.get('location')
        user.is_verified = False # Farmers might need verification too
        if commit:
            user.save()
        return user


# ==========================================
# 2. BUYER REGISTRATION
# ==========================================

class BuyerRegistrationForm(forms.ModelForm):
    password = forms.CharField(label=_("PIN"), widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-amber-500 focus:ring-amber-500',
        'placeholder': '4-digit PIN',
        'maxlength': '4',
        'inputmode': 'numeric'
    }))
    confirm_password = forms.CharField(label=_("Confirm PIN"), widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-amber-500 focus:ring-amber-500',
        'placeholder': 'Confirm PIN',
        'maxlength': '4',
        'inputmode': 'numeric'
    }))

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-amber-500',
                'placeholder': 'Selam'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-amber-500',
                'placeholder': 'Tesfaye'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-amber-500',
                'placeholder': '0911...'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and len(password) != 4:
            self.add_error('password', "PIN must be exactly 4 digits.")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "PINs do not match!")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.user_type = 'buyer'
        user.is_verified = True # Buyers are auto-verified
        if commit:
            user.save()
        return user


# ==========================================
# 3. SUPPLIER REGISTRATION
# ==========================================

class SupplierRegistrationForm(forms.ModelForm):
    password = forms.CharField(label=_("PIN"), widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-blue-500 focus:ring-blue-500',
        'placeholder': '4-digit PIN',
        'maxlength': '4',
        'inputmode': 'numeric'
    }))
    confirm_password = forms.CharField(label=_("Confirm PIN"), widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-blue-500 focus:ring-blue-500',
        'placeholder': 'Confirm PIN',
        'maxlength': '4',
        'inputmode': 'numeric'
    }))

    class Meta:
        model = CustomUser
        fields = ['business_name', 'first_name', 'last_name', 'phone_number', 'password']
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-blue-500',
                'placeholder': 'Business Name'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-blue-500',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-blue-500',
                'placeholder': 'Last Name'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-blue-500',
                'placeholder': '0911...'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and len(password) != 4:
            self.add_error('password', "PIN must be exactly 4 digits.")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "PINs do not match!")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.user_type = 'supplier'
        user.is_verified = False
        if commit:
            user.save()
        return user


# ==========================================
# 4. DELIVERY REGISTRATION (FIXED)
# ==========================================

class DeliveryRegistrationForm(forms.ModelForm):
    # 1. User Account Fields
    password = forms.CharField(label=_("Create PIN"), widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-red-500 focus:ring-red-500',
        'placeholder': '4-digit PIN',
        'maxlength': '4',
        'inputmode': 'numeric'
    }))

    # 2. Profile Specific Fields (Explicitly defined here, NOT in Meta)
    # These will be accessed via form.cleaned_data in the View
    vehicle_type = forms.ChoiceField(
        choices=[
            ('motorcycle', 'Motorcycle'),
            ('van', 'Minivan'),
            ('isuzu', 'Isuzu/Truck')
        ],
        widget=forms.Select(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-red-500 bg-white',
    }))

    max_capacity_kg = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-red-500',
        'placeholder': 'Capacity in KG (e.g. 500)'
    }))

    license_number = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-red-500',
        'placeholder': 'License Number'
    }))

    # Image fields
    national_id = forms.ImageField(widget=forms.FileInput(attrs={
        'class': 'block w-full text-sm text-stone-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-bold file:bg-red-50 file:text-red-700 hover:file:bg-red-100'
    }))

    license_image = forms.ImageField(widget=forms.FileInput(attrs={
        'class': 'block w-full text-sm text-stone-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-bold file:bg-red-50 file:text-red-700 hover:file:bg-red-100'
    }))

    class Meta:
        model = CustomUser
        # IMPORTANT: Only include fields that exist on the CustomUser model here.
        # Do NOT include vehicle_type, license_number, etc. here.
        fields = [
            'first_name', 'last_name', 'phone_number', 'password'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-red-500',
                'placeholder': 'Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-red-500',
                'placeholder': 'Surname'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-200 focus:border-red-500',
                'placeholder': '0911...'
            }),
        }

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password and len(password) != 4:
            raise ValidationError("PIN must be exactly 4 digits.")
        return password

    def save(self, commit=True):
        # 1. Save the User part
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.user_type = 'delivery'
        user.is_verified = False # Delivery ALWAYS starts as unverified

        if commit:
            user.save()

        return user


# ==========================================
# 5. PROFILE UPDATE
# ==========================================

class ProfileUpdateForm(forms.ModelForm):
    # Personal Info Styling
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-emerald-500 focus:ring-emerald-500',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-emerald-500 focus:ring-emerald-500',
        'placeholder': 'Last Name'
    }))
    location = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-emerald-500 focus:ring-emerald-500',
        'placeholder': 'City, Region'
    }))

    # Custom File Input Styling for Tailwind
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100'
    }))

    # Banking Info (Styled with Yellow/Amber to match template)
    bank_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-yellow-300 focus:border-yellow-500 focus:ring-yellow-500 bg-yellow-50',
        'placeholder': 'e.g. CBE / Awash'
    }))
    bank_account_number = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-yellow-300 focus:border-yellow-500 focus:ring-yellow-500 bg-yellow-50',
        'placeholder': 'Account Number'
    }))

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'location', 'profile_picture', 'bank_name', 'bank_account_number']