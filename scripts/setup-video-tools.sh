#!/usr/bin/env bash
# Reinstalls the video-editing toolchain in a fresh cloud session.
# Usage: bash scripts/setup-video-tools.sh
set -euo pipefail
export UV_TOOL_BIN_DIR=/usr/local/bin

# ffmpeg 7+ (Lemo-Opuscar needs it; Ubuntu ships 6.1). The static build in the
# imageio-ffmpeg wheel on PyPI goes to /usr/local/bin, ahead of the system copy.
tmp=$(mktemp -d)
pip3 download -q --no-deps imageio-ffmpeg -d "$tmp"
python3 -m zipfile -e "$tmp"/imageio_ffmpeg-*.whl "$tmp/whl"
install -m 755 "$(find "$tmp/whl" -name 'ffmpeg-linux-*' -type f | head -1)" /usr/local/bin/ffmpeg
rm -rf "$tmp"

# Video CLIs (HyperFrames, Remotion)
npm install -g hyperframes@latest @remotion/cli@latest

# Download/transcription tools (yt-dlp, OpenAI Whisper + faster-whisper)
uv tool install --upgrade "yt-dlp[default]"
uv tool install --upgrade openai-whisper --with faster-whisper

# onetake (Python deps; playwright pinned to match the preinstalled Chromium)
pip3 install --break-system-packages "playwright==1.63.0" numpy scipy Pillow matplotlib opencv-python-headless fonttools brotli

# Lemo-Opuscar: the plugin is enabled in .claude/settings.json; this fetches its
# style library to ~/lemo-opuscar and installs its core packages.
LEMO_SETUP=$(find ~/.claude/plugins -path '*lemo-opuscar/scripts/setup.sh' 2>/dev/null | head -1)
if [ -n "$LEMO_SETUP" ]; then sh "$LEMO_SETUP" && sh "$LEMO_SETUP" deps; fi

# Skills for HyperFrames, Remotion and onetake are committed in .claude/skills,
# so Claude Code loads them automatically from this repo.

ffmpeg -version | head -1; node --version; python3 --version
hyperframes --version; yt-dlp --version; whisper --help | head -1
