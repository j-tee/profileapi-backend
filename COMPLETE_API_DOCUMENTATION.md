# Portfolio API - Complete Backend Documentation

> **Generated:** November 21, 2025  
> **API Version:** 1.0  
> **Base URL Production:** `https://profileapi.alphalogiquetechnologies.com`  
> **Base URL Development:** `http://localhost:8000`

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication Overview](#authentication-overview)
3. [Authentication Endpoints](#authentication-endpoints)
4. [User Management Endpoints](#user-management-endpoints)
5. [Profile Endpoints](#profile-endpoints)
6. [Project Endpoints](#project-endpoints)
7. [Experience Endpoints](#experience-endpoints)
8. [Education Endpoints](#education-endpoints)
9. [Skills Endpoints](#skills-endpoints)
10. [Certifications Endpoints](#certifications-endpoints)
11. [Contact Endpoints](#contact-endpoints)
12. [Response Structures](#response-structures)
13. [Error Handling](#error-handling)
14. [Permissions & Roles](#permissions--roles)

---

## Quick Start

### Authentication Flow
```bash
# 1. Register a new user
curl -X POST https://profileapi.alphalogiquetechnologies.com/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'

# 2. Login to get tokens
curl -X POST https://profileapi.alphalogiquetechnologies.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'

# 3. Use access token for authenticated requests
curl -H "Authorization: Bearer <access_token>" \
  https://profileapi.alphalogiquetechnologies.com/api/auth/profile/
```

### Public Endpoints (No Auth Required)
- All `GET` requests for profiles, projects, experiences, education, skills, certifications
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/token/refresh/`
- `POST /api/contacts/submit/` (public contact form)

### Protected Endpoints (Auth Required)
- All `POST`, `PUT`, `PATCH`, `DELETE` operations (except register/login)
- User profile management
- Admin/Editor content management

---

## Authentication Overview

### Token Types
- **Access Token**: Short-lived (15 minutes), used for API requests
- **Refresh Token**: Long-lived (7 days), used to get new access tokens

### Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### User Roles
| Role | Value | Description |
|------|-------|-------------|
| Super Admin | `super_admin` | Full system access |
| Editor | `editor` | Can manage content (profiles, projects, etc.) |
| Viewer | `viewer` | Read-only access, can send messages |

---

## Authentication Endpoints

### 1. Register User

**POST** `/api/auth/register/`

**Access:** Public (No authentication required)

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+233501234567"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone": "+233501234567",
    "role": "viewer",
    "is_verified": false,
    "is_active": true,
    "mfa_enabled": false,
    "created_at": "2025-11-21T10:30:00Z",
    "updated_at": "2025-11-21T10:30:00Z"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Validation Rules:**
- `email`: Valid email format, unique in system
- `password`: Min 8 characters, Django password validation
- `password_confirm`: Must match `password`
- `first_name`, `last_name`: Required, max 150 characters
- `phone`: Optional, format: `+[country][number]`

---

### 2. Login

**POST** `/api/auth/login/`

**Access:** Public (No authentication required)

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "mfa_token": "123456"
}
```

**Fields:**
- `email`: Required
- `password`: Required
- `mfa_token`: Required only if MFA is enabled (6 digits)

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone": "+233501234567",
    "role": "viewer",
    "is_verified": false,
    "is_active": true,
    "mfa_enabled": false,
    "created_at": "2025-11-21T10:30:00Z",
    "updated_at": "2025-11-21T10:30:00Z"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Error Responses:**
```json
// 400 - Invalid credentials
{
  "non_field_errors": ["Unable to log in with provided credentials."]
}

// 400 - MFA required
{
  "mfa_required": true,
  "message": "MFA token required"
}

// 400 - Invalid MFA token
{
  "non_field_errors": ["Invalid MFA token or backup code."]
}

// 400 - Account disabled
{
  "non_field_errors": ["User account is disabled."]
}
```

---

### 3. Refresh Token

**POST** `/api/auth/token/refresh/`

**Access:** Public (requires refresh token)

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error (401 Unauthorized):**
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

---

### 4. Get Current User Profile

**GET** `/api/auth/profile/`

**Access:** Authenticated users only

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "phone": "+233501234567",
  "role": "viewer",
  "is_verified": false,
  "is_active": true,
  "mfa_enabled": false,
  "created_at": "2025-11-21T10:30:00Z",
  "updated_at": "2025-11-21T10:30:00Z"
}
```

---

### 5. Update User Profile

**PATCH** `/api/auth/profile/`

**Access:** Authenticated users only

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+233509876543"
}
```

**Editable Fields:**
- `first_name`
- `last_name`
- `phone`

**Note:** Cannot change `email`, `role`, or `is_active` via this endpoint

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "full_name": "Jane Smith",
  "phone": "+233509876543",
  "role": "viewer",
  "is_verified": false,
  "is_active": true,
  "mfa_enabled": false,
  "created_at": "2025-11-21T10:30:00Z",
  "updated_at": "2025-11-21T10:35:00Z"
}
```

---

### 6. Change Password

**POST** `/api/auth/password/change/`

**Access:** Authenticated users only

**Request Body:**
```json
{
  "old_password": "OldPass123!",
  "new_password": "NewSecurePass456!",
  "new_password_confirm": "NewSecurePass456!"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "Invalid old password"
}
// or
{
  "new_password": "Password fields didn't match."
}
```

---

### 7. MFA Setup

**POST** `/api/auth/mfa/setup/`

**Access:** Authenticated users only

**Response (200 OK):**
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KG...",
  "backup_codes": [
    "12345678",
    "87654321",
    "11223344"
  ],
  "message": "Scan the QR code with your authenticator app and verify with a token"
}
```

---

### 8. MFA Verify (Enable)

**POST** `/api/auth/mfa/verify/`

**Access:** Authenticated users only (after MFA setup)

**Request Body:**
```json
{
  "token": "123456"
}
```

**Response (200 OK):**
```json
{
  "message": "MFA enabled successfully",
  "mfa_enabled": true
}
```

---

### 9. MFA Disable

**POST** `/api/auth/mfa/disable/`

**Access:** Authenticated users only

**Request Body:**
```json
{
  "password": "MyPassword123!"
}
```

**Response (200 OK):**
```json
{
  "message": "MFA disabled successfully"
}
```

---

### 10. User Activity Logs

**GET** `/api/auth/activity/`

**Access:** Authenticated users only

**Description:** Users see their own activity. Super admins see all activities.

**Query Parameters:**
- `user_id` (UUID) - Filter by user ID (super admin only)
- `action` (string) - Filter by action type

**Response (200 OK):**
```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "user_email": "user@example.com",
      "action": "USER_LOGIN",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "details": {},
      "timestamp": "2025-11-21T10:30:00Z"
    }
  ]
}
```

**Activity Types:**
- `USER_REGISTERED`
- `USER_LOGIN`
- `PROFILE_UPDATED`
- `PASSWORD_CHANGED`
- `MFA_SETUP_INITIATED`
- `MFA_ENABLED`
- `MFA_DISABLED`
- `MESSAGE_SENT`
- And more...

---

## User Management Endpoints

**(Super Admin Only)**

### 11. List Users

**GET** `/api/auth/users/`

**Access:** Super Admin only

**Query Parameters:**
- `role` - Filter by role (`super_admin`, `editor`, `viewer`)
- `is_active` - Filter by active status (`true`/`false`)
- `search` - Search in email, first name, last name

**Response (200 OK):**
```json
{
  "count": 50,
  "next": "http://...",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "viewer",
      "is_verified": false,
      "is_active": true,
      "mfa_enabled": false,
      "last_login": "2025-11-21T10:30:00Z",
      "created_at": "2025-11-20T08:00:00Z"
    }
  ]
}
```

---

### 12. Get User Details

**GET** `/api/auth/users/{user_id}/`

**Access:** Super Admin only

**Response (200 OK):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "phone": "+233501234567",
  "role": "viewer",
  "is_verified": false,
  "is_active": true,
  "mfa_enabled": false,
  "created_at": "2025-11-20T08:00:00Z",
  "updated_at": "2025-11-21T10:30:00Z"
}
```

---

### 13. Update User Role

**PATCH** `/api/auth/users/{user_id}/update_role/`

**Access:** Super Admin only

**Request Body:**
```json
{
  "role": "editor"
}
```

**Valid Roles:** `super_admin`, `editor`, `viewer`

**Response (200 OK):**
```json
{
  "message": "User role updated successfully",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone": "+233501234567",
    "role": "editor",
    "is_verified": false,
    "is_active": true,
    "mfa_enabled": false,
    "created_at": "2025-11-20T08:00:00Z",
    "updated_at": "2025-11-21T10:35:00Z"
  }
}
```

---

### 14. Deactivate User

**POST** `/api/auth/users/{user_id}/deactivate/`

**Access:** Super Admin only

**Response (200 OK):**
```json
{
  "message": "User deactivated successfully"
}
```

---

### 15. Activate User

**POST** `/api/auth/users/{user_id}/activate/`

**Access:** Super Admin only

**Response (200 OK):**
```json
{
  "message": "User activated successfully"
}
```

---

## Profile Endpoints

### 16. List Profiles

**GET** `/api/profiles/`

**Access:** Public (No authentication required)

**Query Parameters:**
- `search` - Search in headline, summary, city, state, country
- `city` - Filter by city
- `state` - Filter by state/region
- `country` - Filter by country

**Example:** `GET /api/profiles/?search=developer&country=Ghana`

**Response (200 OK):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "full_name": "TeeJay Developer",
      "email": "teejay@example.com",
      "headline": "Full Stack Developer & Cloud Architect",
      "city": "Accra",
      "state": "Greater Accra",
      "country": "Ghana",
      "profile_picture_url": "https://profileapi.alphalogiquetechnologies.com/media/profiles/pictures/teejay.jpg",
      "created_at": "2025-01-15T08:00:00Z"
    }
  ]
}
```

---

### 17. Get Profile Details

**GET** `/api/profiles/{profile_id}/`

**Access:** Public (No authentication required)

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "full_name": "TeeJay Developer",
  "email": "teejay@example.com",
  "phone": "+233501234567",
  "headline": "Full Stack Developer & Cloud Architect",
  "summary": "Passionate software engineer with 8+ years of experience...",
  "city": "Accra",
  "state": "Greater Accra",
  "country": "Ghana",
  "profile_picture": "profiles/pictures/teejay.jpg",
  "profile_picture_url": "https://profileapi.alphalogiquetechnologies.com/media/profiles/pictures/teejay.jpg",
  "cover_image": "profiles/covers/teejay-cover.jpg",
  "cover_image_url": "https://profileapi.alphalogiquetechnologies.com/media/profiles/covers/teejay-cover.jpg",
  "social_links": [
    {
      "id": "uuid",
      "platform": "github",
      "platform_display": "GitHub",
      "url": "https://github.com/teejay",
      "display_name": "TeeJay on GitHub",
      "order": 1
    }
  ],
  "projects_count": 12,
  "experiences_count": 4,
  "education_count": 2,
  "skills_count": 25,
  "certifications_count": 5,
  "created_at": "2025-01-15T08:00:00Z",
  "updated_at": "2025-11-20T14:30:00Z"
}
```

---

### 18. Create Profile

**POST** `/api/profiles/`

**Access:** Super Admin or Editor only

**Request Body (multipart/form-data):**
```
headline: "Full Stack Developer"
summary: "Experienced developer..."
city: "Accra"
state: "Greater Accra"
country: "Ghana"
profile_picture: <file>
cover_image: <file>
```

**Response (201 Created):**
Returns full profile object (same as GET profile details)

---

### 19. Update Profile

**PATCH** `/api/profiles/{profile_id}/`

**Access:** Super Admin or Editor only

**Request Body:**
```json
{
  "headline": "Updated Headline",
  "summary": "Updated summary...",
  "city": "New City"
}
```

**Response (200 OK):**
Returns updated profile object

---

### 20. Delete Profile

**DELETE** `/api/profiles/{profile_id}/`

**Access:** Super Admin or Editor only

**Response (204 No Content)**

---

### 21. Get Profile Social Links

**GET** `/api/profiles/{profile_id}/social_links/`

**Access:** Public

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "platform": "github",
    "platform_display": "GitHub",
    "url": "https://github.com/teejay",
    "display_name": "TeeJay on GitHub",
    "order": 1
  },
  {
    "id": "uuid",
    "platform": "linkedin",
    "platform_display": "LinkedIn",
    "url": "https://linkedin.com/in/teejay",
    "display_name": "Connect on LinkedIn",
    "order": 2
  }
]
```

**Supported Platforms:**
- `github` - GitHub
- `linkedin` - LinkedIn
- `twitter` - Twitter
- `portfolio` - Personal Portfolio
- `other` - Other

---

### 22. Add Social Link to Profile

**POST** `/api/profiles/{profile_id}/add_social_link/`

**Access:** Super Admin or Editor only

**Request Body:**
```json
{
  "platform": "github",
  "url": "https://github.com/username",
  "display_name": "My GitHub",
  "order": 1
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "platform": "github",
  "platform_display": "GitHub",
  "url": "https://github.com/username",
  "display_name": "My GitHub",
  "order": 1
}
```

---

### 23. Delete Social Link

**DELETE** `/api/profiles/{profile_id}/social_links/{link_id}/`

**Access:** Super Admin or Editor only

**Response (204 No Content):**
```json
{
  "message": "Social link deleted successfully"
}
```

---

### 24. List Social Links (All)

**GET** `/api/social-links/`

**Access:** Public

**Query Parameters:**
- `profile` (UUID) - Filter by profile ID
- `platform` - Filter by platform

**Response (200 OK):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "platform": "github",
      "platform_display": "GitHub",
      "url": "https://github.com/username",
      "display_name": "My GitHub",
      "order": 1
    }
  ]
}
```

---

## Project Endpoints

### 25. List Projects

**GET** `/api/projects/`

**Access:** Public (No authentication required)

**Query Parameters:**
- `profile` (UUID) - Filter by profile ID
- `featured` (`true`/`false`) - Filter featured projects
- `current` (`true`/`false`) - Filter current projects
- `featured_only` (`true`/`false`) - Show only featured
- `current_only` (`true`/`false`) - Show only current
- `search` - Search in title, description, technologies, role
- `ordering` - Order by: `start_date`, `-start_date`, `created_at`, `order`, `title`

**Example:** `GET /api/projects/?featured=true&ordering=-start_date`

**Response (200 OK):**
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "proj-uuid",
      "title": "E-Commerce Platform",
      "description": "Full-featured online shopping platform",
      "role": "Lead Developer",
      "technologies": ["Django", "React", "PostgreSQL", "Stripe"],
      "technologies_count": 4,
      "start_date": "2024-06-01",
      "end_date": "2024-12-15",
      "current": false,
      "featured": true,
      "thumbnail": "https://profileapi.alphalogiquetechnologies.com/media/projects/thumb.jpg",
      "project_url": "https://demo.example.com",
      "github_url": "https://github.com/username/project",
      "duration": "6 months",
      "created_at": "2025-01-10T09:00:00Z"
    }
  ]
}
```

---

### 26. Get Project Details

**GET** `/api/projects/{project_id}/`

**Access:** Public (No authentication required)

**Response (200 OK):**
```json
{
  "id": "proj-uuid",
  "profile": "profile-uuid",
  "profile_name": "TeeJay Developer",
  "title": "E-Commerce Platform",
  "description": "Full-featured online shopping platform",
  "long_description": "Comprehensive e-commerce solution with real-time inventory...",
  "technologies": ["Django", "React", "PostgreSQL", "Redis", "Stripe", "AWS"],
  "technologies_count": 6,
  "role": "Lead Developer",
  "team_size": 3,
  "start_date": "2024-06-01",
  "end_date": "2024-12-15",
  "current": false,
  "project_url": "https://demo.example.com",
  "github_url": "https://github.com/username/project",
  "demo_url": "https://demo.example.com",
  "video": "projects/videos/demo.mp4",
  "video_url": "https://profileapi.alphalogiquetechnologies.com/media/projects/videos/demo.mp4",
  "highlights": [
    "Reduced page load time by 60%",
    "Processed $50K+ in transactions"
  ],
  "challenges": [
    "Scaling infrastructure for high traffic",
    "Implementing real-time inventory updates"
  ],
  "outcomes": [
    "99.9% uptime achieved",
    "Customer satisfaction increased by 40%"
  ],
  "featured": true,
  "order": 1,
  "images": [
    {
      "id": "img-uuid",
      "image": "projects/images/home.jpg",
      "image_url": "https://profileapi.alphalogiquetechnologies.com/media/projects/images/home.jpg",
      "caption": "Homepage with featured products",
      "order": 1,
      "uploaded_at": "2025-01-10T10:00:00Z"
    }
  ],
  "duration": "6 months",
  "created_at": "2025-01-10T09:00:00Z",
  "updated_at": "2025-11-20T15:00:00Z"
}
```

---

### 27. Create Project

**POST** `/api/projects/`

**Access:** Super Admin or Editor only

**Request Body (multipart/form-data):**
```
profile: "profile-uuid"
title: "Project Title"
description: "Short description"
long_description: "Detailed description..."
technologies: ["Django", "React", "AWS"]
role: "Lead Developer"
team_size: 3
start_date: "2024-06-01"
end_date: "2024-12-15"  // Optional if current=true
current: false
project_url: "https://example.com"
github_url: "https://github.com/username/project"
demo_url: "https://demo.example.com"
highlights: ["Achievement 1", "Achievement 2"]
challenges: ["Challenge 1"]
outcomes: ["Outcome 1"]
featured: true
order: 1
video: <file>  // Optional, max 100MB, mp4/mov/avi/webm/mkv
images: <file[]>  // Optional, multiple images
```

**Validation Rules:**
- If `current` is `true`, `end_date` must be empty
- If `current` is `false`, `end_date` is required
- `end_date` cannot be before `start_date`
- `technologies`, `highlights`, `challenges`, `outcomes` must be arrays
- Video max size: 100MB
- Image max size: 10MB per image

**Response (201 Created):**
Returns full project object (same as GET project details)

---

### 28. Update Project

**PATCH** `/api/projects/{project_id}/`

**Access:** Super Admin or Editor only

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "featured": true,
  "current": false,
  "end_date": "2024-12-31"
}
```

**Response (200 OK):**
Returns updated project object

---

### 29. Delete Project

**DELETE** `/api/projects/{project_id}/`

**Access:** Super Admin or Editor only

**Response (204 No Content)**

---

### 30. Get Featured Projects

**GET** `/api/projects/featured/`

**Access:** Public

**Response (200 OK):**
Returns array of featured projects (same structure as list)

---

### 31. Get Projects by Profile

**GET** `/api/projects/by_profile/{profile_id}/`

**Access:** Public

**Response (200 OK):**
Returns paginated list of projects for the profile

---

### 32. Upload Project Images

**POST** `/api/projects/{project_id}/upload_images/`

**Access:** Super Admin or Editor only

**Request Body (multipart/form-data):**
```
images: <file[]>  // Multiple image files
caption_0: "Caption for first image"
caption_1: "Caption for second image"
```

**Response (201 Created):**
```json
[
  {
    "id": "img-uuid",
    "image": "projects/images/img1.jpg",
    "image_url": "https://profileapi.alphalogiquetechnologies.com/media/projects/images/img1.jpg",
    "caption": "Caption for first image",
    "order": 0,
    "uploaded_at": "2025-11-21T10:00:00Z"
  }
]
```

---

### 33. Delete Project Image

**DELETE** `/api/projects/{project_id}/delete_image/{image_id}/`

**Access:** Super Admin or Editor only

**Response (204 No Content):**
```json
{
  "message": "Image deleted successfully"
}
```

---

### 34. Reorder Project Images

**POST** `/api/projects/{project_id}/reorder_images/`

**Access:** Super Admin or Editor only

**Request Body:**
```json
{
  "image_order": [
    "img-uuid-3",
    "img-uuid-1",
    "img-uuid-2"
  ]
}
```

**Response (200 OK):**
Returns updated project object with reordered images

---

## Experience Endpoints

### 35. List Experiences

**GET** `/api/experiences/`

**Access:** Public (No authentication required)

**Query Parameters:**
- `profile` (UUID) - Filter by profile ID
- `employment_type` - Filter by type: `full_time`, `part_time`, `contract`, `freelance`, `internship`
- `location_type` - Filter by location: `onsite`, `remote`, `hybrid`
- `current` (`true`/`false`) - Filter current positions
- `search` - Search in title, company, description, technologies
- `ordering` - Order by: `start_date`, `-start_date`, `company`, `order`

**Response (200 OK):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "exp-uuid",
      "profile": "profile-uuid",
      "company": "Tech Solutions Ltd",
      "company_logo": "https://profileapi.alphalogiquetechnologies.com/media/experiences/logos/company.jpg",
      "title": "Senior Full Stack Developer",
      "employment_type": "full_time",
      "location": "Accra, Ghana",
      "location_type": "hybrid",
      "description": "Lead development of enterprise web applications",
      "responsibilities": [
        "Architected microservices infrastructure",
        "Mentored junior developers"
      ],
      "achievements": [
        "Reduced deployment time by 70%",
        "Improved system performance by 40%"
      ],
      "technologies": ["Django", "React", "Docker", "AWS"],
      "start_date": "2022-03-01",
      "end_date": null,
      "current": true,
      "order": 1,
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-11-20T16:00:00Z"
    }
  ]
}
```

---

### 36. Get Experience Details

**GET** `/api/experiences/{experience_id}/`

**Access:** Public

**Response (200 OK):**
Returns detailed experience object (same structure as list item)

---

### 37. Create Experience

**POST** `/api/experiences/`

**Access:** Super Admin or Editor only

**Request Body:**
```json
{
  "profile": "profile-uuid",
  "company": "Tech Solutions Ltd",
  "title": "Senior Full Stack Developer",
  "employment_type": "full_time",
  "location": "Accra, Ghana",
  "location_type": "hybrid",
  "description": "Leading development...",
  "responsibilities": [
    "Architect systems",
    "Mentor developers"
  ],
  "achievements": [
    "Reduced deployment time by 70%"
  ],
  "technologies": ["Django", "React"],
  "start_date": "2022-03-01",
  "end_date": null,
  "current": true,
  "order": 1
}
```

**Employment Types:**
- `full_time` - Full Time
- `part_time` - Part Time
- `contract` - Contract
- `freelance` - Freelance
- `internship` - Internship

**Location Types:**
- `onsite` - On-site
- `remote` - Remote
- `hybrid` - Hybrid

**Response (201 Created):**
Returns created experience object

---

### 38. Update Experience

**PATCH** `/api/experiences/{experience_id}/`

**Access:** Super Admin or Editor only

**Request Body:**
```json
{
  "title": "Updated Title",
  "current": false,
  "end_date": "2025-12-31"
}
```

**Response (200 OK):**
Returns updated experience object

---

### 39. Delete Experience

**DELETE** `/api/experiences/{experience_id}/`

**Access:** Super Admin or Editor only

**Response (204 No Content)**

---

### 40. Get Current Experiences

**GET** `/api/experiences/current/`

**Access:** Public

**Response (200 OK):**
Returns array of current positions only

---

### 41. Get Experiences by Profile

**GET** `/api/experiences/by_profile/{profile_id}/`

**Access:** Public

**Response (200 OK):**
Returns paginated list of experiences for the profile

---

## Education Endpoints

### 42. List Education

**GET** `/api/education/`

**Access:** Public (No authentication required)

**Query Parameters:**
- `profile` (UUID) - Filter by profile ID
- `current` (`true`/`false`) - Filter current education
- `search` - Search in institution, degree, field_of_study, description
- `ordering` - Order by: `start_date`, `-start_date`, `institution`, `order`

**Response (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "edu-uuid",
      "profile": "profile-uuid",
      "institution": "University of Ghana",
      "institution_logo": "https://profileapi.alphalogiquetechnologies.com/media/education/logos/ug.jpg",
      "degree": "Bachelor of Science",
      "field_of_study": "Computer Science",
      "description": "Focused on software engineering...",
      "activities": [
        "President of CS Students Association",
        "Hackathon winner"
      ],
      "grade": "First Class Honours",
      "start_date": "2015-09-01",
      "end_date": "2019-06-15",
      "current": false,
      "order": 1,
      "created_at": "2025-01-15T11:00:00Z",
      "updated_at": "2025-11-20T17:00:00Z"
    }
  ]
}
```

---

### 43. Get Education Details

**GET** `/api/education/{education_id}/`

**Access:** Public

**Response (200 OK):**
Returns detailed education object (same structure as list item)

---

### 44. Create Education

**POST** `/api/education/`

**Access:** Super Admin or Editor only

**Request Body:**
```json
{
  "profile": "profile-uuid",
  "institution": "University of Ghana",
  "degree": "Bachelor of Science",
  "field_of_study": "Computer Science",
  "description": "Computer science program...",
  "activities": [
    "President of CS Students Association",
    "Hackathon winner"
  ],
  "grade": "First Class Honours",
  "start_date": "2015-09-01",
  "end_date": "2019-06-15",
  "current": false,
  "order": 1
}
```

**Response (201 Created):**
Returns created education object

---

### 45. Update Education

**PATCH** `/api/education/{education_id}/`

**Access:** Super Admin or Editor only

**Request Body:**
```json
{
  "degree": "Updated Degree",
  "current": false,
  "end_date": "2019-06-15"
}
```

**Response (200 OK):**
Returns updated education object

---

### 46. Delete Education

**DELETE** `/api/education/{education_id}/`

**Access:** Super Admin or Editor only

**Response (204 No Content)**

---

### 47. Get Education by Profile

**GET** `/api/education/by_profile/{profile_id}/`

**Access:** Public

**Response (200 OK):**
Returns paginated list of education for the profile

---

## Skills Endpoints

### 48. List Skills

**GET** `/api/skills/`

**Access:** Public (No authentication required)

**Query Parameters:**
- `profile` (UUID) - Filter by profile ID
- `category` - Filter by category
- `proficiency_level` - Filter by proficiency: `beginner`, `intermediate`, `advanced`, `expert`
- `search` - Search in skill name
- `ordering` - Order by: `name`, `category`, `proficiency_level`, `years_of_experience`, `order`

**Response (200 OK):**
```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "skill-uuid",
      "profile": "profile-uuid",
      "name": "Django",
      "category": "Backend",
      "proficiency_level": "expert",
      "years_of_experience": 6,
      "endorsements": 15,
      "description": "Expert in building scalable REST APIs",
      "order": 1,
      "created_at": "2025-01-15T12:00:00Z",
      "updated_at": "2025-11-20T18:00:00Z"
    }
  ]
}
```

**Skill Categories:**
- `Frontend`
- `Backend`
- `Database`
- `DevOps`
- `Cloud`
- `Mobile`
- `Design`
- `Tools`
- `Soft Skills`
- `Other`

**Proficiency Levels:**
- `beginner` - Basic understanding
- `intermediate` - Can work independently
- `advanced` - Can handle complex tasks
- `expert` - Deep expertise

---

### 49. Get Skill Details

**GET** `/api/skills/{skill_id}/`

**Access:** Public

**Response (200 OK):**
Returns detailed skill object (same structure as list item)

---

### 50. Create Skill

**POST** `/api/skills/`

**Access:** Super Admin or Editor only

**Request Body:**
```json
{
  "profile": "profile-uuid",
  "name": "Django",
  "category": "Backend",
  "proficiency_level": "expert",
  "years_of_experience": 6,
  "endorsements": 15,
  "description": "Expert in building scalable REST APIs",
  "order": 1
}
```

**Response (201 Created):**
Returns created skill object

---

### 51. Update Skill

**PATCH** `/api/skills/{skill_id}/`

**Access:** Super Admin or Editor only

**Request Body:**
```json
{
  "proficiency_level": "expert",
  "years_of_experience": 7
}
```

**Response (200 OK):**
Returns updated skill object

---

### 52. Delete Skill

**DELETE** `/api/skills/{skill_id}/`

**Access:** Super Admin or Editor only

**Response (204 No Content)**

---

### 53. Get Skills by Profile

**GET** `/api/skills/by_profile/{profile_id}/`

**Access:** Public

**Response (200 OK):**
Returns paginated list of skills for the profile

---

### 54. Get Skills by Category

**GET** `/api/skills/by_category/`

**Access:** Public

**Query Parameters:**
- `profile` (UUID) - Filter by profile ID

**Response (200 OK):**
```json
{
  "Backend": {
    "name": "Backend",
    "count": 5,
    "skills": [
      {
        "id": "skill-uuid",
        "name": "Django",
        "proficiency_level": "expert",
        ...
      }
    ]
  },
  "Frontend": {
    "name": "Frontend",
    "count": 8,
    "skills": [...]
  }
}
```

---

## Certifications Endpoints

### 55. List Certifications

**GET** `/api/certifications/`

**Access:** Public (No authentication required)

**Query Parameters:**
- `profile` (UUID) - Filter by profile ID
- `issuer` - Filter by issuing organization
- `search` - Search in name, issuer, description, skills
- `ordering` - Order by: `issue_date`, `-issue_date`, `name`, `order`

**Response (200 OK):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "cert-uuid",
      "profile": "profile-uuid",
      "name": "AWS Certified Solutions Architect - Professional",
      "issuer": "Amazon Web Services",
      "issue_date": "2024-03-15",
      "expiration_date": "2027-03-15",
      "credential_id": "AWS-PSA-12345678",
      "credential_url": "https://aws.amazon.com/verification/12345678",
      "description": "Professional-level AWS certification...",
      "skills": ["AWS", "Cloud Architecture", "Security"],
      "certificate_image": "certifications/aws-cert.jpg",
      "certificate_image_url": "https://profileapi.alphalogiquetechnologies.com/media/certifications/aws-cert.jpg",
      "order": 1,
      "created_at": "2025-01-15T13:00:00Z",
      "updated_at": "2025-11-20T19:00:00Z"
    }
  ]
}
```

---

### 56. Get Certification Details

**GET** `/api/certifications/{certification_id}/`

**Access:** Public

**Response (200 OK):**
Returns detailed certification object (same structure as list item)

---

### 57. Create Certification

**POST** `/api/certifications/`

**Access:** Super Admin or Editor only

**Request Body (multipart/form-data):**
```
profile: "profile-uuid"
name: "AWS Certified Solutions Architect"
issuer: "Amazon Web Services"
issue_date: "2024-03-15"
expiration_date: "2027-03-15"  // Optional
credential_id: "AWS-PSA-12345678"
credential_url: "https://verify.example.com/12345"
description: "Professional-level certification..."
skills: ["AWS", "Cloud Architecture"]
certificate_image: <file>  // Optional
order: 1
```

**Response (201 Created):**
Returns created certification object

---

### 58. Update Certification

**PATCH** `/api/certifications/{certification_id}/`

**Access:** Super Admin or Editor only

**Request Body:**
```json
{
  "name": "Updated Certification Name",
  "expiration_date": "2028-03-15"
}
```

**Response (200 OK):**
Returns updated certification object

---

### 59. Delete Certification

**DELETE** `/api/certifications/{certification_id}/`

**Access:** Super Admin or Editor only

**Response (204 No Content)**

---

### 60. Get Certifications by Profile

**GET** `/api/certifications/by_profile/{profile_id}/`

**Access:** Public

**Response (200 OK):**
Returns paginated list of certifications for the profile

---

### 61. Get Active Certifications

**GET** `/api/certifications/active/`

**Access:** Public

**Description:** Returns only non-expired certifications

**Response (200 OK):**
Returns array of active certifications

---

## Contact Endpoints

### 62. Submit Contact Message (Public)

**POST** `/api/contacts/submit/`

**Access:** Public (No authentication required - Anonymous submissions allowed!)

**Request Body:**
```json
{
  "sender_name": "Jane Visitor",
  "sender_email": "jane@example.com",
  "message_type": "general_inquiry",
  "subject": "Inquiry about collaboration",
  "message": "Hi, I'm interested in discussing a potential project...",
  "project_budget": "$5,000 - $10,000",
  "project_timeline": "2-3 months"
}
```

**Fields:**
- `sender_name`: Required for anonymous submissions
- `sender_email`: Required for anonymous submissions
- `message_type`: Optional (default: `general_inquiry`)
- `subject`: Required
- `message`: Required
- `project_budget`: Required if `message_type` is `project_proposal`
- `project_timeline`: Optional

**Message Types:**
- `general_inquiry` - General Inquiry
- `project_proposal` - Project Proposal
- `job_opportunity` - Job Opportunity
- `collaboration` - Collaboration Request
- `feedback` - Feedback
- `support` - Support Request
- `other` - Other

**Response (201 Created):**
```json
{
  "message": "Your message has been received! We will get back to you soon.",
  "id": "msg-uuid",
  "status": "success"
}
```

**Error (400 Bad Request):**
```json
{
  "message": "Failed to submit contact form",
  "errors": {
    "sender_email": ["Enter a valid email address."],
    "message": ["This field may not be blank."]
  },
  "status": "error"
}
```

---

### 63. List Contact Messages (Admin)

**GET** `/api/contacts/messages/`

**Access:** Authenticated users (Users see own messages, Admins/Editors see all)

**Query Parameters:**
- `status` - Filter by status: `new`, `in_progress`, `responded`, `closed`
- `message_type` - Filter by message type
- `priority` (`true`/`false`) - Filter priority messages
- `search` - Search in subject, message, sender email

**Response (200 OK):**
```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "msg-uuid",
      "sender_display_name": "Jane Visitor",
      "sender_display_email": "jane@example.com",
      "message_type": "general_inquiry",
      "subject": "Inquiry about collaboration",
      "status": "new",
      "priority": false,
      "reply_count": 0,
      "created_at": "2025-11-21T14:30:00Z",
      "updated_at": "2025-11-21T14:30:00Z"
    }
  ]
}
```

**Message Status:**
- `new` - New (unread)
- `in_progress` - In Progress
- `responded` - Responded
- `closed` - Closed

---

### 64. Get Contact Message Details

**GET** `/api/contacts/messages/{message_id}/`

**Access:** Authenticated (Users see own messages, Admins/Editors see all)

**Response (200 OK):**
```json
{
  "id": "msg-uuid",
  "sender": {
    "id": "user-uuid",
    "email": "jane@example.com",
    "full_name": "Jane Visitor"
  },
  "sender_name": "Jane Visitor",
  "message_type": "general_inquiry",
  "subject": "Inquiry about collaboration",
  "message": "Hi, I'm interested in...",
  "project_budget": null,
  "project_timeline": null,
  "attachments": null,
  "status": "new",
  "priority": false,
  "admin_notes": null,
  "responded_by": null,
  "replied_by_name": null,
  "responded_at": null,
  "reply_count": 0,
  "created_at": "2025-11-21T14:30:00Z",
  "updated_at": "2025-11-21T14:30:00Z"
}
```

**Note:** When an admin/editor retrieves a message with status `new`, it's automatically marked as `read`.

---

### 65. Update Message Status (Admin)

**PATCH** `/api/contacts/messages/{message_id}/update_status/`

**Access:** Super Admin or Editor only

**Request Body:**
```json
{
  "status": "in_progress",
  "priority": true,
  "admin_notes": "Following up with client"
}
```

**Response (200 OK):**
```json
{
  "message": "Status updated successfully",
  "data": {
    "id": "msg-uuid",
    "status": "in_progress",
    "priority": true,
    ...
  }
}
```

---

### 66. Mark Message as Responded (Admin)

**POST** `/api/contacts/messages/{message_id}/mark_responded/`

**Access:** Super Admin or Editor only

**Response (200 OK):**
```json
{
  "message": "Message marked as responded",
  "data": {
    "id": "msg-uuid",
    "status": "responded",
    "responded_by": {...},
    "responded_at": "2025-11-21T15:00:00Z",
    ...
  }
}
```

---

### 67. Get Message Statistics (Admin)

**GET** `/api/contacts/messages/statistics/`

**Access:** Super Admin or Editor only

**Response (200 OK):**
```json
{
  "total_messages": 150,
  "new_messages": 25,
  "in_progress": 10,
  "responded": 100,
  "priority_count": 5,
  "by_type": {
    "general_inquiry": 80,
    "project_proposal": 40,
    "job_opportunity": 15,
    "collaboration": 10,
    "other": 5
  }
}
```

---

### 68. List Message Replies

**GET** `/api/contacts/replies/`

**Access:** Authenticated users

**Query Parameters:**
- `message_id` (UUID) - Filter by message ID

**Response (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "reply-uuid",
      "message": "msg-uuid",
      "author": {
        "id": "user-uuid",
        "email": "admin@example.com",
        "full_name": "Admin User"
      },
      "author_name": "Admin User",
      "content": "Thank you for reaching out...",
      "is_internal": false,
      "created_at": "2025-11-21T15:00:00Z",
      "updated_at": "2025-11-21T15:00:00Z"
    }
  ]
}
```

---

### 69. Create Message Reply

**POST** `/api/contacts/replies/`

**Access:** Authenticated users

**Request Body:**
```json
{
  "message_id": "msg-uuid",
  "content": "Thank you for your inquiry...",
  "is_internal": false
}
```

**Fields:**
- `message_id`: Required (UUID of the message)
- `content`: Required
- `is_internal`: Optional (default: `false`) - Only admins/editors can create internal notes

**Response (201 Created):**
```json
{
  "id": "reply-uuid",
  "message": "msg-uuid",
  "author": {...},
  "author_name": "Admin User",
  "content": "Thank you for your inquiry...",
  "is_internal": false,
  "created_at": "2025-11-21T15:00:00Z",
  "updated_at": "2025-11-21T15:00:00Z"
}
```

---

## Response Structures

### Pagination

All list endpoints return paginated results:

```json
{
  "count": 100,
  "next": "https://profileapi.alphalogiquetechnologies.com/api/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

**Page Size:** Default is 20 items per page

**Query Parameter:** `?page=2` to get next page

---

### Media URLs

All file fields return both relative path and absolute URL:

```json
{
  "profile_picture": "profiles/pictures/user.jpg",
  "profile_picture_url": "https://profileapi.alphalogiquetechnologies.com/media/profiles/pictures/user.jpg"
}
```

**Use the `*_url` fields in your frontend** for direct access to media files.

---

### Date/Time Format

All dates and times use ISO 8601 format:

```json
{
  "created_at": "2025-11-21T14:30:00Z",
  "start_date": "2024-06-01"
}
```

---

### UUID Format

All IDs are UUIDs (RFC 4122):

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message"
}
```

Or for validation errors:

```json
{
  "field_name": ["Error message for this field"],
  "another_field": ["Error 1", "Error 2"]
}
```

---

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Deleted successfully (no response body) |
| 400 | Bad Request | Validation error or invalid data |
| 401 | Unauthorized | Authentication required or invalid token |
| 403 | Forbidden | Permission denied |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

---

### Common Errors

#### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Solution:** Include `Authorization: Bearer <token>` header

---

#### 401 Token Expired
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

**Solution:** Use refresh token to get new access token

---

#### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Solution:** User doesn't have required role (super_admin/editor)

---

#### 404 Not Found
```json
{
  "detail": "Not found."
}
```

**Solution:** Resource with given ID doesn't exist

---

#### 429 Rate Limited
```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

**Solution:** Wait and retry later

---

## Permissions & Roles

### Role Hierarchy

1. **Super Admin** (`super_admin`)
   - Full system access
   - Can manage users, roles
   - Can create/edit/delete all content

2. **Editor** (`editor`)
   - Can create/edit/delete content (profiles, projects, etc.)
   - Cannot manage users or roles
   - Can view all contact messages

3. **Viewer** (`viewer`)
   - Read-only access to public content
   - Can update own profile
   - Can send contact messages
   - Can only see own messages

---

### Endpoint Permissions Summary

| Endpoint | Public | Viewer | Editor | Super Admin |
|----------|--------|--------|--------|-------------|
| Register/Login | ✅ | ✅ | ✅ | ✅ |
| View Profiles/Projects/etc. | ✅ | ✅ | ✅ | ✅ |
| Submit Contact Form | ✅ | ✅ | ✅ | ✅ |
| Update Own Profile | ❌ | ✅ | ✅ | ✅ |
| View Own Messages | ❌ | ✅ | ✅ | ✅ |
| Create/Edit Content | ❌ | ❌ | ✅ | ✅ |
| View All Messages | ❌ | ❌ | ✅ | ✅ |
| Manage Users | ❌ | ❌ | ❌ | ✅ |

---

## API Schema & Documentation

### Interactive Documentation

**Swagger UI:** https://profileapi.alphalogiquetechnologies.com/api/schema/swagger-ui/

**ReDoc:** https://profileapi.alphalogiquetechnologies.com/api/schema/redoc/

**OpenAPI Schema:** https://profileapi.alphalogiquetechnologies.com/api/schema/

---

## Rate Limiting

### Authentication Endpoints

- **Register/Login:** 10 requests per hour per IP address
- **Other Auth:** Standard rate limiting

---

## CORS Configuration

### Allowed Origins (Development)
- `http://localhost:3000`
- `http://localhost:5173`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

### Allowed Methods
- `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`

### Allowed Headers
- `Authorization`
- `Content-Type`
- `Accept`
- `Origin`
- `X-Requested-With`

---

## Media File Upload Limits

| File Type | Max Size | Allowed Formats |
|-----------|----------|-----------------|
| Profile Picture | 10MB | jpg, jpeg, png, gif, webp |
| Cover Image | 10MB | jpg, jpeg, png, gif, webp |
| Project Images | 10MB | jpg, jpeg, png, gif, webp |
| Project Video | 100MB | mp4, mov, avi, webm, mkv |
| Certification Image | 10MB | jpg, jpeg, png, pdf |

---

## Support & Contact

**API Base URL:** https://profileapi.alphalogiquetechnologies.com

**Documentation:** https://profileapi.alphalogiquetechnologies.com/api/schema/swagger-ui/

**Support Email:** teejay@alphalogiquetechnologies.com

---

## Change Log

### Version 1.0 (November 2025)
- Initial API release
- Authentication with JWT
- MFA support
- Public portfolio endpoints
- Contact form (public and admin)
- Full CRUD for all resources
- Role-based permissions

---

## Quick Reference

### Authentication Flow
```
1. POST /api/auth/register/ → Get tokens
2. POST /api/auth/login/ → Get tokens
3. Use access token in header: Authorization: Bearer <token>
4. POST /api/auth/token/refresh/ → Refresh when token expires
```

### Public Endpoints (No Auth)
```
GET  /api/profiles/
GET  /api/profiles/{id}/
GET  /api/projects/
GET  /api/projects/{id}/
GET  /api/experiences/
GET  /api/education/
GET  /api/skills/
GET  /api/certifications/
POST /api/contacts/submit/
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/token/refresh/
```

### Protected Endpoints (Auth Required)
```
GET/PATCH /api/auth/profile/
POST      /api/auth/password/change/
GET/POST  /api/contacts/messages/
POST/PUT/PATCH/DELETE /api/profiles/
POST/PUT/PATCH/DELETE /api/projects/
POST/PUT/PATCH/DELETE /api/experiences/
POST/PUT/PATCH/DELETE /api/education/
POST/PUT/PATCH/DELETE /api/skills/
POST/PUT/PATCH/DELETE /api/certifications/
```

### Admin Only Endpoints
```
GET  /api/auth/users/
POST /api/auth/users/{id}/update_role/
POST /api/auth/users/{id}/activate/
POST /api/auth/users/{id}/deactivate/
GET  /api/contacts/messages/statistics/
```

---

**End of Documentation**
