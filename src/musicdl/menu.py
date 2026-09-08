from __future__ import annotations

import subprocess
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from musicdl import config, deps, history, m3u
from musicdl.backends import soundcloud, spotify, youtube
from musicdl.runner import RunResult, aggregate

console = Console()

BANNER = r"""[bold cyan]
███╗   ███╗██╗   ██╗███████╗██╗ ██████╗██████╗ ██╗
████╗ ████║██║   ██║██╔════╝██║██╔════╝██╔══██╗██║
██╔████╔██║██║   ██║███████╗██║██║     ██║  ██║██║
██║╚██╔╝██║██║   ██║╚════██║██║██║     ██║  ██║██║
██║ ╚═╝ ██║╚██████╔╝███████║██║╚██████╗██████╔╝███████╗
╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝╚═════╝ ╚══════╝
[/bold cyan][dim]  YouTube / YouTube Music / Spotify / SoundCloud downloader[/dim]
"""


def _banner(dest: Path) -> None:
    console.clear()
    console.print(BANNER)
    console.print(
        Panel.fit(
            f"[bold]Dossier de destination[/bold] : [green]{dest}[/green]",
            border_style="cyan",
        )
    )
    warn = config.storage_warning()
    if warn:
        console.print(Panel.fit(f"[yellow]{warn}[/yellow]", border_style="yellow"))
    if not deps.FFMPEG.available:
        console.print(f"[yellow]! {deps.FFMPEG.label} manquant : {deps.FFMPEG.hint}[/yellow]")
    if not deps.js_runtime_ok():
        console.print(f"[yellow]! {deps.js_runtime_hint()}[/yellow]")
    console.print()


def _fmt_source(idx: int, dep: "deps.Dependency") -> str:
    if dep.available:
        return f"  [bold cyan]{idx}.[/bold cyan] {dep.label}"
    return (
        f"  [dim]{idx}. {dep.label}  [red][indisponible][/red][/dim]"
    )


def main_menu() -> None:
    while True:
        dest = config.get_download_folder()
        _banner(dest)
        console.print("  [bold cyan]1.[/bold cyan] Mise a jour des paquets")
        console.print(_fmt_source(2, deps.YOUTUBE))
        console.print(_fmt_source(3, deps.SPOTIFY))
        console.print(_fmt_source(4, deps.SOUNDCLOUD))
        console.print("  [bold cyan]5.[/bold cyan] Changer le dossier de destination")
        console.print("  [bold cyan]0.[/bold cyan] Quitter\n")
        choice = Prompt.ask(
            "[bold]Choix[/bold]", choices=["0", "1", "2", "3", "4", "5"], default="0"
        )

        if choice == "0":
            console.print("\n[dim]Bye.[/dim]")
            return
        if choice == "1":
            _update_packages()
        elif choice == "2":
            if _guard(deps.YOUTUBE):
                _youtube_flow(dest)
        elif choice == "3":
            if _guard(deps.SPOTIFY):
                _spotify_flow(dest)
        elif choice == "4":
            if _guard(deps.SOUNDCLOUD):
                _soundcloud_flow(dest)
        elif choice == "5":
            config.prompt_download_folder()


def _guard(dep: "deps.Dependency") -> bool:
    if dep.available:
        return True
    console.print(f"\n[red]{dep.label} indisponible.[/red]")
    if dep.hint:
        console.print(f"[dim]{dep.hint}[/dim]")
    _pause()
    return False


def _update_packages() -> None:
    console.print("\n[bold]Mise a jour de yt-dlp, spotdl, scdl...[/bold]\n")
    cmd = [
        "uv",
        "sync",
        "--upgrade-package",
        "yt-dlp",
        "--upgrade-package",
        "spotdl",
        "--upgrade-package",
        "scdl",
    ]
    try:
        rc = subprocess.run(cmd).returncode
    except FileNotFoundError:
        console.print(
            "[red]`uv` introuvable dans le PATH. Lance l'outil via `uv run musicdl`.[/red]"
        )
        _pause()
        return
    if rc == 0:
        console.print("\n[green]Paquets a jour.[/green]")
    else:
        console.print(f"\n[red]Echec (code {rc}).[/red]")
    _pause()


# -----------------------------------------------------------------------------
# Sous-menus generiques
# -----------------------------------------------------------------------------

def _content_type() -> str | None:
    console.print("\n[bold]Type de contenu ?[/bold]")
    console.print("  [bold cyan]1.[/bold cyan] Titre unique")
    console.print("  [bold cyan]2.[/bold cyan] Playlist")
    console.print("  [bold cyan]3.[/bold cyan] Album")
    console.print("  [bold cyan]0.[/bold cyan] Retour\n")
    choice = Prompt.ask(
        "[bold]Choix[/bold]", choices=["0", "1", "2", "3"], default="0"
    )
    return {"0": None, "1": "track", "2": "playlist", "3": "album"}[choice]


def _youtube_format() -> str | None:
    console.print("\n[bold]Format ?[/bold]")
    console.print("  [bold cyan]1.[/bold cyan] MP3 (audio seul)")
    console.print("  [bold cyan]2.[/bold cyan] MP4 (video)")
    console.print("  [bold cyan]0.[/bold cyan] Retour\n")
    choice = Prompt.ask("[bold]Choix[/bold]", choices=["0", "1", "2"], default="1")
    return {"0": None, "1": "mp3", "2": "mp4"}[choice]


def _audio_quality() -> str | None:
    console.print("\n[bold]Qualite audio ?[/bold]")
    console.print("  [bold cyan]1.[/bold cyan] Meilleure disponible (defaut)")
    console.print("  [bold cyan]2.[/bold cyan] 320 kbps")
    console.print("  [bold cyan]3.[/bold cyan] 192 kbps")
    console.print("  [bold cyan]4.[/bold cyan] 128 kbps")
    console.print("  [bold cyan]0.[/bold cyan] Retour\n")
    choice = Prompt.ask(
        "[bold]Choix[/bold]", choices=["0", "1", "2", "3", "4"], default="1"
    )
    return {"0": None, "1": "best", "2": "320", "3": "192", "4": "128"}[choice]


def _ask_urls(label: str) -> list[str] | None:
    """Retourne 1 URL, plusieurs URLs collees, ou le contenu d'un fichier .txt."""
    console.print("\n[bold]Source des URLs ?[/bold]")
    console.print("  [bold cyan]1.[/bold cyan] Une seule URL")
    console.print("  [bold cyan]2.[/bold cyan] Plusieurs URLs (coller, ligne vide pour valider)")
    console.print("  [bold cyan]3.[/bold cyan] Fichier .txt (une URL par ligne)")
    console.print("  [bold cyan]0.[/bold cyan] Retour\n")
    mode = Prompt.ask(
        "[bold]Choix[/bold]", choices=["0", "1", "2", "3"], default="1"
    )
    if mode == "0":
        return None
    if mode == "1":
        url = Prompt.ask(f"\n[bold]URL {label}[/bold]").strip()
        return [url] if url else None
    if mode == "2":
        console.print(
            f"\n[bold]URLs {label}[/bold] (colle-les, une par ligne, [dim]ligne vide pour lancer[/dim])"
        )
        urls: list[str] = []
        while True:
            try:
                line = input().strip()
            except EOFError:
                break
            if not line:
                break
            urls.append(line)
        if not urls:
            console.print("[yellow]Aucune URL saisie.[/yellow]")
            return None
        return urls
    # mode 3 : fichier
    path_str = Prompt.ask("\n[bold]Chemin du fichier .txt[/bold]").strip().strip('"')
    if not path_str:
        return None
    p = Path(path_str).expanduser()
    if not p.exists():
        console.print(f"[red]Fichier introuvable : {p}[/red]")
        return None
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        console.print(f"[red]Lecture impossible : {e}[/red]")
        return None
    urls = [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]
    if not urls:
        console.print("[yellow]Le fichier ne contient aucune URL.[/yellow]")
        return None
    console.print(f"[green]{len(urls)} URL(s) chargee(s) depuis {p}[/green]")
    return urls


# -----------------------------------------------------------------------------
# Flows par source
# -----------------------------------------------------------------------------

def _youtube_flow(dest: Path) -> None:
    ct = _content_type()
    if ct is None:
        return
    fmt = _youtube_format()
    if fmt is None:
        return
    quality: str | None = "best"
    if fmt == "mp3":
        quality = _audio_quality()
        if quality is None:
            return
    while True:
        urls = _ask_urls("YouTube")
        if urls is None:
            return
        start_ts = time.time()
        results: list[tuple[str, RunResult]] = []
        for i, url in enumerate(urls, 1):
            if len(urls) > 1:
                console.rule(f"[cyan]{i}/{len(urls)}  {url}[/cyan]")
            res = youtube.download(url, ct, fmt, dest, quality)  # type: ignore[arg-type]
            history.log_run("youtube", ct, fmt, url, res)
            results.append((url, res))
        m3u_files = _maybe_write_m3u(ct, dest, start_ts)
        _batch_report("youtube", results, m3u_files)
        if not _another_url():
            return


def _spotify_flow(dest: Path) -> None:
    ct = _content_type()
    if ct is None:
        return
    quality = _audio_quality()
    if quality is None:
        return
    while True:
        urls = _ask_urls("Spotify")
        if urls is None:
            return
        start_ts = time.time()
        results: list[tuple[str, RunResult]] = []
        for i, url in enumerate(urls, 1):
            if len(urls) > 1:
                console.rule(f"[cyan]{i}/{len(urls)}  {url}[/cyan]")
            res = spotify.download(url, ct, dest, quality)  # type: ignore[arg-type]
            history.log_run("spotify", ct, quality, url, res)
            results.append((url, res))
        m3u_files = _maybe_write_m3u(ct, dest, start_ts)
        _batch_report("spotify", results, m3u_files)
        if not _another_url():
            return


def _soundcloud_flow(dest: Path) -> None:
    ct = _content_type()
    if ct is None:
        return
    while True:
        urls = _ask_urls("SoundCloud")
        if urls is None:
            return
        start_ts = time.time()
        results: list[tuple[str, RunResult]] = []
        for i, url in enumerate(urls, 1):
            if len(urls) > 1:
                console.rule(f"[cyan]{i}/{len(urls)}  {url}[/cyan]")
            res = soundcloud.download(url, ct, dest)  # type: ignore[arg-type]
            history.log_run("soundcloud", ct, None, url, res)
            results.append((url, res))
        m3u_files = _maybe_write_m3u(ct, dest, start_ts)
        _batch_report("soundcloud", results, m3u_files)
        if not _another_url():
            return


def _maybe_write_m3u(content_type: str, dest: Path, start_ts: float) -> list[Path]:
    if content_type != "playlist":
        return []
    return m3u.write_playlist_m3u(dest, start_ts)


# -----------------------------------------------------------------------------
# Recap
# -----------------------------------------------------------------------------

def _batch_report(
    source: str,
    results: list[tuple[str, RunResult]],
    m3u_files: list[Path] | None = None,
) -> None:
    agg = aggregate([r for _, r in results])
    ok_color = "green" if agg.ok_count > 0 else "dim"
    skip_color = "yellow" if agg.skip_count > 0 else "dim"
    err_color = "red" if agg.err_count > 0 else "dim"
    status = "[green]OK[/green]" if agg.rc == 0 else f"[red]Echec (code {agg.rc})[/red]"
    retry_note = " [magenta](retry 403)[/magenta]" if agg.retried_403 else ""
    body = (
        f"{status}{retry_note}  [dim]|[/dim]  {len(results)} URL(s) traitee(s)\n"
        f"[{ok_color}]{agg.ok_count} telecharge(s)[/{ok_color}]  "
        f"[{skip_color}]{agg.skip_count} skip(s)[/{skip_color}]  "
        f"[{err_color}]{agg.err_count} erreur(s)[/{err_color}]"
    )
    if len(results) > 1:
        body += "\n\n[bold]Detail par URL :[/bold]"
        for url, res in results:
            marker = "[green]OK[/green]" if res.rc == 0 else "[red]KO[/red]"
            body += (
                f"\n  {marker}  ok={res.ok_count} skip={res.skip_count} "
                f"err={res.err_count}  [dim]{url}[/dim]"
            )
    if m3u_files:
        body += f"\n\n[bold cyan].m3u ecrit(s) ({len(m3u_files)}) :[/bold cyan]"
        for m in m3u_files:
            body += f"\n  [dim]{m}[/dim]"
    console.print(Panel.fit(body, title=f"Recap {source}", border_style="cyan"))
    console.print(f"[dim]Historique : {history.HISTORY_FILE}[/dim]")


def _another_url() -> bool:
    console.print("\n[bold]Et maintenant ?[/bold]")
    console.print("  [bold cyan]1.[/bold cyan] Telecharger d'autres URLs")
    console.print("  [bold cyan]0.[/bold cyan] Retour au menu principal\n")
    choice = Prompt.ask("[bold]Choix[/bold]", choices=["0", "1"], default="0")
    return choice == "1"


def _pause() -> None:
    Prompt.ask("\n[dim]Entree pour revenir au menu[/dim]", default="")
