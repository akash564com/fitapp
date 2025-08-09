// Handles chat UI and calls /api/chat
export async function sendChat(prompt) {
    const res = await fetch('/api/chat', {
        method: 'POST',
     
