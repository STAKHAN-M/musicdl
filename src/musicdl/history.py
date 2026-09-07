from __future__ import annotations

from datetime import datetime
from pathlib import Path

from musicdl.config import CONFIG_DIR
from musicdl.runner import RunResult

HISTORY_FILE = CONFIG_DIR / "history.log"


def log_run(source: str, content_type: str, fmt: str | None, url: str, result: RunResult) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fmt_str = fmt or "-"
    retried = " retry_403" if result.retried_403 else ""
    line = (
        f"{ts} | {source:10s} | {content_type:8s} | {fmt_str:3s} | "
        f"rc={result.rc} | ok={result.ok_count} skip={result.skip_count} err={result.err_count}"
        f"{retried} | {url}\n"
    )
    with HISTORY_FILE.open("a", encoding="utf-8") as f:
        f.write(line)
