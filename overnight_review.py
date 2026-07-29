<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vigilantia — Market Lean Dashboard</title>
<style>
  :root {
    --bg: #0a0d12;
    --panel: #12161d;
    --border: #232a35;
    --text: #e6e9ef;
    --muted: #8b93a3;
    --long: #3ecf8e;
    --short: #ef5464;
    --neutral: #d9a441;
    --accent: #5b8def;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    padding: 24px;
  }
  .wrap { max-width: 1000px; margin: 0 auto; }
  h1 { font-size: 20px; font-weight: 600; margin-bottom: 4px; letter-spacing: 0.3px; }
  .sub { color: var(--muted); font-size: 13px; margin-bottom: 24px; }
  .grid { display: grid; grid-template-columns: 1fr; gap: 16px; }
  @media (min-width: 720px) { .grid { grid-template-columns: 1fr 1fr; } }
  .panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px 20px;
  }
  .panel h2 {
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--muted);
    margin: 0 0 14px 0;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--accent); display: inline-block; }
  .lean-value { font-size: 34px; font-weight: 700; margin-bottom: 6px; }
  .lean-long { color: var(--long); }
  .lean-short { color: var(--short); }
  .lean-neutral { color: var(--neutral); }
  .row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--border); font-size: 13px; }
  .row:last-child { border-bottom: none; }
  .row .label { color: var(--muted); }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
  .badge-high { background: rgba(239,84,100,0.15); color: var(--short); }
  .badge-low { background: rgba(62,207,142,0.15); color: var(--long); }
  .badge-intact { background: rgba(62,207,142,0.15); color: var(--long); }
  .badge-review { background: rgba(217,164,65,0.15); color: var(--neutral); }
  .caption { font-size: 12px; color: var(--muted); margin-top: 14px; padding-top: 12px; border-top: 1px dashed var(--border); line-height: 1.5; }
  .catalyst-list { list-style: none; padding: 0; margin: 0; font-size: 12.5px; }
  .catalyst-list li { padding: 5px 0; color: var(--text); }
  .catalyst-list .date { color: var(--muted); margin-right: 6px; }
  .flag-item { font-size: 12.5px; padding: 6px 0; border-bottom: 1px solid var(--border); }
  .flag-item:last-child { border-bottom: none; }
  .flag-material { color: var(--short); }
  .flag-quiet { color: var(--muted); }
  .stale { color: var(--muted); font-size: 11px; margin-top: 4px; }
  .empty { color: var(--muted); font-size: 13px; font-style: italic; }
</style>
</head>
<body>
<div class="wrap">
  <h1>VIGILANTIA — Market Lean Dashboard</h1>
  <div class="sub">Fundamentals set the lean. Positioning gates execution. This page never suggests a trade.</div>

  <div class="grid">
    <div class="panel" id="lean-panel">
      <h2><span class="dot"></span>Weekly Lean</h2>
      <div class="empty">Loading...</div>
    </div>

    <div class="panel" id="overnight-panel">
      <h2><span class="dot"></span>Overnight Review</h2>
      <div class="empty">Loading...</div>
    </div>

    <div class="panel" id="calendar-panel">
      <h2><span class="dot"></span>This Week's Catalysts</h2>
      <div class="empty">Loading...</div>
    </div>

    <div class="panel" id="monitor-panel">
      <h2><span class="dot"></span>30-Min Monitor</h2>
      <div class="empty">Loading...</div>
    </div>
  </div>

  <div class="caption">
    Execution stays manual: price reaches a GEX/DEX or IV wall/cluster level → rejects with a pin bar / hammer / engulfing candle → footprint confirms directional aggression or absorption → execute. Nothing on this page triggers a trade.
  </div>
</div>

<script>
async function loadJSON(path) {
  try {
    const res = await fetch(path + '?t=' + Date.now());
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    return null;
  }
}

function leanClass(lean) {
  if (lean === 'LONG') return 'lean-long';
  if (lean === 'SHORT') return 'lean-short';
  return 'lean-neutral';
}

function timeAgo(iso) {
  if (!iso) return '';
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return mins + 'm ago';
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return hrs + 'h ago';
  return Math.floor(hrs / 24) + 'd ago';
}

async function render() {
  const lean = await loadJSON('data/weekly_lean.json');
  const overnight = await loadJSON('data/overnight_review.json');
  const monitor = await loadJSON('data/monitor.json');

  // Lean panel
  const leanPanel = document.getElementById('lean-panel');
  if (lean) {
    leanPanel.innerHTML = `
      <h2><span class="dot"></span>Weekly Lean</h2>
      <div class="lean-value ${leanClass(lean.weekly_lean)}">${lean.weekly_lean || 'N/A'}</div>
      <div class="row"><span class="label">Throttle</span><span>${lean.throttle || 'n/a'}</span></div>
      <div class="row"><span class="label">Size cap</span><span>${lean.size_cap || 'n/a'}</span></div>
      <div class="row"><span class="label">Curve signal</span><span>${lean.curve_signal || 'n/a'}</span></div>
      <div class="row"><span class="label">Fed signal</span><span>${lean.fed_signal || 'n/a'}</span></div>
      <div class="row"><span class="label">Catalyst risk</span><span class="badge ${lean.catalyst_risk === 'HIGH' ? 'badge-high' : 'badge-low'}">${lean.catalyst_risk || 'n/a'}</span></div>
      <div class="stale">Week of ${lean.week_of || '?'} · updated ${timeAgo(lean.generated_at)}</div>
      <div class="caption">This is lean and a size ceiling only — not a trigger.</div>
    `;
  } else {
    leanPanel.innerHTML = `<h2><span class="dot"></span>Weekly Lean</h2><div class="empty">No data yet — runs Sunday 12 PM ET, or trigger it manually from the Actions tab.</div>`;
  }

  // Overnight panel
  const overnightPanel = document.getElementById('overnight-panel');
  if (overnight) {
    const statusBadge = overnight.status === 'LEAN INTACT' ? 'badge-intact' : 'badge-review';
    overnightPanel.innerHTML = `
      <h2><span class="dot"></span>Overnight Review</h2>
      <div class="row"><span class="label">Status</span><span class="badge ${statusBadge}">${overnight.status || 'n/a'}</span></div>
      <div class="row"><span class="label">NDX futures</span><span>${overnight.ndx_futures_pct_change ?? 'n/a'}%</span></div>
      <div class="row"><span class="label">VIX change</span><span>${overnight.vix_change ?? 'n/a'}</span></div>
      <div style="margin-top:10px; font-size:12.5px; color:var(--text);">${overnight.headlines_summary || 'No summary.'}</div>
      <div class="stale">Checked ${timeAgo(overnight.checked_at)}</div>
    `;
  } else {
    overnightPanel.innerHTML = `<h2><span class="dot"></span>Overnight Review</h2><div class="empty">No data yet — runs daily 7 AM ET.</div>`;
  }

  // Calendar panel (pulled from lean data)
  const calendarPanel = document.getElementById('calendar-panel');
  if (lean && lean.catalysts_this_week && lean.catalysts_this_week.length) {
    const items = lean.catalysts_this_week.map(c => `<li><span class="date">${c.date || '?'}</span>${c.event || '?'} <span style="color:var(--muted)">(${c.consensus || '?'})</span></li>`).join('');
    calendarPanel.innerHTML = `<h2><span class="dot"></span>This Week's Catalysts</h2><ul class="catalyst-list">${items}</ul>`;
  } else {
    calendarPanel.innerHTML = `<h2><span class="dot"></span>This Week's Catalysts</h2><div class="empty">None flagged, or no data yet.</div>`;
  }

  // Monitor panel
  const monitorPanel = document.getElementById('monitor-panel');
  if (monitor && monitor.history && monitor.history.length) {
    const items = monitor.history.slice().reverse().slice(0, 8).map(h => {
      const cls = h.material_found ? 'flag-material' : 'flag-quiet';
      const txt = h.material_found ? (h.flag_summary || 'Material event flagged') : 'No material catalysts';
      return `<div class="flag-item ${cls}">${txt} <span class="stale">${timeAgo(h.checked_at)}</span></div>`;
    }).join('');
    monitorPanel.innerHTML = `<h2><span class="dot"></span>30-Min Monitor</h2>${items}`;
  } else {
    monitorPanel.innerHTML = `<h2><span class="dot"></span>30-Min Monitor</h2><div class="empty">No checks yet — runs every 30 min, market hours.</div>`;
  }
}

render();
setInterval(render, 60000); // refresh every minute while the page is open
</script>
</body>
</html>
