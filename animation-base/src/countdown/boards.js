// COUNTDOWN storyboards: one painted panel per row of the scripts (malayalam/02-scripts-ml.md).
// PANELS[i] = { ep, tc, fn }. Rendered with render_boards.mjs at t = 0.5 (still frames).
const PANELS = [];
const P = (ep, tc, fn) => PANELS.push({ ep, tc, fn });
const ML = '"Noto Sans Malayalam", sans-serif';

// ---------- close-up helpers ----------
function bust(name, x, y, r, o = {}) {
  const C = COSTUME[name], sw = o.sw ?? clamp(r / 70, .5, 2);
  boilSeed('bust' + name + (o.key || ''));
  if (o.behind) o.behind();
  const top = C.top, sleeve = C.sleeve;
  paint([[x - r * 2.8, y + r * 4.5], [x - r * 2.5, y + r * 1.9], [x - r * 1.1, y + r * 1.25], [x + r * 1.1, y + r * 1.25], [x + r * 2.5, y + r * 1.9], [x + r * 2.8, y + r * 4.5]],
    { wash: name === 'neha' ? C.top : top, ink: CP.ink, sw, curv: .2 });
  if (C.vest) paint([[x - r * .7, y + r * 1.3], [x + r * .7, y + r * 1.3], [x + r * .9, y + r * 4.5], [x - r * .9, y + r * 4.5]], { wash: CP.vest, ink: CP.ink, sw: sw * .8 });
  if (C.hood) paint(ellPts(x, y + r * 1.35, r * 1.5, r * .55, 16), { wash: C.topDk, ink: CP.ink, sw });
  if (C.dress) paint([[x - r * .9, y + r * 1.3], [x + r * .9, y + r * 1.3], [x, y + r * 2.4]], { wash: CP.shirt, ink: CP.ink, sw: sw * .8 });
  if (C.pallu) paint(ribbon([[x + r * 1.6, y + r * 1.6], [x, y + r * 2.8], [x - r * 1.8, y + r * 4.4]], r * 1.6, r * 1.2), { wash: CP.sareeDk, ink: CP.ink, sw: sw * .8 });
  if (name === 'ammachi' && !o.noWatch) paint(ellPts(x + r * .2, y + r * 3.1, r * .32, r * .32, 14), { wash: CP.brass, ink: CP.ink, sw: sw * .7 });
  if (name === 'keeper') { clockFace(x, y, r * 1.2, { sw, hands: o.hands || null, glow: o.glow ?? .5, face: o.clockFace || null }); return; }
  paint(ribbon([[x, y + r * 1.4], [x, y + r * .6]], r * .62, r * .55), { wash: C.skin, ink: CP.ink, sw: sw * .7 });
  head(name, x, y, r, { view: o.view, flip: o.flip, sw, skin: o.skin || C.skin, skinDk: name === 'neha' ? CP.nehaDk : CP.skinDk, expr: o.expr || 'neutral',
    look: o.look, darkCircles: name === 'meera' && o.expr !== 'smile', glasses: (name === 'arjun' && !o.noGlasses) || name === 'ammachi', shadowEyes: name === 'neha' && !o.nehaEyes, pin: name === 'neha', tears: o.tears });
  if (o.hands) for (const [hx, hy] of o.hands) paint(ellPts(hx, hy, r * .42, r * .5, 14), { wash: C.skin, ink: CP.ink, sw: sw * .8 });
  if (name === 'neha' && o.glitch !== 0) vhs(x, y + r, r * 3, r * 2.2, o.glitch ?? .8);
}
const lyingHead = (name, x, y, r, o = {}) => { push(); translate(x, y); rotate(o.rot ?? -1.45); bust(name, 0, 0, r, o); pop(); };
function phone(x, y, w, o = {}) {   // a phone held in a hand; o.text lines shown on the screen
  boilSeed('phone' + x);
  const h = w * 1.9, sw = clamp(w / 120, .4, 1.4);
  if (o.glowA !== 0) glow(x, y, w * 2.2, '#9FC3E8', o.glowA ?? .7);
  paint(rrPts(x - w / 2, y - h / 2, w, h, w * .12), { wash: '#15171C', ink: CP.ink, sw });
  paint(rrPts(x - w * .44, y - h * .44, w * .88, h * .88, w * .06), { wash: o.screen || '#2F4766', ink: null });
  (o.text || []).forEach(([t, dy, size, col], i) => letter(t, x, y + dy * h, size * w / 100, col || '#EAF2F8', { screen: true, ink: false, font: `${Math.round(size * w / 100)}px ${o.font || ML}` }));
  if (o.hand !== false) paint(through([[x - w * .7, y + h * .55], [x - w * .62, y + h * .05], [x - w * .45, y + h * .2], [x - w * .1, y + h * .62], [x - w * .5, y + h * .9]], 3), { wash: CP.skin, ink: CP.ink, sw });
}
function watchCU(x, y, r, o = {}) {   // Meera's father's watch on her wrist, stopped at 3:00
  boilSeed('watch');
  paint(ribbon([[x - r * 4.5, y + r * 1.6], [x, y + r * .2], [x + r * 4.5, y - r * 1.4]], r * 1.6, r * 1.5), { wash: CP.skin, ink: CP.ink, sw: 1.2 });
  paint(ribbon([[x - r * 5.5, y + r * 2.4], [x - r * 2.5, y + r * 1.6]], r * 2.4, r * 2.2), { wash: CP.maroon, ink: CP.ink, sw: 1.2 });
  paint(ribbon([[x - r * .2, y - r * 1.3], [x + r * .3, y + r * 1.4]], r * .8, r * .8), { wash: '#8E949A', ink: CP.ink, sw: 1 });
  clockFace(x, y, r, { sw: 1.1, hands: o.hands || [Math.PI / 2, 0], rim: CP.silver, col: '#EDEBE4', cracks: false });
  if (o.glowA) glow(x, y, r * 3, '#BFE3FF', o.glowA);
}
function pocketWatch(x, y, r, o = {}) {
  boilSeed('pw');
  inkLine([[x, y - r * 1.1], [x - r * .5, y - r * 2.5], [x - r * 1.5, y - r * 3.5]], 1.4, CP.brassDk, 'ink');
  if (o.open) { paint(ellPts(x, y - r * 2.15, r * 1.05, r * .95, 30), { wash: CP.brass, ink: CP.ink, sw: 1.2 }); paint(ellPts(x, y - r * 2.15, r * .85, r * .75, 30), { wash: '#C9A866', ink: CP.ink, sw: .8 });
    if (o.engrave) { glow(x, y - r * 2.15, r * 1.6, '#FFE2A8', .8); letter(o.engrave, x, y - r * 2.15, r * .2, '#5A3E14', { screen: true, ink: false, font: `${Math.round(r * .2)}px ${ML}` }); } }
  paint(ellPts(x, y, r * 1.1, r * 1.1, 30), { wash: CP.brass, ink: CP.ink, sw: 1.2 });
  clockFace(x, y, r * .9, { sw: 1, rim: CP.brassDk, hands: o.hands || [Math.PI / 2, 0], col: '#EFE8D6', cracks: false });
}
function hand(x, y, s, a = 0, col = CP.skin) {
  push(); translate(x, y); rotate(a);
  paint(through([[-s * 2.5, s * .6], [-s * .6, s * .5], [0, s * .1], [s * 1.6, -s * .1], [s * 1.7, s * .3], [s * .5, s * .7], [s * 1.5, s * .8], [s * 1.4, s * 1.2], [-s * .2, s * 1.3], [-s * 2.5, s * 1.4]], 2),
    { wash: col, ink: CP.ink, sw: clamp(s / 40, .5, 1.4) });
  pop();
}
function plate(x, y, w, txt, o = {}) {
  boilSeed('plate' + txt);
  paint(rrPts(x - w / 2, y - w * .14, w, w * .28, w * .03), { wash: o.col || CP.brass, ink: CP.ink, sw: 1 });
  letter(txt, x, y, w * .085, '#3A2810', { screen: true, ink: false, font: `${Math.round(w * .085)}px ${ML}` });
}
const black = () => full('#050608');
const keeperShadow = (x, y, s, op = 200) => { boilSeed('ksh'); paint([[x - 2 * s, y], [x - 1.4 * s, y - 20 * s], [x - 2.6 * s, y - 24 * s], [x, y - 28.5 * s], [x + 2.6 * s, y - 24 * s], [x + 1.4 * s, y - 20 * s], [x + 2 * s, y]], { wash: '#07080B', washOp: op, ink: null, curv: .2 }); };

// =====================================================================================
// EPISODE 1 · പത്തു മണിയൊച്ച (10)
P(1, '0:00', () => { black(); fogBand(560, 30, CP.fog, 70, 'e1'); });
P(1, '0:04', () => { full('#2C313C'); clockFace(960, 540, 430, { sw: 2, glow: .3 }); vignette(); });
P(1, '0:08', () => titleCard(10));
P(1, '0:12', () => { bedroom({ phoneGlow: [520, 600] }); lyingHead('meera', 245, 600, 62, { expr: 'tired', look: [0, -1] }); paint([[320, 640], [980, 610], [990, 720], [300, 740]], { wash: CP.maroonDk, ink: CP.ink, sw: .9 });
  phone(520, 610, 70, { text: [['2:59', -.05, 34]], hand: false }); });
P(1, '0:20', () => { full('#0E1018'); phone(960, 560, 300, { text: [['3:00', -.08, 40], ['AM', .08, 18]] }); vignette(); });
P(1, '0:24', () => { nightSky(); windowFrame(160, 90, 1600, 900, { ts: 1.4, tx: .55 }); full('#05060A', 40); });
P(1, '0:27', () => { bedroom({ blanket: false }); person('meera', 640, 820, 30, { pose: 'sit', flip: true, expr: 'scared', look: [1, -.3], view: 'q' }); paint([[330, 700], [600, 690], [600, 760], [330, 770]], { wash: CP.maroonDk, ink: CP.ink, sw: .8 }); });
P(1, '0:38', () => { hallway(); person('meera', 960, 900, 22, { pose: 'run', view: 'back' }); });
P(1, '0:45', () => { nightSky(); windowFrame(200, 80, 1520, 880, { ts: 1.1 }); person('meera', 700, 1160, 40, { view: 'back', pose: 'tense' }); });
P(1, '0:52', () => { full('#141824'); windowFrame(400, 60, 1500, 1000, { ts: .9, breath: true, tx: .75 }); bust('meera', 640, 560, 150, { expr: 'scared', view: 'q', flip: true, look: [1, 0] }); });
P(1, '0:56', () => { full('#141824'); watchCU(980, 520, 230, { hands: [Math.PI / 2, 0] }); vignette(); });
P(1, '1:02', () => { nightSky(); tower(960, 1500, 34, { figure: true, glow: .25 }); fogBand(1000, 200, CP.fog, 80, 'e1f'); vignette(); });
P(1, '1:10', () => { bedroom({ blanket: true }); person('meera', 1220, 830, 32, { pose: 'crouch', flip: false, expr: 'terror', look: [-.5, 0] }); });
P(1, '1:15', () => { full('#0B0D14'); windowFrame(140, 60, 1640, 960, { ts: .9, tx: .8 });
  boilSeed('refl'); paint([[1080, 1060], [1110, 380], [1210, 330], [1310, 380], [1340, 1060]], { wash: CP.coat, washOp: 170, ink: null }); clockFace(1210, 250, 95, { sw: .7, glow: .6 }); full('#0B0D14', 30);
  bust('meera', 620, 560, 150, { expr: 'terror', look: [.8, 0] }); });
P(1, '1:22', () => { black(); glow(960, 540, 300, CP.sick, .25); });
P(1, '1:25', () => endCard(10, { next: 9 }));

// =====================================================================================
// EPISODE 2 · ഒഴിഞ്ഞ ബെഞ്ച് (9)
P(2, '0:00', () => { bedroom({ blanket: false }); lyingHead('meera', 245, 600, 62, { expr: 'scared', look: [0, -1] }); paint([[320, 640], [980, 610], [990, 720], [300, 740]], { wash: CP.maroonDk, ink: CP.ink, sw: .9 }); });
P(2, '0:08', () => titleCard(9));
P(2, '0:12', () => { classroom(); person('meera', 520, 1000, 26, { expr: 'tired', view: 'q', flip: true }); person('arjun', 1420, 1000, 26, { pose: 'shrug', expr: 'smile', view: 'q' }); });
P(2, '0:18', () => { classroom(); bust('meera', 560, 520, 140, { expr: 'scared', view: 'q', flip: true, look: [1, .3] }); paint(rectPts(1100, 760, 600, 70), { wash: CP.woodLt, ink: CP.ink, sw: 1 }); paint(rectPts(1150, 640, 120, 130), { wash: CP.wood, ink: CP.ink, sw: .8 }); });
P(2, '0:22', () => { classroom({ dim: true }); bust('arjun', 960, 500, 160, { expr: 'neutral', look: [-.6, 0] }); });
P(2, '0:24', () => { classroom({ dim: true }); bust('meera', 960, 500, 160, { expr: 'smile', look: [.4, 0] }); });
P(2, '0:31', () => { classroom(); for (let i = 0; i < 7; i++) if (i !== 3) person(i % 2 ? 'arjun' : 'meera', 250 + i * 240, 1100, 18, { view: 'back', pose: 'sit', key: 'k' + i }); });
P(2, '0:37', () => { full(CP.woodLt); boilSeed('desk'); for (let i = 0; i < 9; i++) inkLine([[0, 120 * i + 40], [W, 120 * i + 60]], .6, CP.wood, 'inkfine');
  clockFace(900, 520, 280, { col: '#8A6A50', rim: CP.wood, sw: 1.4, cracks: true }); hand(1380, 640, 90, -.3); });
P(2, '0:46', () => { corridor({ clock: true }); person('meera', 360, 1020, 24, { view: 'q', flip: true, expr: 'scared' }); person('arjun', 160, 1040, 24, { view: 'q', flip: true, expr: 'neutral', key: 'a' }); });
P(2, '0:52', () => { full(CP.wood); classPhoto(260, 120, 1400, { clock: false }); });
P(2, '0:56', () => { full(CP.wood); classPhoto(260, 120, 1400, { clock: true }); vignette('#07080C', 120); });
P(2, '1:02', () => { corridor({ clock: true, dark: 60 }); bust('meera', 640, 500, 140, { view: 'q', flip: true, expr: 'scared', look: [1, 0] }); bust('arjun', 1320, 480, 140, { view: 'q', expr: 'neutral', look: [-1, 0], key: 'a' }); });
P(2, '1:08', () => { full(CP.wood); classPhoto(260, 120, 1400, { clock: true, hands: [Math.PI * .8, Math.PI * 1.2] }); });
P(2, '1:15', () => { full('#B8B2A4'); clockFace(960, 520, 420, { sw: 2, hands: [Math.PI, Math.PI], glow: .3 }); paint(rectPts(600, 980, 720, 200), { wash: CP.maroon, ink: CP.ink, sw: 1.4 }); vignette('#07080C', 160); });
P(2, '1:22', () => { corridor({ lightsOff: 3 }); person('meera', 1500, 1040, 28, { pose: 'fallBack', expr: 'terror', view: 'q' }); });
P(2, '1:25', () => endCard(9, { next: 8 }));

// =====================================================================================
// EPISODE 3 · കണ്ണാടിയിലെ പെൺകുട്ടി (8)
P(3, '0:00', () => { bathroom(); mirrorFog(170); paint(ellPts(960, 800, 10, 14, 8), { wash: '#A9C6D8', ink: null }); });
P(3, '0:08', () => titleCard(8));
P(3, '0:12', () => { bathroom(); bust('meera', 960, 400, 110, { expr: 'tired', look: [0, .4] }); mirrorFog(80); });
P(3, '0:20', () => { bathroom(); bust('meera', 960, 400, 110, { expr: 'scared', look: [.6, -.5] }); mirrorFog(60); });
P(3, '0:26', () => { bathroom(); mirrorFog(190, [[800, 420, 60], [1120, 400, 60]]); });
P(3, '0:33', () => { bathroom(); mirrorFog(190, [[800, 420, 60], [1120, 400, 60]]); letter('എണ്ണരുത്', 960, 560, 90, '#4C5864', { screen: true, ink: false, font: `90px ${ML}` }); });
P(3, '0:40', () => { bathroom(); bust('neha', 1150, 330, 80, { glitch: .8 }); bust('meera', 860, 400, 115, { expr: 'scared', look: [0, 0], key: 'm' }); mirrorFog(50); });
P(3, '0:47', () => { bathroom({ mirrorCol: '#4A5A66' }); bust('neha', 960, 380, 130, { glitch: 1 }); });
P(3, '0:54', () => { bathroom(); person('meera', 960, 1100, 30, { pose: 'coverEars', expr: 'terror' }); });
P(3, '0:58', () => { bathroom({ mirrorCol: '#4A5A66' }); bust('neha', 960, 400, 120, { glitch: .7, hands: [[760, 360], [1160, 360]] }); });
P(3, '1:05', () => { bathroom(); bust('meera', 960, 400, 120, { expr: 'whisper', look: [0, .5] }); mirrorFog(40); });
P(3, '1:12', () => { bathroom({ mirrorCol: '#4A5A66' }); bust('neha', 960, 400, 120, { glitch: 1.2, view: 'q', flip: true }); });
P(3, '1:17', () => { bathroom(); boilSeed('coat3'); paint([[1040, 750], [1080, 150], [1340, 150], [1380, 750]], { wash: CP.coat, ink: CP.ink, sw: 1 }); for (let i = 0; i < 3; i++) paint(ellPts(1210, 330 + i * 110, 10, 10, 8), { wash: CP.brass, ink: null });
  bust('meera', 860, 410, 115, { expr: 'terror', look: [.6, 0] }); });
P(3, '1:25', () => endCard(8, { next: 7 }));

// =====================================================================================
// EPISODE 4 · അമ്മച്ചിയുടെ കഥ (7)
P(4, '0:00', () => { sepiaWash(); paint(rectPts(460, 140, 1000, 800), { wash: CP.sepiaLt, ink: CP.ink, sw: 1.2 }); person('neha', 780, 860, 30, { nehaEyes: true, expr: 'smile', glitch: 0 }); person('meera', 1140, 860, 30, { expr: 'smile', key: 'rosa' }); sepiaFilter(); });
P(4, '0:08', () => titleCard(7));
P(4, '0:12', () => { veranda(); rockingChair(820, 820, 1); person('ammachi', 820, 800, 26, { pose: 'sit', flip: false, expr: 'calm' }); person('meera', 1120, 840, 24, { pose: 'sitHug', flip: true, expr: 'tired', key: 'm' }); });
P(4, '0:18', () => { veranda(); bust('ammachi', 960, 460, 150, { expr: 'angryLow', look: [.5, 0] }); });
P(4, '0:23', () => { veranda(); watchCU(900, 560, 170); hand(1450, 400, 100, 2.6, '#9C6C52'); });
P(4, '0:28', () => { sepiaWash(); tower(1300, 960, 18); for (let i = 0; i < 6; i++) inkLine([[1100 + i * 80, 960], [1100 + i * 80, 200]], .8, CP.sepiaDk, 'ink', 0); person('elias', 600, 960, 28, { pose: 'hold2', expr: 'calm', flip: true }); sepiaFilter(); });
P(4, '0:40', () => { sepiaWash(); tower(1200, 1100, 22); for (let i = 0; i < 6; i++) { person('mob', 300 + i * 150, 1040, 24, { pose: i % 2 ? 'point' : 'stand', key: 'mob' + i, flip: true }); glow(330 + i * 150, 560, 120, '#FFB040', .8); }
  paint(rectPts(1160, 830, 80, 270), { wash: CP.sepiaDk, ink: CP.ink, sw: 1 }); sepiaFilter(); });
P(4, '0:50', () => { sepiaWash(); bust('elias', 960, 520, 170, { expr: 'terror' }); clockFace(1060, 470, 170, { sw: 1.2, col: '#E9DCC0' }); sepiaFilter(); });
P(4, '0:58', () => { veranda(); bust('ammachi', 960, 440, 150, { expr: 'sad', look: [0, .6], hands: [[1000, 900]] }); });
P(4, '1:08', () => { veranda(); bust('meera', 960, 460, 150, { expr: 'scared', look: [-.5, 0] }); });
P(4, '1:11', () => { veranda(); bust('ammachi', 960, 460, 150, { expr: 'cry', view: 'q', look: [1, .5] }); });
P(4, '1:16', () => { veranda({ lampOff: true, frozenFlame: true }); pocketWatch(700, 620, 160, { hands: [Math.PI * 1.6, Math.PI * .3] }); glow(700, 620, 400, '#BFE3FF', .5); });
P(4, '1:25', () => endCard(7, { next: 6 }));

// =====================================================================================
// EPISODE 5 · റെക്കോർഡിംഗ് (6): found footage through Arjun's phone
P(5, '0:00', () => { terrace(); bust('arjun', 960, 480, 180, { expr: 'smile', look: [0, 0] }); phoneUI('02:55:10'); });
P(5, '0:08', () => { terrace(); titleCard(6); phoneUI('02:55:18', { glitch: 1 }); });
P(5, '0:12', () => { terrace(); person('meera', 960, 1060, 30, { pose: 'sitHug', expr: 'scared' }); boilSeed('blk'); paint(through([[700, 1080], [740, 640], [960, 520], [1180, 640], [1220, 1080]], 3), { wash: '#5A6B5E', ink: CP.ink, sw: 1 }); bust('meera', 960, 560, 70, { expr: 'scared', key: 'mb' }); phoneUI('02:56:02'); });
P(5, '0:20', () => { nightSky(); tower(960, 1300, 24, {}); fogBand(1000, 220, CP.fog, 120, 'e5f'); phoneUI('02:59:40'); });
P(5, '0:28', () => { nightSky(); tower(960, 1300, 24, { glow: .3 }); fogBand(1000, 220, CP.fog, 120, 'e5f'); phoneUI('03:00:00'); });
P(5, '0:36', () => { terrace({ ts: 5 }); person('keeper', 1100, 905, 8, { glow: .6 }); phoneUI('03:00:22', { glitch: .4 }); });
P(5, '0:50', () => { terrace(); bust('arjun', 960, 480, 180, { expr: 'terror', look: [.8, 0] }); phoneUI('03:00:31'); });
P(5, '0:55', () => { full('#1E2028'); paint(rectPts(-50, 700, W + 100, 500), { wash: '#2A2A30', ink: null }); paint(rectPts(700, 600, 520, 300), { wash: '#3A3A3E', ink: CP.ink, sw: 1 }); person('keeper', 960, 1020, 22, { glow: .8, hands: null }); phoneUI('03:00:36'); });
P(5, '1:02', () => { nightSky(); fogBand(900, 200, CP.fog, 60, 'e5s'); push(); translate(W / 2, H / 2); rotate(.35); translate(-W / 2, -H / 2); phoneUI('03:00:44'); pop(); });
P(5, '1:08', () => { full('#3C4350'); fogBand(540, 500, CP.fogLt, 140, 'e5fog'); phoneUI('03:00:51'); });
P(5, '1:14', () => { full('#3C4350'); fogBand(700, 400, CP.fogLt, 120, 'e5fog'); clockFace(960, 260, 520, { sw: 2, hands: [Math.PI, Math.PI], glow: .6 }); phoneUI('03:00:58', { glitch: .6 }); });
P(5, '1:22', () => { black(); letter('Storage full.', 960, 540, 60, '#E8E8E8', { screen: true, ink: false, font: '60px sans-serif' }); phoneUI('03:01:04'); });
P(5, '1:25', () => endCard(6, { next: 5 }));

// =====================================================================================
// EPISODE 6 · വർക്കി & സൺസ് (5)
P(6, '0:00', () => { market({ day: true, ts: 9 }); boilSeed('sign'); inkLine([[600, 200], [600, 300]], 1, CP.ink); inkLine([[1320, 200], [1320, 300]], 1, CP.ink);
  paint(rectPts(520, 300, 880, 240), { wash: '#6B4A36', ink: CP.ink, sw: 1.4 }); letter('VARKEY & SONS', 960, 380, 80, '#C9B48A', { screen: true, ink: false, font: '80px Georgia, serif' }); letter('CLOCK REPAIR · 1938', 960, 470, 42, '#C9B48A', { screen: true, ink: false, font: '42px Georgia, serif' }); });
P(6, '0:08', () => titleCard(5));
P(6, '0:12', () => { full('#3A3A40'); paint(rectPts(700, 180, 520, 820), { wash: '#4A3A30', ink: CP.ink, sw: 1.2 }); person('arjun', 1200, 1050, 26, { pose: 'hold2', flip: true, expr: 'scared', view: 'q' }); person('meera', 560, 1050, 26, { pose: 'tense', flip: true, expr: 'tired', view: 'q', key: 'm' }); });
P(6, '0:19', () => { shopInterior(); person('meera', 760, 1060, 22, { view: 'back', key: 'm' }); person('arjun', 1100, 1060, 22, { view: 'back' }); });
P(6, '0:27', () => { shopInterior({ dark: 90 }); clockFace(960, 430, 270, { sw: 1.4, hands: [0, Math.PI], cracks: false }); plate(960, 820, 560, 'നേഹ തോമസ് — 1986'); hand(1300, 860, 70, -.4); });
P(6, '0:34', () => { shopInterior({ dark: 90 }); clockFace(960, 380, 250, { sw: 1.4, hands: [0, Math.PI], cracks: false }); inkLine([[960, 640], [1060, 900]], 1.4, CP.brassDk, 'ink', 0); paint(ellPts(1060, 920, 50, 50, 16), { wash: CP.brass, ink: CP.ink, sw: 1 }); plate(760, 760, 420, 'സാം മാത്യു — 2026'); });
P(6, '0:41', () => { shopInterior({ dark: 70 }); clockFace(640, 480, 200, { sw: 1.2, hands: [Math.PI * .1, Math.PI * 1.9], cracks: false, glow: .3, glowCol: '#FFE2A8' }); clockFace(1280, 480, 200, { sw: 1.2, hands: [Math.PI * .2, Math.PI * 1.7], cracks: false, glow: .3, glowCol: '#FFE2A8' });
  plate(640, 780, 420, 'മീര ജോസഫ്'); plate(1280, 780, 420, 'അർജുൻ നായർ'); });
P(6, '0:50', () => { shopInterior({ dark: 100 }); clockFace(960, 430, 270, { sw: 1.4, cracks: true, col: '#C9C0AA' }); for (let i = 0; i < 6; i++) inkLine([[960, 430], [960 + Math.cos(i) * 260, 430 + Math.sin(i * 1.7) * 260]], 1.2, CP.ink, 'ink'); plate(960, 820, 560, 'റോസ ജോസഫ് — 1986'); });
P(6, '0:57', () => { shopInterior({ dark: 40 }); person('meera', 760, 1060, 26, { pose: 'coverEars', expr: 'terror', key: 'm' }); person('arjun', 1160, 1060, 26, { pose: 'coverEars', expr: 'terror' }); });
P(6, '1:03', () => { shopInterior({ dark: 80 }); glow(960, 500, 600, '#E6EEF2', .9); paint(rectPts(780, 140, 360, 700), { wash: '#DDE6EA', ink: CP.ink, sw: 1 }); person('keeper', 960, 840, 22, { glow: .2 }); bust('arjun', 300, 700, 120, { view: 'q', expr: 'terror', look: [1, 0] }); });
P(6, '1:08', () => { shopInterior({ dark: 60 }); person('meera', 600, 1060, 26, { pose: 'run', expr: 'terror', key: 'm' }); person('arjun', 1000, 1060, 26, { pose: 'run', expr: 'terror' }); phone(1250, 1010, 50, { glowA: .4, hand: false }); });
P(6, '1:15', () => { full('#3A3029'); boilSeed('floor'); for (let i = 0; i < 8; i++) inkLine([[0, 140 * i], [W, 140 * i + 30]], .6, '#2A221C', 'inkfine'); phone(960, 620, 220, { text: [['Calling:', -.15, 18], ['മീര 💛', 0, 22]], hand: false });
  for (let i = -1; i <= 1; i++) keyFinger([1500, -40], 1.25 * -1 + Math.PI + i * .12, 700, 34, 1.2); });
P(6, '1:25', () => endCard(5, { next: 4 }));

// =====================================================================================
// EPISODE 7 · നഷ്ടപ്പെട്ട സമയം (4)
P(7, '0:00', () => { full('#0A0B0F'); push(); bathroom(); pop(); paint(rectPts(640, -50, 50, H + 100), { wash: '#0A0B0F', ink: null }); paint(rectPts(1280, -50, 50, H + 100), { wash: '#0A0B0F', ink: null });
  bust('meera', 320, 420, 90, { expr: 'tired', key: 'a' }); push(); paint(rectPts(690, -50, 590, H + 100), { wash: '#8A8F94', ink: null }); pop(); person('meera', 980, 1000, 18, { expr: 'tired', key: 'b' }); paint(rectPts(1330, -50, 640, H + 100), { wash: '#0C0F18', ink: null }); stars(10); person('meera', 1620, 1000, 18, { view: 'back', key: 'c' }); });
P(7, '0:08', () => titleCard(4));
P(7, '0:12', () => { full('#141824'); phone(960, 560, 300, { text: [['11:40', -.08, 34], ['PM', .07, 16]] }); vignette(); });
P(7, '0:20', () => { full('#141824'); phone(960, 560, 320, { screen: '#E9ECEF', text: [['അർജുൻ', -.36, 14, '#222'], ['11:40', -.2, 11, '#555'], ['1:15', -.02, 11, '#555'], ['2:30', .16, 11, '#555']], glowA: .5 }); });
P(7, '0:28', () => { bedroom({ blanket: true }); paint(rectPts(1180, 160, 520, 700), { wash: CP.wood, ink: CP.ink, sw: 1 }); paint(rectPts(1220, 200, 440, 620), { wash: '#4A5664', ink: CP.ink, sw: .7 });
  person('meera', 1440, 800, 18, { expr: 'tired', key: 'refl' }); person('meera', 900, 1060, 30, { view: 'back', key: 'real' }); });
P(7, '0:34', () => { full('#1E2333'); paint(rectPts(960, -50, 20, H + 100), { wash: CP.wood, ink: CP.ink, sw: 1 }); bust('meera', 520, 480, 150, { expr: 'tired', key: 'real' }); full('#1E2333', 0); paint(rectPts(980, -50, 990, H + 100), { wash: '#4A5664', washOp: 120, ink: null }); bust('meera', 1420, 480, 150, { expr: 'smile', key: 'refl' }); });
P(7, '0:42', () => { full('#141824'); phone(960, 560, 300, { text: [['അർജുൻ', -.1, 28], ['📞', .1, 30]] }); vignette(); });
P(7, '0:46', () => { bedroom({ blanket: true }); bust('meera', 960, 460, 160, { expr: 'terror', look: [-.5, 0], hands: [[1200, 520]] }); phone(1240, 470, 60, { hand: false, glowA: .3 }); });
P(7, '0:55', () => { full('#141824'); watchCU(980, 520, 230, { hands: [Math.PI * 2.9 / 6 * 1.0 + Math.PI * .45, Math.PI * 1.95] }); vignette(); });
P(7, '1:02', () => { bedroom({ blanket: true }); person('meera', 900, 900, 30, { pose: 'coverEars', expr: 'closed' }); });
P(7, '1:10', () => { bedroom({ blanket: true }); person('meera', 900, 900, 30, { pose: 'tense', expr: 'scared', look: [.6, 0] }); });
P(7, '1:15', () => { full('#1E2333'); paint(rectPts(560, 60, 800, 980), { wash: CP.wood, ink: CP.ink, sw: 1 }); paint(rectPts(600, 100, 720, 900), { wash: '#4A5664', ink: CP.ink, sw: .8 }); person('meera', 960, 1010, 30, { pose: 'coverEars', expr: 'smile', key: 'refl' }); });
P(7, '1:25', () => endCard(4, { next: 3 }));

// =====================================================================================
// EPISODE 8 · ആടുന്ന കസേര (3)
P(8, '0:00', () => { nightSky(); hills(); fogBand(860, 160, CP.fog, 120, 'e8'); paint([[700, 1080], [900, 820], [1020, 820], [1260, 1080]], { wash: '#3A3632', ink: null }); person('meera', 960, 1000, 24, { pose: 'run', expr: 'terror', flip: true, view: 'q' }); });
P(8, '0:08', () => titleCard(3));
P(8, '0:12', () => { veranda({ lampOff: true, dusk: 0 }); rockingChair(960, 830, 1.1, { rock: .1 }); full('#0B0D14', 50); });
P(8, '0:19', () => { veranda({ lampOff: true, dusk: 0 }); bust('meera', 960, 460, 160, { expr: 'terror', look: [0, -.3] }); });
P(8, '0:23', () => { houseEmpty(); });
P(8, '0:29', () => { full('#4A3B33'); boilSeed('ros'); for (let i = 0; i < 12; i++) { const a = i / 12 * TAU; paint(ellPts(960 + Math.sin(a) * 330, 540 - Math.cos(a) * 330, 22, 22, 10), { wash: '#B8B0A6', ink: CP.ink, sw: .6 }); } paint(starPts(960, 540, 60, .3, 2, 0), { wash: '#B8B0A6', ink: CP.ink, sw: .8 }); vignette(); });
P(8, '0:37', () => { houseEmpty({ momSil: true }); person('meera', 700, 1000, 26, { view: 'q', flip: true, expr: 'cry' }); });
P(8, '0:44', () => { houseEmpty(); bust('meera', 960, 460, 160, { expr: 'cry' }); });
P(8, '0:52', () => { veranda({ lampOff: true, dusk: 0 }); rockingChair(960, 830, 1.1); pocketWatch(960, 600, 60, { hands: [Math.PI * .5, Math.PI * .8] }); glow(960, 600, 200, '#FFE2A8', .5); });
P(8, '0:58', () => { full('#1B1713'); pocketWatch(960, 880, 230, { open: true, engrave: 'പിന്നോട്ട് ചുറ്റണം', hands: [Math.PI * .5, Math.PI * 1.1] }); });
P(8, '1:07', () => { houseEmpty(); bust('meera', 960, 460, 160, { expr: 'determined', look: [.3, 0] }); });
P(8, '1:12', () => { full('#141824'); phone(960, 560, 320, { screen: '#E9ECEF', text: [['അർജുൻ', -.36, 14, '#222'], ['ഞാനും കേട്ടു.', -.12, 12, '#222'], ['ഞാനും നിന്റെ', .04, 12, '#222'], ['കൂടെ വരുന്നു.', .16, 12, '#222']], glowA: .5 }); });
P(8, '1:17', () => valleyWide({ faces: true }));
P(8, '1:25', () => endCard(3, { next: 2 }));

// =====================================================================================
// EPISODE 9 · ഗോപുരത്തിനുള്ളിൽ (2)
P(9, '0:00', () => { full(CP.night); stars(16); tower(960, 1500, 40, {}); boilSeed('chain'); for (let i = 0; i < 9; i++) paint(ellPts(800 + i * 40, 1000 + (i % 2) * 10, 24, 14, 10), { ink: '#8C8478', sw: 1.2 });
  person('arjun', 1250, 1080, 28, { pose: 'hold2', flip: true, expr: 'determined', view: 'q' }); person('meera', 560, 1080, 28, { pose: 'tense', flip: true, view: 'q', expr: 'scared', key: 'm' }); });
P(9, '0:08', () => titleCard(2));
P(9, '0:12', () => { full('#15130F'); boilSeed('stairs'); for (let i = 0; i < 12; i++) { const y = 1080 - i * 90, x = 960 + Math.sin(i * .9) * 420; paint(rectPts(x - 160, y, 320, 34), { wash: '#4A4038', ink: CP.ink, sw: .8 }); }
  person('meera', 1240, 900, 22, { pose: 'walk', view: 'back' }); glow(960, 0, 600, CP.sick, .3); });
P(9, '0:20', () => { gearRoom({ faces: true }); person('meera', 700, 1080, 24, { view: 'back', key: 'm' }); person('arjun', 1000, 1080, 24, { view: 'back' }); });
P(9, '0:30', () => { full('#1B1713'); boilSeed('g1'); const pts = []; for (let k = 0; k < 64; k++) { const a = k / 64 * TAU, rr = 620 * (k % 4 < 2 ? 1 : .9); pts.push([960 + Math.cos(a) * rr, 540 + Math.sin(a) * rr]); }
  paint(pts, { wash: CP.brass, ink: CP.ink, sw: 1.6 }); bust('ammachi', 960, 460, 150, { expr: 'sleep', skin: '#A89470', noWatch: true }); });
P(9, '0:37', () => { full('#1B1713'); boilSeed('g2'); const pts = []; for (let k = 0; k < 64; k++) { const a = k / 64 * TAU, rr = 620 * (k % 4 < 2 ? 1 : .9); pts.push([960 + Math.cos(a) * rr, 540 + Math.sin(a) * rr]); }
  paint(pts, { wash: CP.brassDk, ink: CP.ink, sw: 1.6 }); bust('neha', 960, 460, 150, { glitch: 1 }); });
P(9, '0:44', () => { full('#15130F'); boilSeed('stairs2'); for (let i = 0; i < 12; i++) { const y = 1080 - i * 90, x = 760 + Math.sin(i * .9) * 300; paint(rectPts(x - 160, y, 320, 34), { wash: '#4A4038', ink: CP.ink, sw: .8 }); }
  keeperShadow(1300, 1080, 34, 220); });
P(9, '0:50', () => { gearRoom({ spin: .3 }); person('meera', 900, 1060, 28, { pose: 'fallBack', expr: 'terror', flip: true }); });
P(9, '0:58', () => { gearRoom({ spin: .5 }); person('arjun', 1000, 1060, 28, { pose: 'reachFwd', expr: 'determined', flip: true }); person('meera', 600, 1060, 26, { pose: 'fallBack', expr: 'terror', key: 'm' }); });
P(9, '1:03', () => { gearRoom({ spin: .6, dark: 60 }); bust('arjun', 960, 460, 160, { expr: 'calm', skin: '#B08D4A' }); });
P(9, '1:10', () => { gearRoom({ dark: 80 }); bust('meera', 960, 440, 150, { expr: 'cry', look: [0, .6] }); boilSeed('gl'); for (const x of [880, 1040]) paint(ellPts(x, 940, 62, 56, 18), { ink: CP.ink, sw: 1.4 }); inkLine([[942, 940], [978, 940]], 1, CP.ink); });
P(9, '1:15', () => { full('#15130F'); for (let i = 0; i < 6; i++) paint(rectPts(400 + i * 60, 900 - i * 60, 320, 30), { wash: '#4A4038', ink: CP.ink, sw: .8 }); person('keeper', 1200, 1040, 30, { hands: [Math.PI * 1.75, Math.PI * 1.75], glow: .7 }); bust('meera', 320, 760, 110, { view: 'q', flip: true, expr: 'terror' }); });
P(9, '1:25', () => { endCard(2); boilSeed('c1'); inkLine([[1500, 820], [1530, 900]], 1, '#3A3A40', 'inkfine', 0); letter('1', 1500, 880, 120, '#3A3A40', { screen: true, ink: false, font: '120px Georgia, serif' }); flushLetters(); inkLine([[1490, 820], [1515, 940]], 1.2, '#060709', 'inkfine', 0); });

// =====================================================================================
// EPISODE 10 · അവസാന മണിയൊച്ച (1)
P(10, '0:00', () => { black(); glow(960, 540, 180, '#B33A3A', .5); paint(heartPts(960, 540, 60), { wash: '#5A1E22', ink: null }); });
P(10, '0:06', () => titleCard(1));
P(10, '0:10', () => { clockBack(); person('keeper', 1400, 920, 22, { glow: .5 }); person('meera', 640, 920, 24, { pose: 'tense', flip: true, view: 'q', expr: 'scared' }); });
P(10, '0:18', () => { clockBack(); bust('meera', 760, 460, 150, { expr: 'determined', view: 'q', flip: true }); pocketWatch(1260, 820, 70, {}); hand(1180, 860, 60, 0); });
P(10, '0:26', () => { full('#0D0F14'); bust('keeper', 960, 440, 180, { clockFace: { expr: 'scared', skin: CP.skin }, glow: .7 }); });
P(10, '0:34', () => { full('#0D0F14'); boilSeed('bell'); push(); translate(960, 100); rotate(-.4); paint(through([[-360, 700], [-300, 200], [-120, 40], [120, 40], [300, 200], [360, 700]], 3), { wash: CP.brassDk, ink: CP.ink, sw: 1.6 }); paint(ellPts(0, 700, 360, 60, 24), { wash: '#3A2E1E', ink: CP.ink, sw: 1.2 }); pop(); glow(960, 500, 600, CP.sick, .3); });
P(10, '0:37', () => { clockBack(); person('meera', 900, 920, 30, { pose: 'wind', flip: true, view: 'q', expr: 'determined' }); });
P(10, '0:43', () => { clockBack(); boilSeed('dust'); for (let i = 0; i < 40; i++) paint(ellPts(hash(i) * W, (1 - frac(hash(i + 5) + .3)) * H, 3 + hash(i) * 4, 3 + hash(i) * 4, 6), { wash: '#C9C3B4', washOp: 200, ink: null });
  for (let i = 0; i < 3; i++) inkLine([[300 + i * 600, 900], [300 + i * 600, 500], [270 + i * 600, 540]], 1, CP.cream, 'inkfine'); person('meera', 900, 920, 30, { pose: 'wind', flip: true, view: 'q', expr: 'determined' }); });
P(10, '0:52', () => { full('#0D0F14'); bust('keeper', 1100, 440, 180, { clockFace: { expr: 'calm', skin: '#A87A5E' }, glow: .4 }); for (let i = -1; i <= 1; i++) keyFinger([1500, 760], -Math.PI / 2 + i * .1, 520, 30, 1); bust('meera', 400, 520, 130, { view: 'q', flip: true, expr: 'terror', key: 'm' }); });
P(10, '1:00', () => { clockBack({ light: .7 }); boilSeed('crumb'); for (let i = 0; i < 24; i++) { const x = 900 + hash(i) * 700, y = 200 + hash(i + 3) * 700; clockFace(x, y, 20 + hash(i + 9) * 30, { sw: .4, cracks: false }); } });
P(10, '1:05', () => { market({ day: true, ts: 9 }); person('arjun', 520, 1010, 22, { pose: 'sit', expr: 'smile', key: 'a' }); person('neha', 1250, 990, 22, { nehaEyes: true, expr: 'smile', glitch: .3 }); person('ammachi', 1450, 1000, 22, { expr: 'smile' }); person('meera', 900, 1010, 24, { expr: 'smile', key: 'm' }); });
P(10, '1:12', () => { market({ day: true, ts: 9 }); person('ammachi', 1010, 1040, 32, { pose: 'hug', flip: true, expr: 'cry' }); person('meera', 900, 1040, 32, { pose: 'hug', expr: 'cry', key: 'm' }); });
P(10, '1:18', () => { cityRoom(); lyingHead('boy', 240, 680, 50, { expr: 'shock' }); paint([[300, 720], [1100, 700], [1100, 780], [290, 800]], { wash: '#2D4357', ink: CP.ink, sw: .9 }); });
P(10, '1:25', () => { full('#060709'); letter('40', 960, 470, 300, '#E9E2D0', { screen: true, ink: false, font: '300px Georgia, serif' }); letter('SEASON 2', 960, 800, 80, '#B33A3A', { screen: true, ink: false, font: '80px "Permanent Marker"' }); });

// ---------- render hook: window.PANEL = index ----------
window.PANELS = PANELS;
LOOPS.panel = t => { const p = PANELS[window.PANEL || 0]; p.fn(t); };
LOOPS.panel.len = 1;
