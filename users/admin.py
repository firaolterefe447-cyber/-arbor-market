"""
User Administration Configuration.

This module customizes the Django Admin interface for user management.
FIX: Ensures approving a Driver Profile also sets user.is_verified = True.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    CustomUser,
    FarmerFollow,
    DriverProfile,
    DedicatedEmployee
)


# ==========================================
# 1. INLINE CONFIGURATIONS
# ==========================================

class DriverProfileInline(admin.StackedInline):
    """
    Inline view to manage Driver details directly within the User page.
    """
    model = DriverProfile
    can_delete = False
    verbose_name_plural = '🚛 Logistics Verification (ID & License)'
    fk_name = 'user'

    fields = (
        'workforce_type', 'status', 'reliability_score',
        'national_id_image', 'license_image', 'license_number',
        'vehicle_type', 'max_capacity_kg'
    )


class EmployeeProfileInline(admin.StackedInline):
    """
    Simplified Inline for Dedicated Employees.
    """
    model = DriverProfile
    can_delete = False
    verbose_name = "🚛 Assign Vehicle & License"
    verbose_name_plural = "🚛 Assign Vehicle & License"
    fk_name = 'user'

    fields = ('vehicle_type', 'max_capacity_kg', 'license_number')


# ==========================================
# 2. CUSTOM USER ADMIN
# ==========================================

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Main User Administration Interface.
    """
    model = CustomUser
    inlines = (DriverProfileInline,)
    ordering = ('phone_number',)
    list_per_page = 25

    # --- Field Layouts ---
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'first_name', 'last_name', 'user_type', 'password'),
        }),
    )

    fieldsets = (
        ('Login Information', {
            'fields': ('phone_number', 'password')
        }),
        ('Profile Details', {
            'fields': ('first_name', 'last_name', 'profile_picture', 'location')
        }),
        ('Business & Role', {
            'fields': ('user_type', 'business_name', 'is_verified', 'bank_name', 'bank_account_number')
        }),
        ('System Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')
        }),
    )

    list_display = (
        'profile_pic_circle', 'first_name', 'last_name', 'phone_number',
        'user_type_badge', 'is_verified', 'driver_status_badge', 'date_joined'
    )
    list_editable = ('is_verified',) # Allows quick ticking in the list
    list_filter = ('user_type', 'is_verified', 'is_active', 'driver_profile__status')
    search_fields = ('phone_number', 'first_name', 'last_name', 'business_name')

    actions = ['approve_users']

    # --- Actions ---
    def approve_users(self, request, queryset):
        """Bulk action to verify users and their driver profiles."""
        # 1. Verify User
        queryset.update(is_verified=True)

        # 2. Sync Driver Profile Status
        for user in queryset:
            if hasattr(user, 'driver_profile'):
                user.driver_profile.status = 'approved'
                user.driver_profile.save()

        self.message_user(request, "✅ Selected users verified successfully.")

    approve_users.short_description = "✅ Verify Selected Users"

    # --- Visual Badges ---
    def user_type_badge(self, obj):
        colors = {
            'farmer': '#10b981',  'buyer': '#3b82f6',
            'supplier': '#8b5cf6', 'delivery': '#f59e0b', 'admin': '#ef4444'
        }
        color = colors.get(obj.user_type, '#64748b')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; '
            'border-radius: 20px; font-size: 11px; font-weight: 800;">{}</span>',
            color, obj.user_type.upper()
        )
    user_type_badge.short_description = "Role"

    def driver_status_badge(self, obj):
        if hasattr(obj, 'driver_profile'):
            status = obj.driver_profile.status
            color = 'green' if status == 'approved' else 'orange' if status == 'pending' else 'red'
            return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, status.upper())
        return "-"
    driver_status_badge.short_description = "Logistics Status"

    def profile_pic_circle(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="width: 45px; height: 45px; border-radius: 50%; '
                'border: 3px solid white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); object-fit: cover;" />',
                obj.profile_picture.url
            )
        return format_html(
            '<div style="width: 45px; height: 45px; border-radius: 50%; background: #94a3b8; '
            'color: white; display: flex; align-items: center; justify-content: center; '
            'font-weight: bold; border: 3px solid white;">{}</div>',
            obj.first_name[0] if obj.first_name else "?"
        )
    profile_pic_circle.short_description = "User"


# ==========================================
# 3. DEDICATED EMPLOYEE ADMIN (Proxy)
# ==========================================

@admin.register(DedicatedEmployee)
class DedicatedEmployeeAdmin(admin.ModelAdmin):
    inlines = (EmployeeProfileInline,)
    fields = ('first_name', 'last_name', 'phone_number', 'password', 'is_active')
    list_display = ('first_name', 'last_name', 'phone_number', 'vehicle_info', 'is_active')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user_type='delivery', driver_profile__workforce_type='DEDICATED')

    def vehicle_info(self, obj):
        if hasattr(obj, 'driver_profile'):
            return f"{obj.driver_profile.vehicle_type} ({obj.driver_profile.max_capacity_kg}kg)"
        return "No Vehicle Assigned"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user_type = 'delivery'
            obj.is_verified = True
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

        if hasattr(obj, 'driver_profile'):
            profile = obj.driver_profile
            profile.workforce_type = 'DEDICATED'
            profile.status = 'approved'
            profile.save()


# ==========================================
# 4. DRIVER PROFILE ADMIN (THE FIX IS HERE)
# ==========================================

@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    """
    Independent view for Logistics Managers to review IDs and Licenses.
    """
    list_display = ('user', 'workforce_type', 'id_preview', 'license_preview', 'status')
    list_filter = ('workforce_type', 'status')
    search_fields = ('user__phone_number',)
    actions = ['approve_drivers']

    def id_preview(self, obj):
        if obj.national_id_image:
            return format_html('<img src="{}" style="height: 50px; border-radius: 5px;" />', obj.national_id_image.url)
        return "❌ Missing ID"

    def license_preview(self, obj):
        if obj.license_image:
            return format_html('<img src="{}" style="height: 50px; border-radius: 5px;" />', obj.license_image.url)
        return "❌ Missing License"

    # --- THE FIX: APPROVE DRIVER AND VERIFY USER ---
    def approve_drivers(self, request, queryset):
        # 1. Update Profile Status
        updated_count = queryset.update(status='approved')

        # 2. IMPORTANT: Loop through and update the parent User's verification checkbox
        for profile in queryset:
            profile.user.is_verified = True
            profile.user.save()

        self.message_user(request, f"✅ Approved {updated_count} drivers and verified their user accounts.")

    approve_drivers.short_description = "✅ Approve Driver & Verify User"


@admin.register(FarmerFollow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'farmer', 'created_at')