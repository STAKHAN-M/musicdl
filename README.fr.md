# musicdl

> 🇫🇷 Version française · [🇬🇧 English version](README.en.md)

CLI interactif qui orchestre `yt-dlp`, `spotdl` et `scdl` pour telecharger de
la musique depuis **YouTube / YouTube Music / Spotify / SoundCloud** dans une
arborescence propre `Artiste/Album/N° - Titre.mp3`, avec deduplication, retry
automatique sur erreur 403, generation `.m3u` pour les playlists et log
historique des runs.

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
- **Dossier de destination** memorise dans `~/.musicdl/config.json`, avec
  defaut adapte a la plateforme (Windows/macOS/Linux/Termux).
- **Deduplication** via `--download-archive` yt-dlp (une seule copie par ID).
- **Retry automatique** sur erreur `HTTP 403` YouTube avec un client
  alternatif (`--extractor-args youtube:player_client=default,web,mweb`).
- **Generation `.m3u`** dans le dossier de chaque playlist telechargee, prete
  a etre importee dans Navidrome / Symfonium.
- **Recap agrege** apres chaque run (OK / skip / erreurs, detail par URL).
- **Historique** de chaque run dans `~/.musicdl/history.log`.
- **Detection au demarrage** des dependances : les sources indisponibles sont
  affichees grisees plutot que de crasher au telechargement.

## Installation rapide

### Toutes plateformes (script auto)

```bash
git clone https://github.com/STAKHAN-M/musicdl.git
cd musicdl
./install.sh
```

Le script detecte automatiquement l'environnement (Termux / uv / pip) et
installe la bonne voie.

## Prerequis systeme

Trois outils systeme (installes une seule fois, en dehors du projet).

### Windows (PowerShell)

```powershell
winget install astral-sh.uv        # gestionnaire Python + deps
winget install Gyan.FFmpeg         # conversion audio
winget install DenoLand.Deno       # runtime JS anti-bot yt-dlp
```

### macOS (Homebrew)

```bash
brew install uv ffmpeg deno
```

### Linux (Debian/Ubuntu)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
sudo apt install ffmpeg
curl -fsSL https://deno.land/install.sh | sh
```

### Linux (Arch)

```bash
sudo pacman -S uv ffmpeg deno
```

### Android (Termux)

**Note** : Spotify n'est **pas disponible** sur Termux (spotdl depend de
pydantic-core, une extension Rust sans wheel Android). YouTube, YT Music et
SoundCloud fonctionnent normalement. Node.js remplace deno comme runtime JS.

```bash
pkg install git python ffmpeg nodejs uv
git clone https://github.com/STAKHAN-M/musicdl.git
cd musicdl
./install.sh
musicdl
```

Pour ecrire dans le stockage partage Android (accessible aux lecteurs de
musique), lance `termux-setup-storage` avant le premier lancement de musicdl :

```bash
termux-setup-storage
```

Le dossier propose par defaut sera alors `~/storage/music/`.

## Installation manuelle (sans install.sh)

### Voie uv (recommandee, PC)

```bash
git clone https://github.com/STAKHAN-M/musicdl.git
cd musicdl
uv sync --extra spotify     # ou juste `uv sync` sans Spotify
uv run musicdl
```

### Voie pip + venv classique

```bash
git clone https://github.com/STAKHAN-M/musicdl.git
cd musicdl
python3.12 -m venv .venv
source .venv/bin/activate       # ou .venv\Scripts\activate sur Windows
pip install -e ".[spotify]"     # ou pip install -e . sans Spotify
musicdl
```

## Utilisation

```bash
uv run musicdl
# ou, en venv classique active :
musicdl
```

Au premier lancement, l'outil demande le dossier de destination puis affiche
le menu :

```
MUSICDL
  1. Mise a jour des paquets
  2. YouTube / YouTube Music
  3. Spotify                       [indisponible]  <- si spotdl absent
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
├─ config.py            # ~/.musicdl/config.json + destination par plateforme
├─ history.py           # ~/.musicdl/history.log
├─ deps.py              # detection deps optionnelles au demarrage
├─ runner.py            # subprocess streaming + parsing OK/skip/err + detection 403
├─ m3u.py               # generation .m3u post-download pour playlists
└─ backends/
    ├─ youtube.py       # wrapper yt-dlp (mp3/mp4, qualite, retry 403)
    ├─ spotify.py       # wrapper spotdl (extra optionnel)
    └─ soundcloud.py    # wrapper scdl
```

## Extras optionnels

Spotify est desormais un extra optionnel (evite d'installer pydantic-core sur
les plateformes qui ne le supportent pas, notamment Android/Termux).

```bash
uv sync --extra spotify              # avec uv
pip install -e ".[spotify]"          # avec pip
```

Sans cet extra, l'entree "Spotify" du menu apparait grisee et refuse la
selection avec un message clair.

## Roadmap

- [x] Phase 0 : scaffold, deps, structure
- [x] Phase 1 : CLI interactif, routing par source
- [x] Phase 2 : gestion 403, dedup, `.m3u`, batch, qualite audio
- [x] Phase 3 : garde-fous dependances, install multi-plateforme, Termux
- [ ] Phase 4 : traitement par lot avance, resume interrompu
- [ ] Phase 5 (optionnel) : backend FastAPI + UI web + integration Navidrome/NAS

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
| [hatchling](https://github.com/pypa/hatch) | MIT | PyPA / Ofek Lev |

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
| [Node.js](https://nodejs.org/) | MIT | OpenJS Foundation |

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
