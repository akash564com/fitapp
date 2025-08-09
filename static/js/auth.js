// Firebase modular v9+ example
import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.24.0/firebase-app.js';
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, onAuthStateChanged, signOut } from 'https://www.gstatic.com/firebasejs/9.24.0/firebase-auth.js';

const firebaseConfig = {
    // replace with your firebase config
    apiKey: "REPLACE",
    authDomain: "REPLACE",
    projectId: "REPLACE",
    storageBucket: "REPLACE",
    messagingSenderId: "REPLACE",
    appId: "REPLACE"
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
