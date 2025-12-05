import os
import django

# 1. Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# 2. Create the Admin User
# Change 'admin123' to the password you want!
username = 'admin'
email = 'admin@example.com'
password = 'admin123'

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser: {username}...")
    User.objects.create_superuser(username, email, password)
    print("Superuser created successfully!")
else:
    print(f"Superuser {username} already exists. Skipping creation.")