// Shared helpers for the compositions: every frame is render(t), nothing depends on wall-clock time.
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const prog = (t, a, b) => clamp((t - a) / (b - a));
const mix = (a, b, k) => a + (b - a) * k;
const E = {
  out: (k) => 1 - Math.pow(1 - k, 3),
  out5: (k) => 1 - Math.pow(1 - k, 5),
  in: (k) => k * k * k,
  inOut: (k) => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2),
  // a soft spring: overshoots a little, settles by k = 1
  spring: (k) => (k >= 1 ? 1 : 1 - Math.exp(-6 * k) * Math.cos(9 * k) * (1 - k * 0.15)),
};
const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
function css(el, o) { if (typeof el === 'string') el = $(el); Object.assign(el.style, o); }
// in/out envelope for a scene element: 0 before, rises over [a, a+ri], holds, falls over [b-fo, b]
function life(t, a, b, ri = 0.45, fo = 0.3) { return Math.min(E.out(prog(t, a, a + ri)), 1 - E.in(prog(t, b - fo, b))); }
// words that rise one after another; el holds <span class="w"> children
function words(el, t, start, gap = 0.08, dur = 0.5, rise = 40) {
  [...el.querySelectorAll('.w')].forEach((w, i) => {
    const k = E.out(prog(t, start + i * gap, start + i * gap + dur));
    w.style.opacity = k; w.style.transform = `translateY(${(1 - k) * rise}px)`;
  });
}
function splitWords(el) { el.innerHTML = el.textContent.trim().split(/\s+/).map((w) => `<span class="w">${w}</span>`).join(' '); }
// image sequences: swap the src and wait until it is decoded, so the frame is complete
const seqCache = new Map();
async function frameOf(img, src) {
  if (img.dataset.src === src) return;
  img.dataset.src = src; img.src = src;
  await img.decode();
}
window.ready = (async () => {
  $$('[data-split]').forEach(splitWords);
  await document.fonts.ready;
  await Promise.all($$('img').map((i) => (i.complete ? i.decode().catch(() => {}) : new Promise((r) => { i.onload = () => i.decode().then(r, r); i.onerror = r; }))));
  await Promise.all([...document.fonts].map((f) => f.load().catch(() => {})));
})();
