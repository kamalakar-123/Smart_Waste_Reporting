# 👑 Admin Account Setup Guide

## Overview

The Smart Waste Reporting System now uses **email-based admin access control**. Admin privileges are automatically granted to users who register with specific Gmail addresses.

## 🔐 Admin Email Addresses

The following Gmail IDs have **automatic admin access**:

| Admin Name | Gmail ID | Password (Firebase) |
|------------|----------|---------------------|
| Krishna | krishnakattimanimb@gmail.com | krishna@123 |
| Kamalakara | kamalakaramarathi13@gmail.com | kamalakara@123 |
| Dayananda | dayanandaks045@gmail.com | Daya@123 |
| Darshan | darshan99806@gmail.com | darshan@123 |

## 🚀 How It Works

### 1. **Automatic Role Assignment**
- When a user registers or logs in, the system checks their email against the admin list
- If the email matches, they are automatically assigned the **admin** role
- All other users get the **user** role by default

### 2. **No Password Storage**
- Passwords are **NEVER stored** in the local database
- Firebase Authentication handles all password verification
- The local database only stores user information and their assigned role

### 3. **Dynamic Role Updates**
- If an admin email is added to the list, that user will become an admin on their next login
- If removed from the list, they will be downgraded to regular user

## 📝 Setting Up Admin Accounts

### Step 1: Create Admin Accounts in Firebase

Each admin must create their Firebase account using their designated email:

1. **Go to the registration page**: http://localhost:5000/register
2. **Fill in the details**:
   - Username: (any name)
   - Email: (use the exact Gmail from the admin list)
   - Phone: (optional)
   - Password: (use the password specified above)
   - Confirm Password: (same as password)
3. **Click "Register"**
4. System will automatically detect the admin email and create an **admin account**

### Step 2: Login as Admin

1. **Go to login page**: http://localhost:5000/login
2. **Enter credentials**:
   - Email: (admin Gmail)
   - Password: (Firebase password)
3. **Click "Login"**
4. You will be redirected to the **Admin Dashboard**

### Alternative: Google Sign-In

Admins can also use **"Sign in with Google"** button:
- Click "Sign in with Google"
- Select the admin Gmail account
- System automatically grants admin access
- No password needed for Google authentication

## 🔧 Managing Admin Access

### Adding a New Admin

1. Open `admin_config.py`
2. Add the new email to the `ADMIN_EMAILS` list:
```python
ADMIN_EMAILS = [
    'krishnakattimanimb@gmail.com',
    'kamalakaramarathi13@gmail.com',
    'dayanandaks045@gmail.com',
    'darshan99806@gmail.com',
    'newemail@gmail.com'  # Add new admin here
]
```
3. Save the file
4. Restart the application
5. The new user will get admin access on their next login

### Removing an Admin

1. Open `admin_config.py`
2. Remove or comment out the email from `ADMIN_EMAILS` list
3. Save and restart the application
4. The user will be downgraded to regular user on their next login

## 🛡️ Security Features

✅ **Email-based access control** - Only specific Gmail IDs get admin access
✅ **Firebase password verification** - Secure authentication
✅ **No password storage** - Passwords never stored in local database
✅ **Automatic role sync** - Roles updated on every login
✅ **Centralized admin list** - Easy to manage in one file

## 🎯 Testing Admin Access

### Test 1: Register as Admin
```
Email: krishnakattimanimb@gmail.com
Password: krishna@123
Result: Should create account and show "Admin account created successfully"
```

### Test 2: Login as Admin
```
Email: krishnakattimanimb@gmail.com
Password: krishna@123
Result: Should redirect to Admin Dashboard at /admin/dashboard
```

### Test 3: Login as Regular User
```
Email: anyuser@gmail.com
Password: user123
Result: Should redirect to User Dashboard at /user/dashboard
```

## 📊 Admin Dashboard Features

Once logged in as admin, you can:

- ✅ View total users, workers, and complaints
- ✅ Monitor pending, in-progress, and completed complaints
- ✅ Access all reports via "View All Reports"
- ✅ Manage your profile

## 🚨 Important Notes

1. **Exact Email Match Required**
   - Email must match exactly (case-insensitive)
   - Use the Gmail addresses as listed above

2. **Firebase Account Required**
   - Each admin must create a Firebase account first
   - Use the registration page or Firebase Console

3. **Password Management**
   - Passwords are managed by Firebase
   - Use Firebase Console to reset passwords if needed
   - Link: https://console.firebase.google.com/project/smart-waste-reporting/authentication

4. **Worker Role**
   - To make someone a worker, manually update their role in the database
   - Workers are not managed through the email list

## 🔄 Password Reset

If an admin forgets their password:

1. Go to Firebase Console: https://console.firebase.google.com/project/smart-waste-reporting/authentication
2. Find the user by email
3. Click on the user
4. Send password reset email
5. Or delete the user and have them re-register

## 📞 Troubleshooting

### Issue: "Email not found. Please register first"
**Solution**: Admin needs to register using the registration page first

### Issue: Redirected to User Dashboard instead of Admin Dashboard
**Solution**: 
- Verify the email is exactly in the ADMIN_EMAILS list
- Check for typos in the email
- Restart the application after updating admin_config.py

### Issue: "Registration failed"
**Solution**:
- Email might already be registered
- Check Firebase Console for the account
- Try password reset or delete and re-register

### Issue: Google Sign-In not working
**Solution**:
- Enable Google provider in Firebase Console
- Make sure the Gmail is in the ADMIN_EMAILS list
- Check browser console for errors

## 📋 Admin Checklist

Before going live with admin accounts:

- [ ] All admin emails added to `admin_config.py`
- [ ] Each admin has created their Firebase account
- [ ] Tested login with each admin account
- [ ] Verified admin dashboard access
- [ ] Enabled Email/Password authentication in Firebase Console
- [ ] Enabled Google Sign-In in Firebase Console (if using)
- [ ] Passwords are secure and shared securely with admins
- [ ] `admin_config.py` is included in version control (emails are not sensitive)
- [ ] Regular backup of user database

## 🎉 Quick Start for Admins

**For Krishna, Kamalakara, Dayananda, and Darshan:**

1. **Register**: Go to http://localhost:5000/register
2. **Use your Gmail** from the list above
3. **Set your password** as specified
4. **Login**: Your account will have admin access automatically
5. **Access Admin Dashboard**: You'll see system statistics and management options

---

**Note**: This system provides flexible, email-based admin access without storing passwords locally, ensuring maximum security and ease of management.
