# Builds fictional-but-plausible API responses for filming the dashboard: health series, names,
# routes, serials and the coach note are replaced; distances/durations/dates stay (already public).
import json, math, random
random.seed(7)
d = json.load(open('real.json')); acts = json.load(open('activities.json'))
def wave(i, base, amp, noise): return base + amp*math.sin(i/5.3) + random.uniform(-noise, noise)
days = sorted(d['RHR'].keys())
d['RHR'] = {k: round(wave(i, 52, 2, 1.5)) for i, k in enumerate(days)}
d['HRV'] = {k: [round(wave(i, 52, 7, 4)), 'n', 42, 64] for i, k in enumerate(days)}
d['SLEEP'] = {k: [round(wave(i, 82, 6, 5)), round(wave(i, 455, 25, 30)), round(wave(i, 18, 3, 3)), round(wave(i, 55, 4, 3)), round(wave(i, 25, 3, 3))] for i, k in enumerate(sorted(d['SLEEP']))}
d['SLEEP_HR'] = {k: [round(wave(i, 52, 2, 2)), round(wave(i, 45, 2, 2))] for i, k in enumerate(sorted(d['SLEEP_HR']))}
d['AWAKE'] = {k: round(wave(i, 13, 3, 3)) for i, k in enumerate(days)}
d['STEPS'] = {k: round(wave(i, 9500, 2500, 2000)) for i, k in enumerate(days)}
d['WEIGHT'] = {}; d['WEIGHT_KG'] = None
last = days[-1]; d['RHR'][last] = 51; d['HRV'][last][0] = 56; d['SLEEP'][last][1] = 455
d['FITNESS'] = {'vo2max': 58, 'vo2level': 80, 'thresholdPace': '4:25', 'preds': {'5 km': '21:10', '10 km': '43:50', 'Half': '1:37:30', 'Marathon': '3:24:00'}}
d['FITNESS_HISTORY'] = [[r[0], 58, 80] + r[3:] for r in d['FITNESS_HISTORY']]
d['DEVICES'] = [{**x, 'serial': None, 'warrantyUntil': None} for x in d['DEVICES']]
def title(kind, km, q):
    if kind == 'run': return 'Intervals' if q else ('Long Run' if km >= 14 else 'Easy Run')
    if kind == 'bike': return 'Ride'
    if kind == 'hike': return 'Hike'
    return 'Workout'
def fix_act(a):
    a = list(a); a[2] = title(a[1], a[4] or 0, a[9]); a[10] = ''; return a
d['ACTS'] = [fix_act(a) for a in d['ACTS']]
for r in d['RUNS']: r['name'] = title('run', r['km'], r['quality'])
for b in d['BEST_EFFORTS']: b['activityName'] = 'Run'
def loop(seed):
    rnd = random.Random(seed); pts = []
    for i in range(40):
        t = i/40*2*math.pi; r = 38 + 9*math.sin(3*t + seed) + rnd.uniform(-2, 2)
        pts.append((50 + r*math.cos(t), 50 + r*0.8*math.sin(t)))
    return 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + 'Z'
for i, a in enumerate(acts['acts']):
    a['act'] = fix_act(a['act']); a['route'] = loop(i) if a.get('route') else a.get('route')
coach = {'enabled': True, 'current': {'generatedAt': d['generatedAt'], 'today': d['TODAY'], 'trigger': 'data',
  'health': {'tone': 'good', 'headline': 'Recovered: HRV back in your normal range',
    'summary': 'Sleep HRV is 56 ms, inside your usual 42–64, and resting HR is steady at 51 bpm after a full night. Nothing in your readings holds you back today.',
    'suggestions': [{'title': 'Use the green light', 'detail': 'Recovery is complete, so today suits a proper session instead of more rest.'},
                    {'title': 'Keep sleep steady', 'detail': 'Aim for 7:30 or more before the weekend sessions.'}]},
  'training': {'tone': 'watch', 'headline': 'Load ratio 0.6: rested, now rebuild the base',
    'summary': 'Acute load is well under chronic after race week, so a few consistent days will bring the ratio back up.',
    'suggestions': [{'title': 'Today: easy run', 'detail': '45 to 55 minutes easy, HR under 140.'},
                    {'title': 'Sunday: long and easy', 'detail': '75 to 90 minutes, or a two-hour ride below 125 bpm.'},
                    {'title': 'Focus: consistency', 'detail': 'Three or four sessions a week matter more than any single workout.'}]}}}
real_c = json.load(open('coach.json'))
for k in real_c:
    if k not in coach: coach[k] = None
json.dump(d, open('fake_dashboard.json', 'w'), ensure_ascii=False)
json.dump(acts, open('fake_activities.json', 'w'), ensure_ascii=False)
json.dump(coach, open('fake_coach.json', 'w'), ensure_ascii=False)
print(list(real_c.keys()))
