"""Detection des dependances optionnelles, evaluee au lancement."""

from __future__ import annotations

import importlib.util
import shutil
from dataclasses import dataclass


@dataclass(frozen=True)
class Dependency:
    label: str
    module: str | None = None      # dependance Python
    binary: str | None = None      # outil systeme
    hint: str = ""                 # affiche si absent

    @property
    def available(self) -> bool:
        if self.module and importlib.util.find_spec(self.module) is None:
            return False
        if self.binary and shutil.which(self.binary) is None:
            return False
        return True


YOUTUBE = Dependency("YouTube / YouTube Music", module="yt_dlp")
SPOTIFY = Dependency(
    "Spotify",
    module="spotdl",
    hint='installer avec : pip install "musicdl[spotify]" '
         "(indisponible sur Termux, voir README)",
)
SOUNDCLOUD = Dependency("SoundCloud", module="scdl")

FFMPEG = Dependency(
    "ffmpeg",
    binary="ffmpeg",
    hint="requis pour la conversion audio - pkg install ffmpeg / apt install ffmpeg / winget install Gyan.FFmpeg",
)


def js_runtime_ok() -> bool:
    """deno OU node suffit pour yt-dlp anti-bot."""
    return shutil.which("deno") is not None or shutil.which("node") is not None


def js_runtime_hint() -> str:
    return (
        "aucun runtime JS trouve (deno ou node) - "
        "requis par yt-dlp pour l'anti-bot YouTube. "
        "PC: installer deno. Termux: pkg install nodejs."
    )
