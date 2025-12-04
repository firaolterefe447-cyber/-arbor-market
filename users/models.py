"""
User Models Configuration.

This module defines the custom authentication system based on Phone Numbers
instead of Usernames. It includes:
1. Custom User Manager (Phone-based auth).
2. Custom User Model (Roles: Farmer, Buyer, Supplier, Delivery).
3. Social Features (Following Farmers).
4. Logistics Profiles (Driver verification & Vehicle info).
5. Dedicated Employee Proxy (For HR/Admin organization).
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver


# ==========================================
# 1. CUSTOM USER MANAGER
# ==========================================

class CustomUserManager(BaseUserManager):
    """
    Custom manager to handle user creation via Phone Number.
    """

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError(_('The Phone Number must be set'))

        # Normalize/clean data here if necessary
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(phone_number, password, **extra_fields)


# ==========================================
# 2. CUSTOM USER MODEL
# ==========================================

class CustomUser(AbstractUser):
    """
    The central User model.
    Replaces 'username' with 'phone_number' and adds role-based fields.
    """

    # Disable standard fields
    username = None
    email = None

    # Role Definitions
    USER_TYPE_CHOICES = (
        ('farmer', 'Farmer'),
        ('supplier', 'Supplier'),
        ('buyer', 'Buyer'),
        ('delivery', 'Delivery'),
        ('admin', 'Admin'),
    )

    # --- Identity & Auth ---
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='farmer')
    phone_number = models.CharField(max_length=15, unique=True, help_text=_("Primary identifier for login"))

    # --- Personal Profile ---
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    location = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    # --- Business & Financial ---
    business_name = models.CharField(max_length=100, blank=True)
    bank_name = models.CharField(max_length=50, blank=True, help_text="e.g. CBE, Awash")
    bank_account_number = models.CharField(max_length=50, blank=True)

    # Django Auth Settings
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"


# ==========================================
# 3. SOCIAL GRAPH (Following)
# ==========================================

class FarmerFollow(models.Model):
    """
    Relationship allowing buyers to 'follow' or 'like' specific farmers.
    """
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='following')
    farmer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('buyer', 'farmer')
        verbose_name = "⭐ Farmer Follow"
        verbose_name_plural = "⭐ Farmer Follows"

    def __str__(self):
        return f"{self.buyer.first_name} follows {self.farmer.first_name}"


# ==========================================
# 4. LOGISTICS & DRIVER PROFILE
# ==========================================

class DriverProfile(models.Model):
    """
    Extended profile for users with user_type='delivery'.
    Handles CDN verification, vehicle details, and reliability scores.
    """
    WORKFORCE_TYPES = (
        ('CDN', 'CDN - Independent Contractor'),
        ('DEDICATED', 'Dedicated Fleet - Employee'),
    )

    VERIFICATION_STATUS = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved & Active'),
        ('rejected', 'Rejected'),
    )

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='driver_profile')

    # --- Operational Configuration ---
    workforce_type = models.CharField(max_length=20, choices=WORKFORCE_TYPES, default='CDN')
    status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    reliability_score = models.DecimalField(max_digits=3, decimal_places=2, default=3.00)

    # --- Legal & Compliance (KYC) ---
    national_id_image = models.ImageField(
        upload_to='driver_documents/ids/',
        blank=True, null=True,
        help_text="National ID (Kebele ID) Front"
    )
    license_number = models.CharField(max_length=50, blank=True, null=True)
    license_image = models.ImageField(upload_to='driver_documents/licenses/', blank=True, null=True)

    # --- Vehicle Assets ---
    vehicle_type = models.CharField(max_length=50, help_text="e.g. Isuzu FSR, Toyota Van")
    max_capacity_kg = models.IntegerField(default=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Driver: {self.user.first_name} [{self.workforce_type}]"


# ==========================================
# 5. SIGNALS
# ==========================================

@receiver(post_save, sender=CustomUser)
def create_driver_profile(sender, instance, created, **kwargs):
    """
    Automated Trigger:
    If a user is created with type 'delivery', create an empty DriverProfile for them.
    """
    if created and instance.user_type == 'delivery':
        DriverProfile.objects.create(user=instance)


# ==========================================
# 6. PROXY MODELS
# ==========================================

class DedicatedEmployee(CustomUser):
    """
    Proxy model to allow HR/Admins to manage Full-Time Employees separately
    from general users in the Admin Interface.
    """

    class Meta:
        proxy = True
        verbose_name = "👨‍✈️ Dedicated Employee"
        verbose_name_plural = "👨‍✈️ Dedicated Fleet (Employees)"