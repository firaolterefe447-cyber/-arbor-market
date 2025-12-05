#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "--- 1. INSTALLING PYTHON DEPS ---"
pip install -r requirements.txt

echo "--- 2. CREATING STATIC DIRECTORIES ---"
mkdir -p static

echo "--- 3. BUILDING TAILWIND ---"
python -m pip install django-tailwind
python manage.py tailwind install
python manage.py tailwind build

echo "--- 4. VERIFYING CSS GENERATION ---"
ls -la theme/static/css/dist/styles.css || echo "WARNING: Tailwind CSS file not found!"

echo "--- 5. RESETTING STATICFILES ---"
rm -rf staticfiles

echo "--- 6. COLLECTING STATIC FILES ---"
python manage.py collectstatic --no-input --clear --verbosity 1

echo "--- 7. DATABASE MIGRATION ---"
python manage.py migrate

echo "--- 8. CREATING ADMIN USER ---"
# This now runs the fixed script without email
python create_superuser.py

echo "--- BUILD FINISHED ---"