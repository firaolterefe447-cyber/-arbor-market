"""
Core URL Configuration for Arbor Marketplace.

This module routes user requests to the appropriate view functions.
Organized by: Expert Backend Engineer
"""

import os
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# --- VIEW IMPORTS ---
# Importing views explicitly for clarity and standard explicit-is-better-than-implicit practice.

from users.views import (
    # Auth & Profile
    login_view, logout_view, select_role, profile_view,
    # Registration
    register_farmer, register_supplier, register_delivery, register_buyer,
    delivery_pending
)

from marketplace.views import (
    # Core
    home,
    # Dashboards
    farmer_dashboard, supplier_dashboard, delivery_dashboard,
    # Products (Crops & Inputs)
    add_crop, edit_crop, delete_crop, product_detail,
    add_input, input_market, farmer_storefront,
    # Orders & Checkout
    checkout, my_orders, order_detail, edit_order, cancel_order, update_status,
    # Payments
    telebirr_pay, bank_transfer, approve_payment,
    # Social / Groups
    toggle_follow, liked_farmers,
    group_buy_market, create_group, join_group, my_groups, remove_member, place_group_order,
    # Logistics
    post_trip, accept_job, verify_delivery
)

# --- ADMIN PANEL CUSTOMIZATION ---
admin.site.site_header = "My Super Dashboard"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome Boss"

# --- URL CONFIGURATION ---

# 1. Technical & Admin Routes (Not Translated)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('__reload__/', include('django_browser_reload.urls')),
]

# 2. Translated User-Facing Routes
urlpatterns += i18n_patterns(
    # --- Public & Authentication ---
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('join/', select_role, name='select_role'),

    # --- Registration ---
    path('register/farmer/', register_farmer, name='register'),
    path('register/buyer/', register_buyer, name='register_buyer'),
    path('register/supplier/', register_supplier, name='register_supplier'),
    path('register/delivery/', register_delivery, name='register_delivery'),
    path('join/delivery/pending/', delivery_pending, name='delivery_pending'),

    # --- Shop & Farmers ---
    # Generic generic product view
    path('product/<int:crop_id>/', product_detail, name='product_detail_simple'),
    # Specific item type view
    path('product/<str:item_type>/<int:item_id>/', product_detail, name='product_detail'),
    path('shop/farmer/<int:farmer_id>/', farmer_storefront, name='farmer_storefront'),
    path('farmer/follow/<int:farmer_id>/', toggle_follow, name='toggle_follow'),
    path('my-farmers/', liked_farmers, name='liked_farmers'),

    # --- Dashboards ---
    path('dashboard/', farmer_dashboard, name='dashboard'),
    path('dashboard/farmer/', farmer_dashboard, name='farmer_dashboard'),
    path('dashboard/supplier/', supplier_dashboard, name='supplier_dashboard'),
    path('dashboard/delivery/', delivery_dashboard, name='delivery_dashboard'),
    path('profile/', profile_view, name='profile'),

    # --- Marketplace Actions (Inventory) ---
    path('add-crop/', add_crop, name='create_crop_listing'),
    path('crop/edit/<int:crop_id>/', edit_crop, name='edit_crop'),
    path('crop/delete/<int:crop_id>/', delete_crop, name='delete_crop'),
    path('add-input/', add_input, name='add_input'),
    path('market/inputs/', input_market, name='input_market'),

    # --- Orders & Checkout ---
    path('buy/<str:item_type>/<int:item_id>/', checkout, name='create_order'),
    path('orders/', my_orders, name='my_orders'),
    path('order/track/<int:order_id>/', order_detail, name='order_detail'),
    path('order/edit/<int:order_id>/', edit_order, name='edit_order'),
    path('order/cancel/<int:order_id>/', cancel_order, name='cancel_order'),
    path('order/<int:order_id>/status/<str:new_status>/', update_status, name='update_status'),

    # --- Payments ---
    path('pay/bank/<int:order_id>/', bank_transfer, name='bank_transfer'),
    path('pay/telebirr/<int:order_id>/', telebirr_pay, name='telebirr_pay'),
    path('approve-payment/<int:order_id>/', approve_payment, name='approve_payment'),

    # --- Group Buying ---
    path('groups/', group_buy_market, name='group_buy_market'),
    path('group/create/<str:item_type>/<int:item_id>/', create_group, name='create_group'),
    path('groups/join/<int:group_id>/', join_group, name='join_group'),
    path('my-groups/', my_groups, name='my_groups'),
    path('my-groups/remove/<int:member_id>/', remove_member, name='remove_member'),
    path('my-groups/place-order/<int:group_id>/', place_group_order, name='place_group_order'),

    # --- Logistics & Delivery ---
    path('logistics/post-trip/', post_trip, name='post_trip'),
    path('logistics/accept/<int:order_id>/', accept_job, name='accept_job'),
    path('logistics/verify/<int:order_id>/', verify_delivery, name='verify_delivery'),

    # Configuration: Do not require language prefix for the default language
    prefix_default_language=False,
)

# --- STATIC & MEDIA SERVING (Development Only) ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)