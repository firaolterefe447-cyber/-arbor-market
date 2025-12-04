#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install Python packages
pip install -r requirements.txt

# 2. Install Node.js & Build Tailwind CSS
# This step is CRITICAL for your style to work
python -m pip install django-tailwind
python manage.py tailwind install --no-input
python manage.py tailwind build --no-input

# 3. Collect all static files (images/css)
python manage.py collectstatic --no-input

# 4. Set up the database
python manage.py migrate