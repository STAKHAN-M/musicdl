from __future__ import annotations

from pathlib import Path

# Extensions audio et video reconnues pour l'inclusion dans un .m3u.
_AUDIO_EXTS = {".mp3", ".m4a", ".opus", ".flac", ".ogg", ".aac", ".wav"}
_VIDEO_EXTS = {".mp4", ".webm", ".mkv"}
_MEDIA_EXTS = _AUDIO_EXTS | _VIDEO_EXTS


def write_playlist_m3u(dest: Path, since_ts: float) -> list[Path]:
    """
    Ecrit un fichier .m3u dans chaque sous-dossier direct de `dest` qui a ete
    modifie depuis `since_ts`. Le .m3u liste, en ordre alphabetique (ce qui
    respecte le zero-padding des templates), tous les fichiers media presents.
    Retourne la liste des .m3u ecrits.
    """
    written: list[Path] = []
    if not dest.exists():
        return written

    for sub in sorted(dest.iterdir()):
        if not sub.is_dir():
            continue
        try:
            if sub.stat().st_mtime < since_ts:
                continue
        except OSError:
            continue

        media = sorted(
            p
            for p in sub.iterdir()
            if p.is_file() and p.suffix.lower() in _MEDIA_EXTS
        )
        if not media:
            continue

        m3u_path = sub / f"{sub.name}.m3u"
        content = "#EXTM3U\n" + "\n".join(p.name for p in media) + "\n"
        try:
            m3u_path.write_text(content, encoding="utf-8")
        except OSError:
            continue
        written.append(m3u_path)

    return written
