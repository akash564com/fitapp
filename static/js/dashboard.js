// dashboard.js - fetch stats and draw charts using Chart.js
export async function fetchStats(){
  const res = await fetch('/api/stats');
  return res.json();
}

export async function initDashboard({workoutCanvasSelector, caloriesCanvasSelector} = {}){
  const data = await fetchStats();
  if(!data || !data.stats) return;
  const workouts = Array.isArray(data.stats.weekly_workouts) ? data.stats.weekly_workouts : [];
  const calories = Array.isArray(data.stats.calories) ? data.stats.calories : [];
  const labels = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];

  if(workoutCanvasSelector){
    const el = document.querySelector(workoutCanvasSelector);
    if(el){
      const ctx = el.getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: { labels, datasets: [{ label: 'Workouts', data: workouts }] },
        options: { responsive: true, plugins: { legend: { display: false } } }
      });
    }
  }

  if(caloriesCanvasSelector){
    const el2 = document.querySelector(caloriesCanvasSelector);
    if(el2){
      const ctx2 = el2.getContext('2d');
      new Chart(ctx2, {
        type: 'line',
        data: { labels, datasets: [{ label: 'Calories', data: calories, fill: false }] },
        options: { responsive: true }
      });
    }
  }
}
