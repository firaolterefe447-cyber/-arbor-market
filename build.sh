#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "--- STARTING BUILD SCRIPT ---"

# 1. Install Python packages
pip install -r requirements.txt

# 2. Build Tailwind
# Ensure the theme app is installed and compiled
python -m pip install django-tailwind
python manage.py tailwind install
python manage.py tailwind build

echo "--- CLEARING OLD STATIC FILES ---"
# Force delete the folder to ensure collectstatic cannot skip files
rm -rf staticfiles
rm -rf static

# Create the folder structure fresh
mkdir -p static
mkdir -p staticfiles

echo "--- COLLECTING STATIC FILES ---"
# --no-input: Do not ask for confirmation
# --clear: Delete the destination before copying (Double check)
# --verbosity 2: Show us exactly what files are being copied
python manage.py collectstatic --no-input --clear --verbosity 2

echo "--- MIGRATING DATABASE ---"
python manage.py migrate

echo "--- BUILD FINISHED ---"