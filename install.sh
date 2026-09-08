#!/usr/bin/env bash
set -euo pipefail

if [ -n "${PREFIX:-}" ] && [[ "$PREFIX" == *com.termux* ]]; then
    echo "-> Termux detecte : installation allegee (sans Spotify)"
    pkg install -y python ffmpeg nodejs git
    python -m venv .venv
    . .venv/bin/activate
    pip install -e .
    echo
    echo "Termine. Lance : musicdl"
    echo "Pense a executer termux-setup-storage si ce n'est pas deja fait."
    exit 0
fi

if command -v uv >/dev/null 2>&1; then
    echo "-> uv detecte : installation complete"
    uv sync --extra spotify
    echo "Termine. Lance : uv run musicdl"
else
    echo "-> uv absent : venv + pip"
    python3 -m venv .venv
    . .venv/bin/activate
    pip install -e ".[spotify]"
    echo "Termine. Lance : musicdl"
fi

command -v ffmpeg >/dev/null || echo "! ffmpeg manquant - a installer"
command -v deno >/dev/null || command -v node >/dev/null || \
    echo "! aucun runtime JS (deno/node) - yt-dlp peut echouer sur certaines videos"
