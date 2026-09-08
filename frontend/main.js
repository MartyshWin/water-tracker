/* ==================================================================
   STATE — placeholder in-memory data.
   In the real app: GOAL comes from the intake formula (weight, gender,
   climate, activity), `logs` is fetched from GET /water-logs?date=today.
   ================================================================== */
const GOAL = 2400;
let current = 0;
let logs = [];
let lastEntry = null;   // enables one-tap undo from the toast
let toastTimer = null;

// Fetches today's logs from the backend and renders the initial state.
async function loadLogs(){
  const res = await fetch('/api/logs');
  logs = await res.json();
  current = logs.reduce((sum, l) => sum + Math.round(l.amount_ml * l.hydration_factor), 0);
  renderGlass();
  renderLogs();
}

function renderGlass(){
  const pct = Math.min(100, Math.round((current/GOAL)*100));
  document.getElementById('waterFill').style.height = Math.max(4,pct) + '%';
  document.getElementById('curVal').textContent = current;
  const left = GOAL - current;
  const sub = document.getElementById('goalSub');
  const glass = document.getElementById('glass');
  if(left <= 0){
    sub.textContent = 'цель дня достигнута 🎉';
    glass.classList.add('celebrate');
  } else {
    sub.textContent = 'осталось ' + left + ' мл сегодня';
    glass.classList.remove('celebrate');
  }
}

function renderLogs(){
  const list = document.getElementById('logList');
  list.innerHTML = '';
  logs.slice().reverse().forEach((l) => {
    const time = new Date(l.logged_at).toLocaleTimeString('ru-RU', {hour:'2-digit', minute:'2-digit'});
    const row = document.createElement('div');
    row.className = 'log-item';
    row.innerHTML = `<span class="meta">${time} · ${l.drink_type} · ${l.amount_ml} мл</span>
      <button class="del" onclick="deleteLog(${l.id})">удалить</button>`;
    list.appendChild(row);
  });
}

// Deletes by id (matches the backend's DELETE /api/logs/{id}).
async function deleteLog(id){
  const l = logs.find(x => x.id === id);
  if(!l) return;
  await fetch('/api/logs/' + id, {method:'DELETE'});
  current = Math.max(0, current - Math.round(l.amount_ml * l.hydration_factor));
  logs = logs.filter(x => x.id !== id);
  renderGlass(); renderLogs();
}

// `effective` (amount_ml * hydration_factor) ≠ raw amount_ml: tea/coffee
// hydrate less than water, so the glass fills by the effective volume
// while the log keeps the real poured amount.
async function addEntry(type, amount, factor, meal, comment){
  const res = await fetch('/api/logs', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      drink_type: type,
      amount_ml: amount,
      hydration_factor: factor,
      meal_relation: meal,
      comment: comment
    })
  });
  const entry = await res.json();
  logs.push(entry);
  current += Math.round(entry.amount_ml * entry.hydration_factor);
  lastEntry = entry;
  renderGlass(); renderLogs();
  showToast('Добавлено: ' + type + ' ' + amount + ' мл', undoLast);
}

function quickAdd(type, amount, factor){
  addEntry(type, amount, factor, null, null);
}

// Undo = delete the just-created entry via the same API call as deleteLog.
async function undoLast(){
  if(!lastEntry) return;
  await deleteLog(lastEntry.id);
  lastEntry = null;
  hideToast();
}

function showToast(text, undoFn){
  document.getElementById('toastText').textContent = text;
  document.getElementById('toastUndo').style.display = undoFn ? 'inline' : 'none';
  document.getElementById('toast').classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(hideToast, 4000);
}
function hideToast(){ document.getElementById('toast').classList.remove('show'); }

function selectPill(el, groupId){
  document.querySelectorAll('#'+groupId+' > *').forEach(p => p.classList.remove('active'));
  el.classList.add('active');
  if(groupId === 'amountRow'){ document.getElementById('customAmount').value = ''; }
}

function submitSheet(){
  const type = document.querySelector('#typeRow .active');
  const typeLabel = type.textContent.trim();
  const factor = parseFloat(type.dataset.factor);
  const custom = document.getElementById('customAmount').value;
  const amountPill = document.querySelector('#amountRow .active');
  const amount = custom ? parseInt(custom) : parseInt(amountPill.textContent);
  const meal = document.querySelector('#mealRow .active').textContent.trim();
  const comment = document.getElementById('commentInput').value;
  if(!amount || amount <= 0) return;
  addEntry(typeLabel, amount, factor, meal, comment);
  document.getElementById('commentInput').value = '';
  closeAll();
}

function openSheet(){
  document.getElementById('overlay').classList.add('show');
  document.getElementById('sheet').classList.add('show');
}
function toggleMenu(open){
  document.getElementById('overlay').classList.toggle('show', open);
  document.getElementById('sideMenu').classList.toggle('show', open);
}
function openPanel(name){
  document.getElementById('panel-'+name).classList.add('show');
  toggleMenu(false);
}
function closePanel(name){
  document.getElementById('panel-'+name).classList.remove('show');
}
function closeAll(){
  document.getElementById('overlay').classList.remove('show');
  document.getElementById('sheet').classList.remove('show');
  document.getElementById('sideMenu').classList.remove('show');
}

// Demo-only random fill — swap for real per-day goal-completion % from the API.
function buildHeatmap(){
  const grid = document.getElementById('heatGrid');
  const colors = ['#E2EFEC','#9AD6D0','#4FB6AE','#1B7570'];
  for(let i=0;i<35;i++){
    const cell = document.createElement('div');
    cell.className = 'heat-cell';
    const level = Math.random() < 0.15 ? 0 : Math.floor(Math.random()*4);
    cell.style.background = colors[level];
    grid.appendChild(cell);
  }
}

loadLogs();
buildHeatmap();