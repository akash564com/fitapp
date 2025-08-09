// Firebase modular v9+ example
import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.24.0/firebase-app.js';
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, onAuthStateChanged, signOut } from 'https://www.gstatic.com/firebasejs/9.24.0/firebase-auth.js';

const firebaseConfig = {
  apiKey: "AIzaSyDW6WAqJ4kDumFgdrsR99Xcy4ipH3ePBoY",
  authDomain: "fitai-app-fe8df.firebaseapp.com",
  projectId: "fitai-app-fe8df",
  storageBucket: "fitai-app-fe8df.firebasestorage.app",
  messagingSenderId: "519087526504",
  appId: "1:519087526504:web:6005a09cfc553ed5c421dd"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export async function signIn(email, password){
    const res = await signInWithEmailAndPassword(auth, email, password);
    const idToken = await res.user.getIdToken();
    // send idToken to server to create session
    await fetch('/api/auth/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idToken })
    });
    return res.user;
}

export async function signUp(email, password){
    const res = await createUserWithEmailAndPassword(auth, email, password);
    const idToken = await res.user.getIdToken();
    await fetch('/api/auth/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idToken })
    });
    return res.user;
}

export async function logout(){
    await fetch('/api/auth/logout', { method: 'POST' });
    return await signOut(auth);
}

export function onAuthChange(cb){
    onAuthStateChanged(auth, async (user) => {
        if (user) {
            const token = await user.getIdToken();
            cb({ loggedIn: true, user, token });
        } else cb({ loggedIn: false });
    });
}
