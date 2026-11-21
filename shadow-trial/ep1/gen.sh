#!/bin/bash
# usage: gen.sh id still seconds prompt
cd /home/user/Countdown-/shadow-trial/ep1; export NODE_USE_ENV_PROXY=1
node /home/user/Countdown-/.claude/skills/hyperframes/scripts/plugin-cli.mjs media-use generate --type video --first-frame assets/stills/$2.png --prompt "$4" --seconds $3 --out assets/shots/$1.mp4 > logs/$1.log 2>&1
echo "$1 exit=$? $(grep -o '"credits": [0-9]*' logs/$1.log | tail -1) $(grep -oE '"(error|code|message)": "[^"]*' logs/$1.log | head -2 | tr '\n' ' ')"
