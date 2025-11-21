# Profile to User Migration Guide

## Overview
The Profile model has been merged into the User model. All profile-related fields are now directly on the User model.

## Changes Made

### 1. User Model Updates
Added fields to `accounts.models.User`:
- `headline` - Professional headline
- `summary` - Professional bio/summary
- `city`, `state`, `country` - Location fields
- `profile_picture` - Profile picture
- `cover_image` - Cover/banner image

### 2. SocialLink Model
Moved from `profiles.SocialLink` to `accounts.SocialLink`:
- Now references `User` instead of `Profile`
- ForeignKey: `profile` → `user`

### 3. All Content Models Updated
Updated ForeignKey references from `profile` to `user`:
- `projects.Project`
- `experiences.Experience`
- `education.Education`
- `skills.Skill`
- `certifications.Certification`

### 4. App Removal
- Removed `profiles` app from INSTALLED_APPS
- Removed `api/` include for profiles.urls

## Migration Steps

### Step 1: Backup Database
```bash
python manage.py dumpdata > backup_before_migration.json
```

### Step 2: Create Migrations
```bash
# Make migrations for all affected apps
python manage.py makemigrations accounts
python manage.py makemigrations projects
python manage.py makemigrations experiences
python manage.py makemigrations education
python manage.py makemigrations skills
python manage.py makemigrations certifications
```

### Step 3: Run Data Migration (If you have existing data)

Create a custom data migration to copy Profile data to User:

```bash
python manage.py makemigrations accounts --empty --name merge_profile_to_user
```

Edit the migration file to include:

```python
from django.db import migrations

def merge_profile_data(apps, schema_editor):
    """Copy Profile data to User model"""
    User = apps.get_model('accounts', 'User')
    
    try:
        Profile = apps.get_model('profiles', 'Profile')
        
        for profile in Profile.objects.all():
            user = profile.user
            user.headline = profile.headline
            user.summary = profile.summary
            user.city = profile.city
            user.state = profile.state
            user.country = profile.country
            user.profile_picture = profile.profile_picture
            user.cover_image = profile.cover_image
            user.save()
            
        print(f"Migrated {Profile.objects.count()} profiles to users")
    except LookupError:
        # profiles app already removed, skip
        print("Profiles app not found, skipping data migration")

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', 'XXXX_previous_migration'),  # Update with actual number
    ]
    
    operations = [
        migrations.RunPython(merge_profile_data, migrations.RunPython.noop),
    ]
```

### Step 4: Apply Migrations
```bash
python manage.py migrate
```

### Step 5: Update API Endpoints

**Old Profile Endpoints (REMOVED):**
- `GET /api/profiles/` → Now use `GET /api/auth/users/`
- `GET /api/profiles/{id}/` → Now use `GET /api/auth/users/{id}/`
- `PATCH /api/profiles/{id}/` → Now use `PATCH /api/auth/profile/` (for own profile)
- `GET /api/profiles/{id}/social_links/` → Now use `GET /api/auth/social-links/`

**New Endpoints:**
- `GET /api/auth/profile/` - Get current user with portfolio data
- `PATCH /api/auth/profile/` - Update current user's portfolio
- `GET /api/auth/social-links/` - List own social links
- `POST /api/auth/social-links/` - Create social link
- `PATCH /api/auth/social-links/{id}/` - Update social link
- `DELETE /api/auth/social-links/{id}/` - Delete social link

### Step 6: Update Query Parameters

All endpoints that previously used `?profile={uuid}` now use `?user={uuid}`:

**Projects:**
- Old: `GET /api/projects/?profile={uuid}`
- New: `GET /api/projects/?user={uuid}`

**Experiences:**
- Old: `GET /api/experiences/?profile={uuid}`
- New: `GET /api/experiences/?user={uuid}`

**Education:**
- Old: `GET /api/education/?profile={uuid}`
- New: `GET /api/education/?user={uuid}`

**Skills:**
- Old: `GET /api/skills/?profile={uuid}`
- New: `GET /api/skills/?user={uuid}`

**Certifications:**
- Old: `GET /api/certifications/?profile={uuid}`
- New: `GET /api/certifications/?user={uuid}`

### Step 7: Update Frontend

Update all API calls to use new endpoints and field names:

```typescript
// OLD
const profile = await api.get(`/api/profiles/${profileId}/`);
const projects = await api.get(`/api/projects/?profile=${profileId}`);

// NEW
const user = await api.get(`/api/auth/users/${userId}/`);
const projects = await api.get(`/api/projects/?user=${userId}`);

// For current user's profile
const myProfile = await api.get('/api/auth/profile/');
```

## Benefits

1. **Simpler Architecture**: No separate Profile model to manage
2. **Single Source of Truth**: All user data in one place
3. **Easier Authentication**: User profile data immediately available after login
4. **Cleaner API**: Fewer endpoints, more intuitive structure
5. **Better Performance**: No joins between User and Profile tables

## Rollback Plan

If needed, you can rollback by:
1. Restoring from backup: `python manage.py loaddata backup_before_migration.json`
2. Reverting code changes from git
3. Running migrations again

## Testing

After migration, test:
1. User registration and login
2. Profile viewing and editing
3. Social links CRUD
4. Projects, experiences, education, skills, certifications listing
5. All filter parameters work correctly
6. Image uploads for profile pictures and covers

## Support

If you encounter issues:
1. Check migration logs
2. Verify database schema matches models
3. Test endpoints with Swagger UI: `/api/schema/swagger-ui/`
4. Check Django admin for data integrity
