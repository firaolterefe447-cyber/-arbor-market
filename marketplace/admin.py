"""
Marketplace Admin Configuration.

This module defines the custom administrative interface for the Marketplace app.
It includes visual enhancements for Order tracking, Group Buy progress bars,
and streamlined product management.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Crop, InputProduct, Order,
    GroupBuy, GroupMember, Category
)


# --- 1. CATEGORY MANAGEMENT ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin View for managing Product Categories.
    """
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}


# --- 2. CROP MANAGEMENT (Farmer Produce) ---
@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    """
    Admin View for Farmers' Crops.
    Allows quick editing of categories and names directly from the list view.
    """
    list_display = ('id', 'name', 'farmer', 'category', 'price_per_kg', 'created_at')

    # Enable inline editing for efficient data cleanup
    list_editable = ('category', 'name')
    list_filter = ('category', 'is_active')

    def get_name(self, obj):
        """Fallback display if a crop has no name."""
        if obj.name:
            return obj.name
        return "⚠️ UNNAMED (Needs Edit)"

    get_name.short_description = "Product Name"


# --- 3. ORDER MANAGEMENT (Logistics & Payments) ---
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin View for Order Lifecycle.
    Includes visual color-coding for status and verification checks.
    """
    list_display = (
        'id', 'status_colored', 'product_name',
        'total_price', 'buyer_info', 'payment_status', 'created_at'
    )
    list_filter = ('status', 'payment_method', 'is_payment_verified')
    search_fields = ('id', 'product_name', 'buyer__phone_number')
    readonly_fields = ('created_at',)

    fieldsets = (
        ("Order Status", {
            "fields": ("status", "driver", "is_payment_verified")
        }),
        ("Details", {
            "fields": ("product_name", "quantity", "total_price", "buyer", "seller")
        }),
        ("Logistics", {
            "fields": ("pickup_location", "pickup_phone", "delivery_location", "delivery_phone")
        }),
    )

    def status_colored(self, obj):
        """
        Renders a color-coded badge for the order status.
        """
        colors = {
            'pending': '#f39c12',  # Orange
            'payment_review': '#8e44ad',  # Purple
            'assigned': '#3498db',  # Blue
            'picked_up': '#e67e22',  # Dark Orange
            'delivered': '#2ecc71',  # Green
        }
        color = colors.get(obj.status, '#95a5a6')  # Default Grey

        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; '
            'border-radius: 50px; font-weight: bold; font-size: 11px;">{}</span>',
            color, obj.get_status_display().upper()
        )

    status_colored.short_description = "Order Status"

    def payment_status(self, obj):
        """Renders a checkmark or cross based on verification."""
        if obj.is_payment_verified:
            return format_html('<span style="color: #2ecc71; font-weight: bold;">✔ Verified</span>')
        return format_html('<span style="color: #e74c3c;">✘ Not Verified</span>')

    def buyer_info(self, obj):
        return f"{obj.buyer.first_name} ({obj.buyer.phone_number})"


# --- 4. GROUP BUY MANAGEMENT ---
@admin.register(GroupBuy)
class GroupBuyAdmin(admin.ModelAdmin):
    """
    Admin View for Group Buying.
    Features a visual progress bar indicating how close the group is to the target.
    """
    list_display = ('title', 'visual_progress', 'target_quantity', 'status', 'deadline')
    list_filter = ('status', 'group_type')

    def visual_progress(self, obj):
        """
        Generates an HTML progress bar based on the percentage filled.
        """
        percent = obj.progress_percent()

        # Determine color based on progress
        color = "#e74c3c"  # Red (Low)
        if percent > 50:
            color = "#f39c12"  # Orange (Medium)
        if percent >= 100:
            color = "#2ecc71"  # Green (Done)

        return format_html(
            '''
            <div style="width: 100%; background-color: #ecf0f1; border-radius: 5px; height: 10px; margin-top:5px;">
                <div style="width: {}%; background-color: {}; height: 10px; border-radius: 5px;"></div>
            </div>
            <div style="font-size: 10px; margin-top: 2px;">{}% Filled</div>
            ''',
            min(percent, 100),
            color,
            percent
        )

    visual_progress.short_description = "Group Progress"


# --- 5. SIMPLE REGISTRATIONS ---
admin.site.register(InputProduct)
admin.site.register(GroupMember)