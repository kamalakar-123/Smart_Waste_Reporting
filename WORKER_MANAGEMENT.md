# 👷 Worker Management Guide for Admins

## Overview

As an admin, you have complete control over worker accounts. Workers cannot self-register - only admins can create and manage worker accounts through the Admin Dashboard.

## 🎯 Key Features

### 1. Add New Worker
- Create worker accounts with name, email, and password
- Workers are automatically assigned the "worker" role
- Workers can login and access the Worker Dashboard
- Credentials are not publicly visible

### 2. Remove Worker
- View list of all active workers
- Remove workers who are no longer needed
- Automatic validation prevents removal if worker has active tasks
- Deletes both authentication and database records

## 📋 How to Add a New Worker

### Step 1: Access Admin Dashboard
1. Login as admin
2. Navigate to Admin Dashboard

### Step 2: Click "Add New Worker"
1. Scroll to the "Worker Management" section
2. Click the **"Add New Worker"** button in the top-right

### Step 3: Fill Worker Details
In the modal form, enter:
- **Worker Name** (required): Full name of the worker
- **Email Address** (required): Must be a valid email
- **Phone Number** (optional): Contact number
- **Password** (required): At least 6 characters
- **Confirm Password** (required): Must match the password

### Step 4: Create Account
1. Click **"Create Worker Account"**
2. System validates the information
3. If successful: "Worker account created successfully"
4. The modal closes and the workers list refreshes

### Step 5: Share Credentials
**IMPORTANT**: Securely share the login credentials with the worker:
- Email address
- Password

The worker can now login at: `/login`

## 🗑️ How to Remove a Worker

### Step 1: View Workers List
Scroll to the "Active Workers" table in the Worker Management section

The table shows:
- Worker Name
- Email Address
- Phone Number
- Completed Tasks count
- Join Date
- Remove button

### Step 2: Click Remove
Click the **"Remove"** button next to the worker you want to delete

### Step 3: Confirm Removal
A confirmation dialog appears with warnings:
```
Are you sure you want to remove [Worker Name]?

This will:
- Delete their account
- Remove all authentication access
- This action cannot be undone
```

Click **OK** to confirm or **Cancel** to abort

### Step 4: Validation
The system checks:
- ✅ Worker exists
- ✅ User is actually a worker (not admin/user)
- ✅ No active complaints assigned

If worker has active complaints:
```
Cannot remove worker. They have X active complaint(s). 
Please reassign or complete them first.
```

### Step 5: Removal Complete
If successful:
- Worker deleted from database
- Firebase authentication removed (if applicable)
- Success message displayed
- Workers list automatically refreshes

## 🔐 Security Features

### Access Control
- ✅ Only admins can access worker management
- ✅ API endpoints protected with role validation
- ✅ Unauthorized access returns 403 Forbidden

### Password Handling
- ✅ Passwords hashed before storage (backup)
- ✅ Firebase handles primary authentication
- ✅ Admin cannot view existing passwords
- ✅ Minimum 6 character requirement

### Validation
- ✅ Email format validation
- ✅ Duplicate email prevention
- ✅ Password confirmation required
- ✅ Active complaint check before removal

## 📊 Workers List Information

The workers table displays:

| Column | Description |
|--------|-------------|
| **Name** | Full name of the worker |
| **Email** | Login email address |
| **Phone** | Contact number |
| **Completed Tasks** | Number of complaints resolved |
| **Joined** | Account creation date |
| **Actions** | Remove button |

## ⚠️ Important Notes

### Cannot Remove Workers With Active Tasks
Workers with pending/in-progress complaints cannot be removed:
- Prevents data loss
- Ensures accountability
- Maintains complaint history

**Solution**: Before removing a worker:
1. Reassign their active complaints to other workers
2. Or wait for them to complete their tasks

### Self-Registration Prevention
- Workers CANNOT register themselves
- Registration page only creates user/admin accounts
- Worker role can ONLY be assigned by admin

### Worker Login Flow
When a worker logs in:
1. Enters email/password at `/login`
2. Firebase verifies credentials
3. System checks role in database
4. If role = "worker" → Redirect to Worker Dashboard
5. Access to worker-specific features

## 🎯 Best Practices

### Creating Workers
1. **Use professional emails**: Company email addresses preferred
2. **Strong passwords**: Minimum 6 chars, suggest 8+ with mix of characters
3. **Keep records**: Maintain a list of active workers externally
4. **Secure sharing**: Use secure channels to share credentials

### Managing Workers
1. **Regular review**: Periodically review active workers list
2. **Remove inactive**: Delete accounts no longer needed
3. **Monitor performance**: Check completed tasks count
4. **Update contact info**: Keep phone numbers current

### Security
1. **Change default passwords**: Encourage workers to change passwords after first login
2. **Audit trail**: Monitor worker activity through complaint logs
3. **Immediate removal**: Remove access immediately when worker leaves
4. **No sharing**: Each worker should have unique credentials

## 🔄 Worker Lifecycle

```
1. Admin creates worker account
   ↓
2. Admin shares credentials securely
   ↓
3. Worker logs in with email/password
   ↓
4. Worker redirected to Worker Dashboard
   ↓
5. Worker manages assigned complaints
   ↓
6. When done: Admin removes worker account
```

## 💡 Tips

### For Efficient Management
- Create workers in batches if onboarding multiple
- Use consistent naming convention
- Document password requirements for workers
- Keep emergency contact info updated

### Troubleshooting
**Worker can't login?**
- Verify email is correct (case-insensitive)
- Check password was shared correctly
- Ensure account was created successfully
- Check if Email/Password is enabled in Firebase Console

**Can't remove worker?**
- Check for active complaints
- View worker's complaint history
- Reassign or complete pending tasks first

**Duplicate email error?**
- Email already exists in system
- Check if user/admin has this email
- Use different email address

## 📞 Common Scenarios

### Scenario 1: Onboarding New Worker
```
1. Admin logs into Admin Dashboard
2. Clicks "Add New Worker"
3. Enters: Name: "John Smith", Email: "john@company.com", Password: "secure123"
4. Clicks "Create Worker Account"
5. Success! Admin shares credentials with John
6. John logs in and accesses Worker Dashboard
```

### Scenario 2: Worker Leaving Organization
```
1. Admin reviews worker's active complaints
2. Reassigns pending tasks to other workers
3. In Admin Dashboard, clicks "Remove" next to worker
4. Confirms deletion
5. Worker account deleted immediately
6. Worker can no longer access system
```

### Scenario 3: Worker Forgot Password
```
Option 1 (Firebase):
- Use Firebase Console to send password reset email
- Worker resets password via email link

Option 2 (Admin):
- Admin removes old worker account
- Admin creates new account with same email
- Admin shares new password
```

## 🎓 Training Workers

Once created, ensure workers know:
1. How to login (URL: `/login`)
2. Their email and password
3. How to access Worker Dashboard
4. How to manage complaints
5. Who to contact for issues (admin)

---

## 🚀 Quick Reference

**Add Worker**: Admin Dashboard → "Add New Worker" → Fill form → Create

**Remove Worker**: Admin Dashboard → Workers list → "Remove" → Confirm

**Worker Login**: `/login` → Email + Password → Worker Dashboard

**View Workers**: Admin Dashboard → "Active Workers" table

---

**Remember**: Only admins can create and manage workers. This ensures proper access control and accountability in your waste management system! 👑
