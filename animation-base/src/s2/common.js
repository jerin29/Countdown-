// COUNTDOWN Season 2: shared pieces for the one-take episodes.
// Every episode is one shot: shots([[0, ep]]) with a single continuous camera. Places are joined through "portals"
// (a window, a mirror, a clock face): the far place is drawn first under a transform that maps it into the opening,
// then the near place is painted as a frame with a hole, so the camera can glide through without a cut.

// Clara, the Clockmaker's Daughter: a 1940s frock, hair hanging over her face (her face is never shown before Ep 14).
COSTUME.clara = { h: 12.5, skin: '#8E8A84', top: '#C9C2B4', topDk: '#9C9486', sleeve: '#C9C2B4', legs: '#8E8A84', shoes: '#2A2630',
  torsoW: [1.8, 1.8], limbW: .8, dress: true };
CP.sickGlow = '#9FD48A';

function clara(x, y, u, o = {}) {
  const r = person('clara', x, y, u, { pose: o.pose || 'stand', headView: 'back', key: 'clara' + (o.key || ''), rig: o.rig });
  // long wet hair hanging down over the face and shoulders
  boilSeed('claraHair' + (o.key || ''));
  const [hx, hy] = r.head, hr = r.headR;
  for (let i = -3; i <= 3; i++) {
    const sx = hx + i * hr * .28, sway = Math.sin(T * 1.3 + i) * hr * .05;
    paint(ribbon([[sx, hy - hr * .5], [sx + sway, hy + hr * 1.2], [sx + sway * 2 + i * hr * .05, hy + hr * (2.2 + .25 * hash(i + 7))]], hr * .34, hr * .12), { wash: CP.hair, ink: CP.ink, sw: .6 });
  }
  return r;
}

// a rectangle frame with a rectangular hole: paints everything in [ox,oy,ow,oh] except the hole [hx,hy,hw,hh]
function frameWithHole(ox, oy, ow, oh, hx, hy, hw, hh, style) {
  paint(rectPts(ox, oy, ow, hy - oy), style);                         // top
  paint(rectPts(ox, hy + hh, ow, oy + oh - hy - hh), style);          // bottom
  paint(rectPts(ox, hy - 2, hx - ox, hh + 4), style);                 // left
  paint(rectPts(hx + hw, hy - 2, ox + ow - hx - hw, hh + 4), style);  // right
}

// headphone icon (screen space), cream ink
function headphones(cx, cy, s, a = 1) {
  if (a <= .01) return;
  boilSeed('hp');
  const col = mixCol('#07080C', CP.cream, a);
  const arc = []; for (let i = 0; i <= 16; i++) { const t = Math.PI + i / 16 * Math.PI; arc.push([cx + Math.cos(t) * s, cy + Math.sin(t) * s * 1.05]); }
  inkLine(arc, 3.2, col, 'ink', .5);
  for (const k of [-1, 1]) paint(rrPts(cx + k * s - s * .22, cy - s * .05, s * .44, s * .62, s * .14), { wash: col, ink: null });
}

// the count card: a cracked clock face with the night's number (Season 2 counts 15 → 0)
function countCard(n, lt) {
  full('#060709');
  const k = easeOut(seg(lt, 0, .4)), shake = Math.exp(-lt * 6) * 10;
  boilSeed('cc' + n);
  glow(960, 540, 520, '#5A2626', .55 * k);
  clockFace(960 + jit(shake), 540, 300 * (1.15 - .15 * k), { sw: 1.2, col: '#D8D0BC', hands: [Math.PI / 2, 0] });
  letter(String(n), 960, 548, 260, '#8E1E22', { screen: true, ink: false, font: '260px Georgia, serif', alpha: k });
  if (lt > .35) {
    const c = easeOut(seg(lt, .35, .7));
    inkLine([[850, 240], lerp2([850, 240], [930, 420], c), lerp2([850, 240], [880, 560], c)], 2.6, '#060709', 'ink', 0);
    inkLine([[1150, 760], lerp2([1150, 760], [1040, 650], c), lerp2([1150, 760], [1080, 520], c)], 2, '#060709', 'ink', 0);
  }
}
const lerp2 = (a, b, k) => [lerp(a[0], b[0], k), lerp(a[1], b[1], k)];

// end credits (screen space): Story by … / Created by … / Thank you for watching
function credits(lt) {
  full('#060709');
  const a1 = seg(lt, .2, .9) * (1 - seg(lt, 4.4, 5)), a2 = seg(lt, .7, 1.4) * (1 - seg(lt, 4.4, 5)), a3 = seg(lt, 1.6, 2.3) * (1 - seg(lt, 4.4, 5));
  letter('Story by Jerin Joseph Sebastian', 960, 430, 50, '#E9E2D0', { screen: true, ink: false, font: '50px Georgia, serif', alpha: a1 });
  letter('Created by Claude AI & vidIQ', 960, 520, 40, '#B9B09C', { screen: true, ink: false, font: '40px Georgia, serif', alpha: a2 });
  letter('Thank you for watching', 960, 650, 44, '#8E1E22', { screen: true, ink: false, font: 'italic 44px Georgia, serif', alpha: a3 });
}

// headphone warning (screen space)
function headphoneWarning(lt, dur) {
  full('#050609');
  const a = seg(lt, .25, .8) * (1 - seg(lt, dur - .6, dur));
  headphones(960, 400, 70, a);
  letter('ഹെഡ്‌ഫോൺ ഉപയോഗിക്കുക', 960, 560, 64, '#E9E2D0', { screen: true, ink: false, font: '64px "Noto Sans Malayalam"', alpha: a });
  letter('USE HEADPHONES', 960, 640, 28, '#8C97A6', { screen: true, ink: false, font: '28px Georgia, serif', alpha: a * .9 });
}
