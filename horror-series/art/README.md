# COUNTDOWN — Characters & Storyboards

All the art here is **painted in code** with the hand-painted animation kit in `../../animation-base` (p5.js + p5.brush): flat 2D, ink outlines, paper grain.
Because the characters are code, **the same drawings can be animated** with that kit later. They have a jointed rig, poses and expressions.

## 📖 Start here: `storyboard/COUNTDOWN_storyboard_ml.pdf`
The full storyboard book: a cover, then 6 panels per page for all 10 episodes. Each panel is paired with its timecode and its line from the Malayalam script (what we see 🎬 and what we hear 🔊).
- `storyboard/pages/`: the same pages as JPEGs (easy on a phone).
- `storyboard/panels/`: every panel on its own (1280×720), named `eNN_pMM.jpg`. Use them for an animatic: drop them on the timeline at their timecodes over `../audio/episodes/` and you have a moving storyboard.

## 🎭 `characters/`: model sheets
| File | What |
|------|------|
| `01_meera.jpg` … `05_keeper.jpg` | Turnaround (front, 3/4 both ways, back) + 4 key expressions + colour palette |
| `06_cast.jpg` | Everyone side by side for height comparison |

## Re-draw or change something
The drawings live in `animation-base/src/countdown/`:
- `chars.js`: the cast. `COSTUME` has colours and proportions, `POSES` the body poses, `face()` the expressions.
- `sets.js`: the locations (bedroom, school, bathroom, veranda, terrace, market, clock shop, gear room, the back of the clock, and more).
- `boards.js`: one entry per storyboard panel, in script order.
- `sheets.js`: the model sheets.

```bash
cd animation-base && npm install
node render_boards.mjs --out=../horror-series/art/storyboard/panels      # all panels  (--only=3 for one episode)
node render_boards.mjs --sheets --out=../horror-series/art/characters    # model sheets
python3 ../horror-series/art/tools/build_storyboard.py                   # rebuild the book (PDF + pages)
```
Open `animation-base/countdown.html` in Chrome to look at the drawings live.

## Notes
- These are **storyboard-quality** drawings: clear staging, framing and acting for each shot, in the final colour palette. They are not finished animation frames.
- The only words in the art are things the script puts on screen: phone screens, brass name plates, the shop sign, the mirror's "എണ്ണരുത്", and the title and end cards.
