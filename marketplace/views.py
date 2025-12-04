"""
Marketplace View Definitions.

This module handles the core logic for the Arbor Marketplace, including:
- Dashboard rendering for different user types.
- Product listings, searching, and management.
- Order processing, checkout, and payments.
- Logistics management (Drivers & CDN).
- Group buying mechanics.
"""

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

# Local App Imports
from users.models import CustomUser, FarmerFollow
from .models import (
    Crop, InputProduct, Order, GroupBuy,
    GroupMember, Category, DriverTrip
)
from .forms import (
    CropForm, InputProductForm, CreateGroupBuyForm,
    JoinGroupForm, DriverTripForm
)


# ==========================================
# 1. CORE & DASHBOARDS
# ==========================================

def home(request):
    """
    Landing page with search, filtering, and active crop listings.
    """
    query = request.GET.get('q')
    category_filter = request.GET.get('category')

    # Fetch Categories
    try:
        categories = Category.objects.exclude(slug='uncategorized').order_by('name')
    except Exception:
        categories = Category.objects.all().order_by('name')

    # Base Query
    recent_crops = Crop.objects.filter(is_active=True)

    # Search Logic
    if query:
        recent_crops = recent_crops.filter(
            Q(name__icontains=query) |
            Q(farmer__location__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Category Filter
    if category_filter:
        recent_crops = recent_crops.filter(category__slug=category_filter)

    recent_crops = recent_crops.order_by('-created_at')

    context = {
        'recent_crops': recent_crops,
        'query': query,
        'current_category': category_filter,
        'categories': categories,
    }
    return render(request, 'home.html', context)


@login_required
def farmer_dashboard(request):
    if request.user.user_type != 'farmer':
        return redirect('home')

    my_crops = Crop.objects.filter(farmer=request.user).order_by('-created_at')
    market_crops = Crop.objects.exclude(farmer=request.user).filter(is_active=True).order_by('-created_at')

    # Find bank payments waiting for approval
    pending_payments = Order.objects.filter(
        seller=request.user,
        payment_method='bank',
        is_payment_verified=False
    ).exclude(payment_proof='')

    context = {
        'my_crops': my_crops,
        'market_crops': market_crops,
        'pending_payments': pending_payments,
    }
    return render(request, 'dashboard.html', context)


@login_required
def supplier_dashboard(request):
    if request.user.user_type != 'supplier':
        return redirect('home')

    my_inputs = InputProduct.objects.filter(supplier=request.user)
    market_crops = Crop.objects.filter(is_active=True)

    context = {
        'my_inputs': my_inputs,
        'market_crops': market_crops,
    }
    return render(request, 'supplier_dashboard.html', context)


@login_required
def buyer_dashboard(request):
    crops = Crop.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'buyer_dashboard.html', {'crops': crops})


@login_required
def delivery_dashboard(request):
    """
    Dashboard for Logistics Personnel (Dedicated Fleet & CDN).
    """
    if not hasattr(request.user, 'driver_profile'):
        return redirect('home')

    profile = request.user.driver_profile
    context = {
        'profile': profile,
        'mode': profile.workforce_type,
    }

    if profile.workforce_type == 'DEDICATED':
        # Dedicated Logic: Show assigned manifest
        manifest = Order.objects.filter(
            driver=request.user,
            status__in=['assigned', 'picked_up']
        ).order_by('id')
        context['manifest'] = manifest

    else:
        # CDN Logic: Global View
        my_jobs = Order.objects.filter(driver=request.user).exclude(
            status='delivered'
        ).exclude(status='cancelled').order_by('-created_at')

        my_trips = DriverTrip.objects.filter(driver=request.user)

        # Global Feed: All active orders
        all_orders = Order.objects.exclude(status='cancelled').order_by('-created_at')

        context['all_orders'] = all_orders
        context['job_offers'] = all_orders  # Fallback for legacy templates
        context['my_jobs'] = my_jobs
        context['my_trips'] = my_trips

    return render(request, 'delivery_dashboard.html', context)


# ==========================================
# 2. PRODUCT MANAGEMENT (CRUD)
# ==========================================

@login_required
def add_crop(request):
    if request.method == 'POST':
        form = CropForm(request.POST, request.FILES)
        if form.is_valid():
            crop = form.save(commit=False)
            crop.farmer = request.user
            crop.save()
            return redirect('dashboard')
    else:
        form = CropForm()
    return render(request, 'add_crop.html', {'form': form})


@login_required
def edit_crop(request, crop_id):
    crop = get_object_or_404(Crop, id=crop_id, farmer=request.user)
    if request.method == 'POST':
        form = CropForm(request.POST, request.FILES, instance=crop)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Product updated successfully!")
            return redirect('dashboard')
    else:
        form = CropForm(instance=crop)
    return render(request, 'edit_crop.html', {'form': form, 'crop': crop})


@login_required
def delete_crop(request, crop_id):
    crop = get_object_or_404(Crop, id=crop_id, farmer=request.user)
    if request.method == 'POST':
        crop.delete()
        messages.success(request, "🗑️ Product deleted.")
    return redirect('dashboard')


@login_required
def add_input(request):
    if request.user.user_type != 'supplier':
        return redirect('home')

    if request.method == 'POST':
        form = InputProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.supplier = request.user
            product.save()
            return redirect('supplier_dashboard')
    else:
        form = InputProductForm()
    return render(request, 'add_input.html', {'form': form})


@login_required
def input_market(request):
    inputs = InputProduct.objects.filter(stock_quantity__gt=0).order_by('-created_at')
    return render(request, 'input_market.html', {'inputs': inputs})


@login_required
def product_detail(request, item_type, item_id):
    related_items = []

    if item_type == 'crop':
        item = get_object_or_404(Crop, id=item_id)
        seller = item.farmer

        # Recommendations Logic
        seller_other_items = Crop.objects.filter(farmer=seller, is_active=True).exclude(id=item.id)[:4]
        same_name_items = Crop.objects.filter(name__icontains=item.name, is_active=True).exclude(id=item.id)

        first_letter = item.name[0] if item.name else ''
        same_letter_items = Crop.objects.filter(name__istartswith=first_letter, is_active=True).exclude(
            id=item.id).exclude(id__in=same_name_items)

        related_items = list(same_name_items) + list(same_letter_items)

    elif item_type == 'input':
        item = get_object_or_404(InputProduct, id=item_id)
        seller = item.supplier

        seller_other_items = InputProduct.objects.filter(supplier=seller).exclude(id=item.id)[:4]
        same_name_items = InputProduct.objects.filter(name__icontains=item.name).exclude(id=item.id)

        first_letter = item.name[0] if item.name else ''
        same_letter_items = InputProduct.objects.filter(name__istartswith=first_letter).exclude(
            id=item.id).exclude(id__in=same_name_items)

        related_items = list(same_name_items) + list(same_letter_items)

    context = {
        'item': item,
        'item_type': item_type,
        'seller': seller,
        'seller_other_items': seller_other_items,
        'related_items': related_items[:10],
    }
    return render(request, 'product_detail.html', context)


def farmer_storefront(request, farmer_id):
    farmer = get_object_or_404(CustomUser, id=farmer_id)
    crops = Crop.objects.filter(farmer=farmer, is_active=True).order_by('-created_at')
    context = {
        'farmer': farmer,
        'crops': crops
    }
    return render(request, 'farmer_storefront.html', context)


# ==========================================
# 3. ORDERS & CHECKOUT
# ==========================================

@login_required
def checkout(request, item_type, item_id):
    # Determine Item Type
    if item_type == 'crop':
        item = get_object_or_404(Crop, id=item_id)
        seller = item.farmer
        price = item.price_per_kg
        product_name = item.name
        unit = "kg"
        location = item.farmer.location
        phone = item.farmer.phone_number
    elif item_type == 'input':
        item = get_object_or_404(InputProduct, id=item_id)
        seller = item.supplier
        price = item.price_per_unit
        product_name = item.name
        unit = "units"
        location = item.supplier.location
        phone = item.supplier.phone_number

    if request.method == 'POST':
        qty = int(request.POST.get('quantity', 1))
        pay_method = request.POST.get('payment_method')

        if qty > item.stock_quantity:
            messages.error(request, "Not enough stock!")
            return redirect(request.path)

        # Financial Calculations
        total_amount = price * qty
        commission = total_amount * Decimal('0.05')
        earnings = total_amount - commission

        # Create Order
        order = Order.objects.create(
            buyer=request.user,
            seller=seller,
            product_name=product_name,
            quantity=qty,
            total_price=total_amount,
            commission_fee=commission,
            seller_earnings=earnings,
            pickup_location=location,
            pickup_phone=phone,
            delivery_location=request.user.location,
            delivery_phone=request.user.phone_number,
            payment_method=pay_method,
            status='pending',
            is_payment_verified=False
        )

        # Update Stock
        item.stock_quantity -= qty
        item.save()

        # Routing based on payment method
        if pay_method == 'telebirr':
            messages.info(request, "Redirecting to Telebirr...")
            return redirect('telebirr_pay', order_id=order.id)

        elif pay_method == 'bank':
            return redirect('bank_transfer', order_id=order.id)

        else:
            messages.success(request, "Order placed! Prepare cash for delivery.")
            return redirect('my_orders')

    context = {
        'item': item, 'type': item_type, 'price': price, 'unit': unit,
        'buyer_location': request.user.location, 'buyer_phone': request.user.phone_number
    }
    return render(request, 'checkout.html', context)


@login_required
def my_orders(request):
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Permission Check
    allowed_users = ['delivery', order.buyer.user_type, order.seller.user_type]
    if request.user.user_type == 'delivery' or request.user == order.buyer or request.user == order.seller:
        pass
    else:
        return redirect('home')

    # Driver Self-Assignment Logic
    if request.method == 'POST' and request.user.user_type == 'delivery':
        driver_name = request.POST.get('driver_name')
        driver_phone = request.POST.get('driver_phone')

        if driver_name:
            order.driver_name = driver_name
            order.driver_phone = driver_phone
            order.status = 'assigned'
            order.save()
            messages.success(request, f"Driver {driver_name} assigned successfully!")
            return redirect('order_detail', order_id=order.id)

    return render(request, 'order_detail.html', {'order': order})


@login_required
def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)

    if order.status != 'pending':
        messages.error(request, "⚠️ Cannot edit order! A driver has already been assigned.")
        return redirect('my_orders')

    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity'))

        if new_quantity < 1:
            messages.error(request, "Quantity must be at least 1.")
        else:
            # Recalculate Logic
            unit_price = order.total_price / order.quantity
            order.quantity = new_quantity
            order.total_price = unit_price * new_quantity
            order.commission_fee = order.total_price * Decimal('0.05')
            order.seller_earnings = order.total_price - order.commission_fee
            order.save()

            messages.success(request, "✅ Order updated successfully!")
            return redirect('my_orders')

    return render(request, 'edit_order.html', {'order': order})


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)

    if order.status != 'pending':
        messages.error(request, "⚠️ Cannot cancel order! It is already being processed.")
    else:
        order.delete()
        messages.success(request, "🗑️ Order cancelled successfully.")

    return redirect('my_orders')


# ==========================================
# 4. PAYMENTS
# ==========================================

@login_required
def bank_transfer(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        if 'payment_proof' in request.FILES:
            order.payment_proof = request.FILES['payment_proof']
            order.status = 'payment_review'
            order.save()
            messages.info(request, "⏳ Receipt uploaded. Waiting for approval.")
            return redirect('my_orders')

    return render(request, 'bank_transfer.html', {'order': order})


@login_required
def approve_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, seller=request.user)
    order.is_payment_verified = True
    order.status = 'pending'
    order.save()
    messages.success(request, f"Payment approved for Order #{order.id}. Delivery team notified.")
    return redirect('dashboard')


@login_required
def telebirr_pay(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id, buyer=request.user)
    except Exception:
        return redirect('my_orders')

    if request.method == 'POST':
        # Simulate Success
        order.is_payment_verified = True
        order.save()
        return redirect('my_orders')

    return render(request, 'telebirr_pay.html', {'order': order})


# ==========================================
# 5. LOGISTICS & DELIVERY
# ==========================================

@login_required
def post_trip(request):
    if request.method == 'POST':
        form = DriverTripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.driver = request.user
            trip.save()
            messages.success(request, "✅ Trip Posted! Waiting for matching orders...")
            return redirect('delivery_dashboard')
    else:
        form = DriverTripForm()
    return render(request, 'post_trip.html', {'form': form})


@login_required
def accept_job(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status != 'pending':
        messages.error(request, "This job is already taken!")
        return redirect('delivery_dashboard')

    order.driver = request.user
    order.driver_name = request.user.first_name
    order.driver_phone = request.user.phone_number
    order.status = 'assigned'
    order.save()

    messages.success(request, f"Job Accepted! Pickup at {order.pickup_location}")
    return redirect('delivery_dashboard')


@login_required
def update_status(request, order_id, new_status):
    if request.user.user_type != 'delivery':
        return redirect('home')

    order = get_object_or_404(Order, id=order_id)

    if new_status == 'assigned':
        order.driver = request.user
        order.driver_name = f"{request.user.first_name} {request.user.last_name}"
        order.driver_phone = request.user.phone_number
        order.status = 'assigned'
        order.save()
        messages.success(request, f"Order #{order.id} linked to your profile! 🚚")
    else:
        order.status = new_status
        order.save()

    return redirect('order_detail', order_id=order.id)


@login_required
def verify_delivery(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.driver != request.user:
        messages.error(request, "You are not authorized to process this order.")
        return redirect('delivery_dashboard')

    if request.method == 'POST':
        entered_pin = request.POST.get('pod_code', '').strip()

        if entered_pin == order.delivery_pin:
            order.status = 'delivered'
            order.is_completed = True
            order.save()
            messages.success(request, f"🎉 Success! Order #{order.id} verified and completed.")
            return redirect('delivery_dashboard')
        else:
            messages.error(request, "⛔ INCORRECT PIN! Delivery not approved.")
            return redirect('order_detail', order_id=order.id)

    return redirect('order_detail', order_id=order.id)


# ==========================================
# 6. GROUP BUYING
# ==========================================

@login_required
def group_buy_market(request):
    # Managed Groups
    my_groups = GroupBuy.objects.filter(initiator=request.user).order_by('-created_at')

    # Public Groups
    public_groups = GroupBuy.objects.filter(status='open')

    if request.user.user_type == 'farmer':
        public_groups = public_groups.filter(group_type='farmer_coop')
    elif request.user.user_type == 'buyer':
        public_groups = public_groups.filter(group_type='urban_group')

    public_groups = public_groups.exclude(initiator=request.user).order_by('-created_at')

    context = {
        'my_groups': my_groups,
        'public_groups': public_groups,
    }
    return render(request, 'group_buy_market.html', context)


@login_required
def create_group(request, item_type, item_id):
    target_item = None
    if item_type == 'crop':
        target_item = get_object_or_404(Crop, id=item_id)
    elif item_type == 'input':
        target_item = get_object_or_404(InputProduct, id=item_id)

    if request.method == 'POST':
        form = CreateGroupBuyForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.initiator = request.user

            if item_type == 'crop':
                group.target_crop = target_item
                group.group_type = 'urban_group'
            elif item_type == 'input':
                group.target_input = target_item
                group.group_type = 'farmer_coop'

            group.location = form.cleaned_data.get('delivery_location')
            group.save()

            messages.success(request, f"Group Buy for {target_item.name} launched!")
            return redirect('group_buy_market')
    else:
        form = CreateGroupBuyForm()

    context = {
        'form': form,
        'item_type': item_type,
        'item_id': item_id,
        'target_item': target_item
    }
    return render(request, 'create_group.html', context)


@login_required
def join_group(request, group_id):
    group = get_object_or_404(GroupBuy, id=group_id)

    if group.status != 'open':
        messages.warning(request, f"This group is **{group.status}** and cannot be joined.")
        return redirect('group_buy_market')

    if request.method == 'POST':
        form = JoinGroupForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity_committed']

            group.current_quantity += quantity
            if group.current_quantity >= group.target_quantity:
                group.status = 'confirmed'
                messages.success(request, f"🎉 Group Buy target met! Status is now **Confirmed**.")
            group.save()

            member = form.save(commit=False)
            member.group = group
            member.user = request.user
            member.save()

            messages.success(request, f"Joined group successfully with **{quantity}** units.")
            return redirect('group_buy_market')
    else:
        form = JoinGroupForm()

    return render(request, 'join_group.html', {'group': group, 'form': form})


@login_required
def my_groups(request):
    groups = GroupBuy.objects.filter(initiator=request.user).order_by('-created_at')
    return render(request, 'my_groups.html', {'groups': groups})


@login_required
def remove_member(request, member_id):
    member = get_object_or_404(GroupMember, id=member_id)
    group = member.group

    if request.user != group.initiator:
        return redirect('group_buy_market')

    group.current_quantity -= member.quantity_committed
    group.save()
    member.delete()
    messages.success(request, "Member removed.")

    return redirect('group_buy_market')


@login_required
def place_group_order(request, group_id):
    group = get_object_or_404(GroupBuy, id=group_id)

    if request.user != group.initiator:
        return redirect('group_buy_market')

    if group.current_quantity == 0:
        messages.error(request, "Cannot place empty order!")
        return redirect('group_buy_market')

    # Determine Product & Seller
    if group.target_crop:
        seller = group.target_crop.farmer
        product_name = f"GROUP: {group.target_crop.name}"
        pickup_loc = seller.location
        pickup_phone = seller.phone_number
    elif group.target_input:
        seller = group.target_input.supplier
        product_name = f"CO-OP: {group.target_input.name}"
        pickup_loc = seller.location
        pickup_phone = seller.supplier.phone_number
    else:
        return redirect('group_buy_market')

    # Financial Breakdown
    total_amount = group.current_quantity * group.discount_price
    commission = total_amount * Decimal('0.05')
    earnings = total_amount - commission

    Order.objects.create(
        buyer=request.user,
        seller=seller,
        product_name=product_name,
        quantity=group.current_quantity,
        total_price=total_amount,
        commission_fee=commission,
        seller_earnings=earnings,
        pickup_location=pickup_loc,
        pickup_phone=pickup_phone,
        delivery_location=group.delivery_location,
        delivery_phone=request.user.phone_number,
        status='pending'
    )

    group.status = 'completed'
    group.save()

    messages.success(request, "🎉 Group Order Placed! Sent to Delivery.")
    return redirect('group_buy_market')


# ==========================================
# 7. SOCIAL & FOLLOWS
# ==========================================

@login_required
def toggle_follow(request, farmer_id):
    farmer_to_follow = get_object_or_404(CustomUser, id=farmer_id)

    if request.user == farmer_to_follow:
        messages.warning(request, "You cannot follow yourself!")
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    follow_instance = FarmerFollow.objects.filter(buyer=request.user, farmer=farmer_to_follow)

    if follow_instance.exists():
        follow_instance.delete()
        messages.info(request, f"Unfollowed {farmer_to_follow.first_name}")
    else:
        FarmerFollow.objects.create(buyer=request.user, farmer=farmer_to_follow)
        messages.success(request, f"Added {farmer_to_follow.first_name} to your Liked Farmers!")

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def liked_farmers(request):
    follows = FarmerFollow.objects.filter(buyer=request.user).select_related('farmer')
    return render(request, 'liked_farmers.html', {'follows': follows})