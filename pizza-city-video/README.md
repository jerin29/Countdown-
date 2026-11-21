# Pizza City Express – Weingarten · animated song video

88.7 s, 1920×1080, 30 fps, German song with on-screen lyrics.

- `assets/song.mp3` – the song (generated with vidIQ music, royalty-free)
- `index.html` – root: five scenes, lyrics overlay, song
- `scene-src/*.html` – editable scene sources; run `python3 build_scenes.py` to rebuild `compositions/` (it inserts the shared scooter drawing)
- `compositions/lyrics.html` – lyric lines and their timings
- Render: `npx hyperframes render -o renders/pizza-city-express.mp4`

Scenes: kitchen (intro + verse 1) → oven & box (chorus) → scooter ride past the Basilika and through the Altstadt (verse 2) → doorbell (bridge) → family + end card (final chorus).
