#!/usr/bin/env python
"""
Script to create a superuser quickly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_api.settings')
django.setup()

from accounts.models import User

# Create superuser
email = "admin@portfolio.com"
password = "admin123"
first_name = "Admin"
last_name = "User"

if User.objects.filter(email=email).exists():
    print(f"User with email {email} already exists!")
    user = User.objects.get(email=email)
    print(f"User ID: {user.id}")
    print(f"Email: {user.email}")
    print(f"Is Superuser: {user.is_superuser}")
else:
    user = User.objects.create_superuser(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    print("Superuser created successfully!")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"User ID: {user.id}")
