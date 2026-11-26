// ഒരു റിപ്ലൈ (One Reply) · trial Episode 1 "2:14 AM": painted PLATES (portrait 1080x1920 world).
// Same pipeline as COUNTDOWN S2: these loops paint each place once, big and still; the Python compositor
// (love-story/tools/ep01.py) moves the camera, cuts, draws the phone UI, clock hands, rain and glow.
// Render a plate:  node render.mjs --page=onereply.html --soft-gl --loop=<name> --stills=0,0.1,...,0.7 --out=<dir>
//   t encodes the tile index (round(t*10)); tiles are 1920x1080 views at zoom 2 of the 1080x1920 world.

// ---------- cast ----------
const OR = { warm: '#F2B45C', warmLt: '#FFD99A', screen: '#9FC3E8', night: '#151A28', wall: '#1E2436', teal: '#1F7A78', tealDk: '#155957', gold: '#D9A93A' };
COSTUME.aadhi = { h: 17.2, skin: '#A06A4E', top: '#46505F', topDk: '#333B48', sleeve: '#46505F', legs: '#2B2F3A', shoes: '#1C1D22', torsoW: [2.35, 1.95], limbW: 1.02, hood: true };
COSTUME.nila  = { h: 16.4, skin: '#B98466', top: OR.teal, topDk: OR.tealDk, sleeve: OR.teal, legs: '#E7C27C', shoes: '#7A4A2A', torsoW: [2.0, 1.85], limbW: .88, dress: true };

// Aadhi wears Arjun-style short hair (no glasses); Nila wears long hair + jasmine, gold earrings, a small bindi.
const _orHead = head;
head = function (name, cx, cy, r, o) {
  if (name === 'aadhi') return _orHead('arjun', cx, cy, r, o);
  if (name !== 'nila') return _orHead(name, cx, cy, r, o);
  const view = o.view || 'front', fl = o.flip ? -1 : 1, sw = o.sw;
  if (view !== 'back') { // long hair falling behind the shoulders
    paint(through([[cx - r * 1.1, cy - r * .4], [cx - r * 1.35, cy + r * 1.2], [cx - r * 1.2, cy + r * 2.6], [cx - r * .6, cy + r * 2.2],
      [cx, cy + r * 1.4], [cx + r * .6, cy + r * 2.2], [cx + r * 1.2, cy + r * 2.6], [cx + r * 1.35, cy + r * 1.2], [cx + r * 1.1, cy - r * .4], [cx, cy - r * 1.25]], 3),
      { wash: CP.hair, ink: CP.ink, sw });
  }
  _orHead('meera', cx, cy, r, { ...o, darkCircles: false });
  if (view === 'back') return;
  const q = view === 'q' ? fl * r * .28 : 0;
  paint(ellPts(cx + q, cy - r * .32, r * .07, r * .07, 8), { wash: '#9E2A34', ink: null });                       // bindi
  for (const s of [-1, 1]) { boilSeed('ear' + s); paint(ellPts(cx + s * r * .95, cy + r * .45, r * .1, r * .14, 10), { wash: OR.gold, ink: CP.ink, sw: sw * .5 }); }
  for (let i = 0; i < 7; i++) { boilSeed('jas' + i); const a = -2.2 + i * .28;                                // jasmine string behind the head
    paint(ellPts(cx + Math.cos(a) * r * 1.02 + r * .55, cy + Math.sin(a) * r * 1.02 + r * .2, r * .11, r * .11, 8), { wash: '#F3EEE2', ink: CP.ink, sw: sw * .35 }); }
};

function noGrain() { if (window._ng) return; const c = grainC.getContext('2d'); c.fillStyle = '#fff'; c.fillRect(0, 0, W, H); window._ng = 1; }
function orTile(t, z, drawFn) {          // portrait world 1080x1920 → tiles of 1920x1080 at zoom z (row-major)
  noGrain(); BOILN = 0; boilSeed('frame');
  const RW = 1080, RH = 1920, nx = Math.ceil(RW * z / W), i = Math.round(t * 10), col = i % nx, row = Math.floor(i / nx);
  camBegin((col * W + W / 2) / z, (row * H + H / 2) / z, z); drawFn(); camEnd();
}

// ---------- ROOM (night, rain, wall clock without hands) ----------
// o.a: 'lie' | 'smile' | 'sit' | 'back'
function orRoom(o = {}) {
  boilSeed('orroom');
  paint(rectPts(-200, -200, 1480, 2400), { wash: OR.wall, fill: '#262D42', fillOp: 70, bleed: .1, tex: .5, ink: null });
  // window (top right) with the night city
  const WX = 560, WY = 210, WW = 420, WH = 560;
  paint(rectPts(WX, WY, WW, WH), { wash: '#0D1220', ink: null });
  boilSeed('orsky'); glow(WX + 300, WY + 110, 160, '#B8C6DE', .35);
  paint(ellPts(WX + 300, WY + 110, 34, 34, 20), { wash: '#DCE3EC', ink: null });
  for (let i = 0; i < 9; i++) { boilSeed('orb' + i); const bx = WX + i * 52 - 10, bh = 120 + hash(i * 3.7) * 220;
    paint(rectPts(bx, WY + WH - bh, 48, bh), { wash: i % 2 ? '#141A2A' : '#18203A', ink: null });
    for (let r = 0; r < 6; r++) for (let c = 0; c < 2; c++) { const id = i * 40 + r * 3 + c; if (hash(id) < .55) continue;
      paint(rectPts(bx + 8 + c * 20, WY + WH - bh + 16 + r * 34, 11, 14), { wash: OR.warm, washOp: 170, ink: null }); } }
  const fr = '#3B3029', sw = 1;
  for (const [x, y, w, h] of [[WX - 24, WY - 24, WW + 48, 30], [WX - 24, WY + WH - 6, WW + 48, 34], [WX - 24, WY - 24, 28, WH + 48], [WX + WW - 4, WY - 24, 28, WH + 48], [WX + WW / 2 - 7, WY, 14, WH]])
    paint(rectPts(x, y, w, h), { wash: fr, ink: CP.ink, sw });
  paint([[WX + 20, WY + WH + 40], [WX + WW - 20, WY + WH + 40], [WX + WW + 160, 1500], [WX - 260, 1500]], { fill: '#7D8AA6', fillOp: 26, bleed: .3, ink: null });
  // wall clock (hands added by the compositor)
  clockFace(250, 430, 92, { sw: .8, hands: null, cracks: false, col: '#D8D0BC' });
  // shelf + poster shapes
  paint(rectPts(70, 760, 330, 16), { wash: CP.wood, ink: CP.ink, sw: .7 });
  paint(rectPts(100, 700, 40, 60), { wash: '#5B4A62', ink: CP.ink, sw: .6 }); paint(rectPts(150, 690, 32, 70), { wash: '#4A5A6E', ink: CP.ink, sw: .6 });
  paint(ellPts(300, 735, 34, 26, 14), { wash: '#3E6B4E', ink: CP.ink, sw: .6 });
  // bed
  paint(rectPts(-60, 1240, 1200, 120), { wash: '#3A2E2A', ink: CP.ink, sw: 1 });
  paint(rectPts(-60, 1330, 1200, 700), { wash: '#2C2630', ink: CP.ink, sw: 1 });
  const a = o.a || 'lie';
  if (a === 'sit') {
    paint(rrPts(120, 1040, 300, 120, 50), { wash: '#BDB6A8', ink: CP.ink, sw: .9 });
    bust('aadhi', 480, 1010, 118, { expr: 'smile', look: [.1, .9], key: 'sit' });
    paint(through([[80, 1500], [300, 1330], [480, 1300], [700, 1330], [980, 1480], [1100, 2000], [-60, 2000]], 3), { wash: CP.maroonDk, ink: CP.ink, sw: 1 });
    phone(480, 1310, 120, { glowA: .55, hand: false, screen: '#B9D4EE' });
    for (const s of [-1, 1]) paint(ellPts(480 + s * 64, 1380, 34, 40, 14), { wash: COSTUME.aadhi.skin, ink: CP.ink, sw: .8 });
  } else {
    paint(rrPts(60, 1180, 360, 130, 55), { wash: '#BDB6A8', ink: CP.ink, sw: .9 });
    const expr = a === 'smile' ? 'smile' : a === 'back' ? 'calm' : 'tired', look = a === 'back' ? [0, -1] : [.9, -.7];
    lyingHead('aadhi', 250, 1225, 96, { rot: -1.45, expr, look, key: 'lie' + a });
    paint(through([[330, 1180], [700, 1150], [1140, 1170], [1140, 2000], [300, 2000], [320, 1400]], 3), { wash: CP.maroonDk, ink: CP.ink, sw: 1 });
    if (a !== 'back') {
      paint(ribbon([[520, 1330], [600, 1180], [610, 1060]], 44, 36), { wash: COSTUME.aadhi.sleeve, ink: CP.ink, sw: .9 });
      phone(615, 980, 120, { glowA: .65, hand: false, screen: '#B9D4EE' });
      paint(ellPts(612, 1062, 34, 30, 14), { wash: COSTUME.aadhi.skin, ink: CP.ink, sw: .8 });
    } else {
      phone(520, 1290, 110, { glowA: .45, hand: false, screen: '#B9D4EE' });       // resting on his chest
    }
  }
}

// ---------- FACE close-up (lit from below by the phone) ----------
function orFace(o = {}) {
  boilSeed('orface');
  paint(rectPts(-200, -200, 1480, 2400), { wash: '#141A28', fill: '#1B2133', fillOp: 80, bleed: .1, tex: .5, ink: null });
  boilSeed('orfacebk'); glow(820, 380, 300, '#3A4766', .5);
  for (let i = 0; i < 6; i++) { boilSeed('bk' + i); paint(ellPts(120 + i * 170, 260 + hash(i) * 300, 26, 26, 14), { wash: OR.warm, washOp: 60, ink: null }); }
  boilSeed('orfaceglow'); glow(540, 1500, 700, OR.screen, .55);
  bust('aadhi', 540, 820, 235, { expr: o.expr || 'tired', look: o.look || [0, 1], key: 'cu' + (o.expr || ''), tears: o.tears });
  // the phone edge at the bottom, in both hands
  paint(rrPts(330, 1560, 420, 520, 60), { wash: '#15171C', ink: CP.ink, sw: 1.4 });
  for (const s of [-1, 1]) paint(ellPts(540 + s * 250, 1700, 90, 110, 16), { wash: COSTUME.aadhi.skin, ink: CP.ink, sw: 1.1 });
  boilSeed('orfaceglow2'); glow(540, 1560, 360, OR.screen, .35);
}

// ---------- NILA's reel (terrace at night, fairy lights) ----------
const DANCE = [
  { lean: .04, aL: [2.7, .25], aR: [-1.15, -.9], lL: [.15, 0], lR: [-.25, .3] },
  { lean: 0, aL: [1.25, 1.45], aR: [-1.25, -1.45], lL: [.35, -.4], lR: [-.35, .4] },
  { lean: -.08, aL: [.7, .25], aR: [-2.5, -.35], lL: [-.1, 0], lR: [-.4, .5] },
  { lean: 0, aL: [2.1, .95], aR: [-2.1, -.95], lL: [.4, 0], lR: [-.08, 0] },
];
function orNila(o = {}) {
  boilSeed('ornila');
  paint(rectPts(-200, -200, 1480, 2400), { wash: '#1A1626', fill: '#2A2140', fillOp: 90, bleed: .2, tex: .5, ink: null });
  for (let i = 0; i < 14; i++) { boilSeed('bok' + i); const x = hash(i * 4.1) * 1080, y = 700 + hash(i * 7.3) * 500, r = 30 + hash(i) * 40;
    paint(ellPts(x, y, r, r, 16), { wash: i % 3 ? '#E9A85A' : '#C77AA0', washOp: 70, ink: null }); }
  // terrace wall + floor
  paint(rectPts(-60, 1320, 1200, 110), { wash: '#4A3A44', ink: CP.ink, sw: .9 });
  paint(rectPts(-60, 1420, 1200, 600), { wash: '#3A2C36', fill: '#4A3640', fillOp: 70, bleed: .2, ink: null });
  // fairy-light strings
  for (const [y0, sag] of [[330, 140], [520, 110]]) {
    const pts = []; for (let i = 0; i <= 20; i++) { const x = -40 + i * 58, k = i / 20; pts.push([x, y0 + Math.sin(k * Math.PI) * sag]); }
    inkLine(pts, .7, '#2A2430', 'inkfine', .4);
    pts.forEach(([x, y], i) => { if (i % 2) return; boilSeed('fl' + y0 + i); glow(x, y + 10, 46, OR.warm, .8); paint(ellPts(x, y + 10, 8, 10, 10), { wash: OR.warmLt, ink: null }); });
  }
  // potted plant + lamp for depth
  paint(rectPts(80, 1250, 120, 110), { wash: '#7A4A2A', ink: CP.ink, sw: .8 });
  for (let i = 0; i < 5; i++) paint(ribbon([[140, 1260], [100 + i * 22, 1120 - hash(i) * 60]], 18, 4), { wash: '#3E6B4E', ink: CP.ink, sw: .6 });
  boilSeed('ornilaglow'); glow(540, 1050, 520, OR.warm, .3);
  person('nila', 540, 1660, 48, { rig: DANCE[o.pose || 0], expr: o.expr || 'smile', look: o.look || [0, 0], key: 'd' + (o.pose || 0) });
}

const L1 = (name, fn) => { LOOPS[name] = fn; LOOPS[name].len = 1; };
L1('or_room_lie',   t => orTile(t, 2, () => orRoom({ a: 'lie' })));
L1('or_room_smile', t => orTile(t, 2, () => orRoom({ a: 'smile' })));
L1('or_room_sit',   t => orTile(t, 2, () => orRoom({ a: 'sit' })));
L1('or_room_back',  t => orTile(t, 2, () => orRoom({ a: 'back' })));
L1('or_face_tired', t => orTile(t, 2, () => orFace({ expr: 'tired', look: [0, 1] })));
L1('or_face_wonder',t => orTile(t, 2, () => orFace({ expr: 'shock', look: [0, .8] })));
L1('or_face_smile', t => orTile(t, 2, () => orFace({ expr: 'smile', look: [0, 1] })));
L1('or_face_sad',   t => orTile(t, 2, () => orFace({ expr: 'sad', look: [0, 1] })));
L1('or_face_shock', t => orTile(t, 2, () => orFace({ expr: 'terror', look: [0, .6] })));
for (let p = 0; p < 4; p++) L1('or_nila_' + p, t => orTile(t, 2, () => orNila({ pose: p, look: [[.3, 0], [0, .2], [-.3, -.1], [0, -.2]][p] })));
