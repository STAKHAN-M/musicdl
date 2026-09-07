from __future__ import annotations

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".musicdl"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def get_download_folder() -> Path:
    cfg = load_config()
    folder = cfg.get("download_folder")
    if folder:
        p = Path(folder).expanduser()
        if p.exists():
            return p
    return prompt_download_folder()


def prompt_download_folder() -> Path:
    from rich.console import Console
    from rich.prompt import Prompt

    console = Console()
    default = str(Path.home() / "Musique")
    while True:
        raw = Prompt.ask(
            "[bold cyan]Dossier de destination[/bold cyan]", default=default
        )
        p = Path(raw).expanduser()
        try:
            p.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            console.print(f"[red]Impossible de creer ce dossier : {e}[/red]")
            continue
        cfg = load_config()
        cfg["download_folder"] = str(p)
        save_config(cfg)
        console.print(f"[green]OK, sauvegarde dans {CONFIG_FILE}[/green]\n")
        return p
