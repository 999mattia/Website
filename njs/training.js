// /api/training: the few public numbers from the training dashboard (same Docker network).
// Its /api/dashboard also has weight, resting HR, HRV, sleep, activity names and devices:
// none of that leaves here, only distances, durations and dates.
async function training(r) {
  try {
    const res = await ngx.fetch('http://training-dashboard:8080/api/dashboard', { headers: { Accept: 'application/json' } });
    if (!res.ok) throw new Error(`dashboard ${res.status}`);
    const d = await res.json();
    const today = String(d.TODAY || new Date().toISOString().slice(0, 10)), year = today.slice(0, 4);
    const hist = (d.HISTORY || []).filter((h) => String(h[0]).startsWith(year));   // [date, type, km, movingSec, elevation]
    const sum = (type) => {
      const xs = hist.filter((h) => h[1] === type);
      return { km: Math.round(xs.reduce((s, h) => s + (h[2] || 0), 0) * 10) / 10, count: xs.length };
    };
    const last = (type) => {
      const xs = (d.HISTORY || []).filter((h) => h[1] === type).sort((a, b) => (a[0] < b[0] ? 1 : -1));
      return xs.length ? { date: xs[0][0], km: Math.round(xs[0][2] * 100) / 100, sec: xs[0][3] } : null;
    };
    const months = [];
    for (let m = 1; m <= Number(today.slice(5, 7)); m++) {
      const p = `${year}-${String(m).padStart(2, '0')}`, xs = hist.filter((h) => String(h[0]).startsWith(p));
      const km = (type) => Math.round(xs.filter((h) => h[1] === type).reduce((s, h) => s + (h[2] || 0), 0) * 10) / 10;
      months.push({ run: km('run'), ride: km('bike') });
    }
    const out = { year: Number(year), run: sum('run'), ride: sum('bike'), lastRun: last('run'), lastRide: last('bike'), months };
    r.headersOut['Content-Type'] = 'application/json';
    r.headersOut['Cache-Control'] = 'max-age=300';
    r.return(200, JSON.stringify(out));
  } catch (e) {
    r.return(502, JSON.stringify({ error: 'training data unavailable' }));
  }
}
export default { training };
