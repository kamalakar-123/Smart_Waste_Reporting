# 🚀 Firebase Authentication - Quick Reference

## Installation (One-Time Setup)

```bash
# Run the automated setup script
python setup_firebase.py

# OR manually:
pip install -r requirements.txt
python migrate_db.py
```

## Enable Firebase Authentication

1. Go to: https://console.firebase.google.com/project/smart-waste-reporting/authentication
2. Click **Sign-in method** tab
3. Enable **Email/Password** provider
4. Enable **Google** provider
5. Save changes

## Running the Application

```bash
python app.py
```

Then open: http://localhost:5000

## Quick Test

### Test Registration:
- Navigate to `/register`
- Enter: username, email, password
- Click "Register"
- Should redirect to login

### Test Email Login:
- Navigate to `/login`
- Enter your email and password
- Click "Login"
- Should redirect to dashboard

### Test Google Login:
- Navigate to `/login`
- Click "Sign in with Google"
- Select your Google account
- Should redirect to dashboard

## User Roles & Dashboards

| Role | Dashboard URL | Description |
|------|--------------|-------------|
| user | `/user/dashboard` | Regular users who report waste |
| worker | `/worker/dashboard` | Workers who handle complaints |
| admin | `/admin/dashboard` | System administrators |

## Key Files

| File | Purpose |
|------|---------|
| `static/js/firebase-config.js` | Firebase configuration |
| `static/js/auth.js` | Authentication functions |
| `firebase_admin_config.py` | Backend Firebase setup |
| `templates/login.html` | Login page with Firebase |
| `templates/register.html` | Registration page |

## API Endpoints

- `POST /api/firebase-register` - Register new user
- `POST /api/firebase-login` - Login with Firebase token
- `GET /logout` - Logout user

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Migrate database
python migrate_db.py

# Run setup wizard
python setup_firebase.py

# Run application
python app.py
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Module not found" | Run: `pip install -r requirements.txt` |
| "Firebase not available" | Normal in dev - app works without Admin SDK |
| "Database locked" | Close the app and try again |
| Google sign-in fails | Enable Google provider in Firebase Console |
| Token verification fails | Check Firebase config in firebase-config.js |

## Environment Variables (Optional)

Create a `.env` file for production:

```
FLASK_SECRET_KEY=your-secret-key-here
FIREBASE_PROJECT_ID=smart-waste-reporting
```

## Security Checklist

- ✅ Add `.gitignore` (already done)
- ✅ Never commit `serviceAccountKey.json`
- ✅ Change `SECRET_KEY` in production
- ✅ Enable Firebase security rules
- ✅ Use HTTPS in production
- ✅ Enable email verification (optional)

## Links

- **Firebase Console**: https://console.firebase.google.com/project/smart-waste-reporting
- **Documentation**: See `FIREBASE_SETUP.md`
- **Project**: https://github.com/kamalakar-123/Smart_Waste_Reporting

---

Need help? Check `FIREBASE_SETUP.md` for detailed instructions!
