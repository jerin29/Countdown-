// COUNTDOWN sets: the locations, painted. Every function paints the whole frame in screen space (1920x1080)
// unless noted. o.k (0..1) dims lights etc. Keep each to a few dozen shapes.

const full = (col, op = 255) => paint(rectPts(-80, -80, W + 160, H + 160), { wash: col, washOp: op, ink: null });
const fogBand = (y, h, col = CP.fog, op = 110, key = 'fog') => { boilSeed(key); paint(ellPts(W / 2, y, W * .75, h, 30, 6), { fill: col, fillOp: op, bleed: .35, tex: .3, ink: null }); };
function stars(n = 30, key = 'st') { for (let i = 0; i < n; i++) { const x = hash(i * 3.1) * W, y = hash(i * 7.7) * H * .45; paint(ellPts(x, y, 1.6, 1.6, 6), { wash: '#CFD6E0', ink: null }); } }

// The Varkey tower: (x, y) = base centre, s = scale (tower is ~ 9s wide, 40s tall)
function tower(x, y, s, o = {}) {
  boilSeed('tower' + Math.round(x) + Math.round(s));
  const col = o.col || CP.stone, dk = o.dk || '#262A34', sw = o.sw ?? clamp(s / 14, .3, 1.4);
  paint([[x - 5 * s, y], [x - 4.2 * s, y - 34 * s], [x + 4.2 * s, y - 34 * s], [x + 5 * s, y]], { wash: col, ink: CP.ink, sw });
  paint([[x - 4.8 * s, y - 34 * s], [x, y - 44 * s], [x + 4.8 * s, y - 34 * s]], { wash: dk, ink: CP.ink, sw });
  for (let i = 0; i < 5; i++) inkLine([[x - 4.6 * s, y - (6 + i * 6) * s], [x + 4.6 * s, y - (6 + i * 6) * s]], sw * .5, dk, 'inkfine', 0);
  paint(rrPts(x - 1.2 * s, y - 6 * s, 2.4 * s, 6 * s, 1.2 * s), { wash: '#15171D', ink: CP.ink, sw: sw * .7 });
  clockFace(x, y - 27 * s, 3.2 * s, { sw: sw * .8, glow: o.glow || 0, glowCol: o.glowCol, col: o.faceCol, hands: o.hands || null });
  if (o.figure) paint([[x - .8 * s, y - 24.6 * s], [x - .5 * s, y - 29 * s], [x, y - 29.8 * s], [x + .5 * s, y - 29 * s], [x + .8 * s, y - 24.6 * s]], { wash: CP.coat, washOp: 230, ink: null });
  if (o.faces) for (let i = 0; i < 5; i++) { const a = i / 5 * TAU + .4; paint(ellPts(x + Math.cos(a) * 1.8 * s, y - 27 * s + Math.sin(a) * 1.8 * s, .55 * s, .65 * s, 10), { wash: '#C8D0B8', washOp: 200, ink: CP.ink, sw: sw * .4 }); }
}

function hills(o = {}) {
  boilSeed('hills');
  paint([[-100, 760], [300, 640], [700, 690], [1100, 600], [1500, 660], [2020, 610], [2020, 1200], [-100, 1200]], { wash: o.far || '#2A3142', ink: null, curv: .5 });
  paint([[-100, 880], [400, 800], [900, 850], [1400, 780], [2020, 840], [2020, 1200], [-100, 1200]], { wash: o.near || '#1E2431', ink: null, curv: .5 });
}

function nightSky(o = {}) {
  full(o.sky || CP.night);
  boilSeed('sky');
  paint(ellPts(W * .5, H * .2, W * .8, H * .4, 24, 10), { fill: '#2B3350', fillOp: 120, bleed: .3, tex: .3, ink: null });
  if (o.stars !== false) stars(28);
}

// window frame (x, y, w, h) with tower view inside; o.reflect paints a figure reflected on the glass
function windowFrame(x, y, w, h, o = {}) {
  boilSeed('win' + x);
  push();
  paint(rectPts(x, y, w, h), { wash: '#232A3B', ink: null });
  paint(rectPts(x + w * .05, y + h * .55, w * .9, h * .4), { wash: '#1B2030', ink: null });
  tower(x + w * (o.tx ?? .62), y + h * .78, h / 70 * (o.ts || 1), { glow: o.glow || 0, figure: o.figure, hands: o.hands, faces: o.faces });
  fogBand(y + h * .75, h * .18, CP.fog, 90, 'wf' + x);
  pop();
  const fr = '#3B3029', sw = .9;
  paint(rectPts(x - 26, y - 26, w + 52, 34), { wash: fr, ink: CP.ink, sw });
  paint(rectPts(x - 26, y + h - 8, w + 52, 34), { wash: fr, ink: CP.ink, sw });
  paint(rectPts(x - 26, y - 26, 30, h + 52), { wash: fr, ink: CP.ink, sw });
  paint(rectPts(x + w - 4, y - 26, 30, h + 52), { wash: fr, ink: CP.ink, sw });
  paint(rectPts(x + w / 2 - 8, y, 16, h), { wash: fr, ink: CP.ink, sw: sw * .7 });
  if (o.breath) paint(ellPts(x + w * .3, y + h * .55, w * .14, h * .1, 20, 4), { fill: '#C9D2DA', fillOp: 120, bleed: .3, ink: null });
}

function bedroom(o = {}) {
  full('#1E2333');
  boilSeed('bedroom');
  paint(rectPts(-50, 820, W + 100, 400), { wash: '#2A2526', ink: null });                    // floor
  inkLine([[-50, 820], [W + 50, 820]], 1, CP.ink, 'ink', 0);
  windowFrame(1180, 170, 520, 470, { glow: o.glow || 0, figure: o.figure, breath: o.breath });
  // bed
  paint(rectPts(80, 610, 900, 230), { wash: '#3A3140', ink: CP.ink, sw: 1 });
  paint(rectPts(60, 440, 60, 420), { wash: CP.wood, ink: CP.ink, sw: 1 });
  paint(rrPts(130, 560, 230, 90, 40), { wash: '#C9C1B2', ink: CP.ink, sw: .9 });               // pillow
  if (o.blanket !== false) paint([[330, 600], [980, 590], [990, 700], [320, 720]], { wash: CP.maroonDk, ink: CP.ink, sw: .9, curv: .3 });
  // wall clock (stopped) and a poster
  clockFace(760, 300, 60, { sw: .6, hands: [Math.PI * .0, Math.PI], cracks: false });
  paint(rectPts(420, 220, 170, 220), { wash: '#3B4458', ink: CP.ink, sw: .7 });
  if (o.phoneGlow) glow(o.phoneGlow[0], o.phoneGlow[1], 220, '#9FC3E8', .8);
  if (o.dark !== false) full('#0B0E18', 70);
}

function hallway(o = {}) {
  full('#161A25');
  boilSeed('hall');
  paint([[0, 0], [600, 260], [600, 820], [0, 1080]], { wash: '#232838', ink: CP.ink, sw: .8 });
  paint([[1920, 0], [1320, 260], [1320, 820], [1920, 1080]], { wash: '#232838', ink: CP.ink, sw: .8 });
  paint([[600, 820], [1320, 820], [1920, 1080], [0, 1080]], { wash: '#2A2526', ink: CP.ink, sw: .8 });
  paint(rectPts(780, 330, 360, 490), { wash: '#2C2A2E', ink: CP.ink, sw: .9 });                // door at end
  paint(rectPts(840, 380, 120, 440), { wash: '#0D0F15', ink: null });                           // ajar
}

function classroom(o = {}) {
  full('#8A8F94');
  boilSeed('class');
  paint(rectPts(-50, 700, W + 100, 500), { wash: '#6E675E', ink: null });
  paint(rectPts(260, 140, 900, 360), { wash: '#2F3B36', ink: CP.ink, sw: 1 });                // blackboard
  for (let i = 0; i < 3; i++) { paint(rectPts(1300 + i * 200, 140, 150, 300), { wash: '#B9C2C9', ink: CP.ink, sw: .8 }); inkLine([[1375 + i * 200, 140], [1375 + i * 200, 440]], .6, CP.ink, 'inkfine', 0); }
  for (let r = 0; r < 2; r++) for (let c = 0; c < 4; c++) {
    const x = 160 + c * 430 + r * 60, y = 760 + r * 170, s = 1 + r * .2;
    paint(rectPts(x, y, 300 * s, 40 * s), { wash: CP.woodLt, ink: CP.ink, sw: .8 });
    paint(rectPts(x + 20, y + 40 * s, 16, 120 * s), { wash: CP.wood, ink: CP.ink, sw: .6 });
    paint(rectPts(x + 280 * s - 36, y + 40 * s, 16, 120 * s), { wash: CP.wood, ink: CP.ink, sw: .6 });
  }
  if (o.dim) full('#2A3040', 80);
}

function corridor(o = {}) {
  full('#5F666E');
  boilSeed('corr');
  paint([[0, 900], [1920, 900], [1920, 1080], [0, 1080]], { wash: '#4A4A48', ink: null });
  for (let i = 0; i < 5; i++) {
    const x = 120 + i * 380, on = o.lightsOff ? i >= o.lightsOff : true;
    paint(rectPts(x, 40, 220, 26), { wash: on ? '#E8E4D2' : '#3A3C42', ink: CP.ink, sw: .6 });
    if (on) glow(x + 110, 60, 260, '#FFF1C8', .5);
  }
  // trophy case
  paint(rectPts(560, 280, 800, 520), { wash: CP.wood, ink: CP.ink, sw: 1 });
  paint(rectPts(600, 320, 720, 440), { wash: '#7C8790', ink: CP.ink, sw: .7 });
  classPhoto(830, 420, 260, { small: true, clock: o.clock });
  for (const [x, h] of [[640, 120], [1240, 90], [1170, 140]]) paint([[x, 740], [x + 50, 740], [x + 40, 740 - h], [x + 10, 740 - h]], { wash: CP.brass, ink: CP.ink, sw: .6 });
  if (o.dark) full('#0E1118', o.dark);
}

// the class photo: rows of tiny kids; one has a clock for a head
function classPhoto(x, y, w, o = {}) {
  boilSeed('photo' + x);
  const h = w * .66;
  paint(rectPts(x - 12, y - 12, w + 24, h + 24), { wash: CP.woodLt, ink: CP.ink, sw: .8 });
  paint(rectPts(x, y, w, h), { wash: '#B8B2A4', ink: CP.ink, sw: .6 });
  const r = w / 32;
  for (let row = 0; row < 3; row++) for (let c = 0; c < 7; c++) {
    const cx = x + w * (.1 + c * .133) + (row % 2) * r, cy = y + h * (.25 + row * .28);
    paint(rectPts(cx - r * 1.3, cy + r * .9, r * 2.6, r * 2.6), { wash: row === 1 ? CP.maroon : '#3E4A5C', ink: null });
    if (o.clock && row === 1 && c === 3) clockFace(cx, cy, r * 1.25, { sw: .35, hands: o.hands || null, cracks: false });
    else { paint(ellPts(cx, cy, r, r * 1.1, 10), { wash: CP.skin, ink: CP.ink, sw: .3 }); paint(ellPts(cx, cy - r * .5, r, r * .6, 10), { wash: CP.hair, ink: null }); }
  }
}

function bathroom(o = {}) {
  full('#3D4652');
  boilSeed('bath');
  for (let i = 0; i < 14; i++) for (let j = 0; j < 8; j++) inkLine([[i * 150, j * 150], [i * 150 + 150, j * 150]], .4, '#2E3540', 'inkfine', 0);
  for (let i = 0; i < 14; i++) inkLine([[i * 150, 0], [i * 150, 1080]], .4, '#2E3540', 'inkfine', 0);
  paint(rectPts(560, 120, 800, 620), { wash: CP.woodLt, ink: CP.ink, sw: 1 });                // mirror frame
  paint(rectPts(590, 150, 740, 560), { wash: o.mirrorCol || '#5D6B78', ink: CP.ink, sw: .7 });
  paint(rectPts(480, 780, 960, 120), { wash: '#C9CDD0', ink: CP.ink, sw: 1 });                  // sink
  paint(rectPts(930, 720, 60, 70), { wash: CP.silver, ink: CP.ink, sw: .7 });
}
// fog layer on the mirror (call after anything "in" the mirror). holes: [[x,y,r]] cleared (hand prints)
function mirrorFog(op = 150, holes = []) {
  boilSeed('mfog');
  paint(rectPts(590, 150, 740, 560), { fill: '#C4CCD3', fillOp: op, bleed: .2, tex: .5, ink: null });
  for (const [x, y, r] of holes) paint(through([[x - r, y + r], [x - r, y - r * .5], [x - r * .5, y - r * 1.6], [x, y - r * .6], [x + r * .4, y - r * 1.7], [x + r, y - r * .4], [x + r, y + r]], 2), { wash: '#4C5864', ink: null });
}

function veranda(o = {}) {
  const dusk = o.dusk ?? 1;
  full(mixCol('#2A2440', '#3B3A52', dusk));
  boilSeed('ver');
  paint(rectPts(-50, 0, W + 100, 120), { wash: '#3A2C24', ink: CP.ink, sw: .8 });             // roof edge
  for (const x of [180, 900, 1640]) paint(rectPts(x, 110, 70, 720), { wash: '#C2B49C', ink: CP.ink, sw: .9 });
  paint(rectPts(-50, 820, W + 100, 400), { wash: '#6B3A2E', ink: null });                      // red oxide floor
  inkLine([[-50, 820], [W + 50, 820]], 1, CP.ink, 'ink', 0);
  // nilavilakku (oil lamp)
  const lx = o.lampX ?? 1250, lit = o.lampOff ? 0 : 1;
  paint([[lx - 40, 820], [lx + 40, 820], [lx + 12, 700], [lx - 12, 700]], { wash: CP.brass, ink: CP.ink, sw: .8 });
  paint(ellPts(lx, 690, 60, 16, 16), { wash: CP.brass, ink: CP.ink, sw: .8 });
  if (lit) { glow(lx, 650, 380, CP.lamp, .9); paint(through([[lx - 8, 680], [lx, 640], [lx + 8, 680]], 3), { wash: '#FFD77A', ink: null }); }
  if (o.frozenFlame) paint(through([[lx - 10, 680], [lx, 630], [lx + 10, 680]], 3), { wash: '#BFE3FF', ink: CP.ink, sw: .4 });
}
function rockingChair(x, y, s, o = {}) {
  boilSeed('chair' + x);
  const a = o.rock || 0, sw = .9;
  push(); translate(x, y); rotate(a);
  paint(through([[-260 * s, 0], [0, 30 * s], [260 * s, 0]], 4), { ink: CP.ink, sw: sw * 2.5 });
  paint(rectPts(-170 * s, -230 * s, 30 * s, 230 * s), { wash: CP.wood, ink: CP.ink, sw });
  paint(rectPts(140 * s, -180 * s, 30 * s, 180 * s), { wash: CP.wood, ink: CP.ink, sw });
  paint([[-190 * s, -210 * s], [170 * s, -200 * s], [170 * s, -170 * s], [-190 * s, -180 * s]], { wash: CP.woodLt, ink: CP.ink, sw });
  paint([[-200 * s, -560 * s], [-130 * s, -560 * s], [-120 * s, -200 * s], [-180 * s, -200 * s]], { wash: CP.woodLt, ink: CP.ink, sw });
  pop();
}

function sepiaWash() { full(CP.sepiaLt); boilSeed('sep'); paint(ellPts(W / 2, H / 2, W * .7, H * .6, 30, 20), { fill: CP.sepia, fillOp: 90, bleed: .4, tex: .7, ink: null }); }
function sepiaFilter(k = 1) { full('#8C6E48', 70 * k); }
function vignette(col = '#07080C', op = 200) {
  boilSeed('vig');
  for (const [x, y, rx, ry] of [[-200, H / 2, 420, 900], [W + 200, H / 2, 420, 900], [W / 2, -180, 1300, 300], [W / 2, H + 180, 1300, 300]])
    paint(ellPts(x, y, rx, ry, 24, 10), { fill: col, fillOp: op * .6, bleed: .4, tex: .2, ink: null });
}

function terrace(o = {}) {
  nightSky();
  hills();
  tower(o.tx ?? 1400, 760, o.ts ?? 7, { glow: o.glow || 0, figure: o.figure });
  fogBand(780, 120, CP.fog, 100, 'tf');
  paint(rectPts(-50, 900, W + 100, 300), { wash: '#3A3A3E', ink: CP.ink, sw: .8 });             // parapet
  for (let i = 0; i < 12; i++) inkLine([[i * 170, 900], [i * 170, 1080]], .5, '#2A2A2E', 'inkfine', 0);
}

// phone UI overlay: REC dot + timecode (the found-footage episode)
function phoneUI(tc, o = {}) {
  paint(rectPts(-60, -60, W + 120, 120), { wash: '#08090D', washOp: 160, ink: null });
  paint(ellPts(80, 50, 14, 14, 12), { wash: '#D23A3A', ink: null });
  letter('REC ' + tc, 230, 52, 40, '#F2F2F2', { screen: true, ink: false, font: '40px monospace' });
  for (const [x, y, dx, dy] of [[40, 120, 1, 1], [W - 40, 120, -1, 1], [40, H - 40, 1, -1], [W - 40, H - 40, -1, -1]]) {
    inkLine([[x, y + dy * 80], [x, y], [x + dx * 80, y]], 1, '#E8E8E8', 'inkfine', 0);
  }
  if (o.glitch) vhs(W / 2, H / 2, W, H / 2, o.glitch);
}

function market(o = {}) {
  const day = o.day;
  full(day ? '#C9CFD2' : CP.night);
  if (!day) stars(20);
  boilSeed('mkt');
  paint([[-50, 700], [500, 560], [500, 900], [-50, 980]], { wash: day ? '#9A928A' : '#262A35', ink: CP.ink, sw: .8 });
  paint([[1970, 700], [1420, 560], [1420, 900], [1970, 980]], { wash: day ? '#8E8780' : '#232733', ink: CP.ink, sw: .8 });
  tower(960, 900, o.ts ?? 16, { glow: o.glow || 0, figure: o.figure, col: day ? '#6A6E78' : CP.stone, faces: o.faces, hands: o.hands });
  paint(rectPts(-50, 900, W + 100, 300), { wash: day ? '#8A847C' : '#2A2A30', ink: CP.ink, sw: .8 });
  for (let i = 0; i < 9; i++) inkLine([[i * 240 - 100, 1080], [960 + (i - 4) * 40, 900]], .5, day ? '#6E6860' : '#1E1E24', 'inkfine', 0);
  if (!day) fogBand(880, 140, CP.fog, 110, 'mf');
  if (day) glow(1600, 120, 700, '#FFE8B8', .7);
}

function shopInterior(o = {}) {
  full('#2A2622');
  boilSeed('shop');
  for (let i = 0; i < 26; i++) {
    const x = 90 + (i % 9) * 215 + (Math.floor(i / 9) % 2) * 60, y = 160 + Math.floor(i / 9) * 250, r = 50 + hash(i) * 35;
    clockFace(x, y, r, { sw: .5, hands: [Math.PI * 0, Math.PI], cracks: hash(i + 9) < .3, rim: hash(i + 4) < .5 ? CP.brassDk : CP.wood });
  }
  paint(rectPts(-50, 820, W + 100, 400), { wash: '#3A3029', ink: null });
  paint(rectPts(200, 760, 1500, 80), { wash: CP.woodLt, ink: CP.ink, sw: 1 });                // workbench
  for (let i = 0; i < 4; i++) inkLine([[hash(i) * W, 0], [hash(i + 1) * W, 300]], .4, '#8C8478', 'inkfine');  // cobwebs
  full('#0C0D10', o.dark ?? 60);
}

function gearRoom(o = {}) {
  full('#1B1713');
  boilSeed('gears');
  const G = [[420, 420, 330], [1050, 300, 230], [1500, 640, 380], [760, 860, 250]];
  for (const [i, [x, y, r]] of G.entries()) {
    const a = (o.spin || 0) * (i % 2 ? -1 : 1) + i;
    const pts = []; for (let k = 0; k < 64; k++) { const ang = a + k / 64 * TAU, rr = r * (k % 4 < 2 ? 1 : .88); pts.push([x + Math.cos(ang) * rr, y + Math.sin(ang) * rr]); }
    paint(pts, { wash: i % 2 ? CP.brassDk : CP.brass, ink: CP.ink, sw: 1 });
    paint(ellPts(x, y, r * .25, r * .25, 16), { wash: '#3A2E1E', ink: CP.ink, sw: .8 });
    if (o.faces) for (let k = 0; k < 3; k++) { const ang = a + k * 2.1; face(x + Math.cos(ang) * r * .62, y + Math.sin(ang) * r * .62, r * .13, { expr: 'sleep', skin: '#A89470', sw: .4 }); }
  }
  glow(960, 0, 800, '#7FA36A', .35);
  full('#07080A', o.dark ?? 40);
}

function clockBack(o = {}) {
  full('#0D0F14');
  boilSeed('cback');
  paint(ellPts(960, 500, 520, 520, 48), { wash: '#2C3D3A', ink: CP.ink, sw: 1.2 });
  for (let i = 0; i < 20; i++) paint(ellPts(560 + hash(i) * 800, 520 + hash(i + 7) * 300, 4, 4, 6), { wash: '#F2C46A', ink: null });  // town lights
  glow(960, 700, 500, '#F2C46A', .35);
  for (let i = 0; i < 12; i++) { const a = i / 12 * TAU; inkLine([[960 + Math.sin(a) * 440, 500 - Math.cos(a) * 440], [960 + Math.sin(a) * 500, 500 - Math.cos(a) * 500]], 1.4, CP.cream, 'ink', 0); }
  inkLine([[860, 0], [900, 300], [820, 520], [870, 760]], 1, '#9AA8A6', 'inkfine');
  paint(rectPts(-50, 900, W + 100, 300), { wash: '#1E1A16', ink: CP.ink, sw: .8 });
  paint(ellPts(960, 820, 40, 40, 16), { wash: CP.brassDk, ink: CP.ink, sw: .8 });             // the keyhole boss
  paint(rectPts(952, 800, 16, 40), { wash: CP.ink, ink: null });
  if (o.light) { glow(960, 500, 900, '#FFE2A8', o.light); full('#FFF3D6', 120 * o.light); }
}

function houseEmpty(o = {}) {
  full('#2B2D35');
  boilSeed('house');
  paint(rectPts(-50, 820, W + 100, 400), { wash: '#4A3B33', ink: null });
  for (const x of [300, 820, 1340]) { paint(ellPts(x + 120, 380, 80, 80, 20), { wash: CP.wood, ink: CP.ink, sw: .8 }); }  // clocks turned to the wall: just the backs
  paint(rectPts(1500, 260, 280, 560), { wash: '#1A1B20', ink: CP.ink, sw: .8 });           // doorway
  if (o.momSil) paint([[1600, 820], [1610, 520], [1640, 470], [1680, 470], [1700, 520], [1710, 820]], { wash: '#0B0C10', ink: null });
  if (o.rosary) for (let i = 0; i < 12; i++) { const a = i / 12 * TAU; paint(ellPts(960 + Math.sin(a) * 160, 950 - Math.cos(a) * 60, 10, 8, 8), { wash: '#B8B0A6', ink: CP.ink, sw: .3 }); }
}

function valleyWide(o = {}) {
  nightSky();
  hills({ far: '#232A3A', near: '#181D28' });
  tower(1200, 680, 5.5, { glow: o.glow ?? 1, glowCol: CP.sick, faces: o.faces, faceCol: '#B9D6A2' });
  fogBand(720, 140, CP.fog, 90, 'vf');
}

function cityRoom(o = {}) {
  full('#161B2A');
  boilSeed('city');
  paint(rectPts(1250, 150, 520, 420), { wash: '#202842', ink: CP.ink, sw: .8 });
  for (let i = 0; i < 16; i++) paint(rectPts(1280 + (i % 8) * 60, 300 + Math.floor(i / 8) * 120 + hash(i) * 60, 30, 70), { wash: '#F2C46A', washOp: 160, ink: null });
  clockFace(620, 300, 90, { sw: .6, cracks: true });
  paint(rectPts(100, 700, 1000, 200), { wash: '#3E4E66', ink: CP.ink, sw: .9 });
  paint(rrPts(130, 640, 220, 90, 40), { wash: '#C9C1B2', ink: CP.ink, sw: .8 });
}

function titleCard(n, o = {}) {
  full('#0A0B0F');
  boilSeed('title');
  glow(960, 500, 700, '#3A4A6A', .5);
  clockFace(960, 430, 190, { sw: .9, glow: 0, col: '#D8D0BC' });
  letter('COUNTDOWN', 960, 760, 120, '#E9E2D0', { screen: true, ink: false, font: '120px "Permanent Marker"' });
  if (n != null) letter(String(n), 960, 905, 90, '#B33A3A', { screen: true, ink: false, font: '90px "Permanent Marker"' });
}
function endCard(n, o = {}) {
  full('#060709');
  boilSeed('end' + n);
  letter(String(n), 960, 540, 420, '#E9E2D0', { screen: true, ink: false, font: '420px Georgia, serif' });
  flushLetters();
  inkLine([[900, 300], [990, 470], [930, 560], [1030, 700], [990, 800]], 2.4, '#060709', 'ink', 0);
  inkLine([[990, 470], [1080, 430]], 1.6, '#060709', 'ink', 0);
  if (o.next) { letter(String(o.next), 1500, 900, 80, '#6A6A70', { screen: true, ink: false, font: '80px Georgia, serif' }); flushLetters(); inkLine([[1490, 860], [1510, 930]], 1, '#060709', 'inkfine', 0); }
}
