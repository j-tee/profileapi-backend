# Deploy Auto-Profile Creation Feature to Production

## What This Fixes

1. **Automatic Profile Creation** - Profiles are now created automatically when users log in
2. **Login Response Includes Profile** - Frontend gets profile info and completion status
3. **Profile Update Endpoint** - Users can update their own profile at `/api/profiles/me/`
4. **Profile Completion Check** - Backend tells frontend if profile needs updating

---

## Step 1: Fix ALLOWED_HOSTS (Critical!)

```bash
# SSH to production server
ssh deploy@server

# Edit .env.production
sudo nano /var/www/portfolio/backend/.env.production

# Change this line (REMOVE SPACE after comma):
# FROM:
ALLOWED_HOSTS=profileapi.alphalogiquetechnologies.com, www.profileapi.alphalogiquetechnologies.com

# TO (no space):
ALLOWED_HOSTS=profileapi.alphalogiquetechnologies.com,www.profileapi.alphalogiquetechnologies.com

# Save: Ctrl+X, Y, Enter
```

---

## Step 2: Deploy Code Changes

### Option A: Git Pull (If using Git)

```bash
cd /var/www/portfolio/backend

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install any new dependencies
pip install -r requirements.txt
```

### Option B: Manual File Upload

Upload these modified files to production:
- `profiles/models.py`
- `accounts/signals.py`
- `accounts/views.py`
- `profiles/views.py`

---

## Step 3: Run Database Migrations

```bash
cd /var/www/portfolio/backend
source venv/bin/activate  # if using venv

# Create migration for Profile model changes
python manage.py makemigrations profiles

# Apply migrations
python manage.py migrate

# You should see:
# Applying profiles.0002_alter_profile_city_alter_profile_country_alter_profile_state... OK
```

---

## Step 4: Create Profiles for Existing Users

```bash
# Run Django shell
python manage.py shell
```

```python
# In Django shell, paste this:
from accounts.models import User
from accounts.signals import ensure_user_has_profile

# Create profiles for all existing users
for user in User.objects.all():
    profile = ensure_user_has_profile(user)
    print(f"✅ {user.email} -> Profile ID: {profile.id}")

# Exit shell
exit()
```

---

## Step 5: Restart Services

```bash
# Restart Django app
sudo systemctl restart portfolio_api

# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status portfolio_api
sudo systemctl status nginx
```

---

## Step 6: Verify Everything Works

### Test 1: Check API is Running
```bash
curl https://profileapi.alphalogiquetechnologies.com/api/profiles/
```

### Test 2: Test Login (get profile info)
```bash
curl -X POST https://profileapi.alphalogiquetechnologies.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password"
  }'
```

Expected response should include:
```json
{
  "message": "Login successful",
  "user": {...},
  "profile": {
    "id": "some-uuid",
    "email": "your-email@example.com",
    "full_name": "Your Name",
    "headline": "Your Portfolio - Please update your profile",
    "is_complete": false
  },
  "tokens": {...}
}
```

---

## New API Endpoints Available

### 1. Get My Profile
```http
GET /api/auth/my-portfolio-profile/
Authorization: Bearer <access_token>
```

Response:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "headline": "Full Stack Developer",
  "summary": "...",
  "city": "Accra",
  "state": "Greater Accra",
  "country": "Ghana",
  ...
}
```

### 2. Get or Update My Profile (New!)
```http
GET /api/profiles/me/
Authorization: Bearer <access_token>
```

Response includes completion status:
```json
{
  "profile": {...},
  "is_complete": false,
  "needs_update": true
}
```

### 3. Update My Profile
```http
PATCH /api/profiles/me/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "headline": "Full Stack Developer & Cloud Architect",
  "summary": "Experienced developer...",
  "city": "Accra",
  "state": "Greater Accra",
  "country": "Ghana",
  "phone": "+233XXXXXXXXX"
}
```

---

## Frontend Integration Guide

### 1. Login Flow with Profile Check

```typescript
// Login function
async function login(email: string, password: string) {
  const response = await fetch('https://profileapi.alphalogiquetechnologies.com/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    // Save tokens
    localStorage.setItem('access_token', data.tokens.access);
    localStorage.setItem('refresh_token', data.tokens.refresh);
    
    // Save user and profile info
    localStorage.setItem('user', JSON.stringify(data.user));
    localStorage.setItem('profile', JSON.stringify(data.profile));
    
    // Check if profile needs update
    if (!data.profile.is_complete) {
      // Redirect to profile completion page
      router.push('/complete-profile');
    } else {
      // Redirect to dashboard
      router.push('/dashboard');
    }
  }
}
```

### 2. Profile Completion Page Component

```typescript
// components/CompleteProfile.tsx
import { useState, useEffect } from 'react';

export default function CompleteProfile() {
  const [profile, setProfile] = useState(null);
  const [formData, setFormData] = useState({
    headline: '',
    summary: '',
    city: '',
    state: '',
    country: '',
    phone: ''
  });
  
  useEffect(() => {
    fetchProfile();
  }, []);
  
  const fetchProfile = async () => {
    const token = localStorage.getItem('access_token');
    const response = await fetch(
      'https://profileapi.alphalogiquetechnologies.com/api/profiles/me/',
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    );
    
    const data = await response.json();
    
    if (data.needs_update) {
      // Show profile completion form
      setProfile(data.profile);
      setFormData({
        headline: data.profile.headline,
        summary: data.profile.summary,
        city: data.profile.city || '',
        state: data.profile.state || '',
        country: data.profile.country || '',
        phone: data.profile.phone || ''
      });
    } else {
      // Profile is complete, redirect to dashboard
      window.location.href = '/dashboard';
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const token = localStorage.getItem('access_token');
    const response = await fetch(
      'https://profileapi.alphalogiquetechnologies.com/api/profiles/me/',
      {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      }
    );
    
    const data = await response.json();
    
    if (response.ok) {
      alert('Profile updated successfully!');
      
      if (data.is_complete) {
        // Profile is now complete, go to dashboard
        window.location.href = '/dashboard';
      }
    } else {
      alert('Error updating profile: ' + JSON.stringify(data));
    }
  };
  
  if (!profile) {
    return <div>Loading...</div>;
  }
  
  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Complete Your Profile</h1>
      <p className="text-gray-600 mb-8">
        Please fill in your profile information to get started
      </p>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium mb-2">
            Professional Headline *
          </label>
          <input
            type="text"
            value={formData.headline}
            onChange={(e) => setFormData({...formData, headline: e.target.value})}
            placeholder="e.g., Full Stack Developer & Cloud Architect"
            className="w-full px-4 py-2 border rounded-lg"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">
            Professional Summary * (min 50 characters)
          </label>
          <textarea
            value={formData.summary}
            onChange={(e) => setFormData({...formData, summary: e.target.value})}
            placeholder="Tell us about your experience, skills, and what makes you unique..."
            className="w-full px-4 py-2 border rounded-lg h-32"
            required
            minLength={50}
          />
          <p className="text-sm text-gray-500 mt-1">
            {formData.summary.length} / 50 characters
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">City *</label>
            <input
              type="text"
              value={formData.city}
              onChange={(e) => setFormData({...formData, city: e.target.value})}
              placeholder="Accra"
              className="w-full px-4 py-2 border rounded-lg"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">State/Region *</label>
            <input
              type="text"
              value={formData.state}
              onChange={(e) => setFormData({...formData, state: e.target.value})}
              placeholder="Greater Accra"
              className="w-full px-4 py-2 border rounded-lg"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Country *</label>
            <input
              type="text"
              value={formData.country}
              onChange={(e) => setFormData({...formData, country: e.target.value})}
              placeholder="Ghana"
              className="w-full px-4 py-2 border rounded-lg"
              required
            />
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">
            Phone Number (Optional)
          </label>
          <input
            type="tel"
            value={formData.phone}
            onChange={(e) => setFormData({...formData, phone: e.target.value})}
            placeholder="+233XXXXXXXXX"
            className="w-full px-4 py-2 border rounded-lg"
          />
        </div>
        
        <div className="flex gap-4">
          <button
            type="submit"
            className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700"
          >
            Save Profile
          </button>
          
          <button
            type="button"
            onClick={() => window.location.href = '/dashboard'}
            className="px-6 py-3 border rounded-lg hover:bg-gray-50"
          >
            Skip for Now
          </button>
        </div>
      </form>
    </div>
  );
}
```

### 3. Protected Route Wrapper

```typescript
// components/ProtectedRoute.tsx
import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

export default function ProtectedRoute({ children }) {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);
  
  useEffect(() => {
    checkAuth();
  }, []);
  
  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      router.push('/login');
      return;
    }
    
    // Check profile status
    try {
      const response = await fetch(
        'https://profileapi.alphalogiquetechnologies.com/api/profiles/me/',
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      
      const data = await response.json();
      
      if (data.needs_update && router.pathname !== '/complete-profile') {
        // Redirect to profile completion if needed
        router.push('/complete-profile');
      } else {
        setIsChecking(false);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      router.push('/login');
    }
  };
  
  if (isChecking) {
    return <div>Loading...</div>;
  }
  
  return <>{children}</>;
}
```

---

## Testing in Production

### 1. Test Login
- Login with your account
- Check browser console for response
- Verify profile data is returned

### 2. Test Profile Completion
- Navigate to `/api/profiles/me/` endpoint
- Check `needs_update` field
- If true, show profile completion form

### 3. Test Profile Update
- Submit profile completion form
- Verify update succeeds
- Check `is_complete` becomes true

---

## Troubleshooting

### Issue: Still getting "No profile matches given query"

**Solution:**
```bash
# On production server
python manage.py shell

# Create profiles for all users
from accounts.models import User
from accounts.signals import ensure_user_has_profile
for user in User.objects.all():
    profile = ensure_user_has_profile(user)
    print(f"{user.email} -> {profile.id}")
exit()
```

### Issue: Migration fails

**Solution:**
```bash
# Check current migrations
python manage.py showmigrations profiles

# If stuck, try fake migration then run again
python manage.py migrate profiles --fake
python manage.py makemigrations profiles
python manage.py migrate profiles
```

### Issue: ALLOWED_HOSTS still causing errors

**Solution:**
```bash
# Double-check no spaces in .env.production
cat .env.production | grep ALLOWED_HOSTS

# Should show (no spaces):
# ALLOWED_HOSTS=profileapi.alphalogiquetechnologies.com,www.profileapi.alphalogiquetechnologies.com

# If still has spaces, edit again
sudo nano /var/www/portfolio/backend/.env.production
```

---

## Summary of Changes

✅ Profile model: Made location fields optional  
✅ Signals: Auto-create profile on user login  
✅ Login endpoint: Returns profile info and completion status  
✅ New endpoint: `/api/profiles/me/` for users to manage their profile  
✅ Profile validation: `is_complete` property checks if profile is filled out  

---

## What Happens Now

1. **User logs in** → Profile auto-created if doesn't exist
2. **Backend returns profile** with `is_complete` status
3. **Frontend checks** if `needs_update === true`
4. **If true** → Show profile completion form
5. **User fills form** → Submit to `/api/profiles/me/`
6. **Profile updated** → `is_complete` becomes true
7. **User can access** full dashboard

---

## Need Help?

Check logs:
```bash
# Django logs
sudo journalctl -u portfolio_api -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log

# Django debug (temporary)
python manage.py runserver 0.0.0.0:8000
```
