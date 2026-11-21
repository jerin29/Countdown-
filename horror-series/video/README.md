# COUNTDOWN — Cinematic animatics (Malayalam)

`COUNTDOWN_ep01_cinematic_ml.mp4` … `ep10`: one video per episode, each exactly **1:30**, 1080p, 24 fps, with the mixed Malayalam soundtrack.

This is a **cinematic animatic**: the storyboard panels from `../art/storyboard/` cut to the soundtrack at the script's timecodes, shot like a film.
- **Camera:** each panel has its own move: slow push-ins, pull-backs, drifts and rises. Stingers get a fast accelerating push with a shake.
- **Picture hits on the sound:** every tower-bell chime, impact and screech in the mix shakes the camera, and the loud ones flash the frame. They're timed from the mixer's cue sheets, so they land exactly on the audio.
- **Film look:** a 2:1 letterbox, a cold desaturated grade, vignette, grain and a slight gate flicker.
- **Per-scene effects:**
  - **VHS glitch** whenever Neha appears, and on the Episode 7 time skips.
  - **Phone footage** for all of Episode 5: low resolution, scanlines and glitches.
  - **Scratched old film** for the 1946/1986 flashbacks, which dissolve in from the present.
- **Transitions:** fade in from black, dips around the title and end cards, and a fade out at the end.
- **Subtitles:** Malayalam subtitles are a soft track inside each MP4; turn them on in your player. They're also in `subs/` as `.srt` files for YouTube or your editor.

## Use it
- Post it as a teaser or a "motion comic" episode, or
- use it as the **timing reference for animation**: replace each panel with animated shots and keep the cut, because the audio is already locked.

## Rebuild
```bash
cd animation-base && node render_boards.mjs --w=1920 --h=1080 --out=out/panels_hd   # 1080p panels (not stored in git)
python3 horror-series/video/tools/make_animatic.py            # all episodes   (or: make_animatic.py 3 for one)
```
Camera moves and effects per panel are in the `DIRECT` table at the top of `tools/make_animatic.py`.
