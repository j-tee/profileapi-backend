#!/usr/bin/env python
"""
User Account Management Script
Provides commands for managing user accounts and roles.
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_api.settings')
django.setup()

from accounts.models import User, UserRole
from django.core.exceptions import ValidationError


def list_users():
    """List all users with their roles and status"""
    users = User.objects.all().order_by('-created_at')
    
    if not users.exists():
        print("No users found.")
        return
    
    print("\n" + "="*100)
    print(f"{'Email':<35} {'Name':<25} {'Role':<15} {'Active':<8} {'Verified':<10} {'MFA':<5}")
    print("="*100)
    
    for user in users:
        print(f"{user.email:<35} {user.full_name:<25} {user.get_role_display():<15} "
              f"{'Yes' if user.is_active else 'No':<8} {'Yes' if user.is_verified else 'No':<10} "
              f"{'Yes' if user.mfa_enabled else 'No':<5}")
    
    print("="*100)
    print(f"\nTotal users: {users.count()}\n")


def create_user():
    """Create a new user account"""
    print("\n--- Create New User ---\n")
    
    email = input("Email: ").strip()
    if not email:
        print("Error: Email is required")
        return
    
    # Check if user exists
    if User.objects.filter(email=email).exists():
        print(f"Error: User with email {email} already exists")
        return
    
    first_name = input("First Name: ").strip()
    last_name = input("Last Name: ").strip()
    password = input("Password: ").strip()
    
    # Choose role
    print("\nSelect Role:")
    print("1. Viewer (Read-only access)")
    print("2. Editor (Can edit content)")
    print("3. Super Admin (Full access)")
    
    role_choice = input("Enter choice (1-3): ").strip()
    role_map = {
        '1': UserRole.VIEWER,
        '2': UserRole.EDITOR,
        '3': UserRole.SUPER_ADMIN
    }
    
    role = role_map.get(role_choice, UserRole.VIEWER)
    
    try:
        if role == UserRole.SUPER_ADMIN:
            user = User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
        else:
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
        
        print(f"\n✓ User created successfully!")
        print(f"  Email: {user.email}")
        print(f"  Name: {user.full_name}")
        print(f"  Role: {user.get_role_display()}")
        print(f"  Verified: {user.is_verified}")
        
    except ValidationError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error creating user: {e}")


def update_user_role():
    """Update a user's role"""
    print("\n--- Update User Role ---\n")
    
    email = input("User Email: ").strip()
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        print(f"Error: User with email {email} not found")
        return
    
    print(f"\nCurrent role: {user.get_role_display()}")
    print("\nSelect New Role:")
    print("1. Viewer (Read-only access)")
    print("2. Editor (Can edit content)")
    print("3. Super Admin (Full access)")
    
    role_choice = input("Enter choice (1-3): ").strip()
    role_map = {
        '1': UserRole.VIEWER,
        '2': UserRole.EDITOR,
        '3': UserRole.SUPER_ADMIN
    }
    
    new_role = role_map.get(role_choice)
    if not new_role:
        print("Invalid choice")
        return
    
    user.role = new_role
    if new_role == UserRole.SUPER_ADMIN:
        user.is_superuser = True
        user.is_staff = True
    user.save()
    
    print(f"\n✓ User role updated successfully!")
    print(f"  Email: {user.email}")
    print(f"  New Role: {user.get_role_display()}")


def deactivate_user():
    """Deactivate a user account"""
    print("\n--- Deactivate User ---\n")
    
    email = input("User Email: ").strip()
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        print(f"Error: User with email {email} not found")
        return
    
    if not user.is_active:
        print(f"User {email} is already deactivated")
        return
    
    confirm = input(f"Deactivate user {email}? (yes/no): ").strip().lower()
    if confirm == 'yes':
        user.is_active = False
        user.save()
        print(f"\n✓ User {email} has been deactivated")
    else:
        print("Cancelled")


def activate_user():
    """Activate a user account"""
    print("\n--- Activate User ---\n")
    
    email = input("User Email: ").strip()
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        print(f"Error: User with email {email} not found")
        return
    
    if user.is_active:
        print(f"User {email} is already active")
        return
    
    user.is_active = True
    user.save()
    print(f"\n✓ User {email} has been activated")


def verify_user():
    """Manually verify a user's email"""
    print("\n--- Verify User Email ---\n")
    
    email = input("User Email: ").strip()
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        print(f"Error: User with email {email} not found")
        return
    
    if user.is_verified:
        print(f"User {email} is already verified")
        return
    
    user.is_verified = True
    user.save()
    print(f"\n✓ User {email} has been verified")


def reset_password():
    """Reset a user's password"""
    print("\n--- Reset User Password ---\n")
    
    email = input("User Email: ").strip()
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        print(f"Error: User with email {email} not found")
        return
    
    new_password = input("New Password: ").strip()
    if not new_password:
        print("Error: Password cannot be empty")
        return
    
    confirm = input(f"Reset password for {email}? (yes/no): ").strip().lower()
    if confirm == 'yes':
        user.set_password(new_password)
        user.save()
        print(f"\n✓ Password reset successfully for {email}")
    else:
        print("Cancelled")


def delete_user():
    """Delete a user account"""
    print("\n--- Delete User ---\n")
    print("WARNING: This action cannot be undone!")
    
    email = input("User Email: ").strip()
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        print(f"Error: User with email {email} not found")
        return
    
    print(f"\nUser Details:")
    print(f"  Email: {user.email}")
    print(f"  Name: {user.full_name}")
    print(f"  Role: {user.get_role_display()}")
    
    confirm = input(f"\nType 'DELETE' to confirm deletion: ").strip()
    if confirm == 'DELETE':
        user.delete()
        print(f"\n✓ User {email} has been deleted")
    else:
        print("Cancelled")


def show_menu():
    """Display the main menu"""
    print("\n" + "="*50)
    print("USER ACCOUNT MANAGEMENT")
    print("="*50)
    print("1. List all users")
    print("2. Create new user")
    print("3. Update user role")
    print("4. Verify user email")
    print("5. Activate user")
    print("6. Deactivate user")
    print("7. Reset user password")
    print("8. Delete user")
    print("0. Exit")
    print("="*50)


def main():
    """Main function"""
    print("\n" + "="*50)
    print("Portfolio API - User Management")
    print("="*50)
    
    while True:
        show_menu()
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '1':
            list_users()
        elif choice == '2':
            create_user()
        elif choice == '3':
            update_user_role()
        elif choice == '4':
            verify_user()
        elif choice == '5':
            activate_user()
        elif choice == '6':
            deactivate_user()
        elif choice == '7':
            reset_password()
        elif choice == '8':
            delete_user()
        elif choice == '0':
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == '__main__':
    main()
