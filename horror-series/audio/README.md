# COUNTDOWN — Audio (Malayalam)

All audio for the 10 episodes. Drop these straight into your editor (CapCut, Premiere, DaVinci, etc.).

## 🎬 `episodes/`: ready-made soundtracks (start here)
`COUNTDOWN_ep01_soundtrack_ml.mp3` … `ep10`: each is exactly **1:30**, mixed to **−14 LUFS** (YouTube/Instagram level).
Dialogue, music and effects are placed at the timecodes in `../malayalam/02-scripts-ml.md`. **Animate to this track.**

Timing changes from the script:
- **Ep 4:** Ammachi's long story lines run back to back from 0:28 to 1:15 (the spoken lines are longer than the script's slots).
- **Ep 5:** the title card sits at 0:10, after Arjun's intro.

## 🎵 `songs/`: AI-generated, sung in Malayalam (vidIQ)
| File | Use |
|------|-----|
| `ten-little-chimes-ml.mp3` (1:42) | Theme song "പത്തു മണിയൊച്ച", for end credits and the finale |
| `wind-it-back-ml.mp3` (1:14) | Ending song "പിന്നോട്ട് ചുറ്റാം", for the Ep 10 credits |

## 🎼 `bgm/`: score (computed in code, `tools/make_bgm.py`)
| File | Cue |
|------|-----|
| `M01_main_theme_sting.mp3` | Title card (every episode) |
| `M02_dread_drone_loop.mp3` | Tension bed, loops |
| `M03_neha_theme.mp3`, `M03b_neha_theme_sad.mp3` | Neha / grief |
| `M04_keepers_approach.mp3` | The Keeper comes. Hard cut to silence at 0:17.8 |
| `M05_clockwork_room_loop.mp3` | The clock shop |
| `M06_sepia_memories.mp3` | 1946/1986 flashback |
| `M07_run_cue.mp3` | Chase |
| `M08_gear_room.mp3` | Inside the tower |
| `M09_final_confrontation.mp3` | Finale, including the rewind and the D-major resolution |
| `M10_resolution.mp3` | Morning after / credits |
| `endcards/endcard_hum_NN.wav` | One line of the theme song per episode, numbered by the countdown (10 = Ep 1) |

## 🔊 `sfx/`: 37 effects
The tower bell, ticks, walls of clocks, gears, Keeper footsteps, rocking chair, drips, heartbeat, violin screech, phone sounds, VHS glitches, night ambience, whisper chorus and more. Files ending in `_loop` loop cleanly. See `../malayalam/03-music-and-sound-ml.md` for which episode uses which.

## 🗣️ `voice/`: Malayalam dialogue (AI voices via vidIQ)
- `processed/`: final lines with character effects, named `eNN_character_NN.wav` (e.g. `e04_ammachi_02.wav`). Use these.
- `raw/`: the untouched voice files, so you can re-process them.
- `lines.json`: the exact text of every line.

| Character | Voice | Treatment |
|-----------|-------|-----------|
| Meera, Neha, reflection | Sunaina | Neha: ghost-radio band-limit, wobble, echo. Reflection / phone voice: slowed and pitched down |
| Arjun, Keeper, Elias | Abhilash | Keeper: three pitch layers in a stone-tower echo. Elias: lower and soft. Arjun Ep 5: phone mic |
| Ammachi, Mom, Teacher | Samitha | Ammachi: a little lower and slower. Mom/Teacher: heard from another room |

## Rebuild
```bash
python3 tools/process_voices.py   # raw voice -> processed
python3 tools/make_sfx.py         # effects
python3 tools/make_bgm.py         # score
python3 tools/make_endcards.py    # end-card hums from the theme song
python3 tools/mix_episodes.py     # 10 episode soundtracks (cue sheets are inside, edit them to re-time)
```
Needs `numpy scipy soundfile` and `ffmpeg`.

## Honest notes
- **Nobody has listened to this audio yet.** The AI listening check couldn't run here: its models download from a host this environment's network doesn't allow. Only loudness and peak levels were measured.
- **End-card hums:** these were cut from the theme song by detecting where the vocals start, in song order. Check that each one lands on the right line, and if one is off, change its start time in `tools/make_endcards.py` and re-run it and the mixer.
- **Malayalam pronunciation** in the AI voices and songs is the generators' own. Have a native speaker spot-check it before release.
- The score and effects are synthesized in code: royalty-free and original. The songs and voices were generated with your vidIQ account; check vidIQ's terms for commercial use.
