"""
Marketplace Forms Configuration.

This module handles all form definitions for the marketplace application.
It includes specific Tailwind CSS widget styling to ensure a consistent,
modern UI across the platform.
"""

from django import forms
from .models import (
    Crop,
    InputProduct,
    GroupBuy,
    GroupMember,
    DriverTrip
)


# --- 1. FARMER FORMS ---

class CropForm(forms.ModelForm):
    """
    Form for Farmers to list new produce (Crops).
    """

    class Meta:
        model = Crop
        fields = ['image', 'name', 'price_per_kg', 'stock_quantity', 'location']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-stone-50 border border-stone-200 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition font-bold text-stone-700 placeholder-stone-400',
                'placeholder': 'Product Name (Optional - leave blank if unsure)'
            }),
            'price_per_kg': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-stone-50 border border-stone-200 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition font-bold text-stone-700',
                'placeholder': '0.00'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-stone-50 border border-stone-200 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition font-bold text-stone-700',
                'placeholder': '100'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-stone-50 border border-stone-200 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition font-bold text-stone-700',
                'placeholder': 'e.g. Sebeta, Farm #4'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full text-sm text-stone-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-bold file:bg-green-100 file:text-green-700 hover:file:bg-green-200',
            }),
        }


# --- 2. SUPPLIER FORMS ---

class InputProductForm(forms.ModelForm):
    """
    Form for Suppliers to add agricultural inputs (Fertilizers, Seeds, etc).
    """

    class Meta:
        model = InputProduct
        fields = ['name', 'price_per_unit', 'stock_quantity', 'image']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500',
                'placeholder': 'e.g. DAP Fertilizer 50kg'
            }),
            'price_per_unit': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500',
                'placeholder': 'Price per Bag'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500',
                'placeholder': 'How many bags?'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 bg-gray-50'
            }),
        }


# --- 3. GROUP BUY FORMS ---

class CreateGroupBuyForm(forms.ModelForm):
    """
    Form to initiate a new Group Buy deal.
    """

    class Meta:
        model = GroupBuy
        fields = ['title', 'delivery_location', 'target_quantity', 'discount_price', 'deadline']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full p-3 border rounded-xl',
                'placeholder': 'e.g. Bulk Onion Purchase'
            }),
            'delivery_location': forms.TextInput(attrs={
                'class': 'w-full p-3 border rounded-xl',
                'placeholder': 'Specific Address (e.g. Bole Atlas, Building B)'
            }),
            'target_quantity': forms.NumberInput(attrs={
                'class': 'w-full p-3 border rounded-xl'
            }),
            'discount_price': forms.NumberInput(attrs={
                'class': 'w-full p-3 border rounded-xl'
            }),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'w-full p-3 border rounded-xl',
                'type': 'datetime-local'
            }),
        }


class JoinGroupForm(forms.ModelForm):
    """
    Form for a buyer to pledge a quantity to a Group Buy.
    """

    class Meta:
        model = GroupMember
        fields = ['quantity_committed']

        widgets = {
            'quantity_committed': forms.NumberInput(attrs={
                'class': 'w-full p-3 border rounded-xl',
                'placeholder': 'How much do you want?'
            }),
        }


# --- 4. LOGISTICS FORMS ---

class DriverTripForm(forms.ModelForm):
    """
    Form for Drivers to post available cargo capacity.
    """

    class Meta:
        model = DriverTrip
        fields = ['start_city', 'destination_city', 'available_capacity_kg', 'departure_date']

        widgets = {
            'start_city': forms.TextInput(attrs={
                'class': 'w-full p-3 border rounded-xl',
                'placeholder': 'Origin (e.g. Addis Ababa)'
            }),
            'destination_city': forms.TextInput(attrs={
                'class': 'w-full p-3 border rounded-xl',
                'placeholder': 'Destination (e.g. Adama)'
            }),
            'available_capacity_kg': forms.NumberInput(attrs={
                'class': 'w-full p-3 border rounded-xl',
                'placeholder': 'Max Capacity (KG)'
            }),
            'departure_date': forms.DateTimeInput(attrs={
                'class': 'w-full p-3 border rounded-xl',
                'type': 'datetime-local'
            }),
        }