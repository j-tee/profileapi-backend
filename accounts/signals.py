"""
Signal handlers for automatic profile creation and management
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from profiles.models import Profile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a Profile when a new User is created
    This ensures every user has a corresponding profile
    """
    if created:
        # Check if profile already exists with this email
        if not Profile.objects.filter(email=instance.email).exists():
            Profile.objects.create(
                email=instance.email,
                first_name=instance.first_name,
                last_name=instance.last_name,
                headline=f"{instance.full_name}'s Portfolio",
                summary=f"Welcome to {instance.full_name}'s professional portfolio. "
                        f"Update this section to showcase your skills and experience.",
                city="",
                state="",
                country=""
            )


def ensure_user_has_profile(user):
    """
    Utility function to ensure a user has a profile
    Creates one if it doesn't exist
    Returns the profile
    """
    profile, created = Profile.objects.get_or_create(
        email=user.email,
        defaults={
            'first_name': user.first_name or 'User',
            'last_name': user.last_name or '',
            'headline': f"{user.full_name}'s Portfolio - Please update your profile",
            'summary': f"Welcome to {user.full_name}'s professional portfolio. "
                      f"Please update this section to showcase your skills, experience, and achievements. "
                      f"Tell visitors about your background, expertise, and what makes you unique.",
            'city': '',
            'state': '',
            'country': ''
        }
    )
    
    if created:
        print(f"✅ Profile created for user: {user.email} (ID: {profile.id})")
    
    return profile
