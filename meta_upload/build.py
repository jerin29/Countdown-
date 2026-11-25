"""Build Meta Business Suite upload folders for Hindi and Tamil (videos hard-linked + caption .txt + schedule list)."""
import json, os
R = '/home/user/Countdown-'; OUT = R + '/meta_upload'
S1V = R + '/horror-series/video/vertical_clean'; S2V = R + '/horror-series/season2/video/vertical_clean'
cap1 = json.load(open(OUT + '/s1_captions.json'))
P = json.load(open(R + '/horror-series/season2/social/captions.json'))
TIME = {'hi': ('21:20', '9:20 PM'), 'ta': ('21:40', '9:40 PM')}
S1DATES = {'hi': {4: '2026-11-26', 5: '2026-11-27', 6: '2026-11-28', 7: '2026-11-29', 8: '2026-11-30', 9: '2026-12-01', 10: '2026-12-02'},
           'ta': {6: '2026-11-28', 7: '2026-11-29', 8: '2026-11-30', 9: '2026-12-01', 10: '2026-12-02'}}
for L, folder in (('hi', 'hindi'), ('ta', 'tamil')):
    d = os.path.join(OUT, folder); os.makedirs(d, exist_ok=True)
    items = []
    for ep, date in S1DATES[L].items():
        items.append((date, f'S1 Ep{ep}', f'{S1V}/COUNTDOWN_S1_ep{ep:02d}_{L}_9x16_hook.mp4', cap1[f'{L}{ep}']))
    for p in P:
        if p['lang'] != L: continue
        name = 'S2 Title song' if p['kind'] == 'song' else f"S2 Ep{p['ep']}"
        base = os.path.basename(p['file']).replace('.mp4', '_9x16.mp4')
        if p['kind'] == 'episode' and p['ep'] == 1: base = base.replace('.mp4', '_hook.mp4')
        items.append((p['date'], name, f'{S2V}/{base}', p['caption']))
    items.sort()
    lines = [f'# {folder.title()} — Meta Business Suite schedule ({TIME[L][1]} IST every day)\n',
             '| # | Date | Time | Post | Video file | Caption file |', '|---|---|---|---|---|---|']
    for i, (date, name, src, cap) in enumerate(items, 1):
        stem = f"{i:02d}_{date}_{name.replace(' ', '_')}"
        dst = os.path.join(d, stem + '.mp4')
        if os.path.exists(dst): os.remove(dst)
        os.link(src, dst)
        open(os.path.join(d, stem + '.txt'), 'w').write(cap + '\n')
        lines.append(f'| {i} | {date} | {TIME[L][1]} | {name} | {stem}.mp4 | {stem}.txt |')
    open(os.path.join(d, 'SCHEDULE.md'), 'w').write('\n'.join(lines) + '\n')
    print(folder, len(items))
