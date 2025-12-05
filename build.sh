#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install Python packages
pip install -r requirements.txt

# 2. Create the missing static folder (Crucial Fix)
# This prevents Django from complaining if the folder is missing from Git
mkdir -p static
mkdir -p staticfiles

# 3. Install Node.js & Build Tailwind CSS
python -m pip install django-tailwind
python manage.py tailwind install
python manage.py tailwind build

# 4. NUCLEAR RESET of Static Files
# We delete the destination folder completely to force a fresh copy
rm -rf staticfiles
mkdir staticfiles

# 5. Collect static files
# We use --no-input to prevent prompts
# We use --clear to be double safe
python manage.py collectstatic --no-input --clear

# 6. Set up the database
python manage.py migrate