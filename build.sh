#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install Python packages
pip install -r requirements.txt

# 2. Install Node.js & Build Tailwind CSS
# (We removed --no-input from these two lines)
python -m pip install django-tailwind
python manage.py tailwind install
python manage.py tailwind build

# 3. Collect all static files (images/css)
# (Keep --no-input here, it is correct for this one)
python manage.py collectstatic --no-input

# 4. Set up the database
python manage.py migrate