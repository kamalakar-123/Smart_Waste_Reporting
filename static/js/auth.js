// Firebase Authentication Module
import { auth } from './firebase-config.js';
import { 
    createUserWithEmailAndPassword, 
    signInWithEmailAndPassword,
    signOut,
    onAuthStateChanged,
    GoogleAuthProvider,
    signInWithPopup
} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

// Register new user with email and password
export async function registerWithEmail(email, password, username, phone, role = 'user') {
    try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
        
        // Get Firebase ID token
        const idToken = await user.getIdToken();
        
        // Send user data to backend
        const response = await fetch('/api/firebase-register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                idToken: idToken,
                username: username,
                email: email,
                phone: phone,
                role: role,
                firebase_uid: user.uid
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            return { success: true, user: user, data: data };
        } else {
            // If backend registration fails, we should delete the Firebase user
            await user.delete();
            return { success: false, error: data.message || 'Registration failed' };
        }
    } catch (error) {
        console.error('Registration error:', error);
        return { success: false, error: error.message };
    }
}

// Login with email and password
export async function loginWithEmail(email, password) {
    try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
        
        // Get Firebase ID token
        const idToken = await user.getIdToken();
        
        // Verify with backend
        const response = await fetch('/api/firebase-login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                idToken: idToken,
                email: email
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            return { success: true, user: user, data: data };
        } else {
            return { success: false, error: data.message || 'Login failed' };
        }
    } catch (error) {
        console.error('Login error:', error);
        let errorMessage = 'Login failed';
        
        if (error.code === 'auth/user-not-found') {
            errorMessage = 'Email not found. Please register first.';
        } else if (error.code === 'auth/wrong-password') {
            errorMessage = 'Incorrect password. Please try again.';
        } else if (error.code === 'auth/invalid-email') {
            errorMessage = 'Invalid email address.';
        } else if (error.code === 'auth/user-disabled') {
            errorMessage = 'This account has been disabled.';
        } else if (error.code === 'auth/invalid-credential') {
            errorMessage = 'Invalid email or password. Please check your credentials or register if you haven\'t already.';
        } else if (error.code === 'auth/too-many-requests') {
            errorMessage = 'Too many failed login attempts. Please try again later.';
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        return { success: false, error: errorMessage };
    }
}

// Login with Google
export async function loginWithGoogle() {
    try {
        const provider = new GoogleAuthProvider();
        const result = await signInWithPopup(auth, provider);
        const user = result.user;
        
        // Get Firebase ID token
        const idToken = await user.getIdToken();
        
        // Verify with backend
        const response = await fetch('/api/firebase-login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                idToken: idToken,
                email: user.email,
                username: user.displayName,
                firebase_uid: user.uid,
                is_google_auth: true
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            return { success: true, user: user, data: data };
        } else {
            return { success: false, error: data.message || 'Login failed' };
        }
    } catch (error) {
        console.error('Google login error:', error);
        return { success: false, error: error.message };
    }
}

// Logout
export async function logout() {
    try {
        await signOut(auth);
        
        // Clear backend session
        await fetch('/logout', {
            method: 'GET'
        });
        
        return { success: true };
    } catch (error) {
        console.error('Logout error:', error);
        return { success: false, error: error.message };
    }
}

// Monitor auth state changes
export function onAuthChange(callback) {
    return onAuthStateChanged(auth, callback);
}

// Get current user
export function getCurrentUser() {
    return auth.currentUser;
}

// Get ID token for current user
export async function getIdToken() {
    const user = auth.currentUser;
    if (user) {
        return await user.getIdToken();
    }
    return null;
}
