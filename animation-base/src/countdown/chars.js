// COUNTDOWN: the cast, painted with the kit's brush. Flat 2D, one jointed rig, a costume per character.
// person(name, x, y, u, o): (x, y) = ground point between the feet, u = size unit (a teen is ~16.5u tall).
// o: { pose, view: 'front'|'q'|'back', flip, expr, look:[x,y], lean, glitch, light } ; see POSES and EXPR below.

const CP = {   // COUNTDOWN palette: cold fog, deep shadow, one accent per scene
  ink: '#1C1820', deep: '#12151E', night: '#1B2130', navy: '#232B3E', fog: '#8C97A6', fogLt: '#B7BFC8', stone: '#3A3F4C',
  wall: '#4E5566', wallLt: '#6A7283', wood: '#4A3A30', woodLt: '#6B5444', cream: '#E9E2D0', paper: '#D9D1BF',
  skin: '#B07A5A', skinDk: '#8A5A42', hair: '#1E1A1E', maroon: '#6E2B33', maroonDk: '#4E1E25', denim: '#2F3646',
  yellow: '#D9A93A', yellowDk: '#A87E22', vest: '#525C6E', khaki: '#6B6457', saree: '#E3DCCB', sareeDk: '#B9B09C',
  grey: '#9A9590', nehaSkin: '#8E9DA8', nehaDk: '#65727D', pinafore: '#9DB3C4', pinaforeDk: '#7890A3', shirt: '#D8DDE0',
  coat: '#17151C', coatLt: '#2A2733', brass: '#B08D4A', brassDk: '#7D6230', sick: '#7FA36A', lamp: '#F2B45C', blood: '#7A1E22',
  silver: '#C9CDD2', sepia: '#A88B66', sepiaDk: '#6E5640', sepiaLt: '#D8C4A2'
};

// limb direction: angle 0 points straight down, +pi/2 points screen-right, pi points up
const dirv = a => [Math.sin(a), Math.cos(a)];
const addv = (p, a, len) => [p[0] + Math.sin(a) * len, p[1] + Math.cos(a) * len];

// ---------- poses: joint angles (radians). arm: [shoulder, elbow-relative]; leg: [hip, knee-relative] ----------
// "L"/"R" are the character's screen-left / screen-right limbs in the unflipped drawing.
const POSES = {
  stand:   { lean: 0, aL: [.12, .1], aR: [-.12, -.1], lL: [.06, 0], lR: [-.06, 0] },
  tense:   { lean: -.04, aL: [.35, .5], aR: [-.35, -.5], lL: [.12, 0], lR: [-.1, 0] },
  armsIn:  { lean: 0, aL: [.25, -1.6], aR: [-.25, 1.6], lL: [.05, 0], lR: [-.05, 0] },          // hugging self / hands in sleeves
  coverEars: { lean: 0, aL: [2.6, 1.9], aR: [-2.6, -1.9], lL: [.08, 0], lR: [-.08, 0] },
  reach:   { lean: .12, aL: [.2, .1], aR: [-2.0, .15], lL: [.15, 0], lR: [-.2, 0] },              // right arm reaching out right? (mirrored by flip)
  reachFwd:{ lean: .15, aL: [2.0, .1], aR: [.4, .2], lL: [.2, 0], lR: [-.25, 0] },               // left arm forward (to the right side)
  point:   { lean: .05, aL: [1.75, 0], aR: [-.15, -.1], lL: [.1, 0], lR: [-.08, 0] },
  phone:   { lean: 0, aL: [.25, 2.3], aR: [-.15, -.1], lL: [.07, 0], lR: [-.07, 0] },            // holding phone up at chest
  selfie:  { lean: 0, aL: [2.1, .3], aR: [-.2, -.2], lL: [.08, 0], lR: [-.08, 0] },
  run:     { lean: .32, aL: [1.0, 1.2], aR: [-.9, 1.4], lL: [.9, -1.3], lR: [-.6, .3], dy: -.6 },
  walk:    { lean: .06, aL: [.35, .25], aR: [-.3, .2], lL: [.35, 0], lR: [-.3, .15] },
  sit:     { lean: -.05, aL: [.25, 1.1], aR: [-.25, -1.1], lL: [1.45, -1.45], lR: [1.35, -1.35], sit: true },
  sitHug:  { lean: .2, aL: [.6, 1.8], aR: [.4, 1.9], lL: [1.9, -2.5], lR: [1.8, -2.4], sit: true },   // knees up, hugging them
  crouch:  { lean: .25, aL: [.9, 1.1], aR: [.6, 1.4], lL: [2.0, -2.6], lR: [1.7, -2.5], dy: 3.2 },
  kneel:   { lean: .1, aL: [.4, .6], aR: [-.2, .3], lL: [1.6, -1.6], lR: [.05, -1.55], dy: 3.4 },
  fallBack:{ lean: -.35, aL: [1.2, .5], aR: [-1.6, -.4], lL: [.4, 0], lR: [-.2, 0] },
  hold2:   { lean: .1, aL: [1.3, .9], aR: [-1.0, -1.2], lL: [.15, 0], lR: [-.1, 0] },           // both hands forward holding something
  wind:    { lean: .18, aL: [1.6, .3], aR: [1.3, .6], lL: [.25, 0], lR: [-.25, 0] },             // both hands forward, turning a key
  hug:     { lean: .12, aL: [1.4, 1.6], aR: [1.1, 1.9], lL: [.12, 0], lR: [-.12, 0] },
  shrug:   { lean: 0, aL: [.9, -1.9], aR: [-.9, 1.9], lL: [.08, 0], lR: [-.08, 0] },
  keeperReach: { lean: .1, aL: [.15, .05], aR: [-1.9, .1], lL: [.04, 0], lR: [-.04, 0] },
};

// ---------- faces ----------
// expr: neutral, tired, scared, terror, sad, cry, determined, smile, whisper, shock, calm, sleep, angryLow
function face(cx, cy, r, o = {}) {
  const sw = o.sw ?? Math.max(.35, r / 40), view = o.view || 'front', fl = o.flip ? -1 : 1;
  const shift = view === 'q' ? .28 * r * fl : 0, lx = (o.look?.[0] || 0) * r * .09, ly = (o.look?.[1] || 0) * r * .07;
  const ex = o.expr || 'neutral', skin = o.skin || CP.skin, dk = o.skinDk || CP.skinDk;
  const eyeY = cy + r * .05, gap = view === 'q' ? r * .34 : r * .38;
  const eyes = [[cx + shift - gap, eyeY], [cx + shift + gap, eyeY]];
  const er = r * (ex === 'terror' || ex === 'shock' ? .2 : .16);
  if (o.shadowEyes) { // Neha: eyes lost in shadow
    paint(rrPts(cx + shift - r * .72, eyeY - r * .22, r * 1.44, r * .42, r * .2), { wash: o.shadowCol || '#3B4651', washOp: 230, ink: null });
    if (o.pin) for (const [x, y] of eyes) paint(ellPts(x, y, r * .03, r * .03, 8), { wash: '#E8F0F4', ink: null });
  } else if (ex === 'sleep' || ex === 'closed') {
    for (const [x, y] of eyes) inkLine([[x - er, y], [x, y + er * .35], [x + er, y]], sw, CP.ink, 'inkfine');
  } else {
    for (const [i, [x, y]] of eyes.entries()) {
      const squash = ex === 'tired' ? .55 : ex === 'determined' || ex === 'angryLow' ? .6 : ex === 'sad' || ex === 'cry' ? .75 : 1;
      paint(ellPts(x, y, er * 1.15, er * squash, 16), { wash: '#EEE8DC', ink: CP.ink, sw: sw * .8 });
      const pr = er * (ex === 'terror' ? .35 : .55);
      paint(ellPts(x + lx + shift * .1, y + ly, pr, Math.min(pr, er * squash * .95), 12), { wash: CP.ink, ink: null });
      if (ex === 'tired' || ex === 'determined' || ex === 'angryLow') inkLine([[x - er * 1.2, y - er * squash * .9], [x + er * 1.2, y - er * squash * .9]], sw, CP.ink, 'inkfine');
      // brows
      const bt = { scared: .35, terror: .5, sad: .4, cry: .45, determined: -.35, angryLow: -.4, whisper: .2, shock: .1 }[ex] || 0;
      const s = i === 0 ? 1 : -1;
      inkLine([[x - er * 1.3, y - er * 2.1 + bt * er * s * -1.2], [x + er * 1.3, y - er * 2.1 - bt * er * s * -1.2]], sw * 1.1, CP.hair, 'ink', 0);
    }
  }
  if (o.darkCircles) for (const [x, y] of eyes) inkLine([[x - er, y + er * 1.25], [x, y + er * 1.6], [x + er, y + er * 1.25]], sw * .8, dk, 'inkfine');
  if (o.glasses) for (const [x, y] of eyes) paint(ellPts(x, y, er * 2.3, er * 2.1, 20), { ink: CP.ink, sw: sw * .7 });
  if (o.glasses) inkLine([[eyes[0][0] + er * 2.3, eyeY], [eyes[1][0] - er * 2.3, eyeY]], sw * .7, CP.ink, 'inkfine', 0);
  // nose
  inkLine([[cx + shift + r * .04 * fl, cy + r * .2], [cx + shift + r * .1 * fl, cy + r * .38], [cx + shift - r * .02 * fl, cy + r * .42]], sw * .7, dk, 'inkfine');
  // mouth
  const mx = cx + shift, my = cy + r * .62, mw = r * .22;
  const m = { neutral: 'flat', tired: 'flat', scared: 'o', terror: 'scream', sad: 'frown', cry: 'wail', determined: 'flat', smile: 'smile',
    whisper: 'o', shock: 'O', calm: 'smile', sleep: 'flat', angryLow: 'frown' }[ex] || 'flat';
  if (m === 'flat') inkLine([[mx - mw, my], [mx + mw, my + r * .01]], sw, CP.ink, 'inkfine');
  if (m === 'smile') inkLine([[mx - mw, my - r * .04], [mx, my + r * .06], [mx + mw, my - r * .04]], sw, CP.ink, 'inkfine');
  if (m === 'frown') inkLine([[mx - mw, my + r * .05], [mx, my - r * .03], [mx + mw, my + r * .05]], sw, CP.ink, 'inkfine');
  if (m === 'o') paint(ellPts(mx, my, r * .07, r * .09, 10), { wash: '#3A1F24', ink: CP.ink, sw: sw * .7 });
  if (m === 'O') paint(ellPts(mx, my + r * .04, r * .12, r * .17, 12), { wash: '#3A1F24', ink: CP.ink, sw: sw * .8 });
  if (m === 'scream') paint(ellPts(mx, my + r * .08, r * .16, r * .26, 14), { wash: '#2A1418', ink: CP.ink, sw: sw * .8 });
  if (m === 'wail') paint(ellPts(mx, my + r * .03, r * .14, r * .1, 12), { wash: '#3A1F24', ink: CP.ink, sw: sw * .8 });
  if (ex === 'cry' || o.tears) for (const [x, y] of eyes) inkLine([[x, y + er], [x - r * .02, y + r * .35], [x + r * .01, y + r * .55]], sw * 1.1, '#9FC3D6', 'inkfine');
}

// ---------- heads / hair per character ----------
function head(name, cx, cy, r, o) {
  const view = o.view || 'front', fl = o.flip ? -1 : 1, sw = o.sw;
  const skin = o.skin, back = view === 'back';
  const hairBack = {   // hair drawn behind the head
    meera: () => paint(through([[cx - r * 1.12, cy - r * .3], [cx - r * 1.25, cy + r * .8], [cx - r * 1.05, cy + r * 1.55], [cx - r * .7, cy + r * 1.35], [cx - r * .5, cy + r * 1.7],
      [cx, cy + r * 1.3], [cx + r * .5, cy + r * 1.75], [cx + r * .75, cy + r * 1.35], [cx + r * 1.1, cy + r * 1.6], [cx + r * 1.28, cy + r * .8], [cx + r * 1.12, cy - r * .3],
      [cx, cy - r * 1.25]], 3), { wash: CP.hair, ink: CP.ink, sw }),
    neha: () => {
      for (const s of [-1, 1]) {
        const bx = cx + s * r * .95;
        paint(ribbon([[bx, cy], [bx + s * r * .15, cy + r * 1.2], [bx + s * r * .05, cy + r * 2.4]], r * .42, r * .22), { wash: '#2A2C33', ink: CP.ink, sw });
        paint(starPts(bx + s * r * .05, cy + r * 2.4, r * .32, .35, 2, 0), { wash: CP.pinaforeDk, ink: CP.ink, sw: sw * .7 });
      }
    },
    ammachi: () => paint(ellPts(cx - fl * r * (view === 'q' ? .65 : 0), cy - r * (view === 'front' ? 1.0 : .55), r * .45, r * .38, 14), { wash: '#BDB8B1', ink: CP.ink, sw }),
  };
  if (!back) hairBack[name]?.();
  // the head itself
  paint(ellPts(cx, cy, r * .92, r, 24), { wash: back ? (name === 'ammachi' ? '#BDB8B1' : name === 'neha' ? '#2A2C33' : CP.hair) : skin, ink: CP.ink, sw });
  if (back) {
    if (name === 'meera') hairBack.meera();
    if (name === 'neha') hairBack.neha();
    if (name === 'ammachi') paint(ellPts(cx, cy - r * .3, r * .45, r * .38, 14), { wash: '#BDB8B1', ink: CP.ink, sw });
    return;
  }
  if (name === 'meera' || name === 'arjun' || name === 'neha' || name === 'boy') {
    // fringe
    const q = view === 'q' ? fl * r * .2 : 0;
    const fringe = name === 'arjun' || name === 'boy'
      ? [[cx - r * .95, cy - r * .05], [cx - r * .9, cy - r * .7], [cx - r * .3 + q, cy - r * 1.12], [cx + r * .5 + q, cy - r * 1.05], [cx + r * .95, cy - r * .5], [cx + r * .92, cy - r * .05], [cx + r * .55 + q, cy - r * .55], [cx + q, cy - r * .62], [cx - r * .55 + q, cy - r * .45]]
      : name === 'neha'
        ? [[cx - r * .95, cy + r * .1], [cx - r * .85, cy - r * .75], [cx + q, cy - r * 1.1], [cx + r * .85, cy - r * .75], [cx + r * .95, cy + r * .1], [cx + r * .4 + q, cy - r * .55], [cx + q, cy - r * .6], [cx - r * .4 + q, cy - r * .55]]
        : [[cx - r * .97, cy + r * .2], [cx - r * .95, cy - r * .6], [cx - r * .2 + q, cy - r * 1.12], [cx + r * .7 + q, cy - r * .95], [cx + r * .98, cy - r * .2], [cx + r * .9, cy + r * .4], [cx + r * .55 + q, cy - r * .3], [cx + r * .25 + q, cy - r * .55], [cx - r * .1 + q, cy - r * .3], [cx - r * .35 + q, cy - r * .62], [cx - r * .7, cy - r * .1]];
    paint(fringe, { wash: name === 'neha' ? '#2A2C33' : CP.hair, ink: CP.ink, sw, curv: .4 });
  }
  if (name === 'ammachi') {
    paint([[cx - r * .95, cy], [cx - r * .85, cy - r * .7], [cx, cy - r * 1.05], [cx + r * .85, cy - r * .7], [cx + r * .95, cy], [cx + r * .6, cy - r * .55], [cx, cy - r * .7], [cx - r * .6, cy - r * .55]],
      { wash: '#BDB8B1', ink: CP.ink, sw, curv: .5 });
  }
  if (name === 'elias') {
    paint([[cx - r * .95, cy - r * .1], [cx - r * .8, cy - r * .55], [cx - r * .4, cy - r * .5], [cx - r * .6, cy - r * .1]], { wash: '#C9C3BA', ink: CP.ink, sw });
    paint([[cx + r * .95, cy - r * .1], [cx + r * .8, cy - r * .55], [cx + r * .4, cy - r * .5], [cx + r * .6, cy - r * .1]], { wash: '#C9C3BA', ink: CP.ink, sw });
  }
  face(cx, cy, r, { ...o, sw: sw * .9 });
  if (name === 'elias') paint([[cx - r * .35, cy + r * .5], [cx, cy + r * .42], [cx + r * .35, cy + r * .5], [cx + r * .2, cy + r * .6], [cx - r * .2, cy + r * .6]], { wash: '#C9C3BA', ink: CP.ink, sw: sw * .7 });
}

// clock face (the Keeper's head, the tower, wall clocks). hands: null | [hourAngle, minAngle] (radians, 0 = 12 o'clock)
function clockFace(cx, cy, r, o = {}) {
  const sw = o.sw ?? Math.max(.4, r / 45);
  if (o.glow) glow(cx, cy, r * 2.2, o.glowCol || CP.sick, o.glow);
  paint(ellPts(cx, cy, r * 1.08, r * 1.08, 32), { wash: o.rim || CP.brassDk, ink: CP.ink, sw });
  paint(ellPts(cx, cy, r, r, 32), { wash: o.col || CP.cream, ink: CP.ink, sw: sw * .7 });
  boilSeed('ticks' + Math.round(cx) + Math.round(cy));
  for (let i = 0; i < 12; i++) {
    const a = i / 12 * TAU, c = Math.sin(a), s = -Math.cos(a), k = i % 3 === 0 ? .78 : .85;
    inkLine([[cx + c * r * k, cy + s * r * k], [cx + c * r * .93, cy + s * r * .93]], sw * (i % 3 === 0 ? 1.4 : .8), CP.ink, 'inkfine', 0);
  }
  if (o.cracks !== false) {
    inkLine([[cx - r * .15, cy - r * .98], [cx - r * .05, cy - r * .55], [cx - r * .25, cy - r * .2], [cx - r * .1, cy + r * .15]], sw * .8, CP.ink, 'inkfine', 0);
    inkLine([[cx + r * .95, cy + r * .3], [cx + r * .5, cy + r * .25], [cx + r * .35, cy + r * .55]], sw * .7, CP.ink, 'inkfine', 0);
  }
  if (o.face) face(cx, cy + r * .05, r * .55, { ...o.face, sw: sw * .8 });
  if (o.hands) {
    const [ha, ma] = o.hands;
    inkLine([[cx, cy], [cx + Math.sin(ha) * r * .5, cy - Math.cos(ha) * r * .5]], sw * 2.4, CP.ink, 'ink', 0);
    inkLine([[cx, cy], [cx + Math.sin(ma) * r * .78, cy - Math.cos(ma) * r * .78]], sw * 1.6, CP.ink, 'ink', 0);
    paint(ellPts(cx, cy, r * .05, r * .05, 10), { wash: CP.brass, ink: CP.ink, sw: sw * .6 });
  }
}

// key-shaped finger: from p, direction a, length L
function keyFinger(p, a, L, w, sw) {
  const e = addv(p, a, L);
  paint(ribbon([p, addv(p, a, L * .5), e], w, w * .7), { wash: CP.brass, ink: CP.ink, sw });
  const b = addv(p, a, L * .85), perp = a + Math.PI / 2;
  paint([b, addv(b, perp, w * 1.3), addv(addv(b, perp, w * 1.3), a, w * .9), addv(b, a, w * .9)], { wash: CP.brass, ink: CP.ink, sw: sw * .7 });
}

// ---------- costumes ----------
const COSTUME = {
  meera:   { h: 16, skin: CP.skin, top: CP.maroon, topDk: CP.maroonDk, sleeve: CP.maroon, legs: CP.denim, shoes: '#1A1C22', torsoW: [2.3, 2.0], limbW: 1.05, hood: true, watch: true },
  arjun:   { h: 17.5, skin: '#A87256', top: CP.yellow, topDk: CP.yellowDk, sleeve: CP.yellow, legs: CP.khaki, shoes: '#2A2420', torsoW: [2.2, 1.8], limbW: .95, vest: true },
  ammachi: { h: 14.2, skin: '#9C6C52', top: CP.saree, topDk: CP.sareeDk, sleeve: CP.saree, legs: CP.saree, shoes: '#3A322C', torsoW: [2.1, 2.4], limbW: .95, skirt: true, pallu: true, stoop: -.12 },
  neha:    { h: 15.2, skin: CP.nehaSkin, top: CP.pinafore, topDk: CP.pinaforeDk, sleeve: CP.shirt, legs: CP.nehaSkin, shoes: '#2B2F36', torsoW: [2.0, 1.9], limbW: .85, dress: true },
  keeper:  { h: 27, skin: CP.brass, top: CP.coat, topDk: CP.coatLt, sleeve: CP.coat, legs: '#141218', shoes: '#0E0D12', torsoW: [2.6, 1.7], limbW: .9, tails: true, clock: true },
  elias:   { h: 16.5, skin: '#A87A5E', top: '#5B5148', topDk: '#3E3731', sleeve: '#E2DAC8', legs: '#4A433C', shoes: '#2A2420', torsoW: [2.3, 2.2], limbW: 1.0, apron: true },
  boy:     { h: 11, skin: CP.skin, top: '#3E5A74', topDk: '#2D4357', sleeve: '#3E5A74', legs: '#3E5A74', shoes: '#222', torsoW: [1.8, 1.7], limbW: .9 },
  mob:     { h: 16.5, skin: '#2A2328', top: '#2A2328', topDk: '#1C171B', sleeve: '#2A2328', legs: '#2A2328', shoes: '#1C171B', torsoW: [2.4, 2.2], limbW: 1.1, silhouette: true },
};

function person(name, x, y, u, o = {}) {
  const C = COSTUME[name], P = { ...POSES[o.pose || 'stand'], ...(o.rig || {}) };
  const fl = o.flip ? -1 : 1, view = o.view || 'front', back = view === 'back';
  const sw = o.sw ?? clamp(u / 36, .3, 1.5);
  const k = C.h / 16;                         // height scale vs a 16u teen
  const legLen = 7.4 * k * u, torsoLen = 5.4 * k * u, armLen = 5.1 * k * u, headR = (name === 'keeper' ? 2.4 : 1.75) * u * (name === 'boy' ? 1.05 : 1);
  const lean = -(P.lean + (C.stoop || 0)) * fl;
  boilSeed('p_' + name + (o.key || ''));
  push(); translate(x, y); if (o.rot) rotate(o.rot);
  const dy = (P.dy || 0) * u * k;
  const hip = [0, -legLen + dy];
  const sh = [hip[0] + Math.sin(lean) * torsoLen, hip[1] - Math.cos(lean) * torsoLen];
  const sw2 = C.torsoW[0] * u, hw2 = C.torsoW[1] * u;
  const perp = [Math.cos(lean), Math.sin(lean)];
  const hipL = [hip[0] - perp[0] * hw2 * .55, hip[1] - perp[1] * hw2 * .55], hipR = [hip[0] + perp[0] * hw2 * .55, hip[1] + perp[1] * hw2 * .55];
  const shL = [sh[0] - perp[0] * sw2 * .85, sh[1] - perp[1] * sw2 * .85], shR = [sh[0] + perp[0] * sw2 * .85, sh[1] + perp[1] * sw2 * .85];
  const mir = a => -a * fl;
  const limb = (root, [a1, a2], len, w0, w1, col, end) => {
    const j = addv(root, mir(a1), len * .52), e = addv(j, mir(a1 + a2), len * .5);
    paint(ribbon([root, j, e], w0, w1), { wash: col, ink: C.silhouette ? null : CP.ink, sw, curv: 0 });
    return { j, e, a: mir(a1 + a2) };
  };
  const limbW = C.limbW * u;
  const drawLeg = (root, ang, front) => {
    if (C.skirt && !P.sit) return null;
    const lg = limb(root, ang, legLen, limbW * 1.25, limbW * .9, C.legs);
    const foot = [[lg.e[0] - u * .3 * fl, lg.e[1] - u * .25], [lg.e[0] + u * 1.15 * fl, lg.e[1] - u * .2], [lg.e[0] + u * 1.2 * fl, lg.e[1] + u * .25], [lg.e[0] - u * .35 * fl, lg.e[1] + u * .25]];
    paint(foot, { wash: C.shoes, ink: CP.ink, sw: sw * .8 });
    return lg;
  };
  const drawArm = (root, ang, side) => {
    const ar = limb(root, ang, armLen, limbW * 1.1, limbW * .85, C.sleeve);
    if (C.keyFingers || name === 'keeper') {
      for (let i = -1; i <= 1; i++) keyFinger(ar.e, ar.a + i * .22, u * 3.2, u * .32, sw * .7);
    } else {
      paint(ellPts(ar.e[0] + Math.sin(ar.a) * u * .35, ar.e[1] + Math.cos(ar.a) * u * .35, u * .55, u * .62, 12), { wash: C.silhouette ? C.skin : C.skin, ink: C.silhouette ? null : CP.ink, sw: sw * .8 });
    }
    if (C.watch && side === 'L') paint(ellPts(...addv(ar.e, ar.a, -u * .15), u * .5, u * .4, 10), { wash: CP.silver, ink: CP.ink, sw: sw * .7 });
    if (o.hold && side === o.hold.side) o.hold.draw(addv(ar.e, ar.a, u * .5), ar.a, u, sw);
    return ar;
  };
  // back limbs first
  const legs = [['L', hipL, P.lL], ['R', hipR, P.lR]], arms = [['L', shL, P.aL], ['R', shR, P.aR]];
  // skirt / dress / coat tails behind legs
  if (C.tails) {
    paint([[sh[0] - sw2 * .9, sh[1] + u], [sh[0] + sw2 * .9, sh[1] + u], [hip[0] + hw2 * 1.6, -u * 2.5], [hip[0] + hw2 * .6, -u * 1.6], [hip[0], -u * 4],
      [hip[0] - hw2 * .6, -u * 1.6], [hip[0] - hw2 * 1.6, -u * 2.5]], { wash: C.top, ink: CP.ink, sw });
  }
  for (const [s, r, a] of legs) drawLeg(r, a, s === 'R');
  if (C.skirt) {
    const bottom = P.sit ? hip[1] + u * 3.2 : -u * .3;
    paint([[hipL[0] - u * .4, hipL[1] - u * .5], [hipR[0] + u * .4, hipR[1] - u * .5], [hipR[0] + u * 2.2 + (P.sit ? u * 4 * fl : 0), bottom], [hipL[0] - u * 2.0 + (P.sit ? u * 4 * fl : 0), bottom]],
      { wash: C.top, ink: CP.ink, sw });
    inkLine([[hip[0] + u * .5, hip[1]], [hip[0] + u * 1.0 + (P.sit ? u * 3 * fl : 0), bottom - u * .3]], sw * .6, C.topDk, 'inkfine');
    paint([[hipL[0] - u * 2.0 + (P.sit ? u * 4 * fl : 0), bottom - u * .9], [hipR[0] + u * 2.2 + (P.sit ? u * 4 * fl : 0), bottom - u * .9], [hipR[0] + u * 2.2 + (P.sit ? u * 4 * fl : 0), bottom], [hipL[0] - u * 2.0 + (P.sit ? u * 4 * fl : 0), bottom]],
      { wash: C.topDk, ink: null });
  }
  // torso
  const torso = [shL, shR, [hipR[0] + perp[0] * u * .3, hipR[1] + u * .6], [hipL[0] - perp[0] * u * .3, hipL[1] + u * .6]];
  if (C.dress) {
    torso[2] = [hipR[0] + u * 1.4, hipR[1] + u * 3.2]; torso[3] = [hipL[0] - u * 1.4, hipL[1] + u * 3.2];
  }
  if (C.tails) { torso[2] = [hipR[0] + u * .4, hipR[1] + u * 1.2]; torso[3] = [hipL[0] - u * .4, hipL[1] + u * 1.2]; }
  if (C.apron) { torso[2] = [hipR[0] + u * .6, hipR[1] + u * 2.6]; torso[3] = [hipL[0] - u * .6, hipL[1] + u * 2.6]; }
  // arms behind the torso when seen from the front are drawn after; from the back, before
  if (back) for (const [s, r, a] of arms) drawArm(r, a, s);
  if (C.hood && !back) paint(ellPts(sh[0], sh[1] - u * .2, sw2 * .75, u * .9, 16), { wash: C.topDk, ink: CP.ink, sw });
  paint(torso, { wash: C.top, ink: C.silhouette ? null : CP.ink, sw, curv: .15 });
  if (C.hood && back) paint(ellPts(sh[0], sh[1] + u * .9, sw2 * .7, u * 1.4, 16), { wash: C.topDk, ink: CP.ink, sw });
  if (!back) {
    if (C.vest) paint([[sh[0] - u * .8, sh[1] + u * .2], [sh[0] + u * .8, sh[1] + u * .2], [hip[0] + u * .9, hip[1] + u * .4], [hip[0] - u * .9, hip[1] + u * .4]], { wash: CP.vest, ink: CP.ink, sw: sw * .8 });
    if (C.hood) { inkLine([[sh[0] - u * .4, sh[1] + u * .3], [sh[0] - u * .5, sh[1] + u * 2.2]], sw * .7, CP.cream, 'inkfine'); inkLine([[sh[0] + u * .4, sh[1] + u * .3], [sh[0] + u * .5, sh[1] + u * 2.1]], sw * .7, CP.cream, 'inkfine');
      paint(rrPts(hip[0] - u * 1.2, hip[1] - u * 2.2, u * 2.4, u * 1.3, u * .3), { wash: C.topDk, ink: CP.ink, sw: sw * .6 }); }
    if (C.dress) { paint([[sh[0] - u * .7, sh[1]], [sh[0] + u * .7, sh[1]], [sh[0], sh[1] + u * 1.2]], { wash: CP.shirt, ink: CP.ink, sw: sw * .7 }); }
    if (C.pallu) paint(ribbon([[shR[0], shR[1] - u * .2], [sh[0], sh[1] + u * 2], [hipL[0] - u * .6, hipL[1] + u * .5]], u * 1.6, u * 1.0), { wash: CP.sareeDk, ink: CP.ink, sw: sw * .8 });
    if (name === 'ammachi') { // pocket watch on a chain
      inkLine([[sh[0] - u * .6, sh[1] + u * .1], [sh[0], sh[1] + u * 2.0], [sh[0] + u * .6, sh[1] + u * .1]], sw * .6, CP.brassDk, 'inkfine');
      paint(ellPts(sh[0], sh[1] + u * 2.4, u * .55, u * .55, 14), { wash: CP.brass, ink: CP.ink, sw: sw * .7 });
    }
    if (C.apron) paint([[sh[0] - u * 1.2, sh[1] + u * 1.2], [sh[0] + u * 1.2, sh[1] + u * 1.2], [hip[0] + u * 1.6, hip[1] + u * 2.4], [hip[0] - u * 1.6, hip[1] + u * 2.4]], { wash: '#7B6A55', ink: CP.ink, sw: sw * .8 });
    if (name === 'keeper') { paint([[sh[0] - u * .5, sh[1]], [sh[0] + u * .5, sh[1]], [sh[0], sh[1] + u * 4.5]], { wash: '#2E2B36', ink: CP.ink, sw: sw * .7 });
      for (let i = 0; i < 3; i++) paint(ellPts(sh[0], sh[1] + u * (5.5 + i * 1.4), u * .22, u * .22, 8), { wash: CP.brass, ink: null }); }
  }
  if (!back) for (const [s, r, a] of arms) drawArm(r, a, s);
  // neck + head
  const headC = [sh[0] + Math.sin(lean) * u * (C.clock ? 2.2 : 1.9) + (o.headDx || 0) * u, sh[1] - Math.cos(lean) * u * (C.clock ? 2.2 : 1.9) - u * .2];
  if (!C.clock) paint(ribbon([sh, headC], u * .75, u * .7), { wash: C.skin, ink: C.silhouette ? null : CP.ink, sw: sw * .7 });
  if (C.silhouette) paint(ellPts(headC[0], headC[1], headR * .92, headR, 18), { wash: C.skin, ink: null });
  else if (C.clock) clockFace(headC[0], headC[1] - u * .4, headR * 1.15, { sw, hands: o.hands || null, glow: o.glow ?? .35, face: o.clockFace || null, col: o.clockCol });
  else head(name, headC[0], headC[1], headR, { view, flip: o.flip, sw, skin: C.skin, skinDk: name === 'neha' ? CP.nehaDk : CP.skinDk,
    expr: o.expr || 'neutral', look: o.look, darkCircles: name === 'meera' && o.expr !== 'smile', glasses: name === 'arjun' || name === 'ammachi',
    shadowEyes: name === 'neha' && !o.nehaEyes, pin: name === 'neha', tears: o.tears });
  if (name === 'neha') { // dripping water
    boilSeed('drip' + (o.key || ''));
    for (let i = 0; i < 4; i++) paint(ellPts(headC[0] + (i - 1.5) * u * .9, headC[1] + headR * (1.6 + hash(i + 3) * 1.2) + frac(T * .8 + hash(i)) * u * 3, u * .14, u * .22, 8), { wash: '#A9C6D8', ink: null });
  }
  pop();
  if (o.glitch) vhs(x, y - C.h * u * .55, C.h * u * .6, C.h * u * .62, o.glitch);
  return { head: [x + headC[0], y + headC[1]], headR, hand: null };
}

// VHS glitch bars over a region (Neha)
function vhs(cx, cy, w, h, k = 1) {
  boilSeed('vhs' + Math.floor(T * 24));
  for (let i = 0; i < Math.round(4 * k); i++) {
    const yy = cy - h + random() * h * 2, hh = 2 + random() * h * .025, off = (random() - .5) * w * .3 * k;
    paint(rectPts(cx - w * .5 + off, yy, w, hh), { wash: random() < .5 ? '#B9CBD6' : '#E4ECF0', washOp: 255, ink: null });
  }
}
