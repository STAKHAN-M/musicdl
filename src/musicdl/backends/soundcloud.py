from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

from musicdl.runner import RunResult, run_capture

ContentType = Literal["track", "playlist", "album"]


def download(url: str, content_type: ContentType, dest: Path) -> RunResult:
    dest.mkdir(parents=True, exist_ok=True)
    cmd: list[str] = [
        sys.executable,
        "-m",
        "scdl",
        "-l",
        url,
        "--path",
        str(dest),
        "--addtofile",
        "--original-art",
    ]
    if content_type == "playlist":
        cmd += ["--playlist-name-format", "{playlist[title]}"]
    return run_capture(cmd)
