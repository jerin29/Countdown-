// COUNTDOWN S2 · Ep 1 · 15 · നാൽപത് (Forty): the painted PLATES for the one-take episode.
// The film itself is composited in Python (horror-series/season2/video/tools/ep01.py): these loops paint each place once,
// big and still, and the compositor glides a smooth camera across them, Cinemagic-style.
// Render a plate:  node render.mjs --page=s2.html --soft-gl --loop=<name> --stills=0,0.1,0.2,... --out=<dir>
//   t encodes the tile index (round(t*10)); tiles are 1920x1080 views at zoom Z of the plate's world rect.
const EP1 = (() => {
  const WIN = { x: 1180, y: 170, w: 520, h: 470 };          // room window (room coords)
  const HW = { x: 5220, y: 1150, w: 400, h: 225 };          // Aadi's window seen from outside (city coords)
  const SC = HW.w / W;

  function noGrain() { if (window._ng) return; const c = grainC.getContext('2d'); c.fillStyle = '#fff'; c.fillRect(0, 0, W, H); window._ng = 1; }

  // ---------- CITY ----------
  // o.glowOnly: paint only the clock-window glows on black (a mask the compositor pulses on every chime)
  function city(o = {}) {
    const go = !!o.glowOnly;
    boilSeed('sky2');
    paint(rectPts(-2000, -1500, 11000, 6000), { wash: go ? '#000000' : '#0C101C', ink: null });
    if (!go) {
      paint(ellPts(3400, 600, 3800, 900, 30, 20), { fill: '#1D2540', fillOp: 110, bleed: .3, tex: .4, ink: null });
      for (let i = 0; i < 90; i++) { boilSeed('s2st' + i); const x = hash(i * 3.3) * 6000 + 1000, y = hash(i * 9.1) * 1000 + 250, tw = .5 + .5 * hash(i * 2.7);
        paint(ellPts(x, y, 2.4 + tw, 2.4 + tw, 6), { wash: '#CFD6E0', washOp: 140 + 100 * tw, ink: null }); }
      boilSeed('moon2'); glow(2000, 520, 420, '#9FB0C8', .35);
      for (let i = 0; i < 7; i++) { boilSeed('cl' + i); paint(ellPts(1500 + i * 700, 420 + hash(i) * 260, 440, 70, 20, 8), { fill: '#252C42', fillOp: 120, bleed: .4, tex: .5, ink: null }); }
      boilSeed('farhill');
      paint([[2900, 1500], [3500, 1250], [3900, 1200], [4400, 1300], [4900, 1500]], { wash: '#141826', ink: null, curv: .5 });
      glow(3900, 1240 - 27 * 9, 150, CP.sickGlow, .35);
      tower(3900, 1240, 9, { hands: [Math.PI / 2, 0], glow: 0, col: '#1C2130', dk: '#141823' });
    } else glow(3900, 1240 - 27 * 9, 200, '#FFFFFF', 1);
    for (const [layer, base, hMin, hMax, col, n] of [[0, 1650, 260, 520, '#121726', 30], [1, 1900, 320, 760, '#0E121D', 24]]) {
      for (let i = 0; i < n; i++) {
        const bw = 150 + hash(i * 5 + layer) * 170, x = 1000 + i * (6000 / n) + hash(i + layer * 50) * 60, bh = lerp(hMin, hMax, hash(i * 7 + layer * 3));
        if (layer === 1 && x > HW.x - 1300 && x < HW.x + HW.w + 1300) continue;
        boilSeed('bl' + layer + '_' + i);
        if (!go) paint(rectPts(x, base - bh, bw, bh + 600), { wash: col, ink: CP.ink, sw: .5 });
        for (let r = 0; r < 6; r++) for (let c = 0; c < 3; c++) {
          const id = i * 31 + r * 7 + c + layer * 500; if (hash(id) <= .62) continue;
          const wx = x + 20 + c * (bw - 40) / 3, wy = base - bh + 30 + r * 70; if (wy > base - 30) continue;
          const isClock = hash(id + 9) > .55;
          if (go) { if (isClock) glow(wx + 17, wy + 20, 70, '#FFFFFF', 1); continue; }
          paint(rectPts(wx, wy, 34, 40), { wash: isClock ? '#1F2A22' : '#E3B864', washOp: isClock ? 255 : 150, ink: null });
          if (isClock) { glow(wx + 17, wy + 20, 40, CP.sickGlow, .35); clockFace(wx + 17, wy + 20, 12, { sw: .3, cracks: false, hands: [Math.PI / 2, 0], col: '#CFE3C4' }); }
        }
      }
    }
    if (!go) { boilSeed('fog2'); paint(ellPts(3800, 1720, 4200, 140, 30, 10), { fill: CP.fog, fillOp: 70, bleed: .4, tex: .4, ink: null }); }
  }

  // ---------- AADI'S BUILDING (city coords; the window hole is cut by the compositor) ----------
  function facade() {
    boilSeed('facade');
    paint(rectPts(HW.x - 1100, HW.y - 1300, HW.w + 2200, HW.h + 2900), { wash: '#1A1E2B', fill: '#232838', fillOp: 90, bleed: .1, tex: .5, ink: null });
    for (let r = -4; r <= 4; r++) for (let c = -3; c <= 3; c++) {
      if (r === 0 && c === 0) continue;
      const wx = HW.x + c * 560, wy = HW.y + r * 330;
      paint(rectPts(wx, wy, HW.w, HW.h), { wash: '#10131C', ink: CP.ink, sw: .6 });
      if (hash(r * 13 + c * 7) > .7) { glow(wx + 200, wy + 112, 110, CP.sickGlow, .35); clockFace(wx + 200, wy + 112, 40, { sw: .5, cracks: false, hands: [Math.PI / 2, 0] }); }
    }
    paint(rectPts(HW.x, HW.y, HW.w, HW.h), { wash: '#00FF00', ink: null });      // hole (cut by geometry)
    const fr = '#2B2522', sw = .9;
    paint(rectPts(HW.x - 18, HW.y - 18, HW.w + 36, 22), { wash: fr, ink: CP.ink, sw });
    paint(rectPts(HW.x - 30, HW.y + HW.h - 4, HW.w + 60, 26), { wash: fr, ink: CP.ink, sw });
    paint(rectPts(HW.x - 18, HW.y - 18, 22, HW.h + 30), { wash: fr, ink: CP.ink, sw });
    paint(rectPts(HW.x + HW.w - 4, HW.y - 18, 22, HW.h + 30), { wash: fr, ink: CP.ink, sw });
  }

  // ---------- WINDOW PICTURE (close coords 1920x1080) ----------
  // o.girl 0/1, o.expr, o.look
  function windowPicture(o = {}) {
    boilSeed('wp');
    paint(rectPts(-100, -100, W + 200, H + 200), { wash: '#121621', ink: null });
    paint(rectPts(-100, 760, W + 200, 420), { wash: '#1A1A22', ink: null });
    clockFace(1560, 250, 70, { sw: .6, hands: [Math.PI / 2, 0], glow: .5, glowCol: CP.sickGlow });
    if (o.girl) clara(1330, 1010, 46, { key: 'w' });
    bust('boy', 860, 520, 150, { expr: o.expr || 'scared', look: o.look || [0, 0], hands: [[560, 640], [1160, 640]], key: 'aadiW' });
    paint(ellPts(860, 700, 170, 70, 20, 6), { fill: '#C9D2DA', fillOp: 70, bleed: .3, ink: null });
    paint([[200, -100], [420, -100], [120, H + 100], [-100, H + 100]], { fill: '#AEB8C6', fillOp: 22, bleed: .2, ink: null });
  }

  // ---------- ROOM (room coords; window hole cut by the compositor) ----------
  // o.aadi: 'sleep' | 'awake' | 'sit' ; o.phone: true = phone screen lit
  function room(o = {}) {
    boilSeed('room2');
    paint(rectPts(-700, -500, W + 1400, H + 1100), { wash: '#1E2333', fill: '#262C3E', fillOp: 70, bleed: .1, tex: .5, ink: null });
    paint(rectPts(WIN.x, WIN.y, WIN.w, WIN.h), { wash: '#00FF00', ink: null });
    paint(rectPts(-700, 820, W + 1400, 800), { wash: '#24212A', ink: null });
    inkLine([[-700, 820], [W + 700, 820]], 1, CP.ink, 'ink', 0);
    paint([[WIN.x + 40, 830], [WIN.x + WIN.w - 40, 830], [WIN.x + WIN.w - 300, 1180], [WIN.x - 380, 1180]], { fill: '#7D8AA6', fillOp: 38, bleed: .3, ink: null });
    const fr = '#3B3029', sw = .9;
    paint(rectPts(WIN.x - 26, WIN.y - 26, WIN.w + 52, 34), { wash: fr, ink: CP.ink, sw });
    paint(rectPts(WIN.x - 26, WIN.y + WIN.h - 8, WIN.w + 52, 34), { wash: fr, ink: CP.ink, sw });
    paint(rectPts(WIN.x - 26, WIN.y - 26, 30, WIN.h + 52), { wash: fr, ink: CP.ink, sw });
    paint(rectPts(WIN.x + WIN.w - 4, WIN.y - 26, 30, WIN.h + 52), { wash: fr, ink: CP.ink, sw });
    paint(rectPts(WIN.x + WIN.w / 2 - 8, WIN.y, 16, WIN.h), { wash: fr, ink: CP.ink, sw: sw * .7 });
    clockFace(760, 300, 60, { sw: .6, hands: null, cracks: true });           // hands drawn by the compositor
    paint(rectPts(80, 610, 900, 230), { wash: '#2E2A36', ink: CP.ink, sw: 1 });
    paint(rectPts(60, 440, 60, 420), { wash: CP.wood, ink: CP.ink, sw: 1 });
    paint(rrPts(130, 560, 230, 90, 40), { wash: '#BDB6A8', ink: CP.ink, sw: .9 });
    paint(rectPts(1000, 700, 130, 130), { wash: CP.wood, ink: CP.ink, sw: .9 });
    paint(rrPts(1035, 672, 60, 30, 6), { wash: o.phone ? '#B9D4EE' : '#1A1D26', ink: CP.ink, sw: .6 });
    if (o.phone) { glow(1065, 688, 160, '#9FC3E8', .7); letter('3:00', 1065, 688, 16, '#1A2230', { ink: false, font: 'bold 16px Georgia, serif' }); }
    const a = o.aadi || 'sleep';
    if (a !== 'sit') {
      head('boy', 250, 592, 40, { view: 'q', flip: true, sw: .8, skin: COSTUME.boy.skin, expr: a === 'sleep' ? 'sleep' : 'scared', look: a === 'sleep' ? [0, 0] : [.7, -.3] });
      paint([[300, 600], [980, 590], [990, 700], [290, 720]], { wash: CP.maroonDk, ink: CP.ink, sw: .9, curv: .3 });
    } else {
      paint([[420, 640], [980, 600], [990, 700], [400, 720]], { wash: CP.maroonDk, ink: CP.ink, sw: .9, curv: .3 });
      person('boy', 360, 760, 26, { pose: 'sit', view: 'q', expr: 'scared', look: [1, -.4], key: 'aSit' });
    }
  }

  // ---------- CARDS (screen space) ----------
  function cardWarning() { headphoneWarning(2, 5); }
  function cardCount(stage) { countCard(15, stage ? 1 : .3); }
  function cardCredits(n) { credits([1.0, 1.6, 3.0][n]); }

  // ---------- tiling ----------
  // region [x0, y0, w, h] in world px, zoom z → tiles of 1920x1080 (row-major)
  function tile(t, [x0, y0, w, h], z, drawFn) {
    noGrain(); BOILN = 0; boilSeed('frame');   // same boil in every tile, so the seams match
    const nx = Math.ceil(w * z / W), i = Math.round(t * 10), col = i % nx, row = Math.floor(i / nx);
    camBegin(x0 + (col * W + W / 2) / z, y0 + (row * H + H / 2) / z, z); drawFn(); camEnd();
  }
  const R_ROOM = [-200, -100, 2320, 1280], R_CITY = [1400, 250, 5000, 1750], R_FAC = [4100, 700, 2880, 1620], R_CLOSE = [0, 0, W, H], R_CLOCK = [760 - 240, 300 - 135, 480, 270];
  const L = (name, fn) => { LOOPS[name] = fn; LOOPS[name].len = 1; };
  L('e1_room_sleep', t => tile(t, R_ROOM, 2, () => room({ aadi: 'sleep' })));
  L('e1_room_awake', t => tile(t, R_ROOM, 2, () => room({ aadi: 'awake', phone: true })));
  L('e1_room_sit',   t => tile(t, R_ROOM, 2, () => room({ aadi: 'sit', phone: true })));
  L('e1_clock',      t => tile(t, R_CLOCK, 4, () => room({ aadi: 'sleep' })));
  L('e1_city',       t => tile(t, R_CITY, 1, () => city()));
  L('e1_cityglow',   t => tile(t, R_CITY, 1, () => city({ glowOnly: true })));
  L('e1_facade',     t => tile(t, R_FAC, 2, () => facade()));
  L('e1_win_a',      t => tile(t, R_CLOSE, 2, () => windowPicture({ expr: 'scared' })));
  L('e1_win_b',      t => tile(t, R_CLOSE, 2, () => windowPicture({ girl: 1, expr: 'shock' })));
  L('e1_win_c',      t => tile(t, R_CLOSE, 2, () => windowPicture({ girl: 1, expr: 'shock', look: [.8, -.1] })));
  L('e1_win_d',      t => tile(t, R_CLOSE, 2, () => windowPicture({ girl: 1, expr: 'terror' })));
  L('e1_warn',       () => { noGrain(); cardWarning(); });
  L('e1_count',      t => { noGrain(); BOILN = 0; cardCount(Math.round(t * 10)); });
  L('e1_credits',    t => { noGrain(); cardCredits(Math.round(t * 10)); });
  return { WIN, HW };
})();
