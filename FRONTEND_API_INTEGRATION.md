# Portfolio API - Frontend Integration Guide

> **Last Updated:** November 21, 2025  
> **API Version:** 1.0  
> **Base URL Production:** `https://profileapi.alphalogiquetechnologies.com`  
> **Base URL Development:** `http://localhost:8000`

---

## 🚨 IMPORTANT CHANGES - READ FIRST

### What Changed (November 2025)

**OLD BEHAVIOR (REMOVED):**
- ❌ Profiles were auto-created for every user on login
- ❌ Login returned `profile`, `profile_status`, `requires_profile_update`
- ❌ Frontend had to check if profile was complete
- ❌ Endpoints like `/api/auth/my-portfolio-profile/` existed

**NEW BEHAVIOR (CURRENT):**
- ✅ **Profile = Site Owner Only** (manually created in Django admin)
- ✅ **Visitors = Just authenticate** (no profile created)
- ✅ Login returns: `user` + `tokens` only
- ✅ Profile endpoints are **public read-only** for portfolio display
- ✅ No profile completion flow needed

---

## 📋 Table of Contents

1. [Authentication Endpoints](#authentication-endpoints)
2. [Portfolio Profile Endpoints](#portfolio-profile-endpoints)
3. [Projects Endpoints](#projects-endpoints)
4. [Experience Endpoints](#experience-endpoints)
5. [Education Endpoints](#education-endpoints)
6. [Skills Endpoints](#skills-endpoints)
7. [Certifications Endpoints](#certifications-endpoints)
8. [Contact Form Endpoint](#contact-form-endpoint)
9. [Error Response Structure](#error-response-structure)
10. [TypeScript Types](#typescript-types)
11. [Example Integration Code](#example-integration-code)

---

## Authentication Endpoints

### 1. Register New User

**Endpoint:** `POST /api/auth/register/`  
**Authentication:** None (Public)  
**Purpose:** Allow visitors to create an account so they can contact you or comment

**Request Body:**
```json
{
  "email": "visitor@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+233123456789"
}
```

**Field Requirements:**
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `email` | string | ✅ Yes | Must be unique, valid email format |
| `password` | string | ✅ Yes | Min 8 chars, must pass Django validation |
| `password_confirm` | string | ✅ Yes | Must match `password` |
| `first_name` | string | ✅ Yes | Max 150 chars |
| `last_name` | string | ✅ Yes | Max 150 chars |
| `phone` | string | ❌ No | Format: `+[country code][number]` |

**Success Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "visitor@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone": "+233123456789",
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
// 400 - Validation Error
{
  "email": ["User with this email already exists."],
  "password": ["This password is too common."],
  "password_confirm": ["Password fields didn't match."]
}

// 429 - Rate Limit
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

---

### 2. Login

**Endpoint:** `POST /api/auth/login/`  
**Authentication:** None (Public)  
**Purpose:** Authenticate user and get access tokens

**Request Body:**
```json
{
  "email": "visitor@example.com",
  "password": "SecurePass123!",
  "mfa_token": "123456"
}
```

**Field Requirements:**
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `email` | string | ✅ Yes | User's email address |
| `password` | string | ✅ Yes | User's password |
| `mfa_token` | string | ❌ Conditional | Required only if user has MFA enabled (6 digits) |

**Success Response (200):**
```json
{
  "message": "Login successful",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "visitor@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone": "+233123456789",
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

### 3. Refresh Access Token

**Endpoint:** `POST /api/auth/token/refresh/`  
**Authentication:** None (requires refresh token)  
**Purpose:** Get new access token when current one expires

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Response (401):**
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

---

### 4. Get Current User Profile

**Endpoint:** `GET /api/auth/profile/`  
**Authentication:** Bearer Token Required  
**Purpose:** Get authenticated user's account details (NOT portfolio profile)

**Request Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Success Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "visitor@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "phone": "+233123456789",
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

**Endpoint:** `PATCH /api/auth/profile/`  
**Authentication:** Bearer Token Required  
**Purpose:** Update user's account information (name, phone)

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+233987654321"
}
```

**Success Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "visitor@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "full_name": "Jane Smith",
  "phone": "+233987654321",
  "role": "viewer",
  "is_verified": false,
  "is_active": true,
  "mfa_enabled": false,
  "created_at": "2025-11-21T10:30:00Z",
  "updated_at": "2025-11-21T10:35:00Z"
}
```

---

## Portfolio Profile Endpoints

> **NOTE:** These endpoints show the site owner's portfolio information. Most users will NOT have a portfolio profile—only the site owner does.

### 6. List All Portfolio Profiles

**Endpoint:** `GET /api/profiles/`  
**Authentication:** None (Public read)  
**Purpose:** Get list of portfolio profiles (typically just one—the site owner)

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `search` | string | No | Search in headline, summary, or location |
| `city` | string | No | Filter by city |
| `state` | string | No | Filter by state/region |
| `country` | string | No | Filter by country |

**Example Request:**
```
GET /api/profiles/?search=developer
```

**Success Response (200):**
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

### 7. Get Portfolio Profile Details

**Endpoint:** `GET /api/profiles/{profile_id}/`  
**Authentication:** None (Public read)  
**Purpose:** Get full details of a specific portfolio profile

**Example Request:**
```
GET /api/profiles/123e4567-e89b-12d3-a456-426614174000/
```

**Success Response (200):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "full_name": "TeeJay Developer",
  "email": "teejay@example.com",
  "phone": "+233501234567",
  "headline": "Full Stack Developer & Cloud Architect",
  "summary": "Passionate software engineer with 8+ years of experience building scalable web applications and cloud infrastructure. Specialized in Django, React, AWS, and microservices architecture.",
  "city": "Accra",
  "state": "Greater Accra",
  "country": "Ghana",
  "profile_picture": "profiles/pictures/teejay.jpg",
  "profile_picture_url": "https://profileapi.alphalogiquetechnologies.com/media/profiles/pictures/teejay.jpg",
  "cover_image": "profiles/covers/teejay-cover.jpg",
  "cover_image_url": "https://profileapi.alphalogiquetechnologies.com/media/profiles/covers/teejay-cover.jpg",
  "social_links": [
    {
      "id": "789e4567-e89b-12d3-a456-426614174001",
      "platform": "github",
      "platform_display": "GitHub",
      "url": "https://github.com/teejay",
      "display_name": "TeeJay on GitHub",
      "order": 1
    },
    {
      "id": "789e4567-e89b-12d3-a456-426614174002",
      "platform": "linkedin",
      "platform_display": "LinkedIn",
      "url": "https://linkedin.com/in/teejay",
      "display_name": "Connect on LinkedIn",
      "order": 2
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

**Error Response (404):**
```json
{
  "detail": "Not found."
}
```

---

### 8. Get Profile Social Links

**Endpoint:** `GET /api/profiles/{profile_id}/social_links/`  
**Authentication:** None (Public read)  
**Purpose:** Get all social media links for a profile

**Success Response (200):**
```json
[
  {
    "id": "789e4567-e89b-12d3-a456-426614174001",
    "platform": "github",
    "platform_display": "GitHub",
    "url": "https://github.com/teejay",
    "display_name": "TeeJay on GitHub",
    "order": 1
  },
  {
    "id": "789e4567-e89b-12d3-a456-426614174002",
    "platform": "linkedin",
    "platform_display": "LinkedIn",
    "url": "https://linkedin.com/in/teejay",
    "display_name": "Connect on LinkedIn",
    "order": 2
  },
  {
    "id": "789e4567-e89b-12d3-a456-426614174003",
    "platform": "twitter",
    "platform_display": "Twitter",
    "url": "https://twitter.com/teejay",
    "display_name": "@TeeJay",
    "order": 3
  }
]
```

---

## Projects Endpoints

### 9. List All Projects

**Endpoint:** `GET /api/projects/`  
**Authentication:** None (Public read)  
**Purpose:** Get list of portfolio projects

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `search` | string | No | Search in title, description, or technologies |
| `profile` | UUID | No | Filter by profile ID |
| `featured` | boolean | No | Filter featured projects (`true`/`false`) |
| `category` | string | No | Filter by category |
| `technology` | string | No | Filter by technology used |

**Example Request:**
```
GET /api/projects/?featured=true&technology=Django
```

**Success Response (200):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "proj-001-uuid",
      "title": "E-Commerce Platform",
      "slug": "e-commerce-platform",
      "description": "Full-featured online shopping platform with payment integration",
      "short_description": "Online shopping platform",
      "thumbnail": "projects/ecommerce-thumb.jpg",
      "thumbnail_url": "https://profileapi.alphalogiquetechnologies.com/media/projects/ecommerce-thumb.jpg",
      "category": "Web Application",
      "featured": true,
      "technologies": ["Django", "React", "PostgreSQL", "Stripe"],
      "github_url": "https://github.com/teejay/ecommerce",
      "live_url": "https://demo.ecommerce.example.com",
      "start_date": "2024-06-01",
      "end_date": "2024-12-15",
      "created_at": "2025-01-10T09:00:00Z"
    }
  ]
}
```

---

### 10. Get Project Details

**Endpoint:** `GET /api/projects/{project_id}/`  
**Authentication:** None (Public read)  
**Purpose:** Get detailed information about a specific project

**Success Response (200):**
```json
{
  "id": "proj-001-uuid",
  "profile": "123e4567-e89b-12d3-a456-426614174000",
  "title": "E-Commerce Platform",
  "slug": "e-commerce-platform",
  "description": "Comprehensive e-commerce solution with real-time inventory management, secure payment processing via Stripe, order tracking, and admin dashboard. Implemented microservices architecture for scalability.",
  "short_description": "Online shopping platform",
  "thumbnail": "projects/ecommerce-thumb.jpg",
  "thumbnail_url": "https://profileapi.alphalogiquetechnologies.com/media/projects/ecommerce-thumb.jpg",
  "video": "projects/videos/ecommerce-demo.mp4",
  "video_url": "https://profileapi.alphalogiquetechnologies.com/media/projects/videos/ecommerce-demo.mp4",
  "category": "Web Application",
  "featured": true,
  "order": 1,
  "technologies": ["Django", "React", "PostgreSQL", "Redis", "Stripe", "AWS"],
  "github_url": "https://github.com/teejay/ecommerce",
  "live_url": "https://demo.ecommerce.example.com",
  "start_date": "2024-06-01",
  "end_date": "2024-12-15",
  "role": "Lead Developer",
  "team_size": 3,
  "key_achievements": [
    "Reduced page load time by 60%",
    "Processed $50K+ in transactions",
    "99.9% uptime"
  ],
  "images": [
    {
      "id": "img-001-uuid",
      "image": "projects/ecommerce/home.jpg",
      "image_url": "https://profileapi.alphalogiquetechnologies.com/media/projects/ecommerce/home.jpg",
      "caption": "Homepage with featured products",
      "order": 1
    },
    {
      "id": "img-002-uuid",
      "image": "projects/ecommerce/checkout.jpg",
      "image_url": "https://profileapi.alphalogiquetechnologies.com/media/projects/ecommerce/checkout.jpg",
      "caption": "Secure checkout process",
      "order": 2
    }
  ],
  "created_at": "2025-01-10T09:00:00Z",
  "updated_at": "2025-11-20T15:00:00Z"
}
```

---

## Experience Endpoints

### 11. List Work Experiences

**Endpoint:** `GET /api/experiences/`  
**Authentication:** None (Public read)  
**Purpose:** Get list of work experiences

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `profile` | UUID | No | Filter by profile ID |
| `company` | string | No | Filter by company name |
| `is_current` | boolean | No | Filter current positions (`true`/`false`) |

**Success Response (200):**
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "exp-001-uuid",
      "company": "Tech Solutions Ltd",
      "position": "Senior Full Stack Developer",
      "location": "Accra, Ghana",
      "employment_type": "full_time",
      "employment_type_display": "Full Time",
      "is_current": true,
      "start_date": "2022-03-01",
      "end_date": null,
      "description": "Lead development of enterprise web applications using Django and React",
      "responsibilities": [
        "Architected microservices infrastructure",
        "Mentored junior developers",
        "Conducted code reviews"
      ],
      "achievements": [
        "Reduced deployment time by 70%",
        "Improved system performance by 40%"
      ],
      "technologies": ["Django", "React", "Docker", "AWS"],
      "created_at": "2025-01-15T10:00:00Z"
    }
  ]
}
```

---

### 12. Get Experience Details

**Endpoint:** `GET /api/experiences/{experience_id}/`  
**Authentication:** None (Public read)  
**Purpose:** Get detailed information about a work experience

**Success Response (200):**
```json
{
  "id": "exp-001-uuid",
  "profile": "123e4567-e89b-12d3-a456-426614174000",
  "company": "Tech Solutions Ltd",
  "position": "Senior Full Stack Developer",
  "location": "Accra, Ghana",
  "employment_type": "full_time",
  "employment_type_display": "Full Time",
  "is_current": true,
  "start_date": "2022-03-01",
  "end_date": null,
  "description": "Leading the development of enterprise-level web applications for financial services clients. Managing a team of 5 developers and overseeing the entire software development lifecycle.",
  "responsibilities": [
    "Architected and implemented microservices infrastructure using Django and Docker",
    "Led migration from monolithic to microservices architecture",
    "Mentored junior developers on best practices and design patterns",
    "Conducted comprehensive code reviews and technical documentation",
    "Collaborated with product managers to define technical requirements"
  ],
  "achievements": [
    "Reduced deployment time by 70% through CI/CD automation",
    "Improved system performance by 40% via database optimization",
    "Successfully delivered 8 major projects on time and under budget"
  ],
  "technologies": ["Django", "React", "Docker", "AWS", "PostgreSQL", "Redis"],
  "company_website": "https://techsolutions.example.com",
  "order": 1,
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-11-20T16:00:00Z"
}
```

---

## Education Endpoints

### 13. List Education Records

**Endpoint:** `GET /api/education/`  
**Authentication:** None (Public read)  
**Purpose:** Get list of education history

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `profile` | UUID | No | Filter by profile ID |
| `institution` | string | No | Filter by institution name |
| `degree` | string | No | Filter by degree type |

**Success Response (200):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "edu-001-uuid",
      "institution": "University of Ghana",
      "degree": "Bachelor of Science",
      "field_of_study": "Computer Science",
      "location": "Accra, Ghana",
      "start_date": "2015-09-01",
      "end_date": "2019-06-15",
      "grade": "First Class Honours",
      "description": "Focused on software engineering, algorithms, and database systems",
      "created_at": "2025-01-15T11:00:00Z"
    }
  ]
}
```

---

### 14. Get Education Details

**Endpoint:** `GET /api/education/{education_id}/`  
**Authentication:** None (Public read)  
**Purpose:** Get detailed information about an education record

**Success Response (200):**
```json
{
  "id": "edu-001-uuid",
  "profile": "123e4567-e89b-12d3-a456-426614174000",
  "institution": "University of Ghana",
  "degree": "Bachelor of Science",
  "field_of_study": "Computer Science",
  "location": "Accra, Ghana",
  "start_date": "2015-09-01",
  "end_date": "2019-06-15",
  "grade": "First Class Honours (GPA: 3.8/4.0)",
  "description": "Comprehensive computer science program with focus on software engineering principles, data structures and algorithms, database management systems, and artificial intelligence. Completed final year project on machine learning applications in fraud detection.",
  "activities": [
    "President of Computer Science Students Association (2018-2019)",
    "Member of Google Developer Students Club",
    "Hackathon winner - Ghana Tech Summit 2018"
  ],
  "order": 1,
  "created_at": "2025-01-15T11:00:00Z",
  "updated_at": "2025-11-20T17:00:00Z"
}
```

---

## Skills Endpoints

### 15. List All Skills

**Endpoint:** `GET /api/skills/`  
**Authentication:** None (Public read)  
**Purpose:** Get list of skills and proficiency levels

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `profile` | UUID | No | Filter by profile ID |
| `category` | string | No | Filter by skill category |
| `proficiency` | string | No | Filter by proficiency level (`beginner`, `intermediate`, `advanced`, `expert`) |

**Success Response (200):**
```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "skill-001-uuid",
      "name": "Django",
      "category": "Backend",
      "proficiency": "expert",
      "proficiency_display": "Expert",
      "years_of_experience": 6,
      "description": "Expert in building scalable REST APIs and web applications",
      "order": 1,
      "created_at": "2025-01-15T12:00:00Z"
    },
    {
      "id": "skill-002-uuid",
      "name": "React",
      "category": "Frontend",
      "proficiency": "advanced",
      "proficiency_display": "Advanced",
      "years_of_experience": 5,
      "description": "Advanced knowledge of React hooks, context API, and state management",
      "order": 2,
      "created_at": "2025-01-15T12:05:00Z"
    }
  ]
}
```

---

### 16. Get Skill Details

**Endpoint:** `GET /api/skills/{skill_id}/`  
**Authentication:** None (Public read)  
**Purpose:** Get detailed information about a skill

**Success Response (200):**
```json
{
  "id": "skill-001-uuid",
  "profile": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Django",
  "category": "Backend",
  "proficiency": "expert",
  "proficiency_display": "Expert",
  "years_of_experience": 6,
  "description": "Expert-level proficiency in Django framework for building scalable REST APIs and web applications. Deep understanding of ORM, middleware, custom management commands, and Django best practices.",
  "order": 1,
  "created_at": "2025-01-15T12:00:00Z",
  "updated_at": "2025-11-20T18:00:00Z"
}
```

**Proficiency Levels:**
| Value | Display | Description |
|-------|---------|-------------|
| `beginner` | Beginner | Basic understanding, learning phase |
| `intermediate` | Intermediate | Can work independently on tasks |
| `advanced` | Advanced | Can handle complex tasks and mentor others |
| `expert` | Expert | Deep expertise, can architect systems |

---

## Certifications Endpoints

### 17. List Certifications

**Endpoint:** `GET /api/certifications/`  
**Authentication:** None (Public read)  
**Purpose:** Get list of professional certifications

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `profile` | UUID | No | Filter by profile ID |
| `issuing_organization` | string | No | Filter by issuing organization |
| `is_active` | boolean | No | Filter active certifications (`true`/`false`) |

**Success Response (200):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "cert-001-uuid",
      "name": "AWS Certified Solutions Architect - Professional",
      "issuing_organization": "Amazon Web Services",
      "issue_date": "2024-03-15",
      "expiration_date": "2027-03-15",
      "credential_id": "AWS-PSA-12345678",
      "credential_url": "https://aws.amazon.com/verification/12345678",
      "is_active": true,
      "description": "Professional-level AWS certification covering architecture best practices",
      "created_at": "2025-01-15T13:00:00Z"
    }
  ]
}
```

---

### 18. Get Certification Details

**Endpoint:** `GET /api/certifications/{certification_id}/`  
**Authentication:** None (Public read)  
**Purpose:** Get detailed information about a certification

**Success Response (200):**
```json
{
  "id": "cert-001-uuid",
  "profile": "123e4567-e89b-12d3-a456-426614174000",
  "name": "AWS Certified Solutions Architect - Professional",
  "issuing_organization": "Amazon Web Services",
  "issue_date": "2024-03-15",
  "expiration_date": "2027-03-15",
  "credential_id": "AWS-PSA-12345678",
  "credential_url": "https://aws.amazon.com/verification/12345678",
  "is_active": true,
  "description": "Professional-level AWS certification validating advanced technical skills and experience in designing distributed applications and systems on the AWS platform. Covers complex architectural patterns, migration strategies, cost optimization, and security best practices.",
  "skills_covered": [
    "AWS architecture design",
    "Security and compliance",
    "Cost optimization",
    "Migration strategies"
  ],
  "order": 1,
  "created_at": "2025-01-15T13:00:00Z",
  "updated_at": "2025-11-20T19:00:00Z"
}
```

---

## Contact Form Endpoint

### 19. Submit Contact Message (Public)

**Endpoint:** `POST /api/contacts/submit/`  
**Authentication:** None (Public - NO AUTH REQUIRED)  
**Purpose:** Allow visitors to send messages without logging in

**Request Body:**
```json
{
  "sender_name": "Jane Visitor",
  "sender_email": "jane@example.com",
  "subject": "Inquiry about collaboration",
  "message": "Hi, I'm interested in discussing a potential project collaboration. Are you available for a call next week?"
}
```

**Field Requirements:**
| Field | Type | Required | Max Length | Notes |
|-------|------|----------|------------|-------|
| `sender_name` | string | ✅ Yes | 200 chars | Visitor's name |
| `sender_email` | string | ✅ Yes | 254 chars | Valid email format |
| `subject` | string | ✅ Yes | 300 chars | Message subject |
| `message` | string | ✅ Yes | 5000 chars | Message body |

**Success Response (201):**
```json
{
  "id": "msg-001-uuid",
  "sender_name": "Jane Visitor",
  "sender_email": "jane@example.com",
  "subject": "Inquiry about collaboration",
  "message": "Hi, I'm interested in discussing a potential project collaboration. Are you available for a call next week?",
  "status": "unread",
  "status_display": "Unread",
  "created_at": "2025-11-21T14:30:00Z"
}
```

**Status Values:**
| Value | Display | Description |
|-------|---------|-------------|
| `unread` | Unread | Message not yet read |
| `read` | Read | Message has been read |
| `replied` | Replied | Message has been replied to |
| `archived` | Archived | Message archived |

**Error Response (400):**
```json
{
  "sender_email": ["Enter a valid email address."],
  "message": ["This field may not be blank."]
}
```

---

### 20. List Contact Messages (Admin Only)

**Endpoint:** `GET /api/contacts/messages/`  
**Authentication:** Bearer Token Required (Admin/Editor role)  
**Purpose:** Get list of contact messages (admin panel)

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by status (`unread`, `read`, `replied`, `archived`) |
| `search` | string | No | Search in name, email, subject, or message |

**Success Response (200):**
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "msg-001-uuid",
      "sender_name": "Jane Visitor",
      "sender_email": "jane@example.com",
      "subject": "Inquiry about collaboration",
      "message": "Hi, I'm interested in discussing...",
      "status": "unread",
      "status_display": "Unread",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "replied_at": null,
      "created_at": "2025-11-21T14:30:00Z"
    }
  ]
}
```

---

## Error Response Structure

All error responses follow this consistent structure:

### Validation Errors (400)
```json
{
  "field_name": ["Error message for this field"],
  "another_field": ["Error message", "Another error for same field"]
}
```

### Authentication Required (401)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Permission Denied (403)
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Not Found (404)
```json
{
  "detail": "Not found."
}
```

### Rate Limited (429)
```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

### Server Error (500)
```json
{
  "detail": "A server error occurred."
}
```

---

## TypeScript Types

```typescript
// =====================
// Authentication Types
// =====================

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone: string | null;
  role: 'super_admin' | 'editor' | 'viewer';
  is_verified: boolean;
  is_active: boolean;
  mfa_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  refresh: string;
  access: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

export interface RegisterResponse {
  message: string;
  user: User;
  tokens: AuthTokens;
}

export interface LoginRequest {
  email: string;
  password: string;
  mfa_token?: string;
}

export interface LoginResponse {
  message: string;
  user: User;
  tokens: AuthTokens;
}

export interface RefreshTokenRequest {
  refresh: string;
}

export interface RefreshTokenResponse {
  access: string;
}

// =====================
// Portfolio Profile Types
// =====================

export interface SocialLink {
  id: string;
  platform: 'github' | 'linkedin' | 'twitter' | 'portfolio' | 'other';
  platform_display: string;
  url: string;
  display_name: string | null;
  order: number;
}

export interface ProfileListItem {
  id: string;
  full_name: string;
  email: string;
  headline: string;
  city: string;
  state: string;
  country: string;
  profile_picture_url: string | null;
  created_at: string;
}

export interface ProfileDetail {
  id: string;
  full_name: string;
  email: string;
  phone: string | null;
  headline: string;
  summary: string;
  city: string;
  state: string;
  country: string;
  profile_picture: string | null;
  profile_picture_url: string | null;
  cover_image: string | null;
  cover_image_url: string | null;
  social_links: SocialLink[];
  projects_count: number;
  experiences_count: number;
  education_count: number;
  skills_count: number;
  certifications_count: number;
  created_at: string;
  updated_at: string;
}

// =====================
// Project Types
// =====================

export interface ProjectImage {
  id: string;
  image: string;
  image_url: string;
  caption: string | null;
  order: number;
}

export interface ProjectListItem {
  id: string;
  title: string;
  slug: string;
  description: string;
  short_description: string;
  thumbnail: string | null;
  thumbnail_url: string | null;
  category: string;
  featured: boolean;
  technologies: string[];
  github_url: string | null;
  live_url: string | null;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
}

export interface ProjectDetail extends ProjectListItem {
  profile: string;
  video: string | null;
  video_url: string | null;
  order: number;
  role: string | null;
  team_size: number | null;
  key_achievements: string[];
  images: ProjectImage[];
  updated_at: string;
}

// =====================
// Experience Types
// =====================

export type EmploymentType = 'full_time' | 'part_time' | 'contract' | 'freelance' | 'internship';

export interface ExperienceListItem {
  id: string;
  company: string;
  position: string;
  location: string;
  employment_type: EmploymentType;
  employment_type_display: string;
  is_current: boolean;
  start_date: string;
  end_date: string | null;
  description: string;
  responsibilities: string[];
  achievements: string[];
  technologies: string[];
  created_at: string;
}

export interface ExperienceDetail extends ExperienceListItem {
  profile: string;
  company_website: string | null;
  order: number;
  updated_at: string;
}

// =====================
// Education Types
// =====================

export interface EducationListItem {
  id: string;
  institution: string;
  degree: string;
  field_of_study: string;
  location: string;
  start_date: string;
  end_date: string | null;
  grade: string | null;
  description: string;
  created_at: string;
}

export interface EducationDetail extends EducationListItem {
  profile: string;
  activities: string[];
  order: number;
  updated_at: string;
}

// =====================
// Skill Types
// =====================

export type ProficiencyLevel = 'beginner' | 'intermediate' | 'advanced' | 'expert';

export interface SkillListItem {
  id: string;
  name: string;
  category: string;
  proficiency: ProficiencyLevel;
  proficiency_display: string;
  years_of_experience: number | null;
  description: string;
  order: number;
  created_at: string;
}

export interface SkillDetail extends SkillListItem {
  profile: string;
  updated_at: string;
}

// =====================
// Certification Types
// =====================

export interface CertificationListItem {
  id: string;
  name: string;
  issuing_organization: string;
  issue_date: string;
  expiration_date: string | null;
  credential_id: string | null;
  credential_url: string | null;
  is_active: boolean;
  description: string;
  created_at: string;
}

export interface CertificationDetail extends CertificationListItem {
  profile: string;
  skills_covered: string[];
  order: number;
  updated_at: string;
}

// =====================
// Contact Types
// =====================

export type MessageStatus = 'unread' | 'read' | 'replied' | 'archived';

export interface ContactSubmitRequest {
  sender_name: string;
  sender_email: string;
  subject: string;
  message: string;
}

export interface ContactMessage {
  id: string;
  sender_name: string;
  sender_email: string;
  subject: string;
  message: string;
  status: MessageStatus;
  status_display: string;
  created_at: string;
}

export interface ContactMessageDetail extends ContactMessage {
  ip_address: string | null;
  user_agent: string | null;
  replied_at: string | null;
}

// =====================
// Pagination Types
// =====================

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// =====================
// Error Types
// =====================

export interface ValidationError {
  [field: string]: string[];
}

export interface APIError {
  detail: string;
  code?: string;
}
```

---

## Example Integration Code

### React + TypeScript Example

```typescript
// api/client.ts
import axios, { AxiosInstance, AxiosError } from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'https://profileapi.alphalogiquetechnologies.com';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle token refresh on 401
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && originalRequest) {
          const refreshToken = localStorage.getItem('refresh_token');
          
          if (refreshToken) {
            try {
              const { data } = await axios.post(`${BASE_URL}/api/auth/token/refresh/`, {
                refresh: refreshToken,
              });
              
              localStorage.setItem('access_token', data.access);
              
              // Retry original request
              originalRequest.headers.Authorization = `Bearer ${data.access}`;
              return axios(originalRequest);
            } catch (refreshError) {
              // Refresh failed, logout user
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              window.location.href = '/login';
            }
          }
        }
        
        return Promise.reject(error);
      }
    );
  }

  // ==================
  // Authentication
  // ==================

  async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await this.client.post('/api/auth/register/', data);
    return response.data;
  }

  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await this.client.post('/api/auth/login/', data);
    return response.data;
  }

  async refreshToken(refreshToken: string): Promise<RefreshTokenResponse> {
    const response = await this.client.post('/api/auth/token/refresh/', {
      refresh: refreshToken,
    });
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get('/api/auth/profile/');
    return response.data;
  }

  async updateCurrentUser(data: Partial<User>): Promise<User> {
    const response = await this.client.patch('/api/auth/profile/', data);
    return response.data;
  }

  // ==================
  // Portfolio Profiles
  // ==================

  async getProfiles(params?: {
    search?: string;
    city?: string;
    state?: string;
    country?: string;
  }): Promise<PaginatedResponse<ProfileListItem>> {
    const response = await this.client.get('/api/profiles/', { params });
    return response.data;
  }

  async getProfile(id: string): Promise<ProfileDetail> {
    const response = await this.client.get(`/api/profiles/${id}/`);
    return response.data;
  }

  async getProfileSocialLinks(profileId: string): Promise<SocialLink[]> {
    const response = await this.client.get(`/api/profiles/${profileId}/social_links/`);
    return response.data;
  }

  // ==================
  // Projects
  // ==================

  async getProjects(params?: {
    search?: string;
    profile?: string;
    featured?: boolean;
    category?: string;
    technology?: string;
  }): Promise<PaginatedResponse<ProjectListItem>> {
    const response = await this.client.get('/api/projects/', { params });
    return response.data;
  }

  async getProject(id: string): Promise<ProjectDetail> {
    const response = await this.client.get(`/api/projects/${id}/`);
    return response.data;
  }

  // ==================
  // Experiences
  // ==================

  async getExperiences(params?: {
    profile?: string;
    company?: string;
    is_current?: boolean;
  }): Promise<PaginatedResponse<ExperienceListItem>> {
    const response = await this.client.get('/api/experiences/', { params });
    return response.data;
  }

  async getExperience(id: string): Promise<ExperienceDetail> {
    const response = await this.client.get(`/api/experiences/${id}/`);
    return response.data;
  }

  // ==================
  // Education
  // ==================

  async getEducation(params?: {
    profile?: string;
    institution?: string;
  }): Promise<PaginatedResponse<EducationListItem>> {
    const response = await this.client.get('/api/education/', { params });
    return response.data;
  }

  async getEducationDetail(id: string): Promise<EducationDetail> {
    const response = await this.client.get(`/api/education/${id}/`);
    return response.data;
  }

  // ==================
  // Skills
  // ==================

  async getSkills(params?: {
    profile?: string;
    category?: string;
    proficiency?: ProficiencyLevel;
  }): Promise<PaginatedResponse<SkillListItem>> {
    const response = await this.client.get('/api/skills/', { params });
    return response.data;
  }

  async getSkill(id: string): Promise<SkillDetail> {
    const response = await this.client.get(`/api/skills/${id}/`);
    return response.data;
  }

  // ==================
  // Certifications
  // ==================

  async getCertifications(params?: {
    profile?: string;
    issuing_organization?: string;
    is_active?: boolean;
  }): Promise<PaginatedResponse<CertificationListItem>> {
    const response = await this.client.get('/api/certifications/', { params });
    return response.data;
  }

  async getCertification(id: string): Promise<CertificationDetail> {
    const response = await this.client.get(`/api/certifications/${id}/`);
    return response.data;
  }

  // ==================
  // Contact
  // ==================

  async submitContactMessage(data: ContactSubmitRequest): Promise<ContactMessage> {
    const response = await this.client.post('/api/contacts/submit/', data);
    return response.data;
  }

  async getContactMessages(params?: {
    status?: MessageStatus;
    search?: string;
  }): Promise<PaginatedResponse<ContactMessageDetail>> {
    const response = await this.client.get('/api/contacts/messages/', { params });
    return response.data;
  }
}

export const apiClient = new APIClient();
```

### Usage Examples

```typescript
// components/LoginForm.tsx
import React, { useState } from 'react';
import { apiClient } from '../api/client';
import type { LoginRequest } from '../api/types';

export const LoginForm: React.FC = () => {
  const [formData, setFormData] = useState<LoginRequest>({
    email: '',
    password: '',
  });
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const response = await apiClient.login(formData);
      
      // Store tokens
      localStorage.setItem('access_token', response.tokens.access);
      localStorage.setItem('refresh_token', response.tokens.refresh);
      
      // Store user info
      localStorage.setItem('user', JSON.stringify(response.user));
      
      // Redirect to homepage (no profile completion needed!)
      window.location.href = '/';
      
    } catch (err: any) {
      if (err.response?.data?.mfa_required) {
        // Show MFA input field
        setError('Please enter your MFA code');
      } else {
        setError(err.response?.data?.non_field_errors?.[0] || 'Login failed');
      }
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        placeholder="Email"
        required
      />
      <input
        type="password"
        value={formData.password}
        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
        placeholder="Password"
        required
      />
      {error && <p className="error">{error}</p>}
      <button type="submit">Login</button>
    </form>
  );
};
```

```typescript
// components/Portfolio.tsx
import React, { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import type { ProfileDetail } from '../api/types';

export const Portfolio: React.FC = () => {
  const [profile, setProfile] = useState<ProfileDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        // Get list of profiles (usually just one - the site owner)
        const { results } = await apiClient.getProfiles();
        
        if (results.length > 0) {
          // Get full details of first profile
          const details = await apiClient.getProfile(results[0].id);
          setProfile(details);
        }
      } catch (error) {
        console.error('Failed to load profile:', error);
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (!profile) return <div>Profile not found</div>;

  return (
    <div className="portfolio">
      <img src={profile.cover_image_url} alt="Cover" />
      <img src={profile.profile_picture_url} alt={profile.full_name} />
      <h1>{profile.full_name}</h1>
      <h2>{profile.headline}</h2>
      <p>{profile.summary}</p>
      
      <div className="social-links">
        {profile.social_links.map((link) => (
          <a key={link.id} href={link.url} target="_blank" rel="noopener noreferrer">
            {link.platform_display}
          </a>
        ))}
      </div>
      
      <div className="stats">
        <p>{profile.projects_count} Projects</p>
        <p>{profile.experiences_count} Work Experiences</p>
        <p>{profile.skills_count} Skills</p>
      </div>
    </div>
  );
};
```

```typescript
// components/ContactForm.tsx
import React, { useState } from 'react';
import { apiClient } from '../api/client';
import type { ContactSubmitRequest } from '../api/types';

export const ContactForm: React.FC = () => {
  const [formData, setFormData] = useState<ContactSubmitRequest>({
    sender_name: '',
    sender_email: '',
    subject: '',
    message: '',
  });
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      // No authentication required!
      await apiClient.submitContactMessage(formData);
      
      setSuccess(true);
      setFormData({ sender_name: '', sender_email: '', subject: '', message: '' });
      
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to send message');
    }
  };

  if (success) {
    return <div className="success">Message sent successfully!</div>;
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={formData.sender_name}
        onChange={(e) => setFormData({ ...formData, sender_name: e.target.value })}
        placeholder="Your Name"
        required
      />
      <input
        type="email"
        value={formData.sender_email}
        onChange={(e) => setFormData({ ...formData, sender_email: e.target.value })}
        placeholder="Your Email"
        required
      />
      <input
        type="text"
        value={formData.subject}
        onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
        placeholder="Subject"
        required
      />
      <textarea
        value={formData.message}
        onChange={(e) => setFormData({ ...formData, message: e.target.value })}
        placeholder="Message"
        rows={5}
        required
      />
      {error && <p className="error">{error}</p>}
      <button type="submit">Send Message</button>
    </form>
  );
};
```

---

## Important Notes

1. **All media URLs are absolute** - Use the `*_url` fields directly (e.g., `profile_picture_url`, `thumbnail_url`)
2. **Authentication is optional** for most endpoints - Only needed for updating user account or admin actions
3. **Contact form is public** - No authentication required for `/api/contacts/submit/`
4. **Profile endpoints are public read** - Anyone can view portfolio data
5. **Pagination is consistent** - All list endpoints return `count`, `next`, `previous`, `results`
6. **Error structure is consistent** - Always check `field_name` for validation errors or `detail` for general errors
7. **Dates are ISO 8601 format** - e.g., `"2025-11-21T14:30:00Z"`
8. **UUIDs are used for IDs** - Not integers

---

## Testing the API

Use these curl commands to test endpoints:

```bash
# Get portfolio profile
curl https://profileapi.alphalogiquetechnologies.com/api/profiles/

# Get projects
curl https://profileapi.alphalogiquetechnologies.com/api/projects/?featured=true

# Submit contact message (no auth needed!)
curl -X POST https://profileapi.alphalogiquetechnologies.com/api/contacts/submit/ \
  -H "Content-Type: application/json" \
  -d '{
    "sender_name": "Test User",
    "sender_email": "test@example.com",
    "subject": "Test Message",
    "message": "This is a test message"
  }'

# Login
curl -X POST https://profileapi.alphalogiquetechnologies.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

---

## Support

For questions or issues with the API, contact: **teejay@alphalogiquetechnologies.com**

**API Documentation:** [https://profileapi.alphalogiquetechnologies.com/api/schema/swagger-ui/](https://profileapi.alphalogiquetechnologies.com/api/schema/swagger-ui/)
