// meal.js - request meal plan and render an organized layout
import { showToast } from './main.js';

export async function requestMeal(formData){
  const res = await fetch('/api/meal', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
  });
  return res.json();
}

function renderMeal(planText){
  const container = document.createElement('div');
  container.className = 'meal-plan';
  // try to split into day sections (common LLM output uses "Day 1:" etc.)
  const days = String(planText).split(/\n(?=Day\s*\d+[:\-])/i);
  // fallback: if no Day headings, split by two newlines
  const chunks = days.length > 1 ? days : String(planText).split(/\n\s*\n/);
  chunks.forEach(chunk=>{
    const trimmed = chunk.trim();
    if(!trimmed) return;
    const lines = trimmed.split('\n').map(l=>l.trim()).filter(Boolean);
    const card = document.createElement('div');
    card.className = 'meal-day-card';
    const heading = document.createElement('h3');
    heading.textContent = lines[0] || 'Day';
    card.appendChild(heading);
    const list = document.createElement('ul');
    lines.slice(1).forEach(line=>{
      const li = document.createElement('li');
      li.textContent = line;
      list.appendChild(li);
    });
    card.appendChild(list);
    container.appendChild(card);
  });
  return container;
}

export function initMealForm(formSelector, outputSelector){
  const form = document.querySelector(formSelector);
  const out = document.querySelector(outputSelector);
  if(!form || !out) return;
  form.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form));
    out.innerHTML = '<div class="loading">Generating meal plan…</div>';
    try{
      const res = await requestMeal(data);
      if(res.error){
        out.innerHTML = `<div class="error">${res.error}</div>`;
        showToast('Error generating meal plan');
        return;
      }
      const planText = res.plan || (typeof res === 'string' ? res : JSON.stringify(res, null, 2));
      const node = renderMeal(planText);
      out.innerHTML = '';
      out.appendChild(node);
      showToast('Meal plan ready');
    }catch(err){
      console.error(err);
      out.innerHTML = `<div class="error">An unexpected error occurred.</div>`;
      showToast('Network error');
    }
  });
}
