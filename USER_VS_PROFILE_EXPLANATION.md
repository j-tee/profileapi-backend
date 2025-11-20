# User vs Profile: Complete Guide for Frontend Developers

## 🚀 Latest Update: Public API Access

**✅ ALL portfolio content is now PUBLIC!**

Anonymous visitors can now:
- View complete profile, projects, experiences, education, skills, certifications
- Submit contact forms without login
- Browse entire portfolio - **NO authentication required!**

**🔐 Login only required for:**
- Admin dashboard access
- Creating/editing/deleting content
- Viewing contact messages

**New Public Endpoints:**
- `/api/experiences/` - Work history
- `/api/education/` - Academic background  
- `/api/skills/` - Technical skills
- `/api/certifications/` - Certificates & awards
- `/api/contacts/` - Anonymous contact form

---

## 🎯 The Core Confusion - Solved

**The Question Everyone Asks:**
*"Why do we have both a User and a Profile? Aren't they the same thing?"*

**The Answer:**
No, they serve completely different purposes in this personal portfolio system.

---

## 🔑 Two Separate Systems

### 1. **User Account** (Authentication System)
**Location:** `/api/auth/` endpoints  
**Purpose:** Login, permissions, security  
**Think of it as:** The keys to the house (private, for access control)

**What it contains:**
- Email (login credential)
- Password (encrypted)
- Role (super_admin, editor, viewer)
- MFA settings
- Account status (active/inactive)

**Who uses it:**
- You (the portfolio owner) to login
- System administrators
- Backend authentication system

**Important:** This is NOT visible to public visitors!

### 2. **Profile** (Portfolio Content System)
**Location:** `/api/profiles/` endpoints  
**Purpose:** Public portfolio information  
**Think of it as:** Your business card (public, for display)

**What it contains:**
- Full name, headline, bio
- Profile picture, cover image
- Contact info (public email, phone, location)
- Social media links
- Created portfolio content (projects, experiences, education)

**Who uses it:**
- Public visitors to your portfolio site
- Your frontend application to display your information
- Anyone viewing your portfolio (no login required)

**Important:** This IS publicly visible!

---

## 🏗️ Architecture: Personal Portfolio Design

This is a **personal portfolio** (ONE owner), not a multi-user platform.

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR PORTFOLIO SYSTEM                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🔐 PRIVATE (Authentication)          🌍 PUBLIC (Display)   │
│  ─────────────────────────            ────────────────────  │
│                                                              │
│  User Account                         Profile               │
│  └─ juliustetteh@gmail.com           └─ Julius Tetteh      │
│     (login only)                        (portfolio owner)   │
│                                                              │
│  ONE user account                     ONE profile           │
│  (for admin access)                   (your public bio)     │
│                                                              │
│                                       Multiple Projects →   │
│                                       Multiple Experiences → │
│                                       Multiple Skills →      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🌍 Permission Model: Public vs Admin

### What's PUBLIC (No Authentication Required):
✅ **READ operations on ALL portfolio content:**
- View profile information
- Browse all projects
- See work experience history
- View education background
- Browse skills and expertise
- See certifications and awards
- Submit contact form (anonymous)

**No JWT token needed! No login required!**

### What Requires AUTHENTICATION (Admin Only):
🔐 **CREATE/UPDATE/DELETE operations:**
- Create new projects, experiences, education, skills, certifications
- Edit/update any portfolio content
- Delete any portfolio items
- View contact messages from visitors
- Respond to contact messages
- Manage user accounts

**Requires JWT token from `/api/auth/login/`**

### The Rule:
- **Visitors can VIEW everything** (read-only, public)
- **Only you can EDIT** (requires login)
- **Contact forms are anonymous** (no login to send, but login to view)

---

## 🔗 How They Connect (CRITICAL INFO)

### They Are Linked By Email (Not Database Foreign Key!)

**User Account:**
```json
{
  "email": "juliustetteh@gmail.com",
  "password": "...",
  "role": "super_admin"
}
```

**Profile:**
```json
{
  "id": "bcd91fdc-d398-42f5-87b3-f7699fd50eae",
  "email": "juliustetteh@gmail.com",
  "first_name": "Julius",
  "last_name": "Tetteh",
  "headline": "Full Stack Developer & Software Engineer"
}
```

**Key Point:** Same email = same person, but different data systems!

---

## 📋 The Profile UUID You Need

**CRITICAL CONSTANT FOR FRONTEND:**

```typescript
// constants/api.ts
export const PORTFOLIO_OWNER_PROFILE_ID = 'bcd91fdc-d398-42f5-87b3-f7699fd50eae';
export const PORTFOLIO_OWNER_EMAIL = 'juliustetteh@gmail.com';
```

**When to use this UUID:**
- Creating new projects: `formData.append('profile', PORTFOLIO_OWNER_PROFILE_ID)`
- Creating experiences, education, skills: All require this profile UUID
- Filtering content: `GET /api/projects/?profile=${PORTFOLIO_OWNER_PROFILE_ID}`

---

## 🎭 Two Different Frontend Flows

### Flow 1: Public Visitor (No Login)

**What they see:**
```typescript
// Homepage - Public (NO authentication required!)
const HomePage = () => {
  const [profile, setProfile] = useState(null);
  const [projects, setProjects] = useState([]);
  const [experiences, setExperiences] = useState([]);
  const [education, setEducation] = useState([]);
  const [skills, setSkills] = useState([]);
  const [certifications, setCertifications] = useState([]);
  
  const PROFILE_ID = 'bcd91fdc-d398-42f5-87b3-f7699fd50eae';
  const API_BASE = 'http://localhost:8000/api';
  
  useEffect(() => {
    // Fetch all public portfolio data - NO auth tokens needed!
    Promise.all([
      fetch(`${API_BASE}/profiles/${PROFILE_ID}/`).then(r => r.json()),
      fetch(`${API_BASE}/projects/?profile=${PROFILE_ID}`).then(r => r.json()),
      fetch(`${API_BASE}/experiences/by_profile/${PROFILE_ID}/`).then(r => r.json()),
      fetch(`${API_BASE}/education/by_profile/${PROFILE_ID}/`).then(r => r.json()),
      fetch(`${API_BASE}/skills/by_profile/${PROFILE_ID}/`).then(r => r.json()),
      fetch(`${API_BASE}/certifications/active/?profile=${PROFILE_ID}`).then(r => r.json()),
    ]).then(([profileData, projectsData, experiencesData, educationData, skillsData, certsData]) => {
      setProfile(profileData);
      setProjects(projectsData.results || projectsData);
      setExperiences(experiencesData);
      setEducation(educationData);
      setSkills(skillsData);
      setCertifications(certsData);
    });
  }, []);
  
  return (
    <div>
      {/* Hero Section */}
      <section>
        <img src={profile?.profile_picture_url} alt={profile?.full_name} />
        <h1>{profile?.full_name}</h1>
        <p>{profile?.headline}</p>
        <p>{profile?.summary}</p>
      </section>
      
      {/* Projects Section */}
      <section>
        <h2>Projects</h2>
        {projects.map(project => (
          <div key={project.id}>
            <h3>{project.title}</h3>
            <p>{project.description}</p>
          </div>
        ))}
      </section>
      
      {/* Experience Section */}
      <section>
        <h2>Work Experience</h2>
        {experiences.map(exp => (
          <div key={exp.id}>
            <h3>{exp.job_title} at {exp.company}</h3>
            <p>{exp.description}</p>
          </div>
        ))}
      </section>
      
      {/* Skills Section */}
      <section>
        <h2>Skills</h2>
        {skills.map(skill => (
          <span key={skill.id}>{skill.name}</span>
        ))}
      </section>
      
      {/* Contact Form (Anonymous - No login required!) */}
      <section>
        <h2>Get In Touch</h2>
        <ContactForm />
      </section>
    </div>
  );
};

// Anonymous Contact Form - NO authentication required!
const ContactForm = () => {
  const [status, setStatus] = useState('');
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
      const response = await fetch('http://localhost:8000/api/contacts/submit/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sender_name: formData.get('name'),
          sender_email: formData.get('email'),
          subject: formData.get('subject'),
          message: formData.get('message'),
          message_type: formData.get('type') || 'general'
        })
        // NO Authorization header needed!
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setStatus('success');
        alert(data.message); // "Your message has been received! We will get back to you soon."
        e.target.reset();
      } else {
        setStatus('error');
        alert('Failed to send message. Please try again.');
      }
    } catch (error) {
      setStatus('error');
      alert('Network error. Please check your connection.');
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input name="name" placeholder="Your Name" required />
      <input name="email" type="email" placeholder="Your Email" required />
      <input name="subject" placeholder="Subject" required />
      <textarea name="message" placeholder="Your message..." required />
      <select name="type">
        <option value="general">General Inquiry</option>
        <option value="job">Job Opportunity</option>
        <option value="proposal">Project Proposal</option>
        <option value="collaboration">Collaboration</option>
        <option value="feedback">Feedback</option>
      </select>
      <button type="submit">Send Message</button>
      {status && <p className={status}>{status === 'success' ? 'Sent!' : 'Error'}</p>}
    </form>
  );
};
```

**What they can do:**
- View your profile information
- See your projects
- Read your work experiences
- View your education history
- Browse your skills
- See your certifications
- Contact you via form (anonymous)
- **NO login required for any of these!**

### Flow 2: You (Admin/Owner)

**What you see:**
```typescript
// Admin Dashboard - Requires Login
const AdminDashboard = () => {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    
    // 1. Fetch current user (authentication info)
    fetch('http://localhost:8000/api/auth/users/me/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setUser(data));
    
    // 2. Fetch your profile (content to edit)
    fetch('http://localhost:8000/api/profiles/bcd91fdc-d398-42f5-87b3-f7699fd50eae/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setProfile(data));
  }, []);
  
  return (
    <div>
      <h2>Welcome back, {user?.first_name}!</h2>
      <p>Role: {user?.role}</p>
      
      <h3>Your Profile</h3>
      <button onClick={() => editProfile(profile)}>Edit Profile</button>
      <button onClick={() => createProject()}>Add New Project</button>
    </div>
  );
};
```

**What you can do:**
- Login with user account
- Edit profile information
- Create/edit/delete projects
- Manage portfolio content
- **Requires authentication**

---

## ❌ Common Mistakes & Solutions

### Mistake 1: Trying to get profile from user
```typescript
// ❌ WRONG - This endpoint doesn't exist
fetch('/api/users/me/profile/')

// ✅ CORRECT - Use the known profile UUID
fetch('/api/profiles/bcd91fdc-d398-42f5-87b3-f7699fd50eae/')
```

### Mistake 2: Using user ID when creating projects
```typescript
// ❌ WRONG - Projects don't belong to User
formData.append('user', userId);

// ✅ CORRECT - Projects belong to Profile
formData.append('profile', 'bcd91fdc-d398-42f5-87b3-f7699fd50eae');
```

### Mistake 3: Confusing authentication endpoints
```typescript
// ❌ WRONG - User management is under /api/auth/
fetch('/api/users/')

// ✅ CORRECT
fetch('/api/auth/users/')  // User account management
fetch('/api/profiles/')     // Profile content
```

### Mistake 4: Trying to authenticate with profile
```typescript
// ❌ WRONG - Profiles don't have passwords
const profile = await login(profileEmail, password);

// ✅ CORRECT - Login with User account
const user = await fetch('/api/auth/login/', {
  method: 'POST',
  body: JSON.stringify({
    email: 'juliustetteh@gmail.com',
    password: 'pa$$word123'
  })
});
```

---

## 🛠️ Implementation Checklist

### For Public Pages (No Login Required)
- [ ] Create homepage that fetches profile by UUID
- [ ] Display profile information (name, bio, image)
- [ ] Show social links from profile
- [ ] List all projects (`GET /api/projects/?profile={uuid}`)
- [ ] Display work experiences (`GET /api/experiences/by_profile/{uuid}/`)
- [ ] Show education history (`GET /api/education/by_profile/{uuid}/`)
- [ ] Display skills (`GET /api/skills/by_profile/{uuid}/`)
- [ ] Show certifications (`GET /api/certifications/active/?profile={uuid}`)
- [ ] Add anonymous contact form (`POST /api/contacts/` - NO auth required!)
- [ ] All endpoints are PUBLIC - no authentication needed!

### For Admin Pages (Login Required)
- [ ] Create login page using `/api/auth/login/`
- [ ] Store JWT tokens in localStorage
- [ ] Create protected route component
- [ ] Build profile edit form (PATCH `/api/profiles/{uuid}/`)
- [ ] Build project creation form (include profile UUID!)
- [ ] Add image upload functionality
- [ ] Implement logout (clear tokens)

### Configuration
- [ ] Add profile UUID constant to your codebase
- [ ] Set up API base URLs (localhost:8000)
- [ ] Configure CORS if needed
- [ ] Add error handling for 401/403/404

---

## 🔍 Quick Reference

### User Account Endpoints (Authentication)
```
POST   /api/auth/login/              - Login (get JWT tokens)
POST   /api/auth/token/refresh/      - Refresh access token
POST   /api/auth/logout/             - Logout
GET    /api/auth/users/me/           - Get current user info
PATCH  /api/auth/users/me/           - Update user account
```

### Profile Endpoints (Portfolio Content)
```
GET    /api/profiles/                - List all profiles (usually just one)
GET    /api/profiles/{uuid}/         - Get specific profile (your main one)
PATCH  /api/profiles/{uuid}/         - Update profile (admin only)
GET    /api/profiles/{uuid}/social-links/  - Get social links
```

### Project Endpoints (Portfolio Items)
```
GET    /api/projects/                - List all projects (public)
POST   /api/projects/                - Create project (admin, needs profile UUID!)
GET    /api/projects/{uuid}/         - Get project details
PATCH  /api/projects/{uuid}/         - Update project (admin)
DELETE /api/projects/{uuid}/         - Delete project (admin)
```

### Experience Endpoints (Work History)
```
GET    /api/experiences/             - List all experiences (public)
POST   /api/experiences/             - Create experience (admin, needs profile UUID!)
GET    /api/experiences/{uuid}/      - Get experience details (public)
PATCH  /api/experiences/{uuid}/      - Update experience (admin)
DELETE /api/experiences/{uuid}/      - Delete experience (admin)
GET    /api/experiences/by_profile/{profile_uuid}/  - Get experiences by profile (public)
```

### Education Endpoints (Academic History)
```
GET    /api/education/               - List all education (public)
POST   /api/education/               - Create education (admin, needs profile UUID!)
GET    /api/education/{uuid}/        - Get education details (public)
PATCH  /api/education/{uuid}/        - Update education (admin)
DELETE /api/education/{uuid}/        - Delete education (admin)
GET    /api/education/by_profile/{profile_uuid}/    - Get education by profile (public)
```

### Skills Endpoints (Technical Skills)
```
GET    /api/skills/                  - List all skills (public)
POST   /api/skills/                  - Create skill (admin, needs profile UUID!)
GET    /api/skills/{uuid}/           - Get skill details (public)
PATCH  /api/skills/{uuid}/           - Update skill (admin)
DELETE /api/skills/{uuid}/           - Delete skill (admin)
GET    /api/skills/by_profile/{profile_uuid}/       - Get skills by profile (public)
GET    /api/skills/by_category/      - Get skills grouped by category (public)
```

### Certification Endpoints (Certificates & Awards)
```
GET    /api/certifications/          - List all certifications (public)
POST   /api/certifications/          - Create certification (admin, needs profile UUID!)
GET    /api/certifications/{uuid}/   - Get certification details (public)
PATCH  /api/certifications/{uuid}/   - Update certification (admin)
DELETE /api/certifications/{uuid}/   - Delete certification (admin)
GET    /api/certifications/by_profile/{profile_uuid}/  - Get certifications by profile (public)
GET    /api/certifications/active/   - Get only non-expired certifications (public)
```

### Contact Endpoints (Anonymous Contact Forms)
```
POST   /api/contacts/submit/         - Submit contact form (PUBLIC - NO AUTH REQUIRED!)
GET    /api/contacts/messages/       - List contact messages (admin only)
GET    /api/contacts/messages/{uuid}/ - Get contact message (admin only)
PATCH  /api/contacts/messages/{uuid}/ - Update contact message status (admin only)
DELETE /api/contacts/messages/{uuid}/ - Delete contact message (admin only)
GET    /api/contacts/messages/statistics/ - Get message statistics (admin only)
```

---

## 💡 Mental Model

Think of your portfolio system like a house:

```
🏠 Your Portfolio House
│
├── 🔑 Front Door (User Account)
│   └── Only you have the key
│   └── Controls who can enter and edit
│   └── Email: juliustetteh@gmail.com
│   └── Password: pa$$word123
│
└── 📄 Welcome Sign (Profile)
    └── Everyone can see it
    └── Shows who you are
    └── UUID: bcd91fdc-d398-42f5-87b3-f7699fd50eae
    └── Contains: name, bio, projects, skills
```

**Visitors** see the welcome sign (profile).  
**You** use the key (user account) to go inside and change the sign.

---

## 🚀 Start Here

1. **Read this document completely** - Understand the two-system architecture
2. **Save the profile UUID** - You'll need it everywhere
3. **Implement public pages first** - No authentication needed, easier to test
4. **Then add admin features** - Login, edit, create content
5. **Refer to FRONTEND_INTEGRATION_GUIDE.md** - Complete code examples

---

## ❓ Still Confused?

Ask yourself:
- **"Am I building a login page?"** → Use User Account (`/api/auth/`)
- **"Am I displaying portfolio info?"** → Use Profile (`/api/profiles/`)
- **"Am I creating/editing content?"** → Use Profile UUID in the data

**The Rule:** Authentication uses User, Everything else uses Profile.

---

## 📞 Support

If you're still stuck:
1. Check the exact error message
2. Look at the Troubleshooting section in FRONTEND_INTEGRATION_GUIDE.md
3. Verify you're using the correct profile UUID
4. Make sure authentication token is included for admin operations

**Profile UUID (NEVER FORGET THIS):** `bcd91fdc-d398-42f5-87b3-f7699fd50eae`

---

---

## 📊 Complete Public API Summary

### ✅ All Public Endpoints (No Authentication Required)

**Profile & Portfolio Content:**
```bash
GET /api/profiles/bcd91fdc-d398-42f5-87b3-f7699fd50eae/  # Profile info
GET /api/projects/?profile={uuid}                         # All projects
GET /api/experiences/by_profile/{uuid}/                   # Work experience
GET /api/education/by_profile/{uuid}/                     # Education history
GET /api/skills/by_profile/{uuid}/                        # All skills
GET /api/skills/by_category/                              # Skills by category
GET /api/certifications/active/?profile={uuid}            # Active certs
```

**Anonymous Contact:**
```bash
POST /api/contacts/submit/  # Submit contact form (NO AUTH!)
```

### 🔐 Admin-Only Endpoints (Authentication Required)

**Content Management:**
```bash
POST/PATCH/DELETE /api/projects/              # Manage projects
POST/PATCH/DELETE /api/experiences/           # Manage experience
POST/PATCH/DELETE /api/education/             # Manage education
POST/PATCH/DELETE /api/skills/                # Manage skills
POST/PATCH/DELETE /api/certifications/        # Manage certifications
PATCH /api/profiles/{uuid}/                    # Edit profile
```

**Contact Messages:**
```bash
GET /api/contacts/messages/                    # View all messages
GET /api/contacts/messages/{uuid}/             # View message details
PATCH /api/contacts/messages/{uuid}/           # Update status
DELETE /api/contacts/messages/{uuid}/          # Delete message
```

**User Management:**
```bash
POST /api/auth/login/                          # Login
POST /api/auth/logout/                         # Logout
GET /api/auth/users/me/                        # Current user
```

---

**Last Updated:** November 20, 2025  
**Backend Version:** 1.0.0  
**For:** Frontend Development Team  
**Profile UUID:** `bcd91fdc-d398-42f5-87b3-f7699fd50eae`
