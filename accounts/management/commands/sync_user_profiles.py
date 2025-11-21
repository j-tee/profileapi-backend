"""
Django management command to ensure all users have profiles
Run this command to fix existing users without profiles
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from profiles.models import Profile

User = get_user_model()


class Command(BaseCommand):
    help = 'Ensure all users have corresponding portfolio profiles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating profiles',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('User-Profile Sync Tool'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No changes will be made\n'))
        
        users = User.objects.all()
        self.stdout.write(f'Found {users.count()} user(s)\n')
        
        profiles_created = 0
        profiles_existing = 0
        
        for user in users:
            self.stdout.write(f'User: {user.email}')
            self.stdout.write(f'  - UUID: {user.id}')
            self.stdout.write(f'  - Name: {user.full_name}')
            self.stdout.write(f'  - Role: {user.role}')
            
            # Check if profile exists
            try:
                profile = Profile.objects.get(email=user.email)
                self.stdout.write(self.style.SUCCESS(f'  ✅ Profile exists: {profile.id}'))
                self.stdout.write(f'     Name: {profile.full_name}')
                self.stdout.write(f'     Headline: {profile.headline}')
                profiles_existing += 1
            except Profile.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ❌ No profile found'))
                
                if not dry_run:
                    # Create profile
                    profile = Profile.objects.create(
                        email=user.email,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        headline=f"{user.full_name}'s Portfolio",
                        summary=f"Welcome to {user.full_name}'s professional portfolio. "
                                f"Update this section to showcase your skills and experience.",
                        city="",
                        state="",
                        country=""
                    )
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Profile created: {profile.id}'))
                    profiles_created += 1
                else:
                    self.stdout.write(self.style.WARNING(f'     Would create profile for {user.email}'))
            
            self.stdout.write('')
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Summary'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'Total users: {users.count()}')
        self.stdout.write(f'Existing profiles: {profiles_existing}')
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f'Profiles created: {profiles_created}'))
        else:
            self.stdout.write(self.style.WARNING(f'Profiles to create: {users.count() - profiles_existing}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Done!\n'))
        
        # Show all profiles
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('All Portfolio Profiles'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        profiles = Profile.objects.all()
        for profile in profiles:
            self.stdout.write(f'Profile: {profile.full_name}')
            self.stdout.write(f'  - UUID: {profile.id}')
            self.stdout.write(f'  - Email: {profile.email}')
            self.stdout.write(f'  - Headline: {profile.headline}')
            
            # Find matching user
            try:
                user = User.objects.get(email=profile.email)
                self.stdout.write(self.style.SUCCESS(f'  ✅ Linked to user: {user.email} (Role: {user.role})'))
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ⚠️  No user account with this email'))
            
            self.stdout.write('')
