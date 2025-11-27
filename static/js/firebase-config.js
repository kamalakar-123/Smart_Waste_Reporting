// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCDgmjU6brQJ8YdsKPsUwHri9u08rrSYbc",
  authDomain: "smart-waste-reporting.firebaseapp.com",
  projectId: "smart-waste-reporting",
  storageBucket: "smart-waste-reporting.firebasestorage.app",
  messagingSenderId: "317537334400",
  appId: "1:317537334400:web:07921b869b797b6c496265"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export { app, auth };
