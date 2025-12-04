"""
User Views Configuration.

This module handles:
1. Authentication (Login/Logout/Gatekeeping).
2. Registration for all user roles (Farmer, Supplier, Buyer, Delivery).
3. Profile Management.
4. Landing Page Logic.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Local Imports
from .forms import (
    FarmerRegistrationForm,
    SupplierRegistrationForm,
    DeliveryRegistrationForm,
    BuyerRegistrationForm,
    ProfileUpdateForm
)


# ==========================================
# 1. LANDING & NAVIGATION
# ==========================================

def landing_page(request):
    """
    Traffic Control:
    - If logged in -> Redirect to Grand Market (Home).
    - If guest -> Show Landing Page with samples.
    """
    if request.user.is_authenticated:
        return redirect('home')

    # Local import to prevent Circular Import Errors with User model
    from marketplace.models import Crop

    # Show last 50 active crops as a teaser
    recent_crops = Crop.objects.filter(is_active=True).order_by('-created_at')[:50]
    return render(request, 'landing.html', {'recent_crops': recent_crops})


def select_role(request):
    """Page to choose which registration path to take."""
    return render(request, 'select_role.html')


# ==========================================
# 2. AUTHENTICATION (Login/Logout)
# ==========================================

def login_view(request):
    """
    Custom Login View.
    Includes 'Gatekeeper' logic for Delivery drivers (Must be Verified).
    """
    if request.method == 'POST':
        phone = request.POST.get('phone_number')
        pin = request.POST.get('password')

        # Attempt Auth: Try standard username param, fallback to specific field
        user = authenticate(request, username=phone, password=pin)
        if user is None:
            user = authenticate(request, phone_number=phone, password=pin)

        if user is not None:
            # 🛑 LOGISTICS GATEKEEPER CHECK
            if user.user_type == 'delivery':
                if not user.is_verified:
                    return redirect('delivery_pending')
                else:
                    login(request, user)
                    messages.success(request, "🎉 You are verified! Welcome to the Logistics Team.")
                    return redirect('home')

            # Standard Login for Farmers/Buyers/Suppliers
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid Phone Number or PIN")

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ==========================================
# 3. REGISTRATION VIEWS
# ==========================================

def register_farmer(request):
    if request.method == 'POST':
        form = FarmerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-Login
            return redirect('home')
    else:
        form = FarmerRegistrationForm()
    return render(request, 'register.html', {'form': form})


def register_supplier(request):
    if request.method == 'POST':
        form = SupplierRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-Login
            return redirect('home')
    else:
        form = SupplierRegistrationForm()
    return render(request, 'register_supplier.html', {'form': form})


def register_buyer(request):
    if request.method == 'POST':
        form = BuyerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-Login
            return redirect('home')
    else:
        form = BuyerRegistrationForm()
    return render(request, 'register_buyer.html', {'form': form})


def register_delivery(request):
    """
    Registers a Driver and populates the specific DriverProfile.
    Redirects to 'Pending' page instead of Home.
    """
    if request.method == 'POST':
        form = DeliveryRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Save User (Signal creates empty Profile)
            user = form.save()

            # 2. Populate Profile with Form Data
            profile = user.driver_profile

            # Set Defaults (CDN / Pending)
            profile.workforce_type = 'CDN'
            profile.status = 'pending'

            # Legal Docs
            profile.national_id_image = form.cleaned_data['national_id']
            profile.license_image = form.cleaned_data['license_image']
            profile.license_number = form.cleaned_data['license_number']

            # Vehicle Info
            profile.vehicle_type = form.cleaned_data['vehicle_type']
            profile.max_capacity_kg = form.cleaned_data['max_capacity_kg']

            profile.save()

            return redirect('delivery_pending')
    else:
        form = DeliveryRegistrationForm()

    return render(request, 'register_delivery.html', {'form': form})


def delivery_pending(request):
    """Static page telling drivers to wait for approval."""
    return render(request, 'delivery_pending.html')


# ==========================================
# 4. PROFILE MANAGEMENT
# ==========================================

@login_required
def profile_view(request):
    """
    User Profile Update View.
    Handles Personal Info, Banking Details, and Profile Pictures.
    """
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Profile Updated Successfully!")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'profile.html', {'form': form})