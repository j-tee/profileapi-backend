#!/usr/bin/env python
"""
Test super admin login
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_api.settings')
django.setup()

from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken

# Get the super admin user
email = 'juliustetteh@gmail.com'
password = 'pa$$word123'

try:
    user = User.objects.get(email=email)
    
    # Verify password
    if user.check_password(password):
        print(f"✓ Authentication successful!")
        print(f"\nUser Details:")
        print(f"  Email: {user.email}")
        print(f"  Name: {user.full_name}")
        print(f"  Role: {user.role}")
        print(f"  Is Superuser: {user.is_superuser}")
        print(f"  Is Staff: {user.is_staff}")
        print(f"  Is Active: {user.is_active}")
        print(f"  MFA Enabled: {user.mfa_enabled}")
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        print(f"\nJWT Tokens Generated:")
        print(f"  Access Token: {str(refresh.access_token)[:50]}...")
        print(f"  Refresh Token: {str(refresh)[:50]}...")
        
        print(f"\n✓ Super admin account is ready to use!")
        print(f"\nYou can now:")
        print(f"  1. Login at: http://localhost:8000/api/auth/login/")
        print(f"  2. Access admin panel: http://localhost:8000/admin/")
        print(f"  3. API docs: http://localhost:8000/api/docs/")
        
    else:
        print(f"✗ Password verification failed")
        
except User.DoesNotExist:
    print(f"✗ User {email} not found")
