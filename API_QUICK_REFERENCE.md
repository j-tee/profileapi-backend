# Quick API Reference - User-Integrated Structure

## User Profile

### Get Current User Profile
```bash
GET /api/auth/profile/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "super_admin",
  "headline": "Full Stack Developer",
  "summary": "Experienced developer...",
  "city": "San Francisco",
  "state": "California",
  "country": "USA",
  "profile_picture": "url",
  "profile_picture_url": "full_url",
  "cover_image": "url",
  "cover_image_url": "full_url",
  "social_links": [...],
  "projects_count": 5,
  "experiences_count": 3,
  "education_count": 2,
  "skills_count": 12,
  "certifications_count": 4,
  "date_joined": "2024-01-01T00:00:00Z"
}
```

### Update User Profile
```bash
PATCH /api/auth/profile/
Authorization: Bearer <token>
Content-Type: application/json

{
  "headline": "Senior Full Stack Developer",
  "summary": "Updated bio...",
  "city": "New York"
}
```

### Upload Profile Picture
```bash
PATCH /api/auth/profile/
Authorization: Bearer <token>
Content-Type: multipart/form-data

profile_picture: <file>
```

## Projects

### List All Projects
```bash
GET /api/projects/
```

**Query Parameters:**
- `user=<uuid>` - Filter by user
- `featured=true` - Filter featured projects
- `current=true` - Filter current projects
- `search=<term>` - Search in title, description, technologies
- `ordering=-start_date` - Order results

### Get User's Projects
```bash
GET /api/projects/by_user/<user_id>/
```

### Create Project
```bash
POST /api/projects/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Project Name",
  "description": "Short description",
  "long_description": "Detailed description",
  "technologies": ["React", "Django", "PostgreSQL"],
  "role": "Full Stack Developer",
  "team_size": 3,
  "start_date": "2024-01-01",
  "end_date": null,
  "current": true,
  "project_url": "https://example.com",
  "github_url": "https://github.com/user/repo",
  "highlights": ["Feature 1", "Feature 2"],
  "featured": true,
  "order": 0
}
```

**Note:** The `user` field is automatically assigned to the authenticated user.

## Experiences

### List All Experiences
```bash
GET /api/experiences/
```

**Query Parameters:**
- `user=<uuid>` - Filter by user
- `current=true` - Filter current positions
- `employment_type=full_time` - Filter by employment type
- `location_type=remote` - Filter by location type

### Get User's Experiences
```bash
GET /api/experiences/by_user/<user_id>/
```

### Create Experience
```bash
POST /api/experiences/
Authorization: Bearer <token>

{
  "title": "Senior Developer",
  "company": "Tech Corp",
  "employment_type": "full_time",
  "location": "San Francisco, CA",
  "location_type": "hybrid",
  "start_date": "2023-01-01",
  "end_date": null,
  "current": true,
  "description": "Job description",
  "responsibilities": ["Task 1", "Task 2"],
  "achievements": ["Achievement 1"],
  "technologies": ["Python", "React"],
  "order": 0
}
```

**Note:** The `user` field is automatically assigned to the authenticated user.

## Education

### List All Education
```bash
GET /api/education/
```

**Query Parameters:**
- `user=<uuid>` - Filter by user
- `current=true` - Filter current education

### Get User's Education
```bash
GET /api/education/by_user/<user_id>/
```

### Create Education
```bash
POST /api/education/
Authorization: Bearer <token>

{
  "institution": "University Name",
  "degree": "Bachelor of Science",
  "field_of_study": "Computer Science",
  "start_date": "2018-09-01",
  "end_date": "2022-06-01",
  "current": false,
  "grade": "3.8 GPA",
  "description": "Relevant coursework...",
  "activities": ["Club 1", "Society 2"],
  "achievements": ["Award 1"],
  "order": 0
}
```

**Note:** The `user` field is automatically assigned to the authenticated user.

## Skills

### List All Skills
```bash
GET /api/skills/
```

**Query Parameters:**
- `user=<uuid>` - Filter by user
- `category=programming` - Filter by category
- `proficiency_level=expert` - Filter by proficiency

### Get User's Skills
```bash
GET /api/skills/by_user/<user_id>/
```

### Get Skills Grouped by Category
```bash
GET /api/skills/by_category/?user=<uuid>
```

### Create Skill
```bash
POST /api/skills/
Authorization: Bearer <token>

{
  "name": "Python",
  "category": "programming",
  "proficiency_level": "expert",
  "years_of_experience": 5,
  "endorsements": 15,
  "order": 0
}
```

**Note:** The `user` field is automatically assigned to the authenticated user.

**Categories:**
- `programming` - Programming Languages
- `framework` - Frameworks & Libraries
- `database` - Databases
- `devops` - DevOps & Cloud
- `design` - Design & UX
- `soft_skill` - Soft Skills
- `tool` - Tools & Software
- `other` - Other

**Proficiency Levels:**
- `beginner` - Beginner
- `intermediate` - Intermediate
- `advanced` - Advanced
- `expert` - Expert

## Certifications

### List All Certifications
```bash
GET /api/certifications/
```

**Query Parameters:**
- `user=<uuid>` - Filter by user
- `issuer=<name>` - Filter by issuer

### Get User's Certifications
```bash
GET /api/certifications/by_user/<user_id>/
```

### Get Active Certifications
```bash
GET /api/certifications/active/
```

### Create Certification
```bash
POST /api/certifications/
Authorization: Bearer <token>

{
  "name": "AWS Certified Solutions Architect",
  "issuer": "Amazon Web Services",
  "issue_date": "2023-06-01",
  "expiration_date": "2026-06-01",
  "credential_id": "ABC123XYZ",
  "credential_url": "https://verify.example.com",
  "description": "Cloud architecture certification",
  "skills": ["AWS", "Cloud Computing", "Architecture"],
  "order": 0
}
```

**Note:** The `user` field is automatically assigned to the authenticated user.

## Social Links

### List User's Social Links
```bash
GET /api/auth/social-links/
Authorization: Bearer <token>
```

### Create Social Link
```bash
POST /api/auth/social-links/
Authorization: Bearer <token>

{
  "platform": "github",
  "url": "https://github.com/username",
  "username": "username"
}
```

**Platforms:**
- `github`, `linkedin`, `twitter`, `portfolio`, `youtube`, `medium`, `stackoverflow`, `codepen`, `dribbble`, `behance`, `other`

## Authentication

### Login
```bash
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "super_admin"
  }
}
```

### Refresh Token
```bash
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "jwt_refresh_token"
}
```

## Common Response Fields

### Content Models (Projects, Experiences, Education, Skills, Certifications)

All detail serializers now include:
- `user` - UUID of the user who owns the content
- `owner_name` - Full name of the owner (computed)
- `owner_email` - Email of the owner (computed)
- Standard fields specific to each model
- `created_at`, `updated_at` - Timestamps

## HTTP Status Codes

- `200 OK` - Successful GET/PUT/PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Authentication

Most endpoints require authentication using JWT tokens:
```
Authorization: Bearer <access_token>
```

Public endpoints (no auth required):
- GET requests for projects, experiences, education, skills, certifications
- POST /api/auth/login/
- POST /api/auth/register/
- POST /api/auth/token/refresh/

## Pagination

List endpoints return paginated results:
```json
{
  "count": 100,
  "next": "http://api/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

Default page size: 10 items
Override with: `?page_size=20`
