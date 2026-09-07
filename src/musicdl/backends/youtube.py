from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

from musicdl.runner import RunResult, has_403, run_capture

ContentType = Literal["track", "playlist", "album"]
Format = Literal["mp3", "mp4"]
Quality = Literal["best", "320", "192", "128"]

# Fallback clients YouTube pour contourner les erreurs 403 (voir CLAUDE.md).
_FALLBACK_EXTRACTOR_ARGS = "youtube:player_client=default,web,mweb"


def _template(dest: Path, content_type: ContentType) -> str:
    if content_type == "playlist":
        # Zero-pad l'index pour un tri naturel dans l'explorateur.
        return str(
            dest
            / "%(playlist|Playlist)s"
            / "%(playlist_index)03d - %(artist|Inconnu)s - %(title)s.%(ext)s"
        )
    return str(
        dest
        / "%(artist|Inconnu)s"
        / "%(album|Divers)s"
        / "%(track_number|0)02d - %(title)s.%(ext)s"
    )


def _base_cmd(
    url: str, content_type: ContentType, fmt: Format, dest: Path, quality: Quality
) -> list[str]:
    archive = dest / ".yt-dlp-archive.txt"
    output = _template(dest, content_type)

    cmd: list[str] = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--download-archive",
        str(archive),
        "-o",
        output,
        "--add-metadata",
        "--embed-thumbnail",
        "--ignore-errors",
    ]

    if fmt == "mp3":
        audio_q = "0" if quality == "best" else f"{quality}K"
        cmd += ["-x", "--audio-format", "mp3", "--audio-quality", audio_q]
    else:  # mp4
        cmd += ["-f", "bv*+ba/b", "--merge-output-format", "mp4"]

    if content_type == "track":
        cmd.append("--no-playlist")
    else:
        # album/playlist : force le mode playlist meme pour les URLs ambigues
        # (ex: youtube.com/watch?v=X&list=Y).
        cmd.append("--yes-playlist")

    cmd.append(url)
    return cmd


def download(
    url: str,
    content_type: ContentType,
    fmt: Format,
    dest: Path,
    quality: Quality = "best",
) -> RunResult:
    dest.mkdir(parents=True, exist_ok=True)
    cmd = _base_cmd(url, content_type, fmt, dest, quality)
    result = run_capture(cmd)

    # Retry auto en cas de 403 avec un client YouTube alternatif.
    if has_403(result):
        print(
            "\n[!] Erreur 403 detectee. Nouvelle tentative avec un client YouTube alternatif...\n",
            flush=True,
        )
        cmd_retry = _base_cmd(url, content_type, fmt, dest, quality)
        cmd_retry[3:3] = ["--extractor-args", _FALLBACK_EXTRACTOR_ARGS]
        result = run_capture(cmd_retry)
        result.retried_403 = True

    return result
