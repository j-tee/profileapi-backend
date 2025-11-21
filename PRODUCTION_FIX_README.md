# 🚀 PRODUCTION DEPLOYMENT - Quick Fix Guide

## Problem
Users logging in see "No profile matches the given query" error because they have User accounts but no Profile.

## Solution Implemented
✅ Automatic profile creation system with backend signals and enhanced login flow

---

## 📋 Production Deployment Steps

### Step 1: SSH into Production Server

```bash
ssh your-user@your-production-server
```

### Step 2: Navigate to Project

```bash
cd /path/to/profileapi-backend
source venv/bin/activate  # or your virtualenv path
```

### Step 3: Pull Latest Code

```bash
git pull origin main
```

### Step 4: Run the Fix Script

```bash
./fix_production_profiles.sh
```

**OR manually:**

```bash
# Check current state
python manage.py shell -c "from profiles.models import Profile; from accounts.models import User; print(f'Users: {User.objects.count()}, Profiles: {Profile.objects.count()}')"

# Dry run to see what will be created
python manage.py sync_user_profiles --dry-run

# Actually create the profiles
python manage.py sync_user_profiles

# Verify
python manage.py shell -c "from profiles.models import Profile; print(f'Total profiles: {Profile.objects.count()}')"
```

### Step 5: Restart Application

```bash
# If using systemd
sudo systemctl restart portfolio_api.service

# If using gunicorn directly
pkill gunicorn
gunicorn portfolio_api.wsgi:application --config gunicorn_config.py

# If using Docker
docker-compose restart web
```

### Step 6: Test the Fix

```bash
# Test login endpoint
curl -X POST https://your-domain.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"your-email@example.com","password":"your-password"}'

# Should return:
# {
#   "message": "Login successful",
#   "user": {...},
#   "profile": {
#     "id": "...",
#     "email": "...",
#     "full_name": "...",
#     "is_complete": false
#   },
#   "tokens": {...}
# }
```

---

## 🔍 What Changed

### Backend Files Modified:

1. ✅ **`accounts/signals.py`** (NEW) - Auto-creates profiles
2. ✅ **`accounts/apps.py`** - Registers signals
3. ✅ **`accounts/views.py`** - Enhanced login to include profile
4. ✅ **`accounts/urls.py`** - Added `/api/auth/my-portfolio-profile/` endpoint
5. ✅ **`accounts/management/commands/sync_user_profiles.py`** (NEW) - Management command

### New Endpoints:

- `GET /api/auth/my-portfolio-profile/` - Get current user's profile
- Enhanced `POST /api/auth/login/` - Now includes profile in response

---

## 🎯 Key Features

### 1. Automatic Profile Creation
- New users automatically get a profile when they register
- Existing users get a profile created on first login after this update
- Management command to fix all existing users at once

### 2. Enhanced Login Response
Login now returns:
```json
{
  "user": { ... },
  "profile": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "User Name",
    "headline": "User Name's Portfolio",
    "is_complete": false  // <-- Indicates if profile needs completion
  },
  "tokens": { ... }
}
```

### 3. Profile Status Check
- `is_complete: false` means profile needs location info (city/state/country)
- Frontend can show "Complete Your Profile" prompt

---

## 🖥️ Frontend Changes Needed

### Minimal Changes (Use Login Response):

```javascript
// OLD LOGIN
const response = await fetch('/api/auth/login/', {
  method: 'POST',
  body: JSON.stringify({ email, password })
});
const { user, tokens } = await response.json();

// NEW LOGIN (just add profile)
const response = await fetch('/api/auth/login/', {
  method: 'POST',
  body: JSON.stringify({ email, password })
});
const { user, profile, tokens } = await response.json();

// Store profile ID
localStorage.setItem('profile_id', profile.id);

// Check if profile needs completion
if (!profile.is_complete) {
  // Show "Complete Profile" message or redirect
  navigate('/complete-profile');
}
```

### Recommended: Add Profile Completion Flow

Create a simple page where users can complete their profile:
- Headline
- Summary
- Location (city, state, country)
- Phone (optional)
- Profile picture (optional)

See `AUTO_PROFILE_CREATION_GUIDE.md` for complete implementation examples.

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] All users have profiles (`python manage.py sync_user_profiles`)
- [ ] Login returns profile in response
- [ ] New endpoint `/api/auth/my-portfolio-profile/` works
- [ ] Application restarted successfully
- [ ] No errors in application logs
- [ ] Test login with existing user account
- [ ] Test registration with new user
- [ ] Profile shows in frontend

---

## 🐛 Troubleshooting

### Issue: Command not found
```bash
# Make script executable
chmod +x fix_production_profiles.sh
```

### Issue: Profile still not showing
```bash
# Check if signals are working
python manage.py shell
>>> from accounts.signals import ensure_user_has_profile
>>> from accounts.models import User
>>> user = User.objects.first()
>>> profile = ensure_user_has_profile(user)
>>> print(f"Profile ID: {profile.id}")
```

### Issue: Multiple profiles for same email
```bash
# Check for duplicates
python manage.py shell -c "from profiles.models import Profile; from django.db.models import Count; dups = Profile.objects.values('email').annotate(count=Count('email')).filter(count__gt=1); print(list(dups))"
```

---

## 📞 Support

If you encounter issues:

1. Check application logs: `tail -f /var/log/portfolio_api/error.log`
2. Check Django logs in the project directory
3. Verify database connection
4. Ensure all migrations are run: `python manage.py migrate`

---

## 🎉 Expected Outcome

After deployment:
- ✅ No more "No profile matches the given query" errors
- ✅ Users can login successfully
- ✅ Profile automatically created for all users
- ✅ Frontend receives profile information on login
- ✅ System ready for profile completion flow

---

**Deployment Time:** ~5 minutes  
**Downtime:** ~30 seconds (for app restart)  
**Risk Level:** Low (backward compatible)  

---

**Questions? Check:** `AUTO_PROFILE_CREATION_GUIDE.md` for detailed documentation
