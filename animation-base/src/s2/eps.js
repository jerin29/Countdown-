// COUNTDOWN Season 2 · Episodes 2–15: painted plates. Each scene variant is a 1920x1080 picture rendered at 2x as four
// tiles: LOOPS['s2e<N>_<scene>_<variant>'], stills 0,0.1,0.2,0.3. The compositor (video/tools/s2ep.py) moves the camera.

// ---------- small additions to the cast ----------
COSTUME.mom = { h: 15.5, skin: '#A87256', top: '#7A5A6E', topDk: '#5A4052', sleeve: '#7A5A6E', legs: '#7A5A6E', shoes: '#2A2420', torsoW: [2.1, 2.3], limbW: .95, skirt: true, pallu: true };
{ const _head = head; head = function (name, ...a) { return _head(name === 'mom' ? 'meera' : name, ...a); }; }
const SKIN = { meera: CP.skin, arjun: '#A87256', boy: CP.skin, ammachi: '#9C6C52' };

function eyesGlow(x, y, r, col = '#E9F2E0') { for (const k of [-1, 1]) paint(ellPts(x + k * r * .38, y + r * .05, r * .09, r * .06, 8), { wash: col, ink: null }); glow(x, y, r * 1.6, '#9FD48A', .25); }
// a Watcher: a still figure whose head is a clock face, both hands pointing at you
function watcher(x, y, u, o = {}) {
  const r = person('mob', x, y, u, { key: 'wt' + x + y });
  clockFace(r.head[0], r.head[1], r.headR * 1.05, { sw: clamp(u / 30, .3, 1), hands: o.hands || [Math.PI, Math.PI], glow: .35, glowCol: CP.sickGlow, cracks: hash(x) > .5 });
}
function gear(x, y, r, a, col = CP.brass, teeth = 16) {
  const pts = []; for (let k = 0; k < teeth * 4; k++) { const ang = a + k / (teeth * 4) * TAU, rr = r * (k % 4 < 2 ? 1 : .86); pts.push([x + Math.cos(ang) * rr, y + Math.sin(ang) * rr]); }
  paint(pts, { wash: col, ink: CP.ink, sw: clamp(r / 120, .4, 1.2) });
  paint(ellPts(x, y, r * .28, r * .28, 16), { wash: '#3A2E1E', ink: CP.ink, sw: .6 });
}
function rainStreaks(n = 140, key = 'rain', col = '#9FB2C4', op = 110) {
  boilSeed(key); for (let i = 0; i < n; i++) { const x = hash(i * 1.7) * W, y = hash(i * 3.9) * H, l = 30 + 50 * hash(i * 5.3); inkLine([[x, y], [x - 6, y + l]], .5, col, 'inkfine', 0); }
}
function darkRoomBase(col = '#14171F') { full(col); boilSeed('drb'); paint(rectPts(-60, 800, W + 120, 400), { wash: '#1E1C22', ink: null }); inkLine([[-60, 800], [W + 60, 800]], .9, CP.ink, 'ink', 0); }

// ---------- per-episode pictures ----------
const S2 = {};
// Ep 2 · The Ticking Wrist
function wristCU(a) {
  full('#0E0F14'); boilSeed('wrist');
  glow(960, 560, 900, '#3A3040', .5);
  paint(ribbon([[-200, 760], [700, 600], [1400, 540], [2200, 520]], 420, 360), { wash: CP.skin, ink: CP.ink, sw: 1.4 });
  inkLine([[300, 640], [800, 560], [1300, 560]], .7, CP.skinDk, 'inkfine');
  glow(1000, 560, 260, CP.sickGlow, .45);
  gear(1000, 565, 120, a, '#8A5A42', 12);
  paint(ellPts(1000, 565, 150, 120, 24), { fill: CP.skin, fillOp: 120, bleed: .2, ink: null });   // under the skin
  paint(rectPts(1500, 440, 150, 260), { wash: CP.maroon, ink: CP.ink, sw: 1 });                 // hoodie cuff
}
S2[2] = {
  room: { a: () => { bedroom({}); person('meera', 640, 840, 27, { pose: 'phone', view: 'q', expr: 'scared', look: [-.6, .3], key: 'm2' }); },
          b: () => { bedroom({ phoneGlow: [900, 720] }); person('meera', 640, 840, 27, { pose: 'phone', view: 'q', expr: 'shock', look: [.8, .2], key: 'm2' }); } },
  wrist: { a: () => wristCU(0), b: () => wristCU(.26), c: () => wristCU(.52) },
  phone: { a: () => { full('#0A0B10'); glow(960, 540, 600, '#9FC3E8', .5); paint(rrPts(700, 120, 520, 860, 50), { wash: '#16202C', ink: CP.ink, sw: 1.2 });
    paint(rrPts(740, 200, 440, 700, 20), { wash: '#B9D4EE', ink: null }); paint(rrPts(780, 520, 360, 90, 40), { wash: '#2E5A7A', ink: null });
    for (let i = 0; i < 18; i++) paint(rectPts(810 + i * 18, 565 - 10 - 30 * hash(i), 8, 20 + 60 * hash(i)), { wash: '#E9F2F8', ink: null });
    letter('3:00', 960, 300, 90, '#16202C', { ink: false, font: 'bold 90px Georgia, serif' }); } },
};
// Ep 3 · City of Clocks
function aptCorridor(o = {}) {
  full('#12151D'); boilSeed('apt');
  paint([[0, 0], [700, 330], [700, 760], [0, 1080]], { wash: '#1E2230', ink: CP.ink, sw: .8 });
  paint([[1920, 0], [1220, 330], [1220, 760], [1920, 1080]], { wash: '#1E2230', ink: CP.ink, sw: .8 });
  paint([[700, 760], [1220, 760], [1920, 1080], [0, 1080]], { wash: '#23212A', ink: CP.ink, sw: .8 });
  paint(rectPts(700, 330, 520, 430), { wash: '#0A0C11', ink: null });
  glow(960, 330, 260, '#C9B98A', .35);
  const doors = [[90, 260, 260, 600, 1.0], [430, 360, 170, 420, .66], [1320, 360, 170, 420, .66], [1570, 260, 260, 600, 1.0]];
  for (const [i, [x, y, w, h, s]] of doors.entries()) {
    paint(rectPts(x, y, w, h), { wash: '#08090D', ink: CP.ink, sw: .8 });
    glow(x + w / 2, y + h * .4, w * .9, '#B9C8D6', .18);
    if (o.people) person(i === 3 && o.mom ? 'mom' : 'mob', x + w / 2, y + h, 30 * s, { key: 'n' + i, expr: 'neutral' });
    if (o.people) { const r = 1.75 * 30 * s; eyesGlow(x + w / 2, y + h - (i === 3 && o.mom ? 15.5 : 16.5) * 30 * s * .96 - r * .2, r); }
  }
  if (o.aadi) person('boy', 960, 1060, 34, { view: 'back', expr: 'scared', key: 'a3' });
}
S2[3] = {
  corr: { a: () => aptCorridor({ aadi: 1 }), b: () => aptCorridor({ people: 1, aadi: 1 }), c: () => aptCorridor({ people: 1, mom: 1 }) },
  mom: { a: () => { full('#0B0D12'); boilSeed('momcu'); paint(rectPts(560, 0, 800, 1080), { wash: '#06070A', ink: CP.ink, sw: 1 });
    glow(960, 420, 600, '#2E3A44', .6); bust('mom', 960, 470, 190, { expr: 'neutral', key: 'mm' }); eyesGlow(960, 470, 190, '#F2F7EC'); } },
};
// Ep 4 · Late Reflection
function shopMirror(o = {}) {
  full('#1A1714'); boilSeed('barber');
  paint(rectPts(-60, 820, W + 120, 400), { wash: '#2B2520', ink: null });
  paint(rectPts(240, 120, 1440, 640), { wash: CP.wood, ink: CP.ink, sw: 1.1 });
  paint(rectPts(270, 150, 1380, 580), { wash: '#3A4450', ink: CP.ink, sw: .7 });                // mirror
  for (let i = 0; i < 3; i++) glow(500 + i * 460, 120, 240, '#F2D49A', .4);
  if (o.refl) person('arjun', o.reflX ?? 980, 720, 20, { pose: o.reflPose || 'walk', view: 'front', expr: o.reflExpr || 'neutral', key: 'rf' });
  paint(rectPts(270, 150, 1380, 580), { fill: '#A8B6C2', fillOp: 30, bleed: .2, ink: null });
  if (o.fog) { paint(rectPts(270, 150, 1380, 580), { fill: '#C4CCD3', fillOp: 150, bleed: .2, tex: .5, ink: null }); letter('ആദി', 960, 430, 190, '#3A4450', { ink: false, font: 'bold 190px "Noto Sans Malayalam"' }); }
  if (o.arjun) person('arjun', 1000, 1090, 30, { pose: o.pose || 'walk', view: 'back', key: 'ar' });
  for (const x of [380, 1540]) paint(rectPts(x - 60, 790, 120, 30), { wash: '#5A4A3A', ink: CP.ink, sw: .6 });
}
S2[4] = {
  shop: { a: () => shopMirror({ arjun: 1, refl: 1, pose: 'walk', reflPose: 'walk' }),
          b: () => shopMirror({ arjun: 1, refl: 1, pose: 'stand', reflPose: 'walk', reflExpr: 'smile' }),
          c: () => shopMirror({ arjun: 1, fog: 1, pose: 'tense' }) },
  refl: { a: () => { full('#2C3440'); boilSeed('rcu'); glow(960, 500, 700, '#5A6A7A', .4); bust('arjun', 960, 470, 200, { expr: 'smile', look: [0, 0], key: 'rcu' });
    paint(rectPts(0, 0, W, H), { fill: '#A8B6C2', fillOp: 40, bleed: .2, ink: null }); full('#0A0C10', 60); } },
};
// Ep 5 · The Erased Daughter
S2[5] = {
  veranda: { a: () => { veranda({ dusk: .4 }); rainStreaks(); rockingChair(560, 830, .9, {}); person('ammachi', 560, 800, 26, { pose: 'sit', view: 'q', expr: 'sad', key: 'am' }); person('meera', 1350, 830, 27, { pose: 'sitHug', view: 'q', flip: true, expr: 'scared', key: 'm5' }); },
             b: () => { veranda({ dusk: .3, lampOff: 1 }); rainStreaks(); rockingChair(560, 830, .9, { rock: -.08 }); person('meera', 1350, 830, 27, { pose: 'sitHug', view: 'q', flip: true, expr: 'terror', key: 'm5' }); full('#06070A', 70); } },
  photo: { a: () => { sepiaWash(); boilSeed('ph'); tower(1280, 980, 18, { col: '#7A6550', dk: '#5A4836' }); person('elias', 620, 960, 30, { pose: 'fallBack', key: 'el' });
             for (let i = 0; i < 4; i++) person('mob', 300 + i * 130, 980, 28, { pose: 'reach', key: 'mb' + i }); sepiaFilter(1); vignette('#3A2A1A', 200); },
           b: () => { sepiaWash(); boilSeed('ph2'); clockBack({}); clara(960, 960, 30, { pose: 'wind', key: 'c5' }); sepiaFilter(1.2); vignette('#3A2A1A', 220); } },
};
// Ep 6 · Watchers
function watchersStreet(stage) {
  market({ glow: .5, hands: [Math.PI, Math.PI] });
  boilSeed('wst' + stage);
  const rows = stage === 0 ? [[420, 760, 9], [700, 790, 10], [1200, 780, 10], [1520, 760, 9]] : stage === 1 ? [[560, 880, 15], [820, 920, 17], [1150, 910, 16], [1420, 870, 15]] : [[960, 1500, 48]];
  for (const [x, y, u] of rows) watcher(x, y, u);
  if (stage < 2) person('boy', 960, 1070, 30, { view: 'back', pose: 'tense', key: 'a6' });
}
S2[6] = { street: { a: () => watchersStreet(0), b: () => watchersStreet(1), c: () => watchersStreet(2) },
          aadi: { a: () => { full('#0B0D14'); glow(960, 500, 600, '#3A4A3A', .5); bust('boy', 960, 520, 200, { expr: 'terror', tears: 1, key: 'a6c' }); } } };
// Ep 7 · Neha's Warning
S2[7] = {
  bed: { a: () => { bedroom({}); boilSeed('trail'); for (let i = 0; i < 9; i++) paint(ellPts(1000 + i * 90, 880 + (i % 2) * 20, 50, 16, 12), { wash: '#6A8AA0', washOp: 160, ink: null }); },
         b: () => { bedroom({}); for (let i = 0; i < 9; i++) paint(ellPts(1000 + i * 90, 880 + (i % 2) * 20, 50, 16, 12), { wash: '#6A8AA0', washOp: 160, ink: null });
           person('neha', 1150, 860, 27, { expr: 'sad', glitch: .8, key: 'n7' }); person('meera', 500, 760, 26, { pose: 'sitHug', view: 'q', expr: 'terror', key: 'm7' }); } },
  bath: { a: () => { bathroom({}); mirrorFog(110); boilSeed('tub'); paint(rrPts(260, 760, 1400, 280, 120), { wash: '#C9CDD0', ink: CP.ink, sw: 1 }); paint(ellPts(960, 800, 640, 50, 24), { wash: '#1A2A34', ink: CP.ink, sw: .6 }); full('#05070A', 90); },
          b: () => { bathroom({}); mirrorFog(110); paint(rrPts(260, 760, 1400, 280, 120), { wash: '#C9CDD0', ink: CP.ink, sw: 1 }); paint(ellPts(960, 800, 640, 50, 24), { wash: '#1A2A34', ink: CP.ink, sw: .6 });
            boilSeed('hand'); paint(ribbon([[900, 820], [880, 760], [870, 730]], 40, 30), { wash: '#8E9DA8', ink: CP.ink, sw: .8 }); for (let k = 0; k < 4; k++) paint(ribbon([[850 + k * 18, 735], [845 + k * 20, 700], [850 + k * 22, 690]], 12, 8), { wash: '#8E9DA8', ink: CP.ink, sw: .6 }); full('#05070A', 90); } },
};
// Ep 8 · The Second Tower
function tunnel(o = {}) {
  full('#0B0C10'); boilSeed('tun');
  for (let i = 0; i < 6; i++) { const s = 1 - i * .15; paint(ellPts(960, 600, 900 * s, 700 * s, 40), { wash: mixCol('#2A2D34', '#0B0C10', i / 6), ink: CP.ink, sw: .8 }); }
  paint([[600, 1080], [920, 640], [1000, 640], [1320, 1080]], { wash: '#1A1A1E', ink: null });
  inkLine([[760, 1080], [950, 640]], 1, '#7A7A80', 'ink', 0); inkLine([[1160, 1080], [970, 640]], 1, '#7A7A80', 'ink', 0);
  if (o.crack) { inkLine([[1500, 200], [1450, 420], [1520, 600], [1470, 820]], 2, '#000', 'ink', 0); glow(1480, 480, 220, CP.sickGlow, .6); clockFace(1480, 480, 90, { sw: .6, hands: [Math.PI / 2, 0] }); }
  if (o.kids) { person('meera', 820, 1060, 28, { view: 'back', key: 'm8' }); person('boy', 1060, 1060, 24, { view: 'back', key: 'a8' }); glow(940, 700, 300, '#F2E6C8', .4); }
}
function invTower(names) {
  full('#08090C'); boilSeed('inv');
  push(); translate(960, 120); rotate(Math.PI); tower(0, 0, 22, { col: '#262A34', dk: '#1A1D26', hands: [-Math.PI / 2, Math.PI] }); pop();
  glow(960, 120 + 27 * 22, 420, CP.sickGlow, .5);
  if (names) { const c = [960, 120 + 27 * 22], N = ['മീര', 'ആദി', 'അർജുൻ', 'നേഹ', 'സാം', 'റോസ', 'ഏലിയാസ്', 'ആമ്മച്ചി'];
    N.forEach((n, i) => { const a = i / N.length * TAU; letter(n, c[0] + Math.cos(a) * 140, c[1] + Math.sin(a) * 140, i < 2 ? 34 : 24, i < 2 ? '#E9E2D0' : '#8C9686', { ink: false, font: `${i < 2 ? 34 : 24}px "Noto Sans Malayalam"`, rot: a + Math.PI / 2 }); }); }
}
S2[8] = { tunnel: { a: () => tunnel({ kids: 1 }), b: () => tunnel({ crack: 1, kids: 1 }) }, tower: { a: () => invTower(0), b: () => invTower(1) } };
// Ep 9 · Don't Wind It
S2[9] = {
  gears: { a: () => { gearRoom({ spin: 0, dark: 30 }); person('meera', 960, 1060, 30, { pose: 'wind', view: 'back', key: 'm9' }); },
           b: () => { gearRoom({ spin: .25, dark: 30 }); person('meera', 960, 1060, 30, { pose: 'wind', view: 'back', key: 'm9' }); },
           c: () => { gearRoom({ spin: .5, dark: 60 }); person('meera', 760, 1060, 30, { pose: 'fallBack', view: 'q', expr: 'terror', key: 'm9b' }); boilSeed('ch'); paint(ribbon([[1250, 540], [1180, 560], [1120, 575]], 26, 18), { wash: '#8E8A84', ink: CP.ink, sw: .7 }); } },
  arjun: { a: () => { full('#08090C'); glow(960, 520, 500, '#4A3A2A', .5); bust('arjun', 960, 500, 180, { expr: 'terror', key: 'a9' }); full('#05060A', 60); } },
};
// Ep 10 · Ammachi
S2[10] = {
  attic: { a: () => { full('#16130F'); boilSeed('att'); paint([[0, 300], [960, 0], [1920, 300], [1920, 1080], [0, 1080]], { wash: '#221C16', ink: CP.ink, sw: .8 });
             for (let i = 0; i < 6; i++) inkLine([[i * 380, 1080], [960, 0]], .6, '#14110D', 'inkfine', 0); glow(960, 640, 520, CP.lamp, .55);
             person('ammachi', 960, 1000, 30, { pose: 'hold2', expr: 'determined', key: 'am10' }); },
           b: () => { full('#16130F'); boilSeed('att'); paint([[0, 300], [960, 0], [1920, 300], [1920, 1080], [0, 1080]], { wash: '#221C16', ink: CP.ink, sw: .8 });
             for (let i = 0; i < 6; i++) inkLine([[i * 380, 1080], [960, 0]], .6, '#14110D', 'inkfine', 0); glow(960, 640, 520, '#9FD48A', .4);
             person('ammachi', 960, 1000, 30, { pose: 'reach', expr: 'calm', key: 'am10' }); full('#05060A', 60); } },
  chair: { a: () => { veranda({ dusk: .2, lampOff: 1 }); rockingChair(960, 860, 1.1, { rock: .06 }); boilSeed('watch'); glow(1200, 900, 140, CP.sickGlow, .7); paint(ellPts(1200, 900, 30, 30, 14), { wash: CP.brass, ink: CP.ink, sw: .7 }); full('#05060A', 80); } },
};
// Ep 11 · Inside Arjun
S2[11] = {
  arjun: { a: () => { full('#0C0D10'); glow(960, 500, 500, '#5A3A2A', .45); bust('arjun', 960, 470, 190, { expr: 'sad', tears: 1, key: 'a11' });
             boilSeed('chest'); paint(ellPts(960, 960, 220, 160, 24), { wash: '#2A2018', ink: CP.ink, sw: 1 }); gear(900, 950, 80, .3); gear(1030, 980, 60, 1.1, CP.brassDk); full('#05060A', 40); },
           b: () => { full('#0C0D10'); glow(960, 500, 500, '#5A3A2A', .45); bust('arjun', 960, 470, 190, { expr: 'neutral', key: 'a11' });
             clockFace(960 - 190 * .38, 478, 34, { sw: .5, hands: [Math.PI * .5, Math.PI * .5], cracks: false }); clockFace(960 + 190 * .38, 478, 34, { sw: .5, hands: [-Math.PI * .5, -Math.PI * .5], cracks: false }); full('#05060A', 40); } },
  inside: { a: () => { full('#1B1410'); boilSeed('ins'); for (let i = 0; i < 7; i++) gear(200 + hash(i) * 1520, 150 + hash(i + 3) * 780, 120 + hash(i + 7) * 200, i, i % 2 ? CP.brass : CP.brassDk);
              glow(960, 540, 300, '#C9403A', .5); paint(ribbon([[960, 300], [960, 620]], 14, 10), { wash: CP.brass, ink: CP.ink, sw: .8 }); paint(ellPts(960, 640, 60, 60, 20), { wash: '#8E1E22', ink: CP.ink, sw: .9 }); full('#07080A', 50); } },
};
// Ep 12 · The Daughter's Song
function musicBox(o = {}) {
  full('#100E12'); boilSeed('mbox'); glow(960, 560, 500, '#B9A27A', .45);
  paint(rectPts(560, 640, 800, 300), { wash: '#4A2E22', ink: CP.ink, sw: 1.1 }); paint([[560, 640], [1360, 640], [1280, 420], [640, 420]], { wash: '#5A3A2A', ink: CP.ink, sw: 1 });
  paint(ellPts(960, 640, 160, 30, 20), { wash: '#C9B07A', ink: CP.ink, sw: .7 });
  const s = o.spin || 0; push(); translate(960, 620); scale(Math.cos(s * TAU) * .25 + .75, 1);
  paint([[-30, 0], [30, 0], [10, -120], [-10, -120]], { wash: '#E9E2D0', ink: CP.ink, sw: .7 }); clockFace(0, -150, 30, { sw: .4, hands: [Math.PI / 2, 0], cracks: false }); pop();
}
S2[12] = {
  bed: { a: () => { bedroom({}); boilSeed('a12'); head('boy', 250, 592, 40, { view: 'q', flip: true, sw: .8, skin: CP.skin, expr: 'sleep' }); paint([[300, 600], [980, 590], [990, 700], [290, 720]], { wash: CP.maroonDk, ink: CP.ink, sw: .9, curv: .3 });
           person('meera', 760, 840, 26, { pose: 'sit', view: 'q', flip: true, expr: 'calm', key: 'm12' }); },
         b: () => { bedroom({}); head('boy', 250, 592, 40, { view: 'q', flip: true, sw: .8, skin: CP.skin, expr: 'sleep' }); paint([[300, 600], [980, 590], [990, 700], [290, 720]], { wash: CP.maroonDk, ink: CP.ink, sw: .9, curv: .3 });
           person('meera', 760, 840, 26, { pose: 'coverEars', view: 'q', flip: true, expr: 'terror', key: 'm12' }); clara(1500, 840, 20, { key: 'c12' }); full('#05060A', 50); } },
  box: { a: () => musicBox({ spin: 0 }), b: () => musicBox({ spin: .33 }), c: () => musicBox({ spin: .66 }) },
};
// Ep 13 · Every Clock Stops
function frozenStreet(o = {}) {
  market({ glow: .6, hands: [Math.PI / 2, 0] }); rainStreaks(220, 'fr', '#C9D8E6', 150);
  boilSeed('bird'); paint([[1300, 300], [1360, 280], [1420, 300], [1360, 310]], { wash: '#1A1A1E', ink: CP.ink, sw: .6 });
  for (let i = 0; i < 6; i++) person('mob', 300 + i * 260, 960 + (i % 2) * 20, 18, { view: 'back', key: 'fz' + i });
  if (o.kids) { person('meera', 820, 1070, 26, { view: 'q', expr: 'scared', key: 'm13' }); person('boy', 1060, 1070, 22, { view: 'q', flip: true, expr: 'scared', key: 'a13' }); }
}
S2[13] = { street: { a: () => frozenStreet({ kids: 1 }), b: () => { frozenStreet({ kids: 1 }); full('#2A0A0C', 50); } },
           tower: { a: () => { market({ glow: 1, ts: 26, hands: [Math.PI / 2, 0] }); rainStreaks(220, 'fr2', '#C9D8E6', 150); full('#05060A', 40); } } };
// Ep 14 · Her Face
function spiral(o = {}) {
  full('#0C0D10'); boilSeed('sp');
  for (let i = 0; i < 14; i++) { const a = i * .55, y = 1080 - i * 70; paint([[960, y], [960 + Math.cos(a) * 620, y - 20], [960 + Math.cos(a + .5) * 620, y - 70]], { wash: mixCol('#3A3530', '#14120F', i / 14), ink: CP.ink, sw: .7 }); }
  paint(rectPts(1500, 200, 120, 220), { wash: '#2E3A4A', ink: CP.ink, sw: .8 }); glow(1560, 300, 200, '#8FA6C2', .4);
  if (o.kids) { person('meera', 900, 1050, 24, { view: 'back', key: 'm14' }); person('boy', 1060, 1060, 20, { view: 'back', key: 'a14' }); }
}
function claraFace() {
  full('#07080B'); boilSeed('cface'); glow(960, 500, 700, '#3A4A3A', .6);
  paint(ellPts(960, 520, 300, 360, 40), { wash: '#E9E2D6', ink: CP.ink, sw: 1.4 });                     // porcelain half
  paint([[960, 160], [1260, 300], [1260, 760], [960, 880]], { wash: '#B08D4A', ink: CP.ink, sw: 1.2 });   // clockwork half
  gear(1120, 420, 70, .2); gear(1100, 640, 90, 1.0, CP.brassDk); clockFace(1100, 520, 50, { sw: .5, hands: [Math.PI / 2, 0], cracks: false });
  for (const [x, y] of [[860, 470], [1060, 470]]) paint(ellPts(x, y, 46, 30, 16), { wash: '#1A1A1E', ink: CP.ink, sw: .9 });
  paint(ellPts(860, 470, 14, 14, 10), { wash: '#C9E2D2', ink: null });
  inkLine([[860, 500], [850, 620], [860, 700]], 1.6, '#9FC3D6', 'inkfine'); inkLine([[960, 160], [900, 300], [940, 460], [890, 620]], 1.2, CP.ink, 'inkfine');
  for (let i = -4; i <= 4; i++) paint(ribbon([[960 + i * 70, 160], [960 + i * 85, 520], [960 + i * 95, 980]], 34, 14), { wash: CP.hair, ink: CP.ink, sw: .6 });
  paint(ellPts(960, 760, 60, 18, 12), { wash: '#5A2A2A', ink: CP.ink, sw: .8 });
}
S2[14] = { stairs: { a: () => spiral({ kids: 1 }) },
           room: { a: () => { clockBack({}); clara(960, 960, 34, { pose: 'wind', key: 'c14' }); person('meera', 300, 1070, 30, { view: 'q', expr: 'scared', key: 'm14b' }); person('boy', 480, 1075, 25, { view: 'q', expr: 'scared', key: 'a14b' }); } },
           face: { a: () => claraFace() } };
// Ep 15 · Zero
S2[15] = {
  room: { a: () => { clockBack({}); clara(1060, 960, 34, { key: 'c15' }); person('meera', 800, 1000, 30, { pose: 'kneel', view: 'q', expr: 'calm', key: 'm15' }); },
          b: () => { clockBack({ light: .5 }); boilSeed('nm'); letter('ക്ലാര', 960, 500, 120, '#3A2A1A', { ink: false, font: 'bold 120px "Noto Sans Malayalam"' }); person('meera', 800, 1000, 30, { pose: 'kneel', view: 'q', expr: 'cry', key: 'm15' }); glow(1060, 700, 400, '#FFF1C8', .8); } },
  dawn: { a: () => { full('#C9A48A'); boilSeed('dawn'); glow(960, 700, 900, '#FFD8A8', .9); paint(ellPts(960, 300, 1200, 400, 30, 20), { fill: '#E8B88A', fillOp: 120, bleed: .4, ink: null });
            tower(1300, 900, 12, { col: '#6A5A5A', hands: [Math.PI / 2 + .03, .3] }); paint(rectPts(-60, 880, W + 120, 300), { wash: '#4A3A3A', ink: null });
            person('meera', 760, 1040, 28, { view: 'q', expr: 'smile', key: 'm15d' }); person('boy', 960, 1045, 23, { view: 'q', flip: true, expr: 'smile', key: 'a15d' }); } },
  mirror: { a: () => { bathroom({ mirrorCol: '#6D7B88' }); bust('meera', 960, 430, 120, { expr: 'calm', key: 'mm15' }); paint(rectPts(590, 150, 740, 560), { fill: '#A8B6C2', fillOp: 35, bleed: .2, ink: null }); },
            b: () => { bathroom({ mirrorCol: '#6D7B88' }); bust('meera', 960, 430, 120, { expr: 'sleep', key: 'mm15' }); paint(rectPts(590, 150, 740, 560), { fill: '#A8B6C2', fillOp: 35, bleed: .2, ink: null }); } },
};

// ---------- loops ----------
for (const [n, scenes] of Object.entries(S2)) for (const [sc, vars] of Object.entries(scenes)) for (const [v, fn] of Object.entries(vars)) {
  const name = `s2e${n}_${sc}_${v}`;
  LOOPS[name] = t => { if (!window._ng) { const c = grainC.getContext('2d'); c.fillStyle = '#fff'; c.fillRect(0, 0, W, H); window._ng = 1; }
    BOILN = 0; boilSeed('frame'); const i = Math.round(t * 10), col = i % 2, row = Math.floor(i / 2);
    camBegin((col * W + W / 2) / 2, (row * H + H / 2) / 2, 2); fn(); camEnd(); };
  LOOPS[name].len = 1;
}
// count cards 0–15 (two stages each: clean, cracked)
for (let n = 0; n <= 15; n++) { LOOPS['s2_count_' + n] = t => { if (!window._ng) { const c = grainC.getContext('2d'); c.fillStyle = '#fff'; c.fillRect(0, 0, W, H); window._ng = 1; } BOILN = 0; countCard(n, Math.round(t * 10) ? 1 : .3); }; LOOPS['s2_count_' + n].len = 1; }
window.S2_PLATES = () => { const out = []; for (const [n, scenes] of Object.entries(S2)) for (const [sc, vars] of Object.entries(scenes)) for (const v of Object.keys(vars)) out.push(`s2e${n}_${sc}_${v}`); return out; };
