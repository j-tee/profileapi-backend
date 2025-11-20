# Complete Frontend Integration Guide - Julius Tetteh Portfolio

**Version:** 2.0  
**Last Updated:** November 20, 2025  
**For:** Frontend Development Team  
**Backend API:** Django REST Framework 3.15.2

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Understanding the Architecture](#understanding-the-architecture)
3. [Quick Start Configuration](#quick-start-configuration)
4. [Authentication System](#authentication-system)
5. [Profile System](#profile-system)
6. [Projects Management](#projects-management)
7. [Complete Code Examples](#complete-code-examples)
8. [API Reference](#api-reference)
9. [Troubleshooting](#troubleshooting)
10. [Deployment Checklist](#deployment-checklist)

---

## 🎯 Executive Summary

### What You Need to Know

This is **Julius Tetteh's personal portfolio website** - NOT a multi-user platform.

**There is:**
- ✅ **ONE User Account** - `juliustetteh@gmail.com` (for admin access)
- ✅ **ONE Profile** - Contains all portfolio content (public-facing)
- ✅ **Multiple Projects** - Each project belongs to the one profile

**Key IDs You'll Use:**
```typescript
const PORTFOLIO_CONFIG = {
  // Profile UUID (REQUIRED for creating projects)
  PROFILE_ID: 'bcd91fdc-d398-42f5-87b3-f7699fd50eae',
  
  // Owner email (for fetching profile)
  OWNER_EMAIL: 'juliustetteh@gmail.com',
  
  // Admin credentials (for dashboard login)
  ADMIN_EMAIL: 'juliustetteh@gmail.com',
  ADMIN_PASSWORD: 'pa$$word123', // ⚠️ Change this!
  
  // API Base URL
  API_BASE: 'http://localhost:8000'
};
```

---

## 🏗️ Understanding the Architecture

### The Two-System Design

```
┌────────────────────────────────────────────────────────────┐
│                    VISITOR VIEW (Public)                   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  GET /api/profiles/bcd91fdc-d398-42f5-87b3-f7699fd50eae/ │
│  ↓                                                         │
│  Profile Data:                                            │
│  ├── Name: Julius Tetteh                                  │
│  ├── Headline: Full Stack Developer                       │
│  ├── Bio, Photos, Contact Info                           │
│  └── Social Links                                         │
│                                                            │
│  GET /api/projects/by_profile/{PROFILE_ID}/              │
│  ↓                                                         │
│  Projects List:                                           │
│  ├── E-Commerce Platform                                  │
│  ├── Portfolio Website                                    │
│  └── Mobile App                                           │
│                                                            │
│  ⚠️ NO AUTHENTICATION REQUIRED                            │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                  ADMIN VIEW (Private)                      │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1. Login                                                  │
│     POST /api/auth/login/                                 │
│     { email: "juliustetteh@gmail.com", password: "..." } │
│     ↓                                                      │
│     Returns: { access: "token", refresh: "token" }        │
│                                                            │
│  2. Get Profile (to edit)                                 │
│     GET /api/profiles/by_email/?email=...                │
│     Headers: { Authorization: "Bearer <token>" }          │
│                                                            │
│  3. Create/Edit Content                                   │
│     POST /api/projects/                                   │
│     Body: { profile: "bcd91fdc-...", title: "..." }      │
│     Headers: { Authorization: "Bearer <token>" }          │
│                                                            │
│  ⚠️ AUTHENTICATION REQUIRED                               │
└────────────────────────────────────────────────────────────┘
```

### Why Two Systems?

**User Account (`/api/auth/`):**
- Purpose: Security & Authentication
- Used for: Login, permissions, password management
- Contains: Email, password, role, MFA settings
- Private information for admin only

**Profile (`/api/profiles/`):**
- Purpose: Public Portfolio Content
- Used for: Displaying bio, projects, experience
- Contains: Name, headline, bio, photos, location
- Public information for visitors

**Analogy:**
- **User Account** = Your house keys (private, for access)
- **Profile** = Your business card (public, for display)

---

## ⚡ Quick Start Configuration

### Step 1: Create Constants File

```typescript
// lib/constants.ts or config/portfolio.ts

export const PORTFOLIO = {
  // Backend API
  API_BASE_URL: 'http://localhost:8000',
  
  // Profile ID (CRITICAL - needed for all content creation)
  PROFILE_ID: 'bcd91fdc-d398-42f5-87b3-f7699fd50eae',
  
  // Owner information
  OWNER: {
    email: 'juliustetteh@gmail.com',
    name: 'Julius Tetteh',
    phone: '+233203344991'
  },
  
  // Admin credentials
  ADMIN: {
    email: 'juliustetteh@gmail.com',
    password: 'pa$$word123' // ⚠️ Never commit this to Git!
  }
} as const;

// Helper function to build API URLs
export const apiUrl = (path: string) => {
  return `${PORTFOLIO.API_BASE_URL}${path}`;
};
```

### Step 2: Create API Service

```typescript
// lib/api.ts

import { PORTFOLIO, apiUrl } from './constants';

// ============================================
// PUBLIC API (No Authentication Required)
// ============================================

export const publicApi = {
  /**
   * Get the main profile (Julius Tetteh's portfolio)
   */
  async getProfile() {
    const response = await fetch(
      apiUrl(`/api/profiles/${PORTFOLIO.PROFILE_ID}/`)
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch profile');
    }
    
    return response.json();
  },

  /**
   * Get all projects for the portfolio
   */
  async getProjects() {
    const response = await fetch(
      apiUrl(`/api/projects/by_profile/${PORTFOLIO.PROFILE_ID}/`)
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch projects');
    }
    
    return response.json();
  },

  /**
   * Get featured projects only
   */
  async getFeaturedProjects() {
    const response = await fetch(
      apiUrl('/api/projects/featured/')
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch featured projects');
    }
    
    return response.json();
  },

  /**
   * Get single project details
   */
  async getProject(projectId: string) {
    const response = await fetch(
      apiUrl(`/api/projects/${projectId}/`)
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch project');
    }
    
    return response.json();
  },

  /**
   * Submit contact form
   */
  async submitContact(data: {
    name: string;
    email: string;
    subject: string;
    message: string;
  }) {
    const response = await fetch(
      apiUrl('/api/contacts/'),
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to submit contact form');
    }
    
    return response.json();
  }
};

// ============================================
// ADMIN API (Requires Authentication)
// ============================================

export const adminApi = {
  /**
   * Login to admin dashboard
   */
  async login(email: string, password: string) {
    const response = await fetch(
      apiUrl('/api/auth/login/'),
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Login failed');
    }
    
    const data = await response.json();
    
    // Save tokens to localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
    }
    
    return data;
  },

  /**
   * Logout (clear tokens)
   */
  logout() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },

  /**
   * Get access token
   */
  getToken() {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token');
    }
    return null;
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return this.getToken() !== null;
  },

  /**
   * Get authenticated request headers
   */
  getAuthHeaders() {
    const token = this.getToken();
    return {
      'Authorization': `Bearer ${token}`
    };
  },

  /**
   * Update profile information
   */
  async updateProfile(updates: {
    headline?: string;
    summary?: string;
    phone?: string;
    city?: string;
    state?: string;
    country?: string;
  }) {
    const token = this.getToken();
    if (!token) throw new Error('Not authenticated');

    const response = await fetch(
      apiUrl(`/api/profiles/${PORTFOLIO.PROFILE_ID}/`),
      {
        method: 'PATCH',
        headers: {
          ...this.getAuthHeaders(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to update profile');
    }
    
    return response.json();
  },

  /**
   * Create a new project
   * ⚠️ IMPORTANT: profile field is automatically added
   */
  async createProject(projectData: {
    title: string;
    description: string;
    long_description?: string;
    role: string;
    technologies: string[]; // Array of tech names
    start_date: string; // YYYY-MM-DD
    end_date?: string; // YYYY-MM-DD
    current?: boolean;
    project_url?: string;
    github_url?: string;
    demo_url?: string;
    featured?: boolean;
    highlights?: string[];
    challenges?: string;
    outcomes?: string;
  }) {
    const token = this.getToken();
    if (!token) throw new Error('Not authenticated');

    const formData = new FormData();
    
    // ⚠️ CRITICAL: Always include profile ID
    formData.append('profile', PORTFOLIO.PROFILE_ID);
    
    // Add all project fields
    formData.append('title', projectData.title);
    formData.append('description', projectData.description);
    formData.append('role', projectData.role);
    formData.append('start_date', projectData.start_date);
    
    // Handle technologies array
    formData.append('technologies', JSON.stringify(projectData.technologies));
    
    // Optional fields
    if (projectData.long_description) {
      formData.append('long_description', projectData.long_description);
    }
    if (projectData.end_date) {
      formData.append('end_date', projectData.end_date);
    }
    if (projectData.current !== undefined) {
      formData.append('current', String(projectData.current));
    }
    if (projectData.project_url) {
      formData.append('project_url', projectData.project_url);
    }
    if (projectData.github_url) {
      formData.append('github_url', projectData.github_url);
    }
    if (projectData.demo_url) {
      formData.append('demo_url', projectData.demo_url);
    }
    if (projectData.featured !== undefined) {
      formData.append('featured', String(projectData.featured));
    }
    if (projectData.highlights) {
      formData.append('highlights', JSON.stringify(projectData.highlights));
    }
    if (projectData.challenges) {
      formData.append('challenges', projectData.challenges);
    }
    if (projectData.outcomes) {
      formData.append('outcomes', projectData.outcomes);
    }

    const response = await fetch(
      apiUrl('/api/projects/'),
      {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: formData
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to create project');
    }
    
    return response.json();
  },

  /**
   * Update an existing project
   */
  async updateProject(projectId: string, updates: Partial<{
    title: string;
    description: string;
    long_description: string;
    role: string;
    technologies: string[];
    start_date: string;
    end_date: string;
    current: boolean;
    project_url: string;
    github_url: string;
    featured: boolean;
  }>) {
    const token = this.getToken();
    if (!token) throw new Error('Not authenticated');

    const formData = new FormData();
    
    // Add updated fields
    Object.entries(updates).forEach(([key, value]) => {
      if (value !== undefined) {
        if (Array.isArray(value)) {
          formData.append(key, JSON.stringify(value));
        } else {
          formData.append(key, String(value));
        }
      }
    });

    const response = await fetch(
      apiUrl(`/api/projects/${projectId}/`),
      {
        method: 'PATCH',
        headers: this.getAuthHeaders(),
        body: formData
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to update project');
    }
    
    return response.json();
  },

  /**
   * Delete a project
   */
  async deleteProject(projectId: string) {
    const token = this.getToken();
    if (!token) throw new Error('Not authenticated');

    const response = await fetch(
      apiUrl(`/api/projects/${projectId}/`),
      {
        method: 'DELETE',
        headers: this.getAuthHeaders()
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to delete project');
    }
    
    return true;
  },

  /**
   * Upload images for a project
   */
  async uploadProjectImages(
    projectId: string, 
    images: File[], 
    captions?: string[]
  ) {
    const token = this.getToken();
    if (!token) throw new Error('Not authenticated');

    const formData = new FormData();
    
    images.forEach((image) => {
      formData.append('images', image);
    });
    
    if (captions) {
      formData.append('captions', JSON.stringify(captions));
    }

    const response = await fetch(
      apiUrl(`/api/projects/${projectId}/upload_images/`),
      {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: formData
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to upload images');
    }
    
    return response.json();
  },

  /**
   * Add social link to profile
   */
  async addSocialLink(data: {
    platform: 'github' | 'linkedin' | 'twitter' | 'portfolio' | 'other';
    url: string;
    display_name?: string;
    order?: number;
  }) {
    const token = this.getToken();
    if (!token) throw new Error('Not authenticated');

    const response = await fetch(
      apiUrl(`/api/profiles/${PORTFOLIO.PROFILE_ID}/add_social_link/`),
      {
        method: 'POST',
        headers: {
          ...this.getAuthHeaders(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to add social link');
    }
    
    return response.json();
  }
};
```

---

## 🔐 Authentication System

### Understanding User vs Profile

```typescript
// ❌ WRONG THINKING:
// "I need to create a profile when user registers"

// ✅ CORRECT THINKING:
// "There's already ONE user and ONE profile"
// "I just need to LOGIN and manage content"
```

### Login Flow

```typescript
// components/LoginForm.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { adminApi } from '@/lib/api';

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await adminApi.login(email, password);
      
      console.log('Logged in as:', result.user.email);
      console.log('Role:', result.user.role);
      
      // Redirect to dashboard
      router.push('/admin/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="login-form">
      <h2>Admin Login</h2>
      
      {error && (
        <div className="error-message">{error}</div>
      )}
      
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
        disabled={loading}
      />
      
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        disabled={loading}
      />
      
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
```

### Protected Routes

```typescript
// components/ProtectedRoute.tsx
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { adminApi } from '@/lib/api';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  useEffect(() => {
    if (!adminApi.isAuthenticated()) {
      router.push('/admin/login');
    }
  }, [router]);

  if (!adminApi.isAuthenticated()) {
    return <div>Checking authentication...</div>;
  }

  return <>{children}</>;
}

// Usage in admin pages:
// app/admin/dashboard/page.tsx
import { ProtectedRoute } from '@/components/ProtectedRoute';

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <div>Dashboard content here...</div>
    </ProtectedRoute>
  );
}
```

---

## 👤 Profile System

### TypeScript Interfaces

```typescript
// types/profile.ts

export interface Profile {
  id: string;
  first_name: string;
  last_name: string;
  full_name: string; // Computed: "Julius Tetteh"
  headline: string;
  summary: string;
  email: string;
  phone: string;
  city: string;
  state: string;
  country: string;
  profile_picture: string; // Path
  profile_picture_url: string; // Full URL
  cover_image: string; // Path
  cover_image_url: string; // Full URL
  social_links: SocialLink[];
  projects_count: number;
  experiences_count: number;
  education_count: number;
  skills_count: number;
  certifications_count: number;
  created_at: string;
  updated_at: string;
}

export interface SocialLink {
  id: string;
  platform: 'github' | 'linkedin' | 'twitter' | 'portfolio' | 'other';
  platform_display: string; // "GitHub", "LinkedIn", etc.
  url: string;
  display_name: string;
  order: number;
}
```

### Display Profile on Homepage

```tsx
// app/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { publicApi } from '@/lib/api';
import type { Profile } from '@/types/profile';

export default function HomePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const data = await publicApi.getProfile();
        setProfile(data);
      } catch (err) {
        setError('Failed to load profile');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, []);

  if (loading) {
    return (
      <div className="loading">
        <p>Loading...</p>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="error">
        <p>{error || 'Profile not found'}</p>
      </div>
    );
  }

  return (
    <main className="homepage">
      {/* Hero Section */}
      <section className="hero">
        {profile.cover_image_url && (
          <img
            src={profile.cover_image_url}
            alt="Cover"
            className="cover-image"
          />
        )}
        
        <div className="hero-content">
          {profile.profile_picture_url && (
            <img
              src={profile.profile_picture_url}
              alt={profile.full_name}
              className="profile-picture"
            />
          )}
          
          <h1>{profile.full_name}</h1>
          <h2>{profile.headline}</h2>
          <p className="summary">{profile.summary}</p>
          
          {/* Location */}
          <p className="location">
            📍 {profile.city}, {profile.state}, {profile.country}
          </p>
        </div>
      </section>

      {/* Stats */}
      <section className="stats">
        <div className="stat-card">
          <h3>{profile.projects_count}</h3>
          <p>Projects</p>
        </div>
        <div className="stat-card">
          <h3>{profile.experiences_count}</h3>
          <p>Experiences</p>
        </div>
        <div className="stat-card">
          <h3>{profile.skills_count}</h3>
          <p>Skills</p>
        </div>
        <div className="stat-card">
          <h3>{profile.certifications_count}</h3>
          <p>Certifications</p>
        </div>
      </section>

      {/* Social Links */}
      {profile.social_links.length > 0 && (
        <section className="social-links">
          <h3>Connect With Me</h3>
          <div className="links-grid">
            {profile.social_links.map((link) => (
              <a
                key={link.id}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="social-link"
              >
                {link.platform_display}
                {link.display_name && ` (${link.display_name})`}
              </a>
            ))}
          </div>
        </section>
      )}

      {/* Contact Info */}
      <section className="contact-info">
        <h3>Get In Touch</h3>
        <p>📧 <a href={`mailto:${profile.email}`}>{profile.email}</a></p>
        {profile.phone && (
          <p>📱 <a href={`tel:${profile.phone}`}>{profile.phone}</a></p>
        )}
      </section>
    </main>
  );
}
```

### Edit Profile (Admin)

```tsx
// app/admin/profile/edit/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { publicApi, adminApi } from '@/lib/api';
import type { Profile } from '@/types/profile';

export default function EditProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [formData, setFormData] = useState({
    headline: '',
    summary: '',
    phone: '',
    city: '',
    state: '',
    country: ''
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const data = await publicApi.getProfile();
        setProfile(data);
        setFormData({
          headline: data.headline,
          summary: data.summary,
          phone: data.phone || '',
          city: data.city,
          state: data.state,
          country: data.country
        });
      } catch (err) {
        console.error('Failed to load profile:', err);
      }
    };

    loadProfile();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');

    try {
      await adminApi.updateProfile(formData);
      setMessage('Profile updated successfully!');
      
      // Reload profile
      const updated = await publicApi.getProfile();
      setProfile(updated);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  if (!profile) {
    return <div>Loading...</div>;
  }

  return (
    <ProtectedRoute>
      <div className="edit-profile-page">
        <h1>Edit Profile</h1>
        
        {message && (
          <div className={message.includes('success') ? 'success' : 'error'}>
            {message}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Headline</label>
            <input
              type="text"
              value={formData.headline}
              onChange={(e) => setFormData({...formData, headline: e.target.value})}
              required
            />
          </div>
          
          <div className="form-group">
            <label>Summary / Bio</label>
            <textarea
              value={formData.summary}
              onChange={(e) => setFormData({...formData, summary: e.target.value})}
              rows={6}
              required
            />
          </div>
          
          <div className="form-group">
            <label>Phone</label>
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({...formData, phone: e.target.value})}
            />
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label>City</label>
              <input
                type="text"
                value={formData.city}
                onChange={(e) => setFormData({...formData, city: e.target.value})}
                required
              />
            </div>
            
            <div className="form-group">
              <label>State/Region</label>
              <input
                type="text"
                value={formData.state}
                onChange={(e) => setFormData({...formData, state: e.target.value})}
                required
              />
            </div>
            
            <div className="form-group">
              <label>Country</label>
              <input
                type="text"
                value={formData.country}
                onChange={(e) => setFormData({...formData, country: e.target.value})}
                required
              />
            </div>
          </div>
          
          <button type="submit" disabled={saving}>
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      </div>
    </ProtectedRoute>
  );
}
```

---

## 📁 Projects Management

### TypeScript Interfaces

```typescript
// types/project.ts

export interface Project {
  id: string;
  profile: string; // Profile UUID
  profile_name: string; // "Julius Tetteh"
  title: string;
  description: string;
  long_description: string;
  technologies: string[];
  technologies_count: number;
  role: string;
  team_size: number | null;
  start_date: string;
  end_date: string | null;
  current: boolean;
  duration: string; // "6 months" or "Jan 2024 - Present"
  project_url: string;
  github_url: string;
  demo_url: string;
  video: string;
  video_url: string;
  highlights: string[];
  challenges: string;
  outcomes: string;
  featured: boolean;
  order: number;
  images: ProjectImage[];
  thumbnail_url: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectImage {
  id: string;
  image: string;
  image_url: string;
  caption: string;
  order: number;
  uploaded_at: string;
}
```

### Display Projects

```tsx
// app/projects/page.tsx
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { publicApi } from '@/lib/api';
import type { Project } from '@/types/project';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProjects = async () => {
      try {
        const data = await publicApi.getProjects();
        setProjects(data);
      } catch (err) {
        console.error('Failed to load projects:', err);
      } finally {
        setLoading(false);
      }
    };

    loadProjects();
  }, []);

  if (loading) {
    return <div>Loading projects...</div>;
  }

  return (
    <main className="projects-page">
      <h1>My Projects</h1>
      
      <div className="projects-grid">
        {projects.map((project) => (
          <Link
            key={project.id}
            href={`/projects/${project.id}`}
            className="project-card"
          >
            {project.thumbnail_url && (
              <img
                src={project.thumbnail_url}
                alt={project.title}
                className="project-thumbnail"
              />
            )}
            
            {project.featured && (
              <span className="badge featured">Featured</span>
            )}
            
            {project.current && (
              <span className="badge current">Ongoing</span>
            )}
            
            <h2>{project.title}</h2>
            <p className="description">{project.description}</p>
            <p className="role">Role: {project.role}</p>
            
            <div className="technologies">
              {project.technologies.slice(0, 5).map((tech) => (
                <span key={tech} className="tech-badge">{tech}</span>
              ))}
              {project.technologies.length > 5 && (
                <span className="tech-badge">
                  +{project.technologies.length - 5} more
                </span>
              )}
            </div>
            
            <p className="duration">{project.duration}</p>
          </Link>
        ))}
      </div>
    </main>
  );
}
```

### Create Project (Admin)

```tsx
// app/admin/projects/new/page.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { adminApi } from '@/lib/api';

export default function NewProjectPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    long_description: '',
    role: '',
    technologies: '',
    start_date: '',
    end_date: '',
    current: false,
    project_url: '',
    github_url: '',
    demo_url: '',
    featured: false,
    highlights: '',
    challenges: '',
    outcomes: ''
  });
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    setError('');

    try {
      // Convert technologies string to array
      const techArray = formData.technologies
        .split(',')
        .map(t => t.trim())
        .filter(t => t.length > 0);

      // Convert highlights string to array
      const highlightsArray = formData.highlights
        .split('\n')
        .map(h => h.trim())
        .filter(h => h.length > 0);

      const project = await adminApi.createProject({
        title: formData.title,
        description: formData.description,
        long_description: formData.long_description || undefined,
        role: formData.role,
        technologies: techArray,
        start_date: formData.start_date,
        end_date: formData.current ? undefined : formData.end_date,
        current: formData.current,
        project_url: formData.project_url || undefined,
        github_url: formData.github_url || undefined,
        demo_url: formData.demo_url || undefined,
        featured: formData.featured,
        highlights: highlightsArray.length > 0 ? highlightsArray : undefined,
        challenges: formData.challenges || undefined,
        outcomes: formData.outcomes || undefined
      });

      console.log('Project created:', project);
      router.push(`/admin/projects/${project.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project');
    } finally {
      setCreating(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="new-project-page">
        <h1>Create New Project</h1>
        
        {error && (
          <div className="error-message">{error}</div>
        )}
        
        <form onSubmit={handleSubmit}>
          {/* Basic Info */}
          <fieldset>
            <legend>Basic Information</legend>
            
            <div className="form-group">
              <label>Project Title *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                required
                placeholder="E-Commerce Platform"
              />
            </div>
            
            <div className="form-group">
              <label>Short Description *</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                required
                rows={3}
                placeholder="A brief overview of the project..."
              />
            </div>
            
            <div className="form-group">
              <label>Detailed Description</label>
              <textarea
                value={formData.long_description}
                onChange={(e) => setFormData({...formData, long_description: e.target.value})}
                rows={6}
                placeholder="Full project description with context and goals..."
              />
            </div>
          </fieldset>

          {/* Role & Tech */}
          <fieldset>
            <legend>Role & Technologies</legend>
            
            <div className="form-group">
              <label>Your Role *</label>
              <input
                type="text"
                value={formData.role}
                onChange={(e) => setFormData({...formData, role: e.target.value})}
                required
                placeholder="Full Stack Developer"
              />
            </div>
            
            <div className="form-group">
              <label>Technologies * (comma-separated)</label>
              <input
                type="text"
                value={formData.technologies}
                onChange={(e) => setFormData({...formData, technologies: e.target.value})}
                required
                placeholder="React, Django, PostgreSQL, Redis, AWS"
              />
              <small>Separate technologies with commas</small>
            </div>
          </fieldset>

          {/* Timeline */}
          <fieldset>
            <legend>Timeline</legend>
            
            <div className="form-row">
              <div className="form-group">
                <label>Start Date *</label>
                <input
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({...formData, start_date: e.target.value})}
                  required
                />
              </div>
              
              <div className="form-group">
                <label>End Date</label>
                <input
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => setFormData({...formData, end_date: e.target.value})}
                  disabled={formData.current}
                />
              </div>
            </div>
            
            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={formData.current}
                  onChange={(e) => setFormData({...formData, current: e.target.checked})}
                />
                Currently working on this project
              </label>
            </div>
          </fieldset>

          {/* Links */}
          <fieldset>
            <legend>Project Links</legend>
            
            <div className="form-group">
              <label>Live Project URL</label>
              <input
                type="url"
                value={formData.project_url}
                onChange={(e) => setFormData({...formData, project_url: e.target.value})}
                placeholder="https://project-name.com"
              />
            </div>
            
            <div className="form-group">
              <label>GitHub Repository</label>
              <input
                type="url"
                value={formData.github_url}
                onChange={(e) => setFormData({...formData, github_url: e.target.value})}
                placeholder="https://github.com/username/repo"
              />
            </div>
            
            <div className="form-group">
              <label>Demo Video URL</label>
              <input
                type="url"
                value={formData.demo_url}
                onChange={(e) => setFormData({...formData, demo_url: e.target.value})}
                placeholder="https://youtube.com/watch?v=..."
              />
            </div>
          </fieldset>

          {/* Details */}
          <fieldset>
            <legend>Project Details</legend>
            
            <div className="form-group">
              <label>Key Highlights (one per line)</label>
              <textarea
                value={formData.highlights}
                onChange={(e) => setFormData({...formData, highlights: e.target.value})}
                rows={5}
                placeholder="Implemented real-time notifications&#10;Reduced API response time by 40%&#10;Built responsive admin dashboard"
              />
            </div>
            
            <div className="form-group">
              <label>Challenges & Solutions</label>
              <textarea
                value={formData.challenges}
                onChange={(e) => setFormData({...formData, challenges: e.target.value})}
                rows={4}
                placeholder="Describe challenges faced and how you solved them..."
              />
            </div>
            
            <div className="form-group">
              <label>Outcomes & Results</label>
              <textarea
                value={formData.outcomes}
                onChange={(e) => setFormData({...formData, outcomes: e.target.value})}
                rows={4}
                placeholder="Describe the impact and results of the project..."
              />
            </div>
          </fieldset>

          {/* Options */}
          <fieldset>
            <legend>Options</legend>
            
            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={formData.featured}
                  onChange={(e) => setFormData({...formData, featured: e.target.checked})}
                />
                Feature this project on homepage
              </label>
            </div>
          </fieldset>

          {/* Submit */}
          <div className="form-actions">
            <button
              type="button"
              onClick={() => router.back()}
              disabled={creating}
            >
              Cancel
            </button>
            <button type="submit" disabled={creating}>
              {creating ? 'Creating...' : 'Create Project'}
            </button>
          </div>
        </form>
      </div>
    </ProtectedRoute>
  );
}
```

---

## 📚 API Reference

### Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

### Authentication

All admin endpoints require JWT token in header:
```
Authorization: Bearer <access_token>
```

### Endpoints Summary

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| **Profile** ||||
| GET | `/api/profiles/{PROFILE_ID}/` | No | Get profile details |
| GET | `/api/profiles/by_email/?email=...` | No | Get profile by email |
| PATCH | `/api/profiles/{PROFILE_ID}/` | Yes | Update profile |
| GET | `/api/profiles/{PROFILE_ID}/social_links/` | No | Get social links |
| POST | `/api/profiles/{PROFILE_ID}/add_social_link/` | Yes | Add social link |
| **Projects** ||||
| GET | `/api/projects/` | No | List all projects |
| GET | `/api/projects/{id}/` | No | Get project details |
| GET | `/api/projects/by_profile/{PROFILE_ID}/` | No | Get profile projects |
| GET | `/api/projects/featured/` | No | Get featured projects |
| POST | `/api/projects/` | Yes | Create project |
| PATCH | `/api/projects/{id}/` | Yes | Update project |
| DELETE | `/api/projects/{id}/` | Yes | Delete project |
| POST | `/api/projects/{id}/upload_images/` | Yes | Upload project images |
| **Auth** ||||
| POST | `/api/auth/login/` | No | Login |
| POST | `/api/auth/token/refresh/` | No | Refresh token |
| GET | `/api/auth/profile/` | Yes | Get logged-in user |
| **Contact** ||||
| POST | `/api/contacts/` | No | Submit contact form |
| GET | `/api/contacts/` | Yes | List contacts (admin) |

---

## ⚠️ Troubleshooting

### Common Errors & Solutions

#### 1. "Profile UUID is not valid"

**Error Response:**
```json
{
  "message": "An error occurred!",
  "errors": {
    "profile": ["\"your-profile-uuid\" is not a valid UUID."]
  },
  "status": 400
}
```

**Cause:** You're using placeholder text instead of actual UUID

**Solution:**
```typescript
// ❌ WRONG
const data = {
  profile: "your-profile-uuid",
  title: "My Project"
};

// ✅ CORRECT
const data = {
  profile: "bcd91fdc-d398-42f5-87b3-f7699fd50eae",
  title: "My Project"
};
```

#### 2. "404 Not Found - /api/users/"

**Cause:** Wrong endpoint path

**Solution:**
```typescript
// ❌ WRONG
fetch('http://localhost:8000/api/users/')

// ✅ CORRECT
fetch('http://localhost:8000/api/auth/users/')
```

#### 3. "401 Unauthorized"

**Cause:** Missing or expired token

**Solution:**
```typescript
// Check if logged in
if (!adminApi.isAuthenticated()) {
  router.push('/admin/login');
  return;
}

// Include token in request
headers: {
  'Authorization': `Bearer ${adminApi.getToken()}`
}
```

#### 4. "CORS Error"

**Cause:** Frontend running on different port

**Solution:** Backend already configured for `localhost:5173` and `localhost:3000`. If using different port, update backend `.env`:
```env
CORS_ALLOWED_ORIGINS=http://localhost:YOUR_PORT,http://localhost:5173
```

#### 5. "Profile not found"

**Cause:** Using wrong profile ID or profile doesn't exist

**Solution:**
```typescript
// Always use the correct profile ID
const PROFILE_ID = 'bcd91fdc-d398-42f5-87b3-f7699fd50eae';

// Or fetch by email
const profile = await fetch(
  'http://localhost:8000/api/profiles/by_email/?email=juliustetteh@gmail.com'
);
```

#### 6. "Technologies field error"

**Cause:** Sending array as string or vice versa

**Solution:**
```typescript
// When using FormData (multipart/form-data)
formData.append('technologies', JSON.stringify(['React', 'Django']));

// When using JSON (application/json)
body: JSON.stringify({
  technologies: ['React', 'Django'] // Array
})
```

---

## ✅ Deployment Checklist

### Before Going Live

- [ ] Change admin password from `pa$$word123`
- [ ] Update `PORTFOLIO_CONFIG` in frontend code
- [ ] Remove hardcoded credentials from code
- [ ] Use environment variables for sensitive data
- [ ] Update API_BASE_URL to production URL
- [ ] Test all public pages without authentication
- [ ] Test admin login and CRUD operations
- [ ] Verify CORS settings for production domain
- [ ] Test image uploads and media serving
- [ ] Check mobile responsiveness
- [ ] Test contact form submission
- [ ] Verify all project links work
- [ ] Check social media links
- [ ] Test error handling and loading states
- [ ] Review console for errors
- [ ] Test on different browsers

### Environment Variables

Create `.env.local` in frontend:

```env
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_PROFILE_ID=bcd91fdc-d398-42f5-87b3-f7699fd50eae
NEXT_PUBLIC_OWNER_EMAIL=juliustetteh@gmail.com

# Don't commit admin credentials!
# Use separate admin panel for login
```

### Production URLs

Update constants for production:

```typescript
// lib/constants.ts
export const PORTFOLIO = {
  API_BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  PROFILE_ID: process.env.NEXT_PUBLIC_PROFILE_ID || 'bcd91fdc-d398-42f5-87b3-f7699fd50eae',
  OWNER: {
    email: process.env.NEXT_PUBLIC_OWNER_EMAIL || 'juliustetteh@gmail.com',
    name: 'Julius Tetteh',
    phone: '+233203344991'
  }
} as const;
```

---

## 🆘 Need Help?

### Quick Reference

**Profile ID:** `bcd91fdc-d398-42f5-87b3-f7699fd50eae`  
**Admin Email:** `juliustetteh@gmail.com`  
**API Base:** `http://localhost:8000`

### Key Concepts to Remember

1. **ONE Profile, ONE User** - This is a personal portfolio, not a multi-user platform
2. **Always include profile ID** when creating projects
3. **Public endpoints** - No auth needed for viewing profile/projects
4. **Admin endpoints** - Require JWT token for editing
5. **Use FormData** for file uploads (images, videos)
6. **Use JSON** for simple data updates

### Getting Started Steps

1. Create constants file with profile ID
2. Create API service with public and admin methods
3. Build public pages (homepage, projects)
4. Build admin pages (login, dashboard, project CRUD)
5. Add protected routes for admin pages
6. Test everything!

---

**Documentation Complete! 🎉**

Share this guide with your entire frontend team. Everything they need is in this ONE document.
