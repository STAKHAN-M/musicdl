from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

from musicdl.runner import RunResult, run_capture

ContentType = Literal["track", "playlist", "album"]
Quality = Literal["best", "320", "192", "128"]


def _template(dest: Path, content_type: ContentType) -> str:
    if content_type == "playlist":
        return str(
            dest / "{list-name}" / "{list-position} - {artist} - {title}.{output-ext}"
        )
    return str(
        dest / "{artist}" / "{album}" / "{track-number} - {title}.{output-ext}"
    )


def download(
    url: str,
    content_type: ContentType,
    dest: Path,
    quality: Quality = "best",
) -> RunResult:
    dest.mkdir(parents=True, exist_ok=True)
    template = _template(dest, content_type)
    bitrate = "auto" if quality == "best" else f"{quality}k"
    cmd: list[str] = [
        sys.executable,
        "-m",
        "spotdl",
        "download",
        url,
        "--output",
        template,
        "--format",
        "mp3",
        "--bitrate",
        bitrate,
    ]
    return run_capture(cmd)
