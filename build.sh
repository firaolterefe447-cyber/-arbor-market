#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "--- STARTING BUILD SCRIPT ---"

# 1. Force Create the Static folder
# This ensures settings.py doesn't crash
mkdir -p static

# 2. Install Python packages
pip install -r requirements.txt

# 3. Build Tailwind
python -m pip install django-tailwind
python manage.py tailwind install
python manage.py tailwind build

# 4. Clean and Collect
# We remove the destination folder to force a fresh copy
echo "--- REMOVING OLD STATICFILES FOLDER ---"
rm -rf staticfiles

echo "--- COLLECTING STATIC FILES (VERBOSE) ---"
# --verbosity 2 will list every file copied in the logs
python manage.py collectstatic --no-input --clear --verbosity 2

# 5. Database
python manage.py migrate

echo "--- BUILD FINISHED ---"