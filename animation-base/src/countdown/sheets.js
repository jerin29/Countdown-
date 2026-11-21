// COUNTDOWN model sheets (rendered with: node render_boards.mjs --sheets). Labels are allowed here: these are sheets, not film.
const SHEETFONT = '"Noto Sans Malayalam", "Permanent Marker", sans-serif';
function sheetBase(title, sub) {
  full('#D8D2C4');
  paint(rectPts(-50, 900, W + 100, 300), { wash: '#C4BDAE', ink: null });
  inkLine([[40, 900], [1180, 900]], .8, CP.ink, 'inkfine', 0);
  letter(title, 60, 70, 64, CP.ink, { screen: true, ink: false, align: 'left', font: `64px ${SHEETFONT}` });
  letter(sub, 62, 130, 28, '#4A4450', { screen: true, ink: false, align: 'left', font: `28px ${SHEETFONT}` });
}
const label = (t, x, y, s = 24) => letter(t, x, y, s, '#4A4450', { screen: true, ink: false, font: `${s}px ${SHEETFONT}` });
function swatches(cols, x = 1260, y = 960) {
  cols.forEach(([c, n], i) => { paint(rectPts(x + i * 110, y - 40, 80, 60), { wash: c, ink: CP.ink, sw: .5 }); label(n, x + i * 110 + 40, y + 45, 16); });
}
function sheetFor(name, title, sub, u, exprs, cols, extra = {}) {
  return t => {
    sheetBase(title, sub);
    const views = [['front', false, 'മുന്നിൽ'], ['q', true, '3/4'], ['q', false, '3/4'], ['back', false, 'പിന്നിൽ']];
    views.forEach(([v, f, l], i) => { person(name, 170 + i * 270, 900, u, { view: v, flip: f, expr: extra.expr || 'neutral', key: 'v' + i, glitch: name === 'neha' ? .25 : 0, nehaEyes: extra.nehaEyes, hands: extra.hands }); label(l, 170 + i * 270, 950); });
    exprs.forEach(([e, l, o = {}], i) => {
      const x = 1340 + (i % 2) * 300, y = 300 + Math.floor(i / 2) * 330;
      paint(rrPts(x - 140, y - 140, 280, 300, 20), { wash: '#E6E0D3', ink: CP.ink, sw: .5 });
      if (name === 'keeper') { clockFace(x, y + 10, 95, { sw: .8, glow: 0, ...o }); }
      else bust(name, x, y, 62, { expr: e, key: 'e' + i, glitch: 0, ...o });
      paint(rectPts(x - 142, y + 115, 284, 50), { wash: '#E6E0D3', ink: null });
      label(l, x, y + 140, 22);
    });
    swatches(cols);
  };
}
LOOPS.sheet_01_meera = sheetFor('meera', 'മീര ജോസഫ് · MEERA (16)', 'നായിക · ഉറക്കമില്ലാത്തവൾ, എല്ലാം എണ്ണുന്നവൾ · അപ്പന്റെ വെള്ളി വാച്ച് · ഉയരം 16u', 26,
  [['tired', 'ക്ഷീണം'], ['terror', 'ഭയം'], ['cry', 'കരച്ചിൽ'], ['determined', 'ദൃഢനിശ്ചയം']],
  [[CP.maroon, 'ഹൂഡി'], [CP.denim, 'ജീൻസ്'], [CP.skin, 'തൊലി'], [CP.hair, 'മുടി'], [CP.silver, 'വാച്ച്']], { expr: 'tired' });
LOOPS.sheet_02_arjun = sheetFor('arjun', 'അർജുൻ നായർ · ARJUN (16)', 'ഉറ്റ സുഹൃത്ത് · യൂട്യൂബർ ആകാൻ കൊതിക്കുന്നവൻ · മഞ്ഞ = സുരക്ഷ, ജീവൻ · ഉയരം 17.5u', 24,
  [['smile', 'തമാശ'], ['neutral', 'സംശയം', { look: [-.7, 0] }], ['terror', 'പേടി'], ['calm', 'ത്യാഗം', { skin: CP.brass }]],
  [[CP.yellow, 'ജാക്കറ്റ്'], [CP.vest, 'വെസ്റ്റ്'], [CP.khaki, 'പാന്റ്'], ['#A87256', 'തൊലി']], { expr: 'smile' });
LOOPS.sheet_03_ammachi = sheetFor('ammachi', 'അമ്മച്ചി · റോസ (72) · AMMACHI', 'മീരയുടെ അമ്മൂമ്മ · 1986-ൽ രക്ഷപ്പെട്ടവൾ · നിന്നുപോയ പോക്കറ്റ് വാച്ച് · ഉയരം 14.2u', 28,
  [['calm', 'സ്നേഹം'], ['angryLow', 'തണുപ്പ്'], ['cry', 'കുറ്റബോധം', { view: 'q' }], ['sleep', 'ചക്രത്തിൽ', { skin: '#A89470', noWatch: true }]],
  [[CP.saree, 'സാരി'], [CP.sareeDk, 'പല്ലു'], ['#BDB8B1', 'മുടി'], [CP.brass, 'വാച്ച്'], ['#9C6C52', 'തൊലി']], { expr: 'calm' });
LOOPS.sheet_04_neha = sheetFor('neha', 'നേഹ · NEHA (എന്നും 15)', 'പ്രേതബാലിക · 1986-ലെ യൂണിഫോം · കണ്ണുകൾ നിഴലിൽ · മുടിയിൽ നിന്ന് വെള്ളം · VHS ഗ്ലിച്ച്', 27,
  [['neutral', 'നിഴൽ കണ്ണുകൾ'], ['neutral', 'മുന്നറിയിപ്പ്', { view: 'q', flip: true }], ['smile', 'സ്വതന്ത്ര (എപ്പി. 10)', { nehaEyes: true }], ['neutral', 'ഗ്ലിച്ച്', { glitch: 1 }]],
  [[CP.pinafore, 'പിനഫോർ'], [CP.shirt, 'ഷർട്ട്'], [CP.nehaSkin, 'തൊലി'], ['#2A2C33', 'മുടി'], ['#A9C6D8', 'വെള്ളം']]);
LOOPS.sheet_05_keeper = sheetFor('keeper', 'കാവൽക്കാരൻ · THE KEEPER', 'ഏലിയാസ് വർക്കി · 7 അടിയിലധികം · ക്ലോക്ക്-തല, താക്കോൽ-വിരലുകൾ · ഒരിക്കലും ഓടില്ല · ഉയരം 27u', 15,
  [['', 'സൂചികളില്ല'], ['', 'അടുത്ത ഇര', { hands: [Math.PI * .75, Math.PI * .75] }], ['', 'മീരയുടെ മുഖം', { face: { expr: 'terror' } }], ['', 'ഏലിയാസ് (എപ്പി. 10)', { face: { expr: 'calm', skin: '#A87A5E' } }]],
  [[CP.coat, 'കോട്ട്'], [CP.cream, 'ക്ലോക്ക്'], [CP.brass, 'പിച്ചള'], [CP.sick, 'പച്ച വെളിച്ചം']]);
LOOPS.sheet_06_cast = t => {
  sheetBase('കഥാപാത്രങ്ങൾ · THE CAST', 'ഉയരങ്ങളുടെ താരതമ്യം · height comparison');
  inkLine([[40, 900], [1880, 900]], .8, CP.ink, 'inkfine', 0);
  for (let i = 0; i <= 28; i += 4) { inkLine([[60, 900 - i * 26], [1860, 900 - i * 26]], .3, '#A8A194', 'inkfine', 0); }
  const cast = [['meera', 'മീര', {}], ['arjun', 'അർജുൻ', { expr: 'smile' }], ['ammachi', 'അമ്മച്ചി', { expr: 'calm' }], ['neha', 'നേഹ', { glitch: .3 }], ['elias', 'ഏലിയാസ് (1946)', { expr: 'calm' }], ['keeper', 'കാവൽക്കാരൻ', {}], ['boy', 'കുട്ടി (സീസൺ 2)', {}]];
  cast.forEach(([n, l, o], i) => { person(n, 170 + i * 260, 900, 26, { ...o, key: 'c' + i }); label(l, 170 + i * 260, 950, 26); });
};
for (const k of Object.keys(LOOPS)) if (k.startsWith('sheet_')) LOOPS[k].len = 1;
