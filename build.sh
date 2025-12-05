#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "--- 1. INSTALLING PYTHON DEPS ---"
pip install -r requirements.txt

echo "--- 2. CREATING STATIC DIRECTORIES ---"
# Ensure the 'static' folder exists so settings.py doesn't complain
mkdir -p static

echo "--- 3. BUILDING TAILWIND ---"
python -m pip install django-tailwind
python manage.py tailwind install
python manage.py tailwind build

echo "--- 4. VERIFYING CSS GENERATION ---"
# This will print the file path if it exists.
# If you see "No such file" in logs, Tailwind failed.
ls -la theme/static/css/dist/styles.css || echo "WARNING: Tailwind CSS file not found!"

echo "--- 5. RESETTING STATICFILES ---"
# Force delete the destination to prevent cache issues
rm -rf staticfiles

echo "--- 6. COLLECTING STATIC FILES ---"
# --no-input: automatic yes
# --clear: wipe destination
# --verbosity 1: keep logs clean but show summary
python manage.py collectstatic --no-input --clear --verbosity 1

echo "--- 7. DATABASE MIGRATION ---"
python manage.py migrate