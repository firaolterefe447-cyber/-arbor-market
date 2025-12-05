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

# 2. Create the Admin
if not User.objects.filter(phone_number=ADMIN_PHONE).exists():
    print(f"Creating superuser for phone: {ADMIN_PHONE}...")

    # We pass ONLY phone_number and password.
    # No email, no username.
    User.objects.create_superuser(
        phone_number=ADMIN_PHONE,
        password=ADMIN_PASSWORD
    )
    print("Superuser created successfully!")
else:
    print(f"Superuser {ADMIN_PHONE} already exists. Skipping.")