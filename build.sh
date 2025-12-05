#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "--- STARTING BUILD ---"

# 1. Setup Static Folders
mkdir -p static

# 2. Install Packages
pip install -r requirements.txt

# 3. Build Tailwind
python -m pip install django-tailwind
python manage.py tailwind install
python manage.py tailwind build

# 4. Collect Static Files
rm -rf staticfiles
echo "--- COPYING STATIC FILES ---"
python manage.py collectstatic --no-input --clear --verbosity 1

# 5. Database Migrations (MUST BE DONE BEFORE CREATING USER)
python manage.py migrate

# 6. Create Admin User (The New Step)
echo "--- CREATING ADMIN USER ---"
python create_superuser.py

echo "--- BUILD FINISHED ---"