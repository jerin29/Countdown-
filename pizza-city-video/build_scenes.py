# Generates the scene files that share the scooter drawing. Edit here, then re-run: python3 build_scenes.py
SCOOT = '''
 <g class="{cls}-rider">
  <path d="M-20 -140 L 45 -115 L 45 -75" stroke="#2B4A8A" stroke-width="26" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M-45 -135 L -15 -265 L 45 -255 L 35 -135 Z" fill="#2E8B57" stroke="#2B1B17" stroke-width="6" stroke-linejoin="round"/>
  <path d="M20 -235 L 105 -238" stroke="#2E8B57" stroke-width="22" stroke-linecap="round"/>
  <circle cx="110" cy="-238" r="13" fill="#F2C9A0" stroke="#2B1B17" stroke-width="4"/>
  <circle cx="15" cy="-305" r="44" fill="#F2C9A0" stroke="#2B1B17" stroke-width="6"/>
  <path d="M-32 -308 A47 47 0 0 1 62 -308 L 66 -296 L -36 -296 Z" fill="#FFC93C" stroke="#2B1B17" stroke-width="6" stroke-linejoin="round"/>
  <circle cx="42" cy="-286" r="5" fill="#2B1B17"/>
  <path d="M30 -268 Q 44 -258 56 -270" stroke="#2B1B17" stroke-width="5" fill="none" stroke-linecap="round"/>
 </g>
 <rect x="-185" y="-245" width="130" height="110" rx="12" fill="#E63A2E" stroke="#2B1B17" stroke-width="6"/>
 <text x="-120" y="-178" text-anchor="middle" font-family="Archivo Black" font-size="36" fill="#FFF3DC">PCE</text>
 <path d="M-175 -55 Q-175 -140 -60 -140 L 45 -140 L 70 -55 Z" fill="#E63A2E" stroke="#2B1B17" stroke-width="6" stroke-linejoin="round"/>
 <path d="M40 -140 L 108 -240 L 126 -232 L 78 -55 Z" fill="#E63A2E" stroke="#2B1B17" stroke-width="6" stroke-linejoin="round"/>
 <rect x="92" y="-256" width="70" height="16" rx="8" fill="#2B1B17"/>
 <circle cx="138" cy="-205" r="17" fill="#FFE9A0" stroke="#2B1B17" stroke-width="5"/>
 <g class="{cls}-wheel" transform="translate(-115 -45)"><circle r="46" fill="#2B1B17"/><circle r="20" fill="#D9D9D9"/><rect x="-4" y="-40" width="8" height="80" fill="#8C8C8C"/></g>
 <g class="{cls}-wheel" transform="translate(120 -45)"><circle r="46" fill="#2B1B17"/><circle r="20" fill="#D9D9D9"/><rect x="-4" y="-40" width="8" height="80" fill="#8C8C8C"/></g>
'''
import pathlib
for f in pathlib.Path('scene-src').glob('*.html'):
    s = f.read_text()
    for cls in ['o','r','d','f']:
        s = s.replace('{{SCOOTER:%s}}' % cls, SCOOT.replace('{cls}', cls))
    pathlib.Path('compositions', f.name).write_text(s)
    print('built', f.name)
