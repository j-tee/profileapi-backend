# Automatic Profile Creation - Implementation Guide

## 🎯 Overview

**Problem Solved:** Users can now log in without worrying about missing profiles. The system automatically creates a portfolio profile for every user account.

**Key Features:**
- ✅ Automatic profile creation on user registration
- ✅ Automatic profile creation on first login (if missing)
- ✅ Profile information included in login response
- ✅ Dedicated endpoint to get current user's profile
- ✅ Management command to fix existing users

---







## 🏗️ Backend Changes

### 1. Signal-Based Auto-Creation

Every time a user is created or logs in, the system automatically creates a profile if one doesn't exist.

**Location:** `accounts/signals.py`

```python
# Automatically creates profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            email=instance.email,
            first_name=instance.first_name,
            last_name=instance.last_name,
            headline=f"{instance.full_name}'s Portfolio",
            # ... default values
        )
```

### 2. Enhanced Login Response

The login endpoint now returns profile information along with user data.

**Endpoint:** `POST /api/auth/login/`

**New Response Format:**
```json
{
  "message": "Login successful",
  "user": {
    "id": "e4313f3e-d110-4f4e-a512-732ed0923d2c",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "role": "super_admin",
    "mfa_enabled": false
  },
  "profile": {
    "id": "5a2bcef7-6472-4a5e-9c5f-8c283b8fda85",
    "email": "user@example.com",
    "full_name": "John Doe",
    "headline": "John Doe's Portfolio",
    "is_complete": false
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbG...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbG..."
  }
}
```

**Profile Status Indicators:**
- `is_complete`: `false` means profile needs to be updated (missing city/state/country)
- `is_complete`: `true` means profile has all required information

### 3. New Endpoint: Get My Portfolio Profile

**Endpoint:** `GET /api/auth/my-portfolio-profile/`

**Purpose:** Get the full portfolio profile for the currently authenticated user

**Authentication:** Required (Bearer token)

**Request:**
```bash
GET /api/auth/my-portfolio-profile/
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": "5a2bcef7-6472-4a5e-9c5f-8c283b8fda85",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "headline": "John Doe's Portfolio",
  "summary": "Welcome to John Doe's professional portfolio...",
  "email": "user@example.com",
  "phone": null,
  "city": "",
  "state": "",
  "country": "",
  "profile_picture": null,
  "profile_picture_url": null,
  "cover_image": null,
  "cover_image_url": null,
  "social_links": [],
  "created_at": "2024-11-21T05:30:00Z",
  "updated_at": "2024-11-21T05:30:00Z"
}
```

---

## 🔧 Management Command

To fix existing users who don't have profiles:

```bash
# Run in production
python manage.py sync_user_profiles

# Dry run to see what would be created
python manage.py sync_user_profiles --dry-run
```

**What it does:**
- Scans all user accounts
- Creates missing profiles automatically
- Reports which profiles were created
- Shows profile-user relationships

---

## 💻 Frontend Integration

### Option 1: Use Profile from Login Response (Recommended)

```typescript
// Login component
const handleLogin = async (email: string, password: string) => {
  try {
    const response = await fetch('https://your-api.com/api/auth/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      // Store tokens
      localStorage.setItem('access_token', data.tokens.access);
      localStorage.setItem('refresh_token', data.tokens.refresh);
      
      // Store user info
      localStorage.setItem('user', JSON.stringify(data.user));
      
      // Store profile info (NEW!)
      localStorage.setItem('profile', JSON.stringify(data.profile));
      
      // Check if profile needs completion
      if (!data.profile.is_complete) {
        // Redirect to profile completion page
        navigate('/complete-profile');
      } else {
        // Redirect to dashboard
        navigate('/dashboard');
      }
    }
  } catch (error) {
    console.error('Login failed:', error);
  }
};
```

### Option 2: Fetch Profile After Login

```typescript
// After successful login, fetch the full profile
const fetchMyProfile = async () => {
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch('https://your-api.com/api/auth/my-portfolio-profile/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const profile = await response.json();
    localStorage.setItem('profile', JSON.stringify(profile));
    
    // Check if profile needs completion
    if (!profile.city || !profile.state || !profile.country) {
      navigate('/complete-profile');
    }
    
    return profile;
  } catch (error) {
    console.error('Failed to fetch profile:', error);
  }
};
```

### Complete Profile Flow Component

```typescript
import React, { useState, useEffect } from 'react';

const CompleteProfilePage = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    // Get profile from storage or fetch it
    const storedProfile = localStorage.getItem('profile');
    if (storedProfile) {
      setProfile(JSON.parse(storedProfile));
    } else {
      fetchProfile();
    }
  }, []);
  
  const fetchProfile = async () => {
    const token = localStorage.getItem('access_token');
    const response = await fetch('https://your-api.com/api/auth/my-portfolio-profile/', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setProfile(data);
    localStorage.setItem('profile', JSON.stringify(data));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const token = localStorage.getItem('access_token');
    const formData = new FormData(e.target);
    
    try {
      const response = await fetch(`https://your-api.com/api/profiles/${profile.id}/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          headline: formData.get('headline'),
          summary: formData.get('summary'),
          city: formData.get('city'),
          state: formData.get('state'),
          country: formData.get('country'),
          phone: formData.get('phone')
        })
      });
      
      if (response.ok) {
        const updatedProfile = await response.json();
        localStorage.setItem('profile', JSON.stringify(updatedProfile));
        alert('Profile updated successfully!');
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Failed to update profile:', error);
      alert('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };
  
  if (!profile) return <div>Loading...</div>;
  
  return (
    <div className="complete-profile-container">
      <h1>Complete Your Profile</h1>
      <p>Please fill in your portfolio information to get started.</p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Professional Headline</label>
          <input
            name="headline"
            type="text"
            defaultValue={profile.headline}
            placeholder="e.g., Full Stack Developer & Software Engineer"
            required
          />
        </div>
        
        <div className="form-group">
          <label>Professional Summary</label>
          <textarea
            name="summary"
            defaultValue={profile.summary}
            placeholder="Tell us about yourself and your experience..."
            rows={5}
            required
          />
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <label>City</label>
            <input
              name="city"
              type="text"
              defaultValue={profile.city}
              placeholder="e.g., Accra"
              required
            />
          </div>
          
          <div className="form-group">
            <label>State/Region</label>
            <input
              name="state"
              type="text"
              defaultValue={profile.state}
              placeholder="e.g., Greater Accra"
              required
            />
          </div>
        </div>
        
        <div className="form-group">
          <label>Country</label>
          <input
            name="country"
            type="text"
            defaultValue={profile.country}
            placeholder="e.g., Ghana"
            required
          />
        </div>
        
        <div className="form-group">
          <label>Phone (optional)</label>
          <input
            name="phone"
            type="tel"
            defaultValue={profile.phone}
            placeholder="+233 XX XXX XXXX"
          />
        </div>
        
        <div className="form-actions">
          <button type="submit" disabled={loading}>
            {loading ? 'Saving...' : 'Save Profile'}
          </button>
          <button type="button" onClick={() => navigate('/dashboard')}>
            Skip for Now
          </button>
        </div>
      </form>
    </div>
  );
};

export default CompleteProfilePage;
```

### Context/Hook for Profile Management

```typescript
// hooks/useProfile.ts
import { useState, useEffect } from 'react';

export const useProfile = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const fetchProfile = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        throw new Error('Not authenticated');
      }
      
      const response = await fetch('https://your-api.com/api/auth/my-portfolio-profile/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch profile');
      }
      
      const data = await response.json();
      setProfile(data);
      localStorage.setItem('profile', JSON.stringify(data));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  const updateProfile = async (updates) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`https://your-api.com/api/profiles/${profile.id}/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      });
      
      if (!response.ok) {
        throw new Error('Failed to update profile');
      }
      
      const updatedProfile = await response.json();
      setProfile(updatedProfile);
      localStorage.setItem('profile', JSON.stringify(updatedProfile));
      
      return updatedProfile;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };
  
  const isProfileComplete = () => {
    return profile && profile.city && profile.state && profile.country;
  };
  
  useEffect(() => {
    // Check localStorage first
    const storedProfile = localStorage.getItem('profile');
    if (storedProfile) {
      setProfile(JSON.parse(storedProfile));
      setLoading(false);
    } else {
      fetchProfile();
    }
  }, []);
  
  return {
    profile,
    loading,
    error,
    fetchProfile,
    updateProfile,
    isProfileComplete
  };
};
```

### Usage in Components

```typescript
// Dashboard.tsx
import { useProfile } from './hooks/useProfile';

const Dashboard = () => {
  const { profile, loading, isProfileComplete } = useProfile();
  
  if (loading) return <div>Loading...</div>;
  
  if (!isProfileComplete()) {
    return (
      <div className="alert">
        <p>⚠️ Your profile is incomplete. Please complete it to get the most out of your portfolio.</p>
        <Link to="/complete-profile">Complete Profile</Link>
      </div>
    );
  }
  
  return (
    <div>
      <h1>Welcome, {profile.full_name}!</h1>
      <p>{profile.headline}</p>
      {/* Dashboard content */}
    </div>
  );
};
```

---

## 🔄 Migration Path for Existing Production Users

### Step 1: Run the Sync Command

```bash
# SSH into your production server
ssh user@your-server

# Navigate to project directory
cd /path/to/profileapi-backend

# Activate virtual environment
source venv/bin/activate

# Run the sync command
python manage.py sync_user_profiles
```

### Step 2: Verify Profiles Created

```bash
# Check how many profiles exist
python manage.py shell -c "from profiles.models import Profile; print(f'Total profiles: {Profile.objects.count()}')"

# List all profiles with their emails
python manage.py shell -c "from profiles.models import Profile; [print(f'{p.email}: {p.id}') for p in Profile.objects.all()]"
```

### Step 3: Update Frontend

1. Update your login handler to use the new response format
2. Add profile completion check after login
3. Create a profile completion page
4. Update existing code that references profile UUIDs

---

## 📊 Profile Status Indicators

The system provides helpful indicators about profile completeness:

```typescript
// Check profile status
const checkProfileStatus = (profile) => {
  const checks = {
    hasBasicInfo: profile.first_name && profile.last_name,
    hasHeadline: profile.headline && profile.headline !== `${profile.full_name}'s Portfolio`,
    hasSummary: profile.summary && !profile.summary.startsWith('Welcome to'),
    hasLocation: profile.city && profile.state && profile.country,
    hasPhoto: profile.profile_picture,
    hasContact: profile.phone || profile.email,
  };
  
  const completeness = Object.values(checks).filter(Boolean).length;
  const total = Object.keys(checks).length;
  const percentage = (completeness / total) * 100;
  
  return {
    ...checks,
    completeness,
    total,
    percentage,
    isComplete: checks.hasLocation // Minimum requirement
  };
};
```

---

## 🎨 UI/UX Recommendations

### 1. Profile Completion Progress Bar

```tsx
const ProfileProgressBar = ({ profile }) => {
  const status = checkProfileStatus(profile);
  
  return (
    <div className="profile-progress">
      <div className="progress-bar">
        <div 
          className="progress-fill" 
          style={{ width: `${status.percentage}%` }}
        />
      </div>
      <p>{status.percentage.toFixed(0)}% Complete</p>
      
      <ul className="checklist">
        {!status.hasHeadline && <li>✏️ Add a professional headline</li>}
        {!status.hasSummary && <li>✏️ Write your professional summary</li>}
        {!status.hasLocation && <li>📍 Add your location</li>}
        {!status.hasPhoto && <li>📷 Upload a profile picture</li>}
        {!status.hasContact && <li>📞 Add contact information</li>}
      </ul>
    </div>
  );
};
```

### 2. First-Time Login Flow

```typescript
// After login
const handlePostLogin = (loginResponse) => {
  const isFirstLogin = !localStorage.getItem('has_logged_in_before');
  
  if (isFirstLogin) {
    localStorage.setItem('has_logged_in_before', 'true');
    
    // Show welcome modal
    showWelcomeModal({
      title: 'Welcome to Your Portfolio!',
      message: 'Let\'s set up your profile to get started.',
      onContinue: () => navigate('/complete-profile')
    });
  } else if (!loginResponse.profile.is_complete) {
    // Returning user with incomplete profile
    showNotification({
      type: 'info',
      message: 'Your profile is incomplete. Complete it to unlock all features.',
      action: { label: 'Complete Now', onClick: () => navigate('/complete-profile') }
    });
  }
};
```

---

## 🔐 Security Considerations

1. **Authentication Required**: Profile endpoints require valid JWT tokens
2. **User Isolation**: Users can only access/modify their own profile
3. **Validation**: All profile updates are validated server-side
4. **Rate Limiting**: Login and profile endpoints are rate-limited

---

## 🐛 Troubleshooting

### Issue: User has no profile after login

**Solution:**
```bash
python manage.py sync_user_profiles
```

### Issue: Profile not showing in login response

**Check:**
1. Signals are properly registered in `accounts/apps.py`
2. `accounts.signals` is imported in `apps.py`'s `ready()` method
3. Profile model is accessible from accounts app

### Issue: Multiple profiles with same email

**Prevention:** The system uses `get_or_create` to prevent duplicates

**Fix if it happens:**
```python
# In Django shell
from profiles.models import Profile
from accounts.models import User

# Find duplicates
from django.db.models import Count
duplicates = Profile.objects.values('email').annotate(count=Count('email')).filter(count__gt=1)

# Keep the newest, delete others
for dup in duplicates:
    profiles = Profile.objects.filter(email=dup['email']).order_by('-created_at')
    for old_profile in profiles[1:]:
        old_profile.delete()
```

---

## 📝 API Reference Summary

### Login with Profile
```
POST /api/auth/login/
Body: { "email": "user@example.com", "password": "password" }
Response: { user, profile, tokens }
```

### Get My Profile
```
GET /api/auth/my-portfolio-profile/
Headers: { "Authorization": "Bearer <token>" }
Response: { id, email, first_name, ..., social_links }
```

### Update My Profile
```
PATCH /api/profiles/{profile_id}/
Headers: { "Authorization": "Bearer <token>" }
Body: { "headline": "...", "city": "...", ... }
Response: { updated profile }
```

---

## ✅ Deployment Checklist

- [ ] Run migrations (if any new migrations exist)
- [ ] Run `python manage.py sync_user_profiles` to fix existing users
- [ ] Update frontend login handler
- [ ] Create profile completion page
- [ ] Test login flow with existing users
- [ ] Test login flow with new users
- [ ] Update environment variables if needed
- [ ] Clear any cached profile data
- [ ] Monitor logs for profile creation

---

**Last Updated:** November 21, 2025  
**Backend Version:** 2.0.0 (Auto-Profile Feature)  
**Status:** Production Ready
