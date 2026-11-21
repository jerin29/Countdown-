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

> The MP4s are **not stored in git** (63–95 MB each). They were sent to you in the chat; rebuild them any time with the commands below.

## Use it
- Post it as a teaser or a "motion comic" episode, or
- use it as the **timing reference for animation**: replace each panel with animated shots and keep the cut, because the audio is already locked.

## Rebuild
```bash
cd animation-base && node render_boards.mjs --w=1920 --h=1080 --out=out/panels_hd   # 1080p panels (not stored in git)
python3 horror-series/video/tools/make_animatic.py            # all episodes   (or: make_animatic.py 3 for one)
```
Camera moves and effects per panel are in the `DIRECT` table at the top of `tools/make_animatic.py`.

## Instagram Reels / Shorts teasers (9:16, ~30 s)
`tools/make_teasers.py` cuts a hook-first vertical teaser from each episode into `teasers/` (not in git):
- **0–4 s:** the episode's scariest moment, with a big Malayalam hook line.
- **Middle:** the key beats, with the best dialogue and the chimes.
- **End:** the cracking countdown number, the lullaby hum and a "next chime tomorrow · Follow" prompt.

They're 1080×1920, with burned-in Malayalam subtitles, the series title, loudness at −14 LUFS, and a cover image each.
To re-cut one, edit its `CUTS` (start/end seconds in the 1:30 episode) or its `HOOK` line, then run `python3 tools/make_teasers.py 3`.

## Series promo (9:16, 76 s)
`tools/make_promo.py` builds a single trailer in `promo/` (not in git), set to the Malayalam theme song "പത്തു മണിയൊച്ച" (intro, both verses and the whispered bridge):
- full-screen vertical shots from all 10 episodes, each reframed by hand on its subject;
- short Malayalam story lines on screen;
- bell-hit flashes;
- the title card with "10 എപ്പിസോഡുകൾ · ഉടൻ വരുന്നു".

To change the shots, their timings or the lines, edit `SHOTS` / `LINES`.

## Hindi version with English subtitles (`hi/`)
`hi/COUNTDOWN_epNN_cinematic_hi.mp4`: all 10 episodes with Hindi dialogue, 1:30 each, 1080p. English subtitles are burned into the picture and also included as a track you can turn off. The `.srt` files are in `hi/subs/`. The videos themselves aren't stored in git.
- **Voices:** Hindi AI voices (vidIQ), with the same character effects as the Malayalam version. Sia: Meera and Neha. Bunty: Arjun. Raju: the Keeper and Elias. Zara: Ammachi, Mom and the Teacher.
- **Music:** the Hindi lullaby "दस घंटियाँ" (`audio/songs/ten-little-chimes-hi.mp3`) for the end-card hums. Score and effects are the same as the Malayalam version.
- **On-screen text:** in Hindi (the mirror writing, name plates, phone screens, the engraving), with English captions.
- **Rebuild:**
  ```bash
  COUNTDOWN_LANG=hi python3 audio/tools/process_voices.py hi
  COUNTDOWN_LANG=hi python3 audio/tools/mix_episodes.py
  cd animation-base && node render_boards.mjs --lang=hi --only=3,6,7,8 --w=1920 --h=1080 --out=out/panels_hd_hi
  COUNTDOWN_LANG=hi python3 horror-series/video/tools/make_animatic.py
  ```
  Copy `out/panels_hd` to `out/panels_hd_hi` before rendering the Hindi panels.
- Hindi dialogue is in `audio/voice_hi/lines.json` and the English subtitle text in `audio/voice_hi/subtitles_en.json`.
