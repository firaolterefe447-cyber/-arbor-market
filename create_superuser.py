import os
import django

# 1. Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# --- YOUR CREDENTIALS ---
ADMIN_PHONE = '0952687749'
ADMIN_PASSWORD = '7744'
# Email is often required by Django internally, even if you log in with phone
ADMIN_EMAIL = 'admin@arbormarket.com'

# 2. Create the Admin
# We look for the phone number, not a username
if not User.objects.filter(phone_number=ADMIN_PHONE).exists():
    print(f"Creating superuser for phone: {ADMIN_PHONE}...")

    # We create the user using phone_number as the unique ID
    User.objects.create_superuser(
        phone_number=ADMIN_PHONE,
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD
    )
    print("Superuser created successfully!")
else:
    print(f"Superuser {ADMIN_PHONE} already exists. Skipping creation.")