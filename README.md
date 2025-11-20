# Portfolio API Backend

A professional Django REST API for managing personal portfolio data with authentication, authorization, and multi-factor authentication (MFA) support.

## Features

- 🔐 **Authentication & Authorization**: JWT-based auth with role-based access control
- 🛡️ **Multi-Factor Authentication (MFA)**: TOTP-based 2FA with backup codes
- 👤 **User Management**: Custom user model with email authentication
- 📧 **Email Verification**: Account verification and password reset
- 📱 **Contact Management**: Handle contact form submissions
- 👨‍💼 **Profile Management**: Professional profiles with experiences, education, skills, projects, and certifications
- 📊 **API Documentation**: Auto-generated Swagger/ReDoc documentation
- 🔒 **Security**: Rate limiting, CORS configuration, and activity tracking
- 🎨 **REST Framework**: Built with Django REST Framework

## Tech Stack

- **Framework**: Django 5.1.3
- **API**: Django REST Framework 3.15.2
- **Authentication**: JWT (djangorestframework-simplejwt)
- **MFA**: PyOTP + QR Code generation
- **Database**: PostgreSQL (configured via env vars, falls back to SQLite for local dev)
- **Documentation**: drf-spectacular (OpenAPI 3.0)
- **Image Processing**: Pillow
- **CORS**: django-cors-headers
- **Configuration**: python-decouple

## Project Structure

```
backend/
├── accounts/          # User authentication and management
├── contacts/          # Contact form handling
├── profiles/          # User profiles
├── experiences/       # Work experience data
├── education/         # Education history
├── skills/            # Skills management
├── projects/          # Project portfolio
├── certifications/    # Certifications
├── portfolio_api/     # Main project settings
├── media/             # Uploaded files
├── manage.py          # Django management script
└── requirements.txt   # Python dependencies
```

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```
   - Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set your configurations, especially the PostgreSQL credentials (or leave `DB_ENGINE` set to `django.db.backends.sqlite3` if you prefer SQLite for local dev):
   - `SECRET_KEY`: Generate a secure secret key
   - `DEBUG`: Set to `False` in production
   - `ALLOWED_HOSTS`: Add your domain names
   - `DB_ENGINE`: `django.db.backends.postgresql` (or `django.db.backends.sqlite3`)
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: PostgreSQL connection details
   - Email settings for production

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create media directory**
   ```bash
   mkdir media
   ```

8. **Create a superuser** (Optional - Super admin already created)
   
   A super admin account has been created with:
   - **Email**: juliustetteh@gmail.com
   - **Password**: pa$$word123
   
   To create additional admin users, use the user management script:
   ```bash
   python manage_users.py
   ```

9. **Run the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

## API Documentation

Once the server is running, access the API documentation:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `POST /api/auth/logout/` - Logout user
- `POST /api/auth/password-reset/` - Request password reset
- `POST /api/auth/password-reset-confirm/` - Confirm password reset
- `GET /api/auth/verify-email/{token}/` - Verify email

### MFA (Multi-Factor Authentication)
- `POST /api/auth/mfa/setup/` - Setup MFA
- `POST /api/auth/mfa/enable/` - Enable MFA
- `POST /api/auth/mfa/disable/` - Disable MFA
- `POST /api/auth/mfa/verify/` - Verify MFA token
- `POST /api/auth/mfa/backup-codes/` - Generate backup codes

### Contact
- `POST /api/contacts/` - Submit contact form
- `GET /api/contacts/` - List contacts (admin only)

### Profiles
- `GET /api/profiles/` - List profiles (public)
- `GET /api/profiles/{id}/` - Get profile details (public)
- `POST /api/profiles/` - Create profile (admin/editor only)
- `PATCH /api/profiles/{id}/` - Update profile (admin/editor only)
- `DELETE /api/profiles/{id}/` - Delete profile (admin/editor only)

### Projects
- `GET /api/projects/` - List projects (public)
- `GET /api/projects/{id}/` - Get project details (public)
- `POST /api/projects/` - Create project (admin/editor only)
- `PATCH /api/projects/{id}/` - Update project (admin/editor only)
- `DELETE /api/projects/{id}/` - Delete project (admin/editor only)

### Admin Panel
Access the Django admin at: http://localhost:8000/admin/

---

## 📖 Documentation for Frontend Developers

**👉 [FRONTEND_INTEGRATION_GUIDE.md](FRONTEND_INTEGRATION_GUIDE.md) - COMPLETE FRONTEND GUIDE**

This single comprehensive document contains everything your frontend team needs:
- Understanding User vs Profile architecture
- Quick start configuration with profile ID
- Authentication system implementation
- Complete code examples (React/Next.js)
- Full API reference
- Troubleshooting guide
- Deployment checklist

**Additional Resources:**
- **[API_INTEGRATION_GUIDE.md](API_INTEGRATION_GUIDE.md)** - Detailed API endpoint documentation

## User Roles

The system supports three user roles with hierarchical permissions:

1. **Super Admin**: Full access to all features
   - Manage all users (create, update, delete)
   - Assign roles to other users
   - Access all admin functionalities
   - Full CRUD on all content

2. **Editor**: Can edit content
   - View and respond to messages
   - Edit portfolio content
   - Cannot manage users

3. **Viewer**: Read-only access
   - View public content
   - Send contact messages

### Super Admin Account

**Default Super Admin:**
- **Email:** `juliustetteh@gmail.com`
- **Password:** `pa$$word123`
- **Role:** Super Admin (Full Access)

⚠️ **Security Note:** Change the default password after initial setup:
```bash
python manage.py changepassword juliustetteh@gmail.com
```

**Access Points:**
- **API Login:** POST http://localhost:8000/api/auth/login/
- **Admin Panel:** http://localhost:8000/admin/
- **API Docs:** http://localhost:8000/api/docs/

**📖 For detailed user management instructions, see [USER_MANAGEMENT.md](USER_MANAGEMENT.md)**
   - Manage own profile

## User Account Management

### Super Admin Account

The primary super admin account is configured as:
- **Email**: `juliustetteh@gmail.com`
- **Password**: `pa$$word123` (⚠️ **Change after first login**)
- **Role**: Super Admin
- **Permissions**: Full system access, Django admin panel, user management

You can login at:
- **API**: `POST /api/auth/login/` (see API_INTEGRATION_GUIDE.md)
- **Admin Panel**: http://localhost:8000/admin/

### Interactive Management Script

Use the provided script for easy user management:

```bash
source venv/bin/activate
python manage_users.py
```

**Available Operations:**
- List all users with their roles and status
- Create new user accounts with specific roles
- Update user roles (Viewer → Editor → Super Admin)
- Verify user email addresses
- Activate/Deactivate user accounts
- Reset user passwords
- Delete user accounts

### Command Line User Creation

Create users via Django shell:

```bash
python manage.py shell
```

```python
from accounts.models import User, UserRole

# Create a viewer (default role)
user = User.objects.create_user(
    email='user@example.com',
    password='securepassword',
    first_name='John',
    last_name='Doe'
)

# Create an editor
editor = User.objects.create_user(
    email='editor@example.com',
    password='securepassword',
    first_name='Jane',
    last_name='Editor',
    role=UserRole.EDITOR
)

# Create a super admin
admin = User.objects.create_superuser(
    email='admin@example.com',
    password='securepassword',
    first_name='Admin',
    last_name='User'
)
```

### Default Super Admin

The system has a pre-configured super admin account:
- **Email**: juliustetteh@gmail.com
- **Password**: pa$$word123
- **Role**: Super Admin

**Security Note**: Change this password immediately in production!

## Environment Variables

Key environment variables (see `.env.example` for full list):

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL settings shown; set DB_ENGINE=django.db.backends.sqlite3 to fall back)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=portfolio_db
DB_USER=portfolio_user
DB_PASSWORD=strongpassword
DB_HOST=localhost
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# JWT
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7

# Email (for production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Security Features

- JWT token authentication
- Password hashing with Django's PBKDF2
- Rate limiting on authentication endpoints
- CORS configuration
- CSRF protection
- MFA with TOTP (Google Authenticator compatible)
- Backup codes for MFA recovery
- User activity tracking
- Email verification

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files
```bash
python manage.py collectstatic
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Configure a production database (PostgreSQL recommended)
3. Set up proper `ALLOWED_HOSTS`
4. Configure email backend for SMTP
5. Use a web server (Gunicorn/uWSGI) with Nginx
6. Enable HTTPS
7. Set up proper media and static file serving
8. Configure database backups
9. Set up monitoring and logging

### Example Production Settings
```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/portfolio_db
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

## CI/CD & Deployment

The backend is deployed automatically via the GitHub Actions workflow located at `.github/workflows/backend-ci-cd.yml`. A push to the `main` branch triggers the workflow, which:

- installs dependencies and runs `python manage.py test` in the action runner,
- copies the repository (excluding `.git*`, the local `venv`, `media`, `db.sqlite3`, and IDE folders) to the remote `/var/www/portfolio/backend`, and
- connects over SSH to prepare the server (`python3 -m venv venv`, `pip install -r requirements.txt`, `python manage.py migrate --noinput`, `mkdir -p media`).

### Required GitHub secrets

| Secret | Description |
|--------|-------------|
| `DEPLOY_HOST` | Remote host (currently `68.66.251.79`). |
| `DEPLOY_PORT` | SSH port (`7822`). |
| `DEPLOY_USER` | SSH user (`deploy`). |
| `DEPLOY_KEY` | Private SSH key for the `deploy` account (PEM/ed25519 with a trailing newline). |
| `DEPLOY_PATH` | Target directory (`/var/www/portfolio/backend`). |

Make sure the private key you store in `DEPLOY_KEY` has access to the remote server and that the corresponding public key is installed for `deploy@68.66.251.79`. You can test connectivity manually with `ssh -p 7822 deploy@68.66.251.79` before relying on the workflow.

### Remote prerequisites

- Install the system dependencies on the server (run once manually):
   ```bash
   sudo apt update && sudo apt install -y python3 python3-venv python3-pip
   ```
- The workflow will create (if missing) a virtual environment inside `/var/www/portfolio/backend/venv`, install the Python dependencies, run database migrations, and create the `media` directory so uploads persist across releases.
- Avoid making manual edits inside `/var/www/portfolio/backend`; always deploy through GitHub push so the workflow can keep the remote copy in sync.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is proprietary software.

## Support

For issues and questions, please open an issue on the repository.

## Changelog

### Version 1.0.0
- Initial release
- User authentication with JWT
- Multi-factor authentication
- Portfolio management features
- API documentation
- Role-based access control
