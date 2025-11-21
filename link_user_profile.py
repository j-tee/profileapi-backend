#!/usr/bin/env python
"""
Script to link User accounts with Profile or create Profile for User
This resolves the issue where superuser has no associated profile
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_api.settings')
django.setup()

from accounts.models import User
from profiles.models import Profile


def link_or_create_profile():
    """Link superuser to profile or create new profile"""
    
    print("\n" + "="*60)
    print("User-Profile Linking Tool")
    print("="*60 + "\n")
    
    # Get all users without a profile
    users = User.objects.all()
    
    print(f"Found {users.count()} user(s):\n")
    for user in users:
        print(f"User: {user.email}")
        print(f"  - UUID: {user.id}")
        print(f"  - Name: {user.full_name}")
        print(f"  - Role: {user.role}")
        
        # Check if profile exists with same email
        try:
            profile = Profile.objects.get(email=user.email)
            print(f"  ✅ Profile found: {profile.id}")
            print(f"     Name: {profile.full_name}")
            print(f"     Headline: {profile.headline}")
        except Profile.DoesNotExist:
            print(f"  ❌ No profile found for this email")
            print(f"     Creating profile...")
            
            # Create profile for this user
            profile = Profile.objects.create(
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                headline=f"{user.full_name}'s Portfolio",
                summary=f"Professional portfolio of {user.full_name}",
                city="Accra",
                state="Greater Accra",
                country="Ghana"
            )
            print(f"  ✅ Profile created: {profile.id}")
            print(f"     Name: {profile.full_name}")
        
        print()
    
    print("\n" + "="*60)
    print("Profile Summary")
    print("="*60 + "\n")
    
    profiles = Profile.objects.all()
    for profile in profiles:
        print(f"Profile: {profile.full_name}")
        print(f"  - UUID: {profile.id}")
        print(f"  - Email: {profile.email}")
        print(f"  - Headline: {profile.headline}")
        
        # Find matching user
        try:
            user = User.objects.get(email=profile.email)
            print(f"  ✅ Linked to user: {user.email} (Role: {user.role})")
        except User.DoesNotExist:
            print(f"  ⚠️  No user account with this email")
        
        print()
    
    print("="*60)
    print("✅ Done! User-Profile linking complete.")
    print("="*60 + "\n")
    
    # Display the profile UUID for frontend use
    if profiles.exists():
        main_profile = profiles.first()
        print("\n🎯 IMPORTANT - Use this Profile UUID in your frontend:")
        print(f"\nconst PORTFOLIO_OWNER_PROFILE_ID = '{main_profile.id}';")
        print(f"const PORTFOLIO_OWNER_EMAIL = '{main_profile.email}';\n")


if __name__ == '__main__':
    try:
        link_or_create_profile()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
