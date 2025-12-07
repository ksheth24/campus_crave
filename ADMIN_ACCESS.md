# Admin Access Instructions

## Quick Access
1. Start the server: `python manage.py runserver`
2. Navigate to: http://127.0.0.1:8000/admin/
3. Login with:
   - Username: `admin`
   - Password: `admin123`

## Create a New Admin Account

If you need to create a new superuser account:

```bash
python manage.py createsuperuser
```

This will prompt you for:
- Username
- Email (optional)
- Password

## Reset Admin Password

If you forgot the admin password:

```bash
python manage.py changepassword admin
```

Or for any user:
```bash
python manage.py changepassword <username>
```

## Admin Features

Once logged in, you can:

1. **Review Seller Verification Applications**
   - Go to: Accounts → Seller verification applications
   - View pending applications
   - Click "View ID Document" to see uploaded student IDs
   - Click "Approve" or "Reject" for individual applications
   - Use bulk actions to approve/reject multiple applications

2. **Manage Users**
   - Go to: Authentication and Authorization → Users
   - View all user accounts
   - Edit user details

3. **Manage User Profiles**
   - Go to: Accounts → User profiles
   - View verified seller status
   - Manually verify/unverify sellers

4. **Manage Meals**
   - Go to: Accounts → Meals
   - View all meal listings
   - Edit or delete meals

## Troubleshooting

**Can't access admin panel?**
- Make sure you're using a superuser account (staff users cannot access admin)
- Check that the user has `is_staff=True` and `is_superuser=True`

**Create superuser programmatically:**
```python
python manage.py shell
```
Then run:
```python
from django.contrib.auth.models import User
User.objects.create_superuser('username', 'email@example.com', 'password')
```

