(() => {
  let now = 1000; const d0 = Date.now(); const realNow = Date.now.bind(Date);
  performance.now = () => now;
  Date.now = () => d0 + now;
  let q = [], id = 0;
  window.requestAnimationFrame = (cb) => { q.push(cb); return ++id; };
  window.cancelAnimationFrame = () => {};
  window.__step = (ms) => { now += ms; const c = q; q = []; for (const f of c) f(now); };
})();
