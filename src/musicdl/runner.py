from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass, field


@dataclass
class RunResult:
    rc: int
    lines: list[str] = field(default_factory=list)
    ok_count: int = 0
    skip_count: int = 0
    err_count: int = 0
    retried_403: bool = False


# Marqueurs de sortie yt-dlp / spotdl / scdl.
_OK_PATTERNS = (
    re.compile(r"^\[download\] Destination:"),          # yt-dlp: nouveau fichier
    re.compile(r"^\[ExtractAudio\] Destination:"),      # yt-dlp: extraction audio
    re.compile(r"^Downloaded \".+\": "),                 # spotdl
    re.compile(r"^Successfully downloaded", re.I),      # scdl
)
_SKIP_PATTERNS = (
    re.compile(r"has already been recorded in the archive"),  # yt-dlp --download-archive
    re.compile(r"has already been downloaded"),               # yt-dlp
    re.compile(r"Skipping \".+\":", re.I),                    # spotdl (deja present)
    re.compile(r"already exists", re.I),                      # scdl
)
_ERR_PATTERNS = (
    re.compile(r"^ERROR:", re.I),
    re.compile(r"HTTP Error \d+"),
)
_403_PATTERN = re.compile(r"HTTP Error 403|Forbidden", re.I)


def run_capture(cmd: list[str]) -> RunResult:
    """Execute cmd en streamant stdout+stderr vers le terminal ET en capturant les lignes."""
    print(f"\n> {' '.join(cmd)}\n", flush=True)
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    lines: list[str] = []
    assert proc.stdout is not None
    for raw in proc.stdout:
        line = raw.rstrip("\n")
        sys.stdout.write(raw)
        sys.stdout.flush()
        lines.append(line)
    rc = proc.wait()
    result = RunResult(rc=rc, lines=lines)
    _tally(result)
    return result


def _tally(result: RunResult) -> None:
    for line in result.lines:
        if any(p.search(line) for p in _OK_PATTERNS):
            result.ok_count += 1
        elif any(p.search(line) for p in _SKIP_PATTERNS):
            result.skip_count += 1
        elif any(p.search(line) for p in _ERR_PATTERNS):
            result.err_count += 1


def has_403(result: RunResult) -> bool:
    return any(_403_PATTERN.search(line) for line in result.lines)


def aggregate(results: list[RunResult]) -> RunResult:
    """Fusionne plusieurs RunResult en un seul (pour affichage du recap batch)."""
    agg = RunResult(rc=0)
    for r in results:
        agg.ok_count += r.ok_count
        agg.skip_count += r.skip_count
        agg.err_count += r.err_count
        if r.retried_403:
            agg.retried_403 = True
        if r.rc != 0:
            agg.rc = r.rc
    return agg
