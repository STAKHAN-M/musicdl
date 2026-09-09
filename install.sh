#!/usr/bin/env bash
# musicdl installer - detects OS and installs prerequisites (uv, ffmpeg, JS
# runtime) before syncing the project. Designed for non-devs: run this from
# the cloned repo directory and it takes care of everything.
set -euo pipefail

# ---------------------------------------------------------------------------
# OS detection
# ---------------------------------------------------------------------------
detect_os() {
    if [ -n "${PREFIX:-}" ] && [[ "$PREFIX" == *com.termux* ]]; then
        echo "termux"; return
    fi
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"; return
    fi
    if [ -f /etc/arch-release ]; then
        echo "arch"; return
    fi
    if [ -f /etc/debian_version ]; then
        echo "debian"; return
    fi
    echo "linux-other"
}

have() { command -v "$1" >/dev/null 2>&1; }

OS=$(detect_os)
echo "==> OS detecte : $OS"
echo

# ---------------------------------------------------------------------------
# 1. Prerequis systeme
# ---------------------------------------------------------------------------

install_ffmpeg() {
    case "$OS" in
        termux)      pkg install -y ffmpeg ;;
        macos)       brew install ffmpeg ;;
        debian)      sudo apt-get update && sudo apt-get install -y ffmpeg ;;
        arch)        sudo pacman -S --noconfirm ffmpeg ;;
        *) echo "!! ffmpeg : installe-le manuellement pour ta distrib" ; return 1 ;;
    esac
}

install_js_runtime() {
    # Node sur Termux (deno non dispo), deno partout ailleurs
    case "$OS" in
        termux)      pkg install -y nodejs ;;
        macos)       brew install deno ;;
        debian)      curl -fsSL https://deno.land/install.sh | sh ;;
        arch)        sudo pacman -S --noconfirm deno ;;
        *) echo "!! deno/node : installe-le manuellement" ; return 1 ;;
    esac
}

install_uv() {
    case "$OS" in
        termux)      pkg install -y uv || pip install --user uv ;;
        macos)       brew install uv ;;
        arch)        sudo pacman -S --noconfirm uv ;;
        *)           curl -LsSf https://astral.sh/uv/install.sh | sh ;;
    esac
    # uv installe via curl atterrit dans ~/.local/bin ou ~/.cargo/bin
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
}

# git sur Termux (pas garanti pre-installe)
if [ "$OS" = "termux" ] && ! have git; then
    echo "-> git manquant, installation"
    pkg install -y git
fi

if ! have ffmpeg; then
    echo "-> ffmpeg manquant, installation"
    install_ffmpeg
else
    echo "-> ffmpeg deja installe"
fi

if ! have deno && ! have node; then
    echo "-> aucun runtime JS (deno/node), installation"
    install_js_runtime
else
    echo "-> runtime JS deja disponible"
fi

if ! have uv; then
    echo "-> uv manquant, installation"
    install_uv
    if ! have uv; then
        echo
        echo "!! uv installe mais pas encore dans le PATH de ce shell."
        echo "   Ouvre un NOUVEAU terminal et relance : ./install.sh"
        exit 1
    fi
else
    echo "-> uv deja installe"
fi

echo

# ---------------------------------------------------------------------------
# 2. Sync du projet
# ---------------------------------------------------------------------------

if [ "$OS" = "termux" ]; then
    # Voie pip pour eviter le mur pydantic-core sur Android (spotdl exclu)
    echo "==> Termux : installation allegee (sans Spotify)"
    if [ ! -d .venv ]; then
        python -m venv .venv
    fi
    . .venv/bin/activate
    pip install -e .
    echo
    echo "OK. Lance : musicdl"
    echo
    if [ ! -d "$HOME/storage" ]; then
        echo "!! Pense a lancer : termux-setup-storage"
        echo "   pour que tes fichiers soient visibles par les lecteurs de musique."
    fi
else
    echo "==> uv sync (avec Spotify)"
    uv sync --extra spotify
    echo
    echo "OK. Lance : uv run musicdl"
fi
