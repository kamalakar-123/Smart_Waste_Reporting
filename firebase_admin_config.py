import firebase_admin
from firebase_admin import credentials, auth
import os

# Initialize Firebase Admin SDK
# Note: For production, use a service account key file
# For now, we'll use the application default credentials
try:
    if not firebase_admin._apps:
        # If you have a service account key, uncomment and use this:
        # cred = credentials.Certificate('path/to/serviceAccountKey.json')
        # firebase_admin.initialize_app(cred)
        
        # Using default credentials (works with environment variables)
        firebase_admin.initialize_app()
        print("Firebase Admin initialized successfully")
except Exception as e:
    print(f"Firebase Admin initialization error: {e}")
    # Continue without Firebase if initialization fails
    pass

def verify_firebase_token(id_token):
    """
    Verify Firebase ID token and return decoded token
    Returns None if token is invalid
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Token verification error: {e}")
        return None

def get_firebase_user(uid):
    """
    Get Firebase user by UID
    """
    try:
        user = auth.get_user(uid)
        return user
    except Exception as e:
        print(f"Error getting Firebase user: {e}")
        return None
