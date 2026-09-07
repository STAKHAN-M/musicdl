# musicdl

CLI interactif qui orchestre `yt-dlp`, `spotdl` et `scdl` pour telecharger de
la musique depuis **YouTube / YouTube Music / Spotify / SoundCloud** dans une
arborescence propre `Artiste/Album/N° - Titre.mp3`, avec gestion de la
deduplication, retry automatique sur erreur 403, generation `.m3u` pour les
playlists et log historique des runs.

```
███╗   ███╗██╗   ██╗███████╗██╗ ██████╗██████╗ ██╗
████╗ ████║██║   ██║██╔════╝██║██╔════╝██╔══██╗██║
██╔████╔██║██║   ██║███████╗██║██║     ██║  ██║██║
██║╚██╔╝██║██║   ██║╚════██║██║██║     ██║  ██║██║
██║ ╚═╝ ██║╚██████╔╝███████║██║╚██████╗██████╔╝███████╗
╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝╚═════╝ ╚══════╝
```

## Fonctionnalites

- **Menu interactif** style `theHarvester` : selection de la source, du type de
  contenu (titre / playlist / album), du format (MP3 / MP4 sur YouTube), et de
  la qualite audio (best / 320 / 192 / 128 kbps).
- **Batch** : traiter une URL, plusieurs URLs collees, ou un fichier `.txt`.
- **Dossier de destination** memorise dans `~/.musicdl/config.json` (portable
  entre PC, telephone via Termux, NAS...).
- **Deduplication** via `--download-archive` yt-dlp (une seule copie par ID).
- **Retry automatique** sur erreur `HTTP 403` YouTube avec un client
  alternatif (`--extractor-args youtube:player_client=default,web,mweb`).
- **Generation `.m3u`** dans le dossier de chaque playlist telechargee, prete
  a etre importee dans Navidrome / Symfonium.
- **Recap agrege** apres chaque run (OK / skip / erreurs, detail par URL).
- **Historique** de chaque run dans `~/.musicdl/history.log`.

## Prerequis

- [uv](https://docs.astral.sh/uv/) — gestion Python + venv + deps
- **ffmpeg** — conversion audio : `winget install Gyan.FFmpeg`
- **deno** — runtime JS requis par yt-dlp anti-bot : `winget install DenoLand.Deno`

Python 3.12 est installe automatiquement par `uv` (declare dans `.python-version`),
sans toucher a votre Python systeme.

## Installation

```powershell
git clone https://github.com/STAKHAN-M/yt_music_dl.git
cd yt_music_dl
uv sync
```

## Utilisation

```powershell
uv run musicdl
```

Au premier lancement, l'outil demande le dossier de destination puis affiche
le menu principal :

```
MUSICDL
  1. Mise a jour des paquets (yt-dlp, spotdl, scdl)
  2. YouTube / YouTube Music
  3. Spotify
  4. SoundCloud
  5. Changer le dossier de destination
  0. Quitter
```

Chaque source enchaine ensuite :
`Type de contenu → [Format YT] → [Qualite audio] → Source des URLs → Telechargement → Recap`

## Arborescence de sortie

```
<dossier>/
├─ Artiste/
│   └─ Album/
│       ├─ 01 - Titre A.mp3
│       └─ 02 - Titre B.mp3
└─ Ma Playlist/
    ├─ 001 - Artiste - Titre.mp3
    ├─ 002 - Artiste - Titre.mp3
    └─ Ma Playlist.m3u
```

## Structure du projet

```
src/musicdl/
├─ __init__.py          # entree main()
├─ menu.py              # menus interactifs + banner
├─ config.py            # ~/.musicdl/config.json
├─ history.py           # ~/.musicdl/history.log
├─ runner.py            # subprocess streaming + parsing OK/skip/err + detection 403
├─ m3u.py               # generation .m3u post-download pour playlists
└─ backends/
    ├─ youtube.py       # wrapper yt-dlp (mp3/mp4, qualite, retry 403)
    ├─ spotify.py       # wrapper spotdl
    └─ soundcloud.py    # wrapper scdl
```

## Roadmap

Voir la section _Roadmap suggeree_ dans [CLAUDE.md](CLAUDE.md) :

- [x] Phase 0 : scaffold, migration Python 3.12+, deps.
- [x] Phase 1 : CLI interactif, routing par source.
- [x] Phase 2 : gestion 403, dedup, `.m3u`, batch, qualite audio.
- [ ] Phase 3 : traitement par lot avance (multi-playlists, resume interrompu).
- [ ] Phase 4 (optionnel) : backend FastAPI + UI web + integration Navidrome/NAS.

## Credits & licences des dependances

Ce projet **ne fait pas** le telechargement lui-meme : il orchestre trois
outils open source excellents.

| Outil | Licence | Auteurs / Projet |
|---|---|---|
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Unlicense (domaine public) | yt-dlp contributors (fork de youtube-dl) |
| [spotdl](https://github.com/spotDL/spotify-downloader) | MIT | spotDL contributors |
| [scdl](https://github.com/flyingrub/scdl) | GPL-2.0 | Nicolas Casajus (`flyingrub`) et contributeurs |
| [typer](https://github.com/tiangolo/typer) | MIT | Sebastian Ramirez (`tiangolo`) |
| [rich](https://github.com/Textualize/rich) | MIT | Will McGugan / Textualize |

**Note sur scdl (GPL-2.0)** : scdl est declare en dependance (installe par
`uv sync`) et invoque en sous-processus (`python -m scdl`). Il n'est ni
statiquement lie ni redistribue par ce projet, ce qui reste conforme a la
GPL-2.0 (agregation). Toute redistribution _bundlant_ scdl devrait respecter
la GPL.

Outils systeme utilises mais non embarques :

| Outil | Licence | Projet |
|---|---|---|
| [ffmpeg](https://ffmpeg.org/) | LGPL / GPL selon build | FFmpeg team |
| [deno](https://deno.land/) | MIT | Deno Land Inc. |

## Licence

Le code de **ce projet** est publie sous licence [MIT](LICENSE).
Voir la section _Credits & licences_ ci-dessus pour les licences des
dependances.

## Legal / usage

Outil a **usage strictement personnel**. L'utilisation de yt-dlp / spotdl /
scdl sur du contenu librement accessible releve d'une zone toleree mais
contraire aux CGU des plateformes. L'utilisateur est seul responsable du
respect des lois locales sur le droit d'auteur et des conditions
d'utilisation des services concernes.
