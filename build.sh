#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install Python packages
pip install -r requirements.txt

# 2. Install Node.js & Build Tailwind CSS
python -m pip install django-tailwind
python manage.py tailwind install
python manage.py tailwind build

# 3. Collect all static files (images/css)
# Added --clear to ensure we start fresh and get the new tailwind build
python manage.py collectstatic --no-input --clear

# 4. Set up the database
python manage.py migrate