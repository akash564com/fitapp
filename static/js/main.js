// main.js - utility UI behaviors shared across the site
export function showToast(msg, ms = 3000){
  let t = document.querySelector('.site-toast');
  if(!t){
    t = document.createElement('div');
    t.className = 'site-toast';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.classList.add('visible');
  clearTimeout(t._hideTimer);
  t._hideTimer = setTimeout(()=> t.classList.remove('visible'), ms);
}

export function initLanguageSwitcher(buttonSelector){
  const btn = document.querySelector(buttonSelector);
  if(!btn) return;
  btn.addEventListener('click', async ()=>{
    const lang = document.documentElement.lang === 'en' ? 'hi' : 'en';
    document.documentElement.lang = lang;
    try{
      const res = await fetch(`/static/translations/${lang}.json`);
      const translations = await res.json();
      document.querySelectorAll('[data-i18n]').forEach(el=>{
        const key = el.getAttribute('data-i18n');
        if(translations && translations[key]) el.textContent = translations[key];
      });
      showToast('Language switched');
    }catch(err){
      console.error(err);
      showToast('Could not load translations');
    }
  });
}

export function initAuthUI(){
  if(window.onAuthChange){
    window.onAuthChange(({loggedIn, user})=>{
      document.querySelectorAll('.auth-logged-in').forEach(el=> el.style.display = loggedIn ? '' : 'none');
      document.querySelectorAll('.auth-logged-out').forEach(el=> el.style.display = loggedIn ? 'none' : '');
      const nameEls = document.querySelectorAll('[data-user-name]');
      nameEls.forEach(el=> el.textContent = user ? (user.displayName || user.email || '') : '');
    });
  }
}
