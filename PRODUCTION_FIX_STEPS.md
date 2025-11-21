# Production Fix Steps

## Issue 1: Fix ALLOWED_HOSTS (CRITICAL - Do This First!)

### Current Problem:
```bash
ALLOWED_HOSTS=profileapi.alphalogiquetechnologies.com, www.profileapi.alphalogiquetechnologies.com
                                                      ^^^ SPACE HERE CAUSES ERROR!
```

### Fix on Production Server:

```bash
# Edit the .env.production file
sudo nano /var/www/portfolio/backend/.env.production

# Change this line (remove spaces after comma):
# FROM:
ALLOWED_HOSTS=profileapi.alphalogiquetechnologies.com, www.profileapi.alphalogiquetechnologies.com

# TO (no spaces!):
ALLOWED_HOSTS=profileapi.alphalogiquetechnologies.com,www.profileapi.alphalogiquetechnologies.com

# Save and exit (Ctrl+X, Y, Enter)
```

### Restart Services:
```bash
sudo systemctl restart portfolio_api
sudo systemctl restart nginx
```

---

## Issue 2: Create Profile for Logged-in User

Once ALLOWED_HOSTS is fixed, you need to create a profile for your user.

### Option A: Create Profile via Django Shell (Recommended)

```bash
# On production server
cd /var/www/portfolio/backend

# Activate virtual environment (if you have one)
source venv/bin/activate  # or wherever your venv is

# Run Django shell
python manage.py shell

# Then in the Python shell, paste this:
from accounts.models import User
from profiles.models import Profile

# Find your logged-in user
user = User.objects.get(email='juliustetteh@gmail.com')  # Use your actual email

# Check if profile exists
try:
    profile = Profile.objects.get(email=user.email)
    print(f"Profile already exists: {profile.id}")
except Profile.DoesNotExist:
    # Create the profile
    profile = Profile.objects.create(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        headline=f"{user.full_name}'s Portfolio",
        summary=f"Professional portfolio of {user.full_name}",
        city="Your City",  # Update these
        state="Your State",
        country="Your Country"
    )
    print(f"Profile created successfully!")
    print(f"Profile ID: {profile.id}")
    print(f"Use this ID in your frontend!")

# Exit shell
exit()
```

### Option B: Create Migration File to Auto-Create Profiles

This is the better long-term solution. Create this file on your production server:

```bash
# On production server
nano /var/www/portfolio/backend/profiles/management/commands/create_missing_profiles.py
```

Paste this content:

```python
from django.core.management.base import BaseCommand
from accounts.models import User
from profiles.models import Profile


class Command(BaseCommand):
    help = 'Create profiles for users who do not have one'

    def handle(self, *args, **kwargs):
        users_without_profile = []
        
        for user in User.objects.all():
            try:
                Profile.objects.get(email=user.email)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Profile exists for {user.email}')
                )
            except Profile.DoesNotExist:
                profile = Profile.objects.create(
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    headline=f"{user.full_name}'s Portfolio",
                    summary=f"Professional portfolio of {user.full_name}",
                    city="Not Set",
                    state="Not Set",
                    country="Not Set"
                )
                users_without_profile.append(user.email)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created profile for {user.email} - ID: {profile.id}')
                )
        
        if users_without_profile:
            self.stdout.write(
                self.style.SUCCESS(f'\nCreated {len(users_without_profile)} profile(s)')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nAll users already have profiles')
            )
```

Then run:
```bash
python manage.py create_missing_profiles
```

---

## Issue 3: Update Frontend Profile ID

After creating the profile, you'll get a profile UUID. Update your frontend:

```typescript
// In your frontend constants/config
export const PORTFOLIO_OWNER_PROFILE_ID = 'NEW-UUID-FROM-ABOVE';
```

---

## Complete Fix Sequence:

1. **Fix ALLOWED_HOSTS** (remove spaces)
2. **Restart services**
3. **Create profile** using Option A or B
4. **Note the profile UUID**
5. **Update frontend** with the correct UUID
6. **Test login again**

---

## Verification:

After applying fixes, test:

```bash
# Check if Django is running
sudo systemctl status portfolio_api

# Check nginx
sudo systemctl status nginx

# Test API directly
curl https://profileapi.alphalogiquetechnologies.com/api/profiles/

# Check your specific profile (use the UUID you got)
curl https://profileapi.alphalogiquetechnologies.com/api/profiles/YOUR-UUID-HERE/
```

---

## Common Commands:

```bash
# View Django logs
sudo journalctl -u portfolio_api -f

# View Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Restart services
sudo systemctl restart portfolio_api
sudo systemctl restart nginx

# Check Django migrations
python manage.py showmigrations

# Run migrations if needed
python manage.py migrate
```
