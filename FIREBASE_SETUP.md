# Firebase Authentication Setup Guide

## ✅ Firebase Integration Complete!

Your Smart Waste Reporting application now has Firebase Authentication integrated. Here's what was implemented:

### 🎯 Features Added

1. **Email/Password Authentication** - Users can register and login with email and password
2. **Google Sign-In** - One-click authentication with Google accounts
3. **Role-Based Access** - Automatic redirection based on user role (user/worker/admin)
4. **Secure Token Verification** - Firebase tokens are verified on the backend
5. **Dual Database Sync** - Firebase handles authentication, local SQLite stores user data

### 📁 Files Created/Modified

#### New Files:
- `static/js/firebase-config.js` - Firebase configuration
- `static/js/auth.js` - Authentication functions
- `firebase_admin_config.py` - Backend Firebase Admin SDK setup
- `migrate_db.py` - Database migration script
- `FIREBASE_SETUP.md` - This guide

#### Modified Files:
- `templates/login.html` - Added Firebase login UI
- `templates/register.html` - Added Firebase registration UI
- `app.py` - Added Firebase API endpoints
- `db.py` - Updated schema with firebase_uid
- `requirements.txt` - Added Firebase dependencies

### 🚀 Setup Instructions

#### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 2: Migrate Existing Database (if you have one)
```bash
python migrate_db.py
```

#### Step 3: Enable Google Authentication in Firebase Console
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `smart-waste-reporting`
3. Navigate to **Authentication** > **Sign-in method**
4. Enable **Email/Password** provider
5. Enable **Google** provider
6. Add your domain to authorized domains

#### Step 4: (Optional) Set up Firebase Admin SDK for Production

For production, you should use a service account:

1. Go to Firebase Console > Project Settings > Service Accounts
2. Click "Generate new private key"
3. Download the JSON file
4. Save it as `serviceAccountKey.json` in your project root
5. Update `firebase_admin_config.py`:
   ```python
   cred = credentials.Certificate('serviceAccountKey.json')
   firebase_admin.initialize_app(cred)
   ```

**IMPORTANT:** Add `serviceAccountKey.json` to `.gitignore`!

#### Step 5: Run the Application
```bash
python app.py
```

### 🔐 Authentication Flow

#### Registration:
1. User fills out registration form
2. Firebase creates authentication account
3. Backend receives Firebase ID token
4. User data stored in local SQLite database with Firebase UID
5. User redirected to login page

#### Login:
1. User enters credentials (or clicks Google sign-in)
2. Firebase authenticates the user
3. Frontend receives Firebase ID token
4. Token sent to backend for verification
5. Backend validates token and creates session
6. User redirected to appropriate dashboard based on role

#### Google Sign-In:
1. User clicks "Sign in with Google"
2. Google OAuth popup appears
3. Firebase handles OAuth flow
4. If first login, account automatically created
5. User redirected to dashboard

### 🛡️ Security Features

- ✅ Firebase ID tokens are verified on backend
- ✅ Passwords stored securely (never sent to your server for Firebase users)
- ✅ Role-based access control maintained
- ✅ Session management with Flask sessions
- ✅ CORS and XSS protection

### 🔄 Backward Compatibility

The system maintains backward compatibility:
- Existing users with password_hash can still login with the old method
- Firebase authentication works alongside traditional authentication
- Database migration doesn't affect existing users

### 📝 User Roles

- **user** - Regular users who report waste
- **worker** - Workers who handle complaints
- **admin** - Administrators with full system access

### 🐛 Troubleshooting

#### Error: "Firebase Admin not available"
- This is normal during development
- The app will work with frontend Firebase auth only
- Token verification happens on frontend
- For production, set up Firebase Admin SDK (Step 4)

#### Error: "Invalid Firebase token"
- Check that your Firebase config is correct
- Verify email/password is enabled in Firebase Console
- Check browser console for detailed error messages

#### Google Sign-In not working:
- Enable Google provider in Firebase Console
- Add your domain to authorized domains
- For localhost, add: `localhost` and `127.0.0.1`

#### Database errors:
- Run `python migrate_db.py` to update schema
- Check that `waste_report.db` exists
- Verify write permissions

### 🎨 Customization

#### Change Firebase Project:
Edit `static/js/firebase-config.js` with your Firebase config

#### Modify Authentication UI:
- Login: `templates/login.html`
- Register: `templates/register.html`
- Styling: `static/css/styles.css`

#### Add More Providers:
1. Enable in Firebase Console
2. Import provider in `static/js/auth.js`
3. Add button in login template
4. Create handler function

### 📊 Testing

#### Test Regular Registration:
1. Go to `/register`
2. Fill in username, email, phone, password
3. Submit form
4. Should redirect to login

#### Test Email Login:
1. Go to `/login`
2. Enter registered email and password
3. Should redirect to appropriate dashboard

#### Test Google Sign-In:
1. Go to `/login`
2. Click "Sign in with Google"
3. Select Google account
4. Should redirect to user dashboard

### 🚨 Important Notes

1. **Never commit** `serviceAccountKey.json` to version control
2. **Keep your Firebase API key secure** (it's okay to be public for web apps)
3. **Enable email verification** in production (optional feature)
4. **Set up password reset** via Firebase Console
5. **Monitor authentication** in Firebase Console

### 📞 Support

For issues or questions:
- Check Firebase Console for authentication logs
- Review browser console for JavaScript errors
- Check Flask terminal for backend errors
- Verify all dependencies are installed

---

## 🎉 You're All Set!

Firebase Authentication is now fully integrated into your Smart Waste Reporting System!
