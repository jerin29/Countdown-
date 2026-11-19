#!/usr/bin/env bash
# Reinstalls the video-editing toolchain in a fresh cloud session.
# Usage: bash scripts/setup-video-tools.sh
set -euo pipefail
export UV_TOOL_BIN_DIR=/usr/local/bin

# Video CLIs (HyperFrames, Remotion)
npm install -g hyperframes@latest @remotion/cli@latest

# Download/transcription tools (yt-dlp, OpenAI Whisper + faster-whisper)
uv tool install --upgrade "yt-dlp[default]"
uv tool install --upgrade openai-whisper --with faster-whisper

# onetake (Python deps; playwright pinned to match the preinstalled Chromium)
pip3 install --break-system-packages "playwright==1.63.0" numpy scipy Pillow matplotlib opencv-python-headless fonttools brotli

# Skills for HyperFrames, Remotion and onetake are committed in .claude/skills,
# so Claude Code loads them automatically from this repo.

ffmpeg -version | head -1; node --version; python3 --version
hyperframes --version; yt-dlp --version; whisper --help | head -1
