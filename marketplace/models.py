"""
Marketplace Models Configuration.

This module defines the database structure for the application, including:
- Products (Crops, Inputs)
- Transactions (Orders, Group Buys)
- Logistics (Driver Trips, Dispatch Logic)

Refactored for PEP 8 compliance and structural integrity.
"""

import random
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


# --- 1. CATEGORIES ---

class Category(models.Model):
    """
    Categorization for Crops (e.g., Root Vegetables, Fruits).
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(
        max_length=50,
        unique=True,
        help_text="Unique ID for the URL (e.g., 'root-vegetables')"
    )
    icon = models.CharField(
        max_length=10,
        default="🌱",
        help_text="Paste an emoji here"
    )

    class Meta:
        verbose_name = "📂 Category"
        verbose_name_plural = "📂 Categories"

    def __str__(self):
        return self.name


# --- 2. PRODUCT LISTINGS ---

class Crop(models.Model):
    """
    Produce listed by Farmers.
    """
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='crops'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='crops'
    )
    name = models.CharField(
        verbose_name=_("Product Name"),
        max_length=100,
        blank=True,
        null=True
    )
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(help_text="Quantity in KG")
    location = models.CharField(
        max_length=100,
        default="Farm Location",
        help_text="e.g. Sebeta"
    )
    image = models.ImageField(upload_to='crop_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "🌾 Crop"
        verbose_name_plural = "🌾 Crops"

    def __str__(self):
        display_name = self.name if self.name else "Unnamed Crop"
        return f"{display_name} - {self.farmer.phone_number}"


class InputProduct(models.Model):
    """
    Agricultural inputs (fertilizers, seeds) listed by Suppliers.
    """
    supplier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inputs'
    )
    name = models.CharField(max_length=100)  # e.g. DAP Fertilizer
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(help_text="Quantity in Bags/Packs")
    image = models.ImageField(upload_to='input_images/', blank=True, null=True)
    visible_to_farmers_only = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "🚜 Input Product"
        verbose_name_plural = "🚜 Input Products"

    def __str__(self):
        return f"{self.name} - {self.supplier.business_name}"


# --- 3. LOGISTICS ---

class DriverTrip(models.Model):
    """
    CDN Drivers post this to indicate availability: 'I am going to Arba Minch tomorrow'.
    """
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_city = models.CharField(max_length=100)
    destination_city = models.CharField(max_length=100)
    available_capacity_kg = models.IntegerField()
    departure_date = models.DateTimeField()

    class Meta:
        verbose_name = "🚚 Driver Trip"
        verbose_name_plural = "🚚 Driver Trips"

    def __str__(self):
        return f"{self.driver.first_name}: {self.start_city} -> {self.destination_city}"


# --- 4. ORDER MANAGEMENT ---

class Order(models.Model):
    """
    Central transaction model handling purchases, payments, and logistics logic.
    """

    # --- Choices ---
    STATUS_CHOICES = (
        ('payment_review', 'Payment Verification Needed'),
        ('pending', 'Pending Delivery'),
        ('assigned', 'Driver Assigned'),
        ('picked_up', 'Picked Up'),
        ('delivered', 'Delivered'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash on Delivery'),
        ('telebirr', 'Telebirr'),
        ('bank', 'Mobile Banking'),
    )

    DISPATCH_METHODS = (
        ('PENDING', 'Calculating...'),
        ('DEDICATED', 'Dedicated Fleet (Urban)'),
        ('CDN', 'Crowd-Delivery Network (Bulk/Long-Haul)'),
    )

    # --- Core Relationships ---
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders_bought'
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders_sold'
    )

    # --- Product Details ---
    product_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    product_image = models.ImageField(upload_to='order_snapshots/', blank=True, null=True)

    # --- Logistics Data ---
    pickup_location = models.CharField(max_length=200)
    pickup_phone = models.CharField(max_length=20)
    delivery_location = models.CharField(max_length=200)
    delivery_phone = models.CharField(max_length=20)

    # Driver Assignment
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries'
    )
    driver_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name of the person delivering")
    driver_phone = models.CharField(max_length=20, blank=True, null=True, help_text="Phone of the driver")

    # --- Financials ---
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    is_payment_verified = models.BooleanField(default=False)

    commission_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="5% Platform Fee")
    seller_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                          help_text="Amount the seller actually gets")

    # --- Status & Tracking ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    # Tracking Codes
    delivery_pin = models.CharField(max_length=4, blank=True, null=True)
    pod_code = models.CharField(max_length=10, blank=True, null=True, help_text="Proof of Delivery Code")

    # --- Logistics Algorithm Data ---
    weight_kg = models.IntegerField(default=10, help_text="Total weight used for logic")
    distance_km = models.IntegerField(default=5, help_text="Distance used for logic")
    dispatch_method = models.CharField(max_length=20, choices=DISPATCH_METHODS, default='PENDING')

    class Meta:
        verbose_name = "📦 Order"
        verbose_name_plural = "📦 Orders"

    def __str__(self):
        return f"Order #{self.id} - {self.status}"

    def save(self, *args, **kwargs):
        """
        Unified Save Method:
        1. Generates PINs and POD Codes.
        2. Runs the Hybrid Logistics Algorithm to determine dispatch method.
        """

        # 1. Generate Proof of Delivery (POD) Code
        if not self.pod_code:
            self.pod_code = str(random.randint(1000, 9999))

        # 2. Generate Delivery PIN (For Buyer verification)
        if not self.delivery_pin:
            self.delivery_pin = str(random.randint(1000, 9999))

        # 3. Hybrid Dispatch Logic Algorithm
        # Constants
        W_MAX = 100  # KG Threshold
        D_MAX = 50  # KM Threshold

        if self.weight_kg > W_MAX or self.distance_km > D_MAX:
            self.dispatch_method = 'CDN'
        else:
            self.dispatch_method = 'DEDICATED'

        super().save(*args, **kwargs)


# --- 5. GROUP BUYING ---

class GroupBuy(models.Model):
    """
    Group Buying logic for aggregating demand to get discounts.
    """
    GROUP_TYPES = (
        ('farmer_coop', 'Farmer Cooperative (Buying Inputs)'),
        ('urban_group', 'Urban Buyers (Buying Crops)'),
    )

    STATUS_CHOICES = (
        ('open', 'Open for Joining'),
        ('confirmed', 'Target Met - Confirmed'),
        ('completed', 'Delivered & Closed'),
        ('expired', 'Failed - Time Expired'),
    )

    initiator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_groups')

    # Targets
    target_crop = models.ForeignKey('Crop', on_delete=models.SET_NULL, null=True, blank=True)
    target_input = models.ForeignKey('InputProduct', on_delete=models.SET_NULL, null=True, blank=True)

    # Details
    title = models.CharField(max_length=200)
    group_type = models.CharField(max_length=20, choices=GROUP_TYPES)
    delivery_location = models.CharField(max_length=200, help_text="Where will members collect their share?")

    # Metrics
    target_quantity = models.IntegerField(help_text="Goal Quantity")
    current_quantity = models.IntegerField(default=0)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit if goal is met")

    deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "🤝 Group Buy"
        verbose_name_plural = "🤝 Group Buys"

    def __str__(self):
        return f"{self.title} ({self.current_quantity}/{self.target_quantity})"

    @property
    def progress_percent(self):
        """Calculates percentage of the target quantity filled."""
        if self.target_quantity > 0:
            percent = (self.current_quantity / self.target_quantity) * 100
            return min(percent, 100)  # Cap at 100%
        return 0


class GroupMember(models.Model):
    """
    Records an individual user joining a Group Buy.
    """
    group = models.ForeignKey(GroupBuy, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quantity_committed = models.IntegerField()
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} in {self.group.title}"