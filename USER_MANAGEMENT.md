# User Account Management - Quick Reference

## Current Super Admin

**Email**: juliustetteh@gmail.com  
**Password**: pa$$word123  
**Role**: Super Admin  
**Access**: Full system control

⚠️ **Security**: Change the default password after first login!

---

## Login Methods

### 1. API Login (for applications)

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juliustetteh@gmail.com",
    "password": "pa$$word123"
  }'
```

**Response** includes JWT tokens for authenticated requests.

### 2. Admin Panel (for web interface)

URL: http://localhost:8000/admin/  
Login with: juliustetteh@gmail.com / pa$$word123

---

## Managing Users

### Interactive Script (Recommended)

```bash
source venv/bin/activate
python manage_users.py
```

**Menu Options:**
1. List all users
2. Create new user
3. Update user role
4. Verify user email
5. Activate user
6. Deactivate user
7. Reset user password
8. Delete user

### Quick Commands

#### Create a new Editor

```bash
python manage.py shell -c "
from accounts.models import User, UserRole
User.objects.create_user(
    email='editor@example.com',
    password='password123',
    first_name='Editor',
    last_name='User',
    role=UserRole.EDITOR
)
print('Editor created successfully')
"
```

#### Create a new Viewer

```bash
python manage.py shell -c "
from accounts.models import User, UserRole
User.objects.create_user(
    email='viewer@example.com',
    password='password123',
    first_name='Viewer',
    last_name='User',
    role=UserRole.VIEWER
)
print('Viewer created successfully')
"
```

#### Change User Role to Editor

```bash
python manage.py shell -c "
from accounts.models import User, UserRole
user = User.objects.get(email='viewer@example.com')
user.role = UserRole.EDITOR
user.save()
print(f'User {user.email} is now an Editor')
"
```

#### Deactivate a User

```bash
python manage.py shell -c "
from accounts.models import User
user = User.objects.get(email='user@example.com')
user.is_active = False
user.save()
print(f'User {user.email} deactivated')
"
```

---

## User Roles & Permissions

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Super Admin** | Full system access, user management, all CRUD operations | Site owner, primary administrator |
| **Editor** | Edit content, respond to messages, manage portfolio | Content managers, collaborators |
| **Viewer** | Read content, send messages, manage own profile | Regular users, visitors |

---

## API Endpoints for User Management

All endpoints require Super Admin authentication.

### List Users
```
GET /api/auth/users/
Authorization: Bearer <access_token>
```

### Get User Details
```
GET /api/auth/users/{user_id}/
Authorization: Bearer <access_token>
```

### Update User Role
```
PATCH /api/auth/users/{user_id}/update_role/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "role": "editor"
}
```

### Activate User
```
POST /api/auth/users/{user_id}/activate/
Authorization: Bearer <access_token>
```

### Deactivate User
```
POST /api/auth/users/{user_id}/deactivate/
Authorization: Bearer <access_token>
```

---

## Security Best Practices

1. **Change default password immediately**
   ```bash
   python manage_users.py
   # Select option 7 (Reset user password)
   # Enter: juliustetteh@gmail.com
   # Set new strong password
   ```

2. **Use strong passwords**
   - Minimum 8 characters
   - Mix of uppercase, lowercase, numbers, symbols
   - Avoid common words

3. **Limit Super Admin accounts**
   - Create only necessary Super Admin accounts
   - Use Editor role for content managers
   - Use Viewer role for regular users

4. **Regular audits**
   ```bash
   python manage_users.py
   # Select option 1 to review all users
   # Deactivate unused accounts
   ```

5. **Enable MFA for Super Admins**
   - Login to API
   - Call `POST /api/auth/mfa/setup/`
   - Scan QR code with authenticator app
   - Save backup codes securely

---

## Troubleshooting

### Forgot Super Admin Password?

Reset via command line:
```bash
python manage.py shell -c "
from accounts.models import User
user = User.objects.get(email='juliustetteh@gmail.com')
user.set_password('new_password_here')
user.save()
print('Password reset successfully')
"
```

### User Can't Login?

Check user status:
```bash
python manage.py shell -c "
from accounts.models import User
user = User.objects.get(email='user@example.com')
print(f'Active: {user.is_active}')
print(f'Verified: {user.is_verified}')
print(f'Role: {user.role}')
"
```

### Need to Create Emergency Super Admin?

```bash
python manage.py createsuperuser
# Follow prompts to create new super admin
```

---

## Additional Resources

- **Full API Documentation**: `API_INTEGRATION_GUIDE.md`
- **Main README**: `README.md`
- **User Management Script**: `manage_users.py`
- **Django Admin**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/docs/

---

**Last Updated**: November 20, 2025
