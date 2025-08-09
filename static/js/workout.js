// workout.js - request a workout plan and render it nicely
import { showToast } from './main.js';

export async function requestWorkout(formData){
  const res = await fetch('/api/workout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
  });
  return res.json();
}

function renderPlan(planText){
  const container = document.createElement('div');
  container.className = 'workout-plan';
  const lines = String(planText).split('\n');
  lines.forEach(line=>{
    if(!line.trim()) return;
    const el = document.createElement('p');
    if(/^\s*day\s*\d+/i.test(line) || /warm-?up/i.test(line) || /cool-?down/i.test(line)){
      el.className = 'plan-heading';
    } else if(/\d+\s*x\s*\d+/.test(line) || /sets?\b/i.test(line) || /reps?\b/i.test(line)){
      el.className = 'plan-exercise';
    } else {
      el.className = 'plan-text';
    }
    el.textContent = line.trim();
    container.appendChild(el);
  });
  return container;
}

export function initWorkoutForm(formSelector, outputSelector){
  const form = document.querySelector(formSelector);
  const out = document.querySelector(outputSelector);
  if(!form || !out) return;
  form.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form));
    out.innerHTML = '<div class="loading">Generating workout plan…</div>';
    try{
      const res = await requestWorkout(data);
      if(res.error){
        out.innerHTML = `<div class="error">${res.error}</div>`;
        showToast('Error generating plan');
        return;
      }
      const planText = res.plan || (typeof res === 'string' ? res : JSON.stringify(res, null, 2));
      const node = renderPlan(planText);
      out.innerHTML = '';
      out.appendChild(node);
      showToast('Workout plan ready');
    }catch(err){
      console.error(err);
      out.innerHTML = `<div class="error">An unexpected error occurred.</div>`;
      showToast('Network error');
    }
  });
}
