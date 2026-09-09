"""Genere une capture SVG du menu principal via Rich."""

from __future__ import annotations

import io
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

BANNER = r"""[bold cyan]
███╗   ███╗██╗   ██╗███████╗██╗ ██████╗██████╗ ██╗
████╗ ████║██║   ██║██╔════╝██║██╔════╝██╔══██╗██║
██╔████╔██║██║   ██║███████╗██║██║     ██║  ██║██║
██║╚██╔╝██║██║   ██║╚════██║██║██║     ██║  ██║██║
██║ ╚═╝ ██║╚██████╔╝███████║██║╚██████╗██████╔╝███████╗
╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝╚═════╝ ╚══════╝
[/bold cyan][dim]  YouTube / YouTube Music / Spotify / SoundCloud downloader[/dim]
"""


def main() -> None:
    # StringIO evite l'erreur d'encodage cp1252 sur console Windows legacy.
    console = Console(
        record=True,
        width=88,
        force_terminal=True,
        color_system="truecolor",
        file=io.StringIO(),
    )
    console.print(BANNER)
    console.print(
        Panel.fit(
            "[bold]Dossier de destination[/bold] : [green]~/Music[/green]",
            border_style="cyan",
        )
    )
    console.print()
    console.print("  [bold cyan]1.[/bold cyan] Mise a jour des paquets")
    console.print("  [bold cyan]2.[/bold cyan] YouTube / YouTube Music")
    console.print("  [bold cyan]3.[/bold cyan] Spotify")
    console.print("  [bold cyan]4.[/bold cyan] SoundCloud")
    console.print("  [bold cyan]5.[/bold cyan] Changer le dossier de destination")
    console.print("  [bold cyan]0.[/bold cyan] Quitter")
    console.print()
    console.print("[bold]Choix[/bold] [magenta]\\[0/1/2/3/4/5][/magenta] [cyan](0)[/cyan]: [white]2[/white]")
    console.print()
    console.print("[bold]Type de contenu ?[/bold]")
    console.print("  [bold cyan]1.[/bold cyan] Titre unique")
    console.print("  [bold cyan]2.[/bold cyan] Playlist")
    console.print("  [bold cyan]3.[/bold cyan] Album")
    console.print("  [bold cyan]0.[/bold cyan] Retour")

    out = Path(__file__).parent / "musicdl-menu.svg"
    console.save_svg(str(out), title="musicdl")
    print(f"OK: {out}")


if __name__ == "__main__":
    main()
