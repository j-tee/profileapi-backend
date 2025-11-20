# Portfolio API Integration Guide for Frontend Developers

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000` (Development)  
**API Prefix:** `/api/`  
**Date:** November 19, 2025

---




## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Formats](#requestresponse-formats)
5. [Error Handling](#error-handling)
6. [Code Examples](#code-examples)
7. [Best Practices](#best-practices)

---

## Overview

This API provides endpoints for managing a professional portfolio with authentication, user management, contact messages, profiles, experiences, education, skills, projects, and certifications.

### Key Features

- **JWT Authentication** with refresh tokens
- **Multi-Factor Authentication (MFA)** support
- **Role-Based Access Control** (Super Admin, Editor, Viewer)
- **RESTful API** design
- **Pagination** on list endpoints
- **Filtering & Search** capabilities
- **Rate Limiting** on auth endpoints

### Tech Stack

- Django 5.1.3
- Django REST Framework 3.15.2
- JWT Authentication (Simple JWT)
- SQLite/PostgreSQL Database

---

## Authentication

### Authentication Flow

1. **Register/Login** → Receive access & refresh tokens
2. **Include access token** in Authorization header for protected endpoints
3. **Refresh token** when access token expires
4. **MFA** (optional) - Required if enabled for user

### Token Management

**Access Token:**
- Lifetime: 60 minutes (default)
- Include in header: `Authorization: Bearer <access_token>`

**Refresh Token:**
- Lifetime: 7 days (default)
- Used to obtain new access tokens

### User Roles

| Role | Permissions | Description |
|------|------------|-------------|
| `super_admin` | Full access | Can manage all users and content |
| `editor` | Edit content | Can edit portfolio content |
| `viewer` | Read-only | Can only view content |

---

## API Endpoints

### Authentication Endpoints

#### 1. Register User

```http
POST /api/auth/register/
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "password_confirm": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone": "+1234567890",
    "role": "viewer",
    "is_verified": false,
    "is_active": true,
    "mfa_enabled": false,
    "created_at": "2025-11-19T10:30:00Z",
    "updated_at": "2025-11-19T10:30:00Z"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Validation Errors (400 Bad Request):**
```json
{
  "email": ["User with this email already exists."],
  "password": ["This password is too common."],
  "password_confirm": ["Password fields didn't match."]
}
```

---

#### 2. Login User

```http
POST /api/auth/login/
```

**Request Body (No MFA):**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Request Body (With MFA):**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "mfa_token": "123456"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone": "+1234567890",
    "role": "viewer",
    "is_verified": false,
    "is_active": true,
    "mfa_enabled": false,
    "created_at": "2025-11-19T10:30:00Z",
    "updated_at": "2025-11-19T10:30:00Z"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**MFA Required Response (400 Bad Request):**
```json
{
  "mfa_required": true,
  "message": "MFA token required"
}
```

---

#### 3. Refresh Token

```http
POST /api/auth/token/refresh/
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

#### 4. Get User Profile

```http
GET /api/auth/profile/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "role": "viewer",
  "is_verified": false,
  "is_active": true,
  "mfa_enabled": false,
  "created_at": "2025-11-19T10:30:00Z",
  "updated_at": "2025-11-19T10:30:00Z"
}
```

---

#### 5. Update User Profile

```http
PATCH /api/auth/profile/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+9876543210"
}
```

**Response (200 OK):**
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "full_name": "Jane Smith",
  "phone": "+9876543210",
  "role": "viewer",
  "is_verified": false,
  "is_active": true,
  "mfa_enabled": false,
  "created_at": "2025-11-19T10:30:00Z",
  "updated_at": "2025-11-19T11:15:00Z"
}
```

---

#### 6. Change Password

```http
POST /api/auth/password/change/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "old_password": "OldPassword123!",
  "new_password": "NewSecurePassword456!",
  "new_password_confirm": "NewSecurePassword456!"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

---

### Multi-Factor Authentication (MFA)

#### 7. Setup MFA

```http
POST /api/auth/mfa/setup/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...",
  "backup_codes": [
    "a1b2c3d4-e5f6g7h8",
    "i9j0k1l2-m3n4o5p6",
    "q7r8s9t0-u1v2w3x4",
    "y5z6a7b8-c9d0e1f2",
    "g3h4i5j6-k7l8m9n0"
  ],
  "message": "Scan the QR code with your authenticator app and verify with a token"
}
```

**Note:** Save backup codes securely. They cannot be retrieved again.

---

#### 8. Verify and Enable MFA

```http
POST /api/auth/mfa/verify/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

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

#### 9. Disable MFA

```http
POST /api/auth/mfa/disable/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "password": "YourPassword123!"
}
```

**Response (200 OK):**
```json
{
  "message": "MFA disabled successfully"
}
```

---

### Contact Messages

#### 10. Create Contact Message

```http
POST /api/contacts/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body (General Inquiry):**
```json
{
  "message_type": "general",
  "subject": "Website Development Inquiry",
  "message": "I would like to discuss a potential project...",
  "attachments": []
}
```

**Request Body (Project Proposal):**
```json
{
  "message_type": "proposal",
  "subject": "E-commerce Platform Development",
  "message": "We need a full-stack e-commerce solution...",
  "project_budget": 15000.00,
  "project_timeline": "3-4 months",
  "attachments": ["https://example.com/requirements.pdf"]
}
```

**Message Types:**
- `general` - General Inquiry
- `proposal` - Project Proposal
- `job` - Job Opportunity
- `collaboration` - Collaboration
- `feedback` - Feedback
- `other` - Other

**Response (201 Created):**
```json
{
  "id": "uuid-string",
  "sender": {
    "id": "uuid-string",
    "email": "client@example.com",
    "first_name": "Jane",
    "last_name": "Client",
    "full_name": "Jane Client",
    "phone": null,
    "role": "viewer",
    "is_verified": false,
    "is_active": true,
    "mfa_enabled": false,
    "created_at": "2025-11-19T10:30:00Z",
    "updated_at": "2025-11-19T10:30:00Z"
  },
  "sender_name": "Jane Client",
  "message_type": "proposal",
  "subject": "E-commerce Platform Development",
  "message": "We need a full-stack e-commerce solution...",
  "project_budget": "15000.00",
  "project_timeline": "3-4 months",
  "attachments": ["https://example.com/requirements.pdf"],
  "status": "new",
  "priority": false,
  "admin_notes": null,
  "responded_by": null,
  "replied_by_name": null,
  "responded_at": null,
  "reply_count": 0,
  "created_at": "2025-11-19T14:20:00Z",
  "updated_at": "2025-11-19T14:20:00Z"
}
```

---

#### 11. List Contact Messages

```http
GET /api/contacts/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status` - Filter by status (`new`, `read`, `in_progress`, `responded`, `archived`)
- `message_type` - Filter by type (`general`, `proposal`, `job`, etc.)
- `priority` - Filter priority messages (`true`/`false`)
- `search` - Search in subject, message, or sender email
- `page` - Page number (pagination)
- `page_size` - Items per page

**Example:**
```http
GET /api/contacts/?status=new&priority=true&page=1
```

**Response (200 OK):**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/contacts/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid-string",
      "sender_name": "Jane Client",
      "sender_email": "client@example.com",
      "message_type": "proposal",
      "subject": "E-commerce Platform Development",
      "status": "new",
      "priority": true,
      "reply_count": 0,
      "created_at": "2025-11-19T14:20:00Z",
      "updated_at": "2025-11-19T14:20:00Z"
    }
  ]
}
```

**Note:** Regular users only see their own messages. Editors and Admins see all messages.

---

#### 12. Get Contact Message Details

```http
GET /api/contacts/{message_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "uuid-string",
  "sender": {
    "id": "uuid-string",
    "email": "client@example.com",
    "first_name": "Jane",
    "last_name": "Client",
    "full_name": "Jane Client",
    "phone": null,
    "role": "viewer",
    "is_verified": false,
    "is_active": true,
    "mfa_enabled": false,
    "created_at": "2025-11-19T10:30:00Z",
    "updated_at": "2025-11-19T10:30:00Z"
  },
  "sender_name": "Jane Client",
  "message_type": "proposal",
  "subject": "E-commerce Platform Development",
  "message": "We need a full-stack e-commerce solution...",
  "project_budget": "15000.00",
  "project_timeline": "3-4 months",
  "attachments": [],
  "status": "read",
  "priority": false,
  "admin_notes": "Follow up on Monday",
  "responded_by": null,
  "replied_by_name": null,
  "responded_at": null,
  "reply_count": 2,
  "created_at": "2025-11-19T14:20:00Z",
  "updated_at": "2025-11-19T15:30:00Z"
}
```

---

#### 13. Update Message Status (Admin Only)

```http
PATCH /api/contacts/{message_id}/update_status/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "status": "in_progress",
  "priority": true,
  "admin_notes": "Scheduled call for next week"
}
```

**Response (200 OK):**
```json
{
  "message": "Status updated successfully",
  "data": {
    "id": "uuid-string",
    "status": "in_progress",
    "priority": true,
    "admin_notes": "Scheduled call for next week"
  }
}
```

---

#### 14. Get Message Statistics (Admin Only)

```http
GET /api/contacts/statistics/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "total_messages": 125,
  "new_messages": 15,
  "in_progress": 8,
  "responded": 95,
  "priority_count": 5,
  "by_type": {
    "general": 45,
    "proposal": 35,
    "job": 20,
    "collaboration": 15,
    "feedback": 10
  }
}
```

---

### Message Replies

#### 15. Create Reply

```http
POST /api/contacts/replies/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "message_id": "uuid-string",
  "content": "Thank you for reaching out. I'd be happy to discuss this project...",
  "is_internal": false
}
```

**Response (201 Created):**
```json
{
  "id": "uuid-string",
  "message": "uuid-string",
  "author": {
    "id": "uuid-string",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User",
    "full_name": "Admin User"
  },
  "author_name": "Admin User",
  "content": "Thank you for reaching out. I'd be happy to discuss this project...",
  "is_internal": false,
  "created_at": "2025-11-19T16:00:00Z",
  "updated_at": "2025-11-19T16:00:00Z"
}
```

**Note:** Set `is_internal: true` for internal notes (visible only to admins).

---

#### 16. List Replies

```http
GET /api/contacts/replies/?message_id={message_id}
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid-string-1",
      "message": "uuid-string",
      "author": {
        "id": "uuid-string",
        "email": "client@example.com",
        "first_name": "Jane",
        "last_name": "Client",
        "full_name": "Jane Client"
      },
      "author_name": "Jane Client",
      "content": "Looking forward to your response.",
      "is_internal": false,
      "created_at": "2025-11-19T15:00:00Z",
      "updated_at": "2025-11-19T15:00:00Z"
    },
    {
      "id": "uuid-string-2",
      "message": "uuid-string",
      "author": {
        "id": "uuid-string",
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "full_name": "Admin User"
      },
      "author_name": "Admin User",
      "content": "Thank you for reaching out...",
      "is_internal": false,
      "created_at": "2025-11-19T16:00:00Z",
      "updated_at": "2025-11-19T16:00:00Z"
    }
  ]
}
```

---

### Profile Management

#### 15. List Profiles

```http
GET /api/profiles/
```

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 10)
- `search` - Search in name, email, or headline
- `city` - Filter by city
- `state` - Filter by state
- `country` - Filter by country

**Response (200 OK):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "bcd91fdc-d398-42f5-87b3-f7699fd50eae",
      "full_name": "Julius Tetteh",
      "first_name": "Julius",
      "last_name": "Tetteh",
      "headline": "Full Stack Developer & Software Engineer",
      "email": "juliustetteh@gmail.com",
      "city": "Accra",
      "state": "Greater Accra Region",
      "country": "Ghana",
      "profile_picture_url": "http://localhost:8000/media/profiles/pictures/profile.jpg",
      "created_at": "2025-11-20T15:45:00Z"
    }
  ]
}
```

---

#### 16. Get Profile Details

```http
GET /api/profiles/{profile_id}/
```

**Response (200 OK):**
```json
{
  "id": "bcd91fdc-d398-42f5-87b3-f7699fd50eae",
  "first_name": "Julius",
  "last_name": "Tetteh",
  "full_name": "Julius Tetteh",
  "headline": "Full Stack Developer & Software Engineer",
  "summary": "Experienced software engineer specializing in web applications...",
  "email": "juliustetteh@gmail.com",
  "phone": "+233203344991",
  "city": "Accra",
  "state": "Greater Accra Region",
  "country": "Ghana",
  "profile_picture": "/media/profiles/pictures/profile.jpg",
  "profile_picture_url": "http://localhost:8000/media/profiles/pictures/profile.jpg",
  "cover_image": "/media/profiles/covers/cover.jpg",
  "cover_image_url": "http://localhost:8000/media/profiles/covers/cover.jpg",
  "social_links": [
    {
      "id": "social-link-uuid",
      "platform": "github",
      "platform_display": "GitHub",
      "url": "https://github.com/username",
      "display_name": "@username",
      "order": 0
    }
  ],
  "projects_count": 5,
  "experiences_count": 3,
  "education_count": 2,
  "skills_count": 15,
  "certifications_count": 4,
  "created_at": "2025-11-20T15:45:00Z",
  "updated_at": "2025-11-20T16:30:00Z"
}
```

---

#### 17. Create Profile (Admin/Editor Only)

```http
POST /api/profiles/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
first_name: Julius
last_name: Tetteh
headline: Full Stack Developer & Software Engineer
summary: Experienced software engineer...
email: juliustetteh@gmail.com
phone: +233203344991
city: Accra
state: Greater Accra Region
country: Ghana
profile_picture: (file)
cover_image: (file)
```

**Response (201 Created):**
```json
{
  "message": "Profile created successfully",
  "profile": {
    "id": "bcd91fdc-d398-42f5-87b3-f7699fd50eae",
    "first_name": "Julius",
    "last_name": "Tetteh",
    "headline": "Full Stack Developer & Software Engineer",
    "email": "juliustetteh@gmail.com",
    ...
  }
}
```

---

#### 18. Update Profile (Admin/Editor Only)

```http
PATCH /api/profiles/{profile_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "headline": "Senior Full Stack Developer",
  "city": "Kumasi"
}
```

**Response (200 OK):**
```json
{
  "message": "Profile updated successfully",
  "profile": { ... }
}
```

---

#### 19. Delete Profile (Admin/Editor Only)

```http
DELETE /api/profiles/{profile_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

---

#### 20. Get Profile by Email

```http
GET /api/profiles/by_email/?email=user@example.com
```

**Response (200 OK):**
```json
{
  "id": "profile-uuid",
  "first_name": "Julius",
  "last_name": "Tetteh",
  ...
}
```

---

#### 21. Get Profile Social Links

```http
GET /api/profiles/{profile_id}/social_links/
```

**Response (200 OK):**
```json
[
  {
    "id": "link-uuid",
    "platform": "github",
    "platform_display": "GitHub",
    "url": "https://github.com/username",
    "display_name": "@username",
    "order": 0
  },
  {
    "id": "link-uuid",
    "platform": "linkedin",
    "platform_display": "LinkedIn",
    "url": "https://linkedin.com/in/username",
    "display_name": "Julius Tetteh",
    "order": 1
  }
]
```

---

#### 22. Add Social Link to Profile (Admin/Editor Only)

```http
POST /api/profiles/{profile_id}/add_social_link/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "platform": "github",
  "url": "https://github.com/username",
  "display_name": "@username",
  "order": 0
}
```

**Available Platforms:**
- `github` - GitHub
- `linkedin` - LinkedIn
- `twitter` - Twitter
- `portfolio` - Portfolio
- `other` - Other

**Response (201 Created):**
```json
{
  "id": "link-uuid",
  "platform": "github",
  "url": "https://github.com/username",
  "display_name": "@username",
  "order": 0
}
```

---

#### 23. Delete Social Link (Admin/Editor Only)

```http
DELETE /api/profiles/{profile_id}/social_links/{link_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204 No Content):**
```json
{
  "message": "Social link deleted successfully"
}
```

---

### Projects Management

#### 24. List Projects

```http
GET /api/projects/
```

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 10)
- `profile` - Filter by profile ID
- `featured_only` - Filter featured projects only (`true`/`false`)
- `current_only` - Filter current projects only (`true`/`false`)
- `search` - Search in title, description, technologies, role
- `ordering` - Sort by field (options: `start_date`, `-start_date`, `created_at`, `-created_at`, `order`, `title`)

**Response (200 OK):**
```json
{
  "count": 15,
  "next": "http://localhost:8000/api/projects/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid-string",
      "title": "E-Commerce Platform",
      "description": "Full-stack e-commerce solution with React and Django",
      "role": "Full Stack Developer",
      "technologies": ["React", "Django", "PostgreSQL", "Redis", "AWS"],
      "technologies_count": 5,
      "start_date": "2024-01-15",
      "end_date": "2024-06-30",
      "current": false,
      "featured": true,
      "thumbnail": "http://localhost:8000/media/projects/thumbnail.jpg",
      "project_url": "https://example-ecommerce.com",
      "github_url": "https://github.com/username/ecommerce",
      "duration": "5 months",
      "created_at": "2025-01-20T10:00:00Z"
    }
  ]
}
```

---

#### 25. Get Project Details

```http
GET /api/projects/{project_id}/
```

**Response (200 OK):**
```json
{
  "id": "uuid-string",
  "profile": "profile-uuid",
  "profile_name": "John Doe",
  "title": "E-Commerce Platform",
  "description": "Full-stack e-commerce solution with React and Django",
  "long_description": "Developed a comprehensive e-commerce platform featuring user authentication, product management, shopping cart, payment integration, order tracking, and admin dashboard. The platform handles 10,000+ daily active users with 99.9% uptime.",
  "technologies": ["React", "Django", "PostgreSQL", "Redis", "AWS", "Stripe", "Docker"],
  "technologies_count": 7,
  "role": "Full Stack Developer & Team Lead",
  "team_size": 5,
  "start_date": "2024-01-15",
  "end_date": "2024-06-30",
  "current": false,
  "project_url": "https://example-ecommerce.com",
  "github_url": "https://github.com/username/ecommerce",
  "demo_url": "https://youtube.com/demo-video",
  "video": "http://localhost:8000/media/projects/videos/demo.mp4",
  "video_url": "http://localhost:8000/media/projects/videos/demo.mp4",
  "highlights": [
    "Reduced page load time by 60% through optimization",
    "Implemented real-time inventory management",
    "Integrated multiple payment gateways",
    "Built comprehensive admin dashboard"
  ],
  "challenges": "Main challenge was scaling the platform to handle Black Friday traffic spikes. Implemented Redis caching and database query optimization to handle 50x normal traffic.",
  "outcomes": "Platform processed $2M+ in transactions within first quarter. Achieved 4.8/5 user satisfaction rating.",
  "featured": true,
  "order": 1,
  "images": [
    {
      "id": "image-uuid-1",
      "image": "/media/projects/image1.jpg",
      "image_url": "http://localhost:8000/media/projects/image1.jpg",
      "caption": "Homepage with product showcase",
      "order": 0,
      "uploaded_at": "2025-01-20T10:30:00Z"
    },
    {
      "id": "image-uuid-2",
      "image": "/media/projects/image2.jpg",
      "image_url": "http://localhost:8000/media/projects/image2.jpg",
      "caption": "Admin dashboard analytics",
      "order": 1,
      "uploaded_at": "2025-01-20T10:31:00Z"
    }
  ],
  "duration": "5 months",
  "created_at": "2025-01-20T10:00:00Z",
  "updated_at": "2025-01-20T10:00:00Z"
}
```

---

#### 26. Create Project (Admin/Editor Only)

```http
POST /api/projects/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Required Role:** Super Admin or Editor

**Request Body (multipart/form-data):**
```json
{
  "profile": "profile-uuid",
  "title": "E-Commerce Platform",
  "description": "Full-stack e-commerce solution",
  "long_description": "Detailed project description...",
  "technologies": ["React", "Django", "PostgreSQL"],
  "role": "Full Stack Developer",
  "team_size": 5,
  "start_date": "2024-01-15",
  "end_date": "2024-06-30",
  "current": false,
  "project_url": "https://example.com",
  "github_url": "https://github.com/username/project",
  "demo_url": "https://youtube.com/demo",
  "highlights": [
    "Achievement 1",
    "Achievement 2"
  ],
  "challenges": "Challenges faced...",
  "outcomes": "Results achieved...",
  "featured": true,
  "order": 1,
  "images": [<file1>, <file2>],
  "video": <video-file>
}
```

**Notes:**
- `images` - Multiple image files (max 10MB each)
- `video` - Video file (max 100MB, formats: mp4, mov, avi, webm, mkv)
- `technologies` and `highlights` must be JSON arrays
- If `current` is `true`, `end_date` must be `null`
- If `current` is `false`, `end_date` is required

**Response (201 Created):**
```json
{
  "id": "uuid-string",
  "profile": "profile-uuid",
  "title": "E-Commerce Platform",
  ...
}
```

---

#### 20. Update Project

```http
PUT /api/projects/{project_id}/
PATCH /api/projects/{project_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Required Role:** Super Admin or Editor

**Request Body:** Same as Create Project (PATCH allows partial updates)

**Response (200 OK):**
```json
{
  "id": "uuid-string",
  "profile": "profile-uuid",
  "title": "Updated Project Title",
  ...
}
```

---

#### 28. Delete Project (Admin/Editor Only)

```http
DELETE /api/projects/{project_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Required Role:** Super Admin or Editor

**Response (204 No Content)**

---

#### 29. Get Featured Projects

```http
GET /api/projects/featured/
```

**Response (200 OK):**
```json
[
  {
    "id": "uuid-string",
    "title": "Featured Project 1",
    "description": "Short description",
    ...
  },
  {
    "id": "uuid-string",
    "title": "Featured Project 2",
    "description": "Short description",
    ...
  }
]
```

---

#### 30. Get Projects by Profile

```http
GET /api/projects/by_profile/{profile_id}/
```

**Query Parameters:**
- `page` - Page number
- `page_size` - Items per page

**Response (200 OK):**
```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [...]
}
```

---

#### 31. Upload Project Images (Admin/Editor Only)

```http
POST /api/projects/{project_id}/upload_images/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Required Role:** Super Admin or Editor

**Request Body:**
```
images: [<file1>, <file2>, <file3>]
caption_0: "Caption for first image"
caption_1: "Caption for second image"
caption_2: "Caption for third image"
```

**Response (201 Created):**
```json
[
  {
    "id": "image-uuid-1",
    "image": "/media/projects/image1.jpg",
    "image_url": "http://localhost:8000/media/projects/image1.jpg",
    "caption": "Caption for first image",
    "order": 3,
    "uploaded_at": "2025-01-20T14:00:00Z"
  },
  {
    "id": "image-uuid-2",
    "image": "/media/projects/image2.jpg",
    "image_url": "http://localhost:8000/media/projects/image2.jpg",
    "caption": "Caption for second image",
    "order": 4,
    "uploaded_at": "2025-01-20T14:00:00Z"
  }
]
```

---

#### 32. Delete Project Image (Admin/Editor Only)

```http
DELETE /api/projects/{project_id}/delete_image/{image_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Required Role:** Super Admin or Editor

**Response (204 No Content)**

---

#### 26. Reorder Project Images

```http
POST /api/projects/{project_id}/reorder_images/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Required Role:** Super Admin or Editor

**Request Body:**
```json
{
  "image_order": [
    "image-uuid-3",
    "image-uuid-1",
    "image-uuid-2"
  ]
}
```

**Response (200 OK):**
```json
{
  "id": "project-uuid",
  "images": [
    {
      "id": "image-uuid-3",
      "order": 0,
      ...
    },
    {
      "id": "image-uuid-1",
      "order": 1,
      ...
    },
    {
      "id": "image-uuid-2",
      "order": 2,
      ...
    }
  ],
  ...
}
```

---

### User Activity Logs

#### 27. List User Activities

```http
GET /api/auth/activities/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters (Admin Only):**
- `user_id` - Filter by user ID
- `action` - Filter by action type
- `page` - Page number

**Response (200 OK):**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/auth/activities/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid-string",
      "user_email": "user@example.com",
      "action": "USER_LOGIN",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "details": {},
      "timestamp": "2025-11-19T14:00:00Z"
    },
    {
      "id": "uuid-string",
      "user_email": "user@example.com",
      "action": "MESSAGE_SENT",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "details": {
        "message_id": "uuid-string",
        "type": "proposal"
      },
      "timestamp": "2025-11-19T14:20:00Z"
    }
  ]
}
```

**Common Activity Actions:**
- `USER_REGISTERED`
- `USER_LOGIN`
- `PROFILE_UPDATED`
- `PASSWORD_CHANGED`
- `MFA_SETUP_INITIATED`
- `MFA_ENABLED`
- `MFA_DISABLED`
- `MESSAGE_SENT`
- `MESSAGE_STATUS_UPDATED`
- `MESSAGE_RESPONDED`

---

## Request/Response Formats

### Data Models

#### User Object

```typescript
interface User {
  id: string;                    // UUID
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;             // Read-only
  phone: string | null;
  role: 'super_admin' | 'editor' | 'viewer';
  is_verified: boolean;
  is_active: boolean;
  mfa_enabled: boolean;
  created_at: string;            // ISO 8601 datetime
  updated_at: string;            // ISO 8601 datetime
}
```

#### Contact Message Object

```typescript
interface ContactMessage {
  id: string;                    // UUID
  sender: User;
  sender_name: string;           // Read-only
  message_type: 'general' | 'proposal' | 'job' | 'collaboration' | 'feedback' | 'other';
  subject: string;
  message: string;
  project_budget: string | null; // Decimal as string
  project_timeline: string | null;
  attachments: string[];         // Array of URLs
  status: 'new' | 'read' | 'in_progress' | 'responded' | 'archived';
  priority: boolean;
  admin_notes: string | null;
  responded_by: User | null;
  replied_by_name: string | null;
  responded_at: string | null;   // ISO 8601 datetime
  reply_count: number;           // Read-only
  created_at: string;            // ISO 8601 datetime
  updated_at: string;            // ISO 8601 datetime
}
```

#### Message Reply Object

```typescript
interface MessageReply {
  id: string;                    // UUID
  message: string;               // Message UUID
  author: User;
  author_name: string;           // Read-only
  content: string;
  is_internal: boolean;
  created_at: string;            // ISO 8601 datetime
  updated_at: string;            // ISO 8601 datetime
}
```

#### Project Object

```typescript
interface Project {
  id: string;                    // UUID
  profile: string;               // Profile UUID
  profile_name: string;          // Read-only
  title: string;
  description: string;           // Short description
  long_description: string | null;
  technologies: string[];        // Array of technology names
  technologies_count: number;    // Read-only
  role: string;
  team_size: number | null;
  start_date: string;            // YYYY-MM-DD
  end_date: string | null;       // YYYY-MM-DD or null if current
  current: boolean;
  project_url: string | null;
  github_url: string | null;
  demo_url: string | null;
  video: string | null;          // File path
  video_url: string | null;      // Full URL (read-only)
  highlights: string[];          // Array of key achievements
  challenges: string | null;
  outcomes: string | null;
  featured: boolean;
  order: number;
  images: ProjectImage[];        // Read-only
  duration: string;              // Read-only, e.g. "5 months"
  created_at: string;            // ISO 8601 datetime
  updated_at: string;            // ISO 8601 datetime
}
```

#### Project Image Object

```typescript
interface ProjectImage {
  id: string;                    // UUID
  image: string;                 // File path
  image_url: string;             // Full URL (read-only)
  caption: string | null;
  order: number;
  uploaded_at: string;           // ISO 8601 datetime
}
```

#### Pagination Response

```typescript
interface PaginatedResponse<T> {
  count: number;                 // Total count
  next: string | null;           // Next page URL
  previous: string | null;       // Previous page URL
  results: T[];                  // Array of items
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Error Response Format

```json
{
  "detail": "Error message",
  "field_name": ["Field-specific error message"]
}
```

**Examples:**

**Validation Error (400):**
```json
{
  "email": ["This field is required."],
  "password": ["This password is too short."]
}
```

**Authentication Error (401):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Permission Error (403):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Not Found Error (404):**
```json
{
  "detail": "Not found."
}
```

**Rate Limit Error (429):**
```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

---

## Code Examples

### JavaScript/TypeScript (Fetch API)

#### Setup API Client

```javascript
// api.js
const API_BASE_URL = 'http://localhost:8000/api';

// Store tokens in memory or secure storage
let accessToken = null;
let refreshToken = null;

export const setTokens = (access, refresh) => {
  accessToken = access;
  refreshToken = refresh;
  // Store in localStorage or sessionStorage (be aware of XSS risks)
  localStorage.setItem('accessToken', access);
  localStorage.setItem('refreshToken', refresh);
};

export const getAccessToken = () => {
  if (!accessToken) {
    accessToken = localStorage.getItem('accessToken');
  }
  return accessToken;
};

export const getRefreshToken = () => {
  if (!refreshToken) {
    refreshToken = localStorage.getItem('refreshToken');
  }
  return refreshToken;
};

export const clearTokens = () => {
  accessToken = null;
  refreshToken = null;
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
};

// Refresh token function
export const refreshAccessToken = async () => {
  const refresh = getRefreshToken();
  if (!refresh) {
    throw new Error('No refresh token available');
  }

  const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh }),
  });

  if (!response.ok) {
    clearTokens();
    throw new Error('Token refresh failed');
  }

  const data = await response.json();
  setTokens(data.access, data.refresh);
  return data.access;
};

// API request wrapper with auto token refresh
export const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = getAccessToken();

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  let response = await fetch(url, {
    ...options,
    headers,
  });

  // If unauthorized and we have a refresh token, try refreshing
  if (response.status === 401 && getRefreshToken()) {
    try {
      const newToken = await refreshAccessToken();
      headers['Authorization'] = `Bearer ${newToken}`;
      
      // Retry the original request
      response = await fetch(url, {
        ...options,
        headers,
      });
    } catch (error) {
      // Refresh failed, redirect to login
      window.location.href = '/login';
      throw error;
    }
  }

  if (!response.ok) {
    const error = await response.json();
    throw error;
  }

  return response.json();
};
```

#### Register User

```javascript
import { apiRequest, setTokens } from './api';

async function registerUser(userData) {
  try {
    const data = await apiRequest('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(userData),
    });

    console.log('Registration successful:', data.message);
    console.log('User:', data.user);

    // Store tokens
    setTokens(data.tokens.access, data.tokens.refresh);

    return data;
  } catch (error) {
    console.error('Registration failed:', error);
    throw error;
  }
}

// Usage
registerUser({
  email: 'user@example.com',
  password: 'SecurePassword123!',
  password_confirm: 'SecurePassword123!',
  first_name: 'John',
  last_name: 'Doe',
  phone: '+1234567890',
});
```

#### Login User

```javascript
import { apiRequest, setTokens } from './api';

async function loginUser(email, password, mfaToken = null) {
  try {
    const payload = { email, password };
    if (mfaToken) {
      payload.mfa_token = mfaToken;
    }

    const data = await apiRequest('/auth/login/', {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    console.log('Login successful:', data.message);
    console.log('User:', data.user);

    // Store tokens
    setTokens(data.tokens.access, data.tokens.refresh);

    return data;
  } catch (error) {
    if (error.mfa_required) {
      // Prompt user for MFA token
      console.log('MFA token required');
      // Show MFA input form
    } else {
      console.error('Login failed:', error);
    }
    throw error;
  }
}

// Usage
loginUser('user@example.com', 'SecurePassword123!');
```

#### Get User Profile

```javascript
import { apiRequest } from './api';

async function getUserProfile() {
  try {
    const data = await apiRequest('/auth/profile/');
    console.log('User profile:', data);
    return data;
  } catch (error) {
    console.error('Failed to fetch profile:', error);
    throw error;
  }
}

// Usage
getUserProfile();
```

#### Create Contact Message

```javascript
import { apiRequest } from './api';

async function sendContactMessage(messageData) {
  try {
    const data = await apiRequest('/contacts/', {
      method: 'POST',
      body: JSON.stringify(messageData),
    });

    console.log('Message sent:', data);
    return data;
  } catch (error) {
    console.error('Failed to send message:', error);
    throw error;
  }
}

// Usage
sendContactMessage({
  message_type: 'proposal',
  subject: 'E-commerce Platform Development',
  message: 'We need a full-stack e-commerce solution...',
  project_budget: 15000.00,
  project_timeline: '3-4 months',
});
```

#### List Contact Messages with Filters

```javascript
import { apiRequest } from './api';

async function getContactMessages(filters = {}) {
  try {
    const params = new URLSearchParams(filters);
    const data = await apiRequest(`/contacts/?${params}`);
    
    console.log(`Total messages: ${data.count}`);
    console.log('Messages:', data.results);
    
    return data;
  } catch (error) {
    console.error('Failed to fetch messages:', error);
    throw error;
  }
}

// Usage
getContactMessages({
  status: 'new',
  priority: 'true',
  page: 1,
});
```

---

### React Hooks Example

```javascript
// useAuth.js
import { useState, useEffect, createContext, useContext } from 'react';
import { apiRequest, setTokens, clearTokens, getAccessToken } from './api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on mount
    const initAuth = async () => {
      const token = getAccessToken();
      if (token) {
        try {
          const userData = await apiRequest('/auth/profile/');
          setUser(userData);
        } catch (error) {
          console.error('Failed to fetch user:', error);
          clearTokens();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password, mfaToken = null) => {
    const payload = { email, password };
    if (mfaToken) payload.mfa_token = mfaToken;

    const data = await apiRequest('/auth/login/', {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    setTokens(data.tokens.access, data.tokens.refresh);
    setUser(data.user);
    return data;
  };

  const register = async (userData) => {
    const data = await apiRequest('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(userData),
    });

    setTokens(data.tokens.access, data.tokens.refresh);
    setUser(data.user);
    return data;
  };

  const logout = () => {
    clearTokens();
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'super_admin',
    isEditor: user?.role === 'editor' || user?.role === 'super_admin',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

```javascript
// ContactForm.jsx
import { useState } from 'react';
import { apiRequest } from './api';
import { useAuth } from './useAuth';

export const ContactForm = () => {
  const { isAuthenticated } = useAuth();
  const [formData, setFormData] = useState({
    message_type: 'general',
    subject: '',
    message: '',
    project_budget: '',
    project_timeline: '',
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!isAuthenticated) {
      setError('Please login to send a message');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload = {
        message_type: formData.message_type,
        subject: formData.subject,
        message: formData.message,
      };

      if (formData.message_type === 'proposal') {
        payload.project_budget = parseFloat(formData.project_budget);
        payload.project_timeline = formData.project_timeline;
      }

      await apiRequest('/contacts/', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      setSuccess(true);
      setFormData({
        message_type: 'general',
        subject: '',
        message: '',
        project_budget: '',
        project_timeline: '',
      });
    } catch (err) {
      setError(err.detail || 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {success && <div className="alert success">Message sent successfully!</div>}
      {error && <div className="alert error">{error}</div>}

      <select
        value={formData.message_type}
        onChange={(e) => setFormData({ ...formData, message_type: e.target.value })}
      >
        <option value="general">General Inquiry</option>
        <option value="proposal">Project Proposal</option>
        <option value="job">Job Opportunity</option>
        <option value="collaboration">Collaboration</option>
        <option value="feedback">Feedback</option>
        <option value="other">Other</option>
      </select>

      <input
        type="text"
        placeholder="Subject"
        value={formData.subject}
        onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
        required
      />

      <textarea
        placeholder="Message"
        value={formData.message}
        onChange={(e) => setFormData({ ...formData, message: e.target.value })}
        required
      />

      {formData.message_type === 'proposal' && (
        <>
          <input
            type="number"
            placeholder="Budget ($)"
            value={formData.project_budget}
            onChange={(e) => setFormData({ ...formData, project_budget: e.target.value })}
            required
          />
          <input
            type="text"
            placeholder="Timeline"
            value={formData.project_timeline}
            onChange={(e) => setFormData({ ...formData, project_timeline: e.target.value })}
          />
        </>
      )}

      <button type="submit" disabled={loading}>
        {loading ? 'Sending...' : 'Send Message'}
      </button>
    </form>
  );
};
```

---

### Axios Example

```javascript
// axiosInstance.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access, refresh } = response.data;
        localStorage.setItem('accessToken', access);
        localStorage.setItem('refreshToken', refresh);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default axiosInstance;
```

```javascript
// Using axios
import axiosInstance from './axiosInstance';

// Register
const registerUser = async (userData) => {
  try {
    const response = await axiosInstance.post('/auth/register/', userData);
    localStorage.setItem('accessToken', response.data.tokens.access);
    localStorage.setItem('refreshToken', response.data.tokens.refresh);
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};

// Get messages
const getMessages = async (filters = {}) => {
  try {
    const response = await axiosInstance.get('/contacts/', { params: filters });
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};
```

---

### Projects Management Examples

```javascript
// projectService.js
import { apiRequest } from './api';

/**
 * Fetch all projects with filters
 */
export const getProjects = async (filters = {}) => {
  try {
    const params = new URLSearchParams();
    
    if (filters.profile) params.append('profile', filters.profile);
    if (filters.featured_only) params.append('featured_only', 'true');
    if (filters.current_only) params.append('current_only', 'true');
    if (filters.search) params.append('search', filters.search);
    if (filters.ordering) params.append('ordering', filters.ordering);
    if (filters.page) params.append('page', filters.page);
    
    const response = await axiosInstance.get(`/projects/?${params}`);
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};

/**
 * Get single project details
 */
export const getProject = async (projectId) => {
  try {
    const response = await axiosInstance.get(`/projects/${projectId}/`);
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};

/**
 * Get featured projects only
 */
export const getFeaturedProjects = async () => {
  try {
    const response = await axiosInstance.get('/projects/featured/');
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};

/**
 * Create new project with images and video
 */
export const createProject = async (projectData, images = [], video = null) => {
  try {
    const formData = new FormData();
    
    // Add project data
    Object.keys(projectData).forEach(key => {
      if (projectData[key] !== null && projectData[key] !== undefined) {
        if (Array.isArray(projectData[key])) {
          formData.append(key, JSON.stringify(projectData[key]));
        } else {
          formData.append(key, projectData[key]);
        }
      }
    });
    
    // Add images
    images.forEach(image => {
      formData.append('images', image);
    });
    
    // Add video
    if (video) {
      formData.append('video', video);
    }
    
    const response = await axiosInstance.post('/projects/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};

/**
 * Update existing project
 */
export const updateProject = async (projectId, projectData, video = null) => {
  try {
    const formData = new FormData();
    
    Object.keys(projectData).forEach(key => {
      if (projectData[key] !== null && projectData[key] !== undefined) {
        if (Array.isArray(projectData[key])) {
          formData.append(key, JSON.stringify(projectData[key]));
        } else {
          formData.append(key, projectData[key]);
        }
      }
    });
    
    if (video) {
      formData.append('video', video);
    }
    
    const response = await axiosInstance.patch(`/projects/${projectId}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};

/**
 * Delete project
 */
export const deleteProject = async (projectId) => {
  try {
    await axiosInstance.delete(`/projects/${projectId}/`);
  } catch (error) {
    throw error.response.data;
  }
};

/**
 * Upload additional images to project
 */
export const uploadProjectImages = async (projectId, images, captions = []) => {
  try {
    const formData = new FormData();
    
    images.forEach((image, index) => {
      formData.append('images', image);
      if (captions[index]) {
        formData.append(`caption_${index}`, captions[index]);
      }
    });
    
    const response = await axiosInstance.post(
      `/projects/${projectId}/upload_images/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};

/**
 * Delete project image
 */
export const deleteProjectImage = async (projectId, imageId) => {
  try {
    await axiosInstance.delete(`/projects/${projectId}/delete_image/${imageId}/`);
  } catch (error) {
    throw error.response.data;
  }
};

/**
 * Reorder project images
 */
export const reorderProjectImages = async (projectId, imageOrder) => {
  try {
    const response = await axiosInstance.post(
      `/projects/${projectId}/reorder_images/`,
      { image_order: imageOrder }
    );
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};
```

```javascript
// ProjectForm.jsx - React component for creating/editing projects
import { useState, useEffect } from 'react';
import { useAuth } from './useAuth';
import { createProject, updateProject, getProject } from './projectService';

export const ProjectForm = ({ projectId = null, onSuccess }) => {
  const { user, isEditor } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    profile: '',
    title: '',
    description: '',
    long_description: '',
    technologies: [],
    role: '',
    team_size: '',
    start_date: '',
    end_date: '',
    current: false,
    project_url: '',
    github_url: '',
    demo_url: '',
    highlights: [],
    challenges: '',
    outcomes: '',
    featured: false,
    order: 0,
  });
  const [images, setImages] = useState([]);
  const [video, setVideo] = useState(null);
  const [techInput, setTechInput] = useState('');
  const [highlightInput, setHighlightInput] = useState('');

  useEffect(() => {
    if (projectId) {
      loadProject();
    }
  }, [projectId]);

  const loadProject = async () => {
    try {
      const data = await getProject(projectId);
      setFormData({
        profile: data.profile,
        title: data.title,
        description: data.description,
        long_description: data.long_description || '',
        technologies: data.technologies || [],
        role: data.role,
        team_size: data.team_size || '',
        start_date: data.start_date,
        end_date: data.end_date || '',
        current: data.current,
        project_url: data.project_url || '',
        github_url: data.github_url || '',
        demo_url: data.demo_url || '',
        highlights: data.highlights || [],
        challenges: data.challenges || '',
        outcomes: data.outcomes || '',
        featured: data.featured,
        order: data.order,
      });
    } catch (err) {
      setError('Failed to load project');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!isEditor) {
      setError('You must be an editor to manage projects');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const projectData = {
        ...formData,
        team_size: formData.team_size ? parseInt(formData.team_size) : null,
        end_date: formData.current ? null : formData.end_date,
      };

      if (projectId) {
        await updateProject(projectId, projectData, video);
      } else {
        await createProject(projectData, images, video);
      }

      if (onSuccess) onSuccess();
    } catch (err) {
      setError(err.message || 'Failed to save project');
    } finally {
      setLoading(false);
    }
  };

  const addTechnology = () => {
    if (techInput.trim()) {
      setFormData({
        ...formData,
        technologies: [...formData.technologies, techInput.trim()],
      });
      setTechInput('');
    }
  };

  const removeTechnology = (index) => {
    setFormData({
      ...formData,
      technologies: formData.technologies.filter((_, i) => i !== index),
    });
  };

  const addHighlight = () => {
    if (highlightInput.trim()) {
      setFormData({
        ...formData,
        highlights: [...formData.highlights, highlightInput.trim()],
      });
      setHighlightInput('');
    }
  };

  const removeHighlight = (index) => {
    setFormData({
      ...formData,
      highlights: formData.highlights.filter((_, i) => i !== index),
    });
  };

  const handleImageChange = (e) => {
    const files = Array.from(e.target.files);
    setImages(files);
  };

  const handleVideoChange = (e) => {
    setVideo(e.target.files[0]);
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}

      <input
        type="text"
        placeholder="Project Title"
        value={formData.title}
        onChange={(e) => setFormData({ ...formData, title: e.target.value })}
        required
      />

      <textarea
        placeholder="Short Description"
        value={formData.description}
        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
        required
      />

      <textarea
        placeholder="Long Description (optional)"
        value={formData.long_description}
        onChange={(e) => setFormData({ ...formData, long_description: e.target.value })}
      />

      <div>
        <input
          type="text"
          placeholder="Add Technology"
          value={techInput}
          onChange={(e) => setTechInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTechnology())}
        />
        <button type="button" onClick={addTechnology}>Add</button>
        <div>
          {formData.technologies.map((tech, index) => (
            <span key={index}>
              {tech}
              <button type="button" onClick={() => removeTechnology(index)}>×</button>
            </span>
          ))}
        </div>
      </div>

      <input
        type="text"
        placeholder="Your Role"
        value={formData.role}
        onChange={(e) => setFormData({ ...formData, role: e.target.value })}
        required
      />

      <input
        type="number"
        placeholder="Team Size (optional)"
        value={formData.team_size}
        onChange={(e) => setFormData({ ...formData, team_size: e.target.value })}
      />

      <input
        type="date"
        placeholder="Start Date"
        value={formData.start_date}
        onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
        required
      />

      <label>
        <input
          type="checkbox"
          checked={formData.current}
          onChange={(e) => setFormData({ ...formData, current: e.target.checked })}
        />
        Currently working on this project
      </label>

      {!formData.current && (
        <input
          type="date"
          placeholder="End Date"
          value={formData.end_date}
          onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
          required
        />
      )}

      <input
        type="url"
        placeholder="Project URL (optional)"
        value={formData.project_url}
        onChange={(e) => setFormData({ ...formData, project_url: e.target.value })}
      />

      <input
        type="url"
        placeholder="GitHub URL (optional)"
        value={formData.github_url}
        onChange={(e) => setFormData({ ...formData, github_url: e.target.value })}
      />

      <div>
        <input
          type="text"
          placeholder="Add Highlight"
          value={highlightInput}
          onChange={(e) => setHighlightInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addHighlight())}
        />
        <button type="button" onClick={addHighlight}>Add</button>
        <ul>
          {formData.highlights.map((highlight, index) => (
            <li key={index}>
              {highlight}
              <button type="button" onClick={() => removeHighlight(index)}>×</button>
            </li>
          ))}
        </ul>
      </div>

      <textarea
        placeholder="Challenges (optional)"
        value={formData.challenges}
        onChange={(e) => setFormData({ ...formData, challenges: e.target.value })}
      />

      <textarea
        placeholder="Outcomes (optional)"
        value={formData.outcomes}
        onChange={(e) => setFormData({ ...formData, outcomes: e.target.value })}
      />

      <div>
        <label>Images (max 10MB each)</label>
        <input
          type="file"
          accept="image/*"
          multiple
          onChange={handleImageChange}
        />
      </div>

      <div>
        <label>Video (max 100MB, mp4/mov/avi/webm/mkv)</label>
        <input
          type="file"
          accept="video/*"
          onChange={handleVideoChange}
        />
      </div>

      <label>
        <input
          type="checkbox"
          checked={formData.featured}
          onChange={(e) => setFormData({ ...formData, featured: e.target.checked })}
        />
        Featured Project
      </label>

      <button type="submit" disabled={loading}>
        {loading ? 'Saving...' : projectId ? 'Update Project' : 'Create Project'}
      </button>
    </form>
  );
};
```

```javascript
// ProjectList.jsx - Display projects with filtering
import { useState, useEffect } from 'react';
import { getProjects, getFeaturedProjects } from './projectService';

export const ProjectList = ({ profileId = null, featuredOnly = false }) => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    ordering: '-start_date',
    page: 1,
  });

  useEffect(() => {
    loadProjects();
  }, [filters, profileId, featuredOnly]);

  const loadProjects = async () => {
    setLoading(true);
    try {
      let data;
      if (featuredOnly) {
        data = await getFeaturedProjects();
        setProjects(Array.isArray(data) ? data : data.results || []);
      } else {
        const filterParams = { ...filters };
        if (profileId) filterParams.profile = profileId;
        data = await getProjects(filterParams);
        setProjects(data.results || []);
      }
    } catch (err) {
      setError('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading projects...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <div>
        <input
          type="text"
          placeholder="Search projects..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
        />
        <select
          value={filters.ordering}
          onChange={(e) => setFilters({ ...filters, ordering: e.target.value })}
        >
          <option value="-start_date">Newest First</option>
          <option value="start_date">Oldest First</option>
          <option value="title">Title A-Z</option>
          <option value="-title">Title Z-A</option>
        </select>
      </div>

      <div className="projects-grid">
        {projects.map(project => (
          <div key={project.id} className="project-card">
            {project.thumbnail && (
              <img src={project.thumbnail} alt={project.title} />
            )}
            <h3>{project.title}</h3>
            <p>{project.description}</p>
            <div className="project-meta">
              <span>{project.role}</span>
              <span>{project.duration}</span>
              {project.featured && <span className="badge">Featured</span>}
            </div>
            <div className="technologies">
              {project.technologies.slice(0, 5).map((tech, idx) => (
                <span key={idx} className="tech-badge">{tech}</span>
              ))}
              {project.technologies.length > 5 && (
                <span>+{project.technologies.length - 5} more</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

## Best Practices

### 1. Token Management

- **Store tokens securely**: Use httpOnly cookies or secure storage
- **Refresh tokens proactively**: Refresh before expiration
- **Clear tokens on logout**: Always clear stored tokens
- **Handle token expiration**: Implement automatic refresh logic

### 2. Error Handling

```javascript
try {
  const data = await apiRequest('/contacts/');
  // Handle success
} catch (error) {
  if (error.detail) {
    // Single error message
    showError(error.detail);
  } else {
    // Field-specific errors
    Object.entries(error).forEach(([field, messages]) => {
      showFieldError(field, messages[0]);
    });
  }
}
```

### 3. Rate Limiting

- Auth endpoints: 10 requests/hour
- General API: 100 requests/hour (anonymous), 1000/hour (authenticated)
- Implement retry logic with exponential backoff

### 4. Pagination

```javascript
const fetchAllPages = async (endpoint) => {
  let allResults = [];
  let nextUrl = `${endpoint}?page=1`;

  while (nextUrl) {
    const data = await apiRequest(nextUrl);
    allResults = [...allResults, ...data.results];
    nextUrl = data.next;
  }

  return allResults;
};
```

### 5. File Uploads

For endpoints that accept file uploads (profile pictures, attachments):

```javascript
const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/upload/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getAccessToken()}`,
      // Don't set Content-Type, browser will set it with boundary
    },
    body: formData,
  });

  return response.json();
};
```

### 6. Search and Filters

```javascript
const buildSearchParams = (filters) => {
  const params = new URLSearchParams();
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      params.append(key, value);
    }
  });
  
  return params.toString();
};

// Usage
const filters = {
  status: 'new',
  search: 'project',
  page: 1,
};

const queryString = buildSearchParams(filters);
const data = await apiRequest(`/contacts/?${queryString}`);
```

### 7. TypeScript Types

```typescript
// types.ts
export type UserRole = 'super_admin' | 'editor' | 'viewer';
export type MessageType = 'general' | 'proposal' | 'job' | 'collaboration' | 'feedback' | 'other';
export type MessageStatus = 'new' | 'read' | 'in_progress' | 'responded' | 'archived';

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone: string | null;
  role: UserRole;
  is_verified: boolean;
  is_active: boolean;
  mfa_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
  mfa_token?: string;
}

export interface AuthResponse {
  message: string;
  user: User;
  tokens: {
    access: string;
    refresh: string;
  };
}

export interface ContactMessage {
  id: string;
  sender: User;
  sender_name: string;
  message_type: MessageType;
  subject: string;
  message: string;
  project_budget: string | null;
  project_timeline: string | null;
  attachments: string[];
  status: MessageStatus;
  priority: boolean;
  admin_notes: string | null;
  responded_by: User | null;
  replied_by_name: string | null;
  responded_at: string | null;
  reply_count: number;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
```

---

## Testing API Endpoints

### Using cURL

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "password_confirm": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'

# Get profile (replace TOKEN)
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Create contact message
curl -X POST http://localhost:8000/api/contacts/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "general",
    "subject": "Test Message",
    "message": "This is a test message"
  }'
```

### Using Postman

1. Import OpenAPI schema from: `http://localhost:8000/api/schema/`
2. Set up environment variables:
   - `base_url`: `http://localhost:8000/api`
   - `access_token`: (will be set after login)
3. Create a pre-request script for auto token refresh

---

## Support & Documentation

- **Interactive API Docs**: http://localhost:8000/api/docs/ (Swagger UI)
- **API Schema**: http://localhost:8000/api/schema/
- **Alternative Docs**: http://localhost:8000/api/redoc/ (ReDoc)

For issues or questions, please contact the backend team or refer to the main README.md.

---

**Last Updated:** November 19, 2025  
**API Version:** 1.0.0
