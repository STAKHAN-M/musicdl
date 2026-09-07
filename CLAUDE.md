# CLAUDE.md

Fichier d'instructions pour Claude Code. Décrit le projet, les conventions
et les pièges connus. À lire en début de session.

---

## Objectif du projet

Construire un **mini-outil de téléchargement de musique** (CLI d'abord, éventuellement
une petite UI web ensuite) qui :

1. Télécharge des titres / albums / playlists depuis **YouTube, YouTube Music,
   SoundCloud et Spotify**.
2. Les range dans une **arborescence propre** `Artiste/Album/N° - Titre.mp3`.
3. Génère les fichiers `.m3u` pour les playlists.
4. **Évite les doublons** de façon fiable.
5. Alimente à terme une bibliothèque **Navidrome** (serveur de streaming
   auto-hébergé, objectif final : remplacer Spotify/SoundCloud par un NAS perso).

L'outil est un **wrapper** au-dessus de `yt-dlp`, `scdl` et `spotdl` — il n'implémente
pas le téléchargement lui-même, il orchestre ces outils avec les bonnes options,
gère l'arborescence, la déduplication et les erreurs récurrentes.

---

## Contexte / historique

Ce projet fait suite à une phase manuelle où les commandes étaient lancées à la main
dans PowerShell. L'objectif est maintenant d'**automatiser et fiabiliser** ce workflow
dans un vrai petit logiciel (portable, réutilisable, versionné sur GitHub).

État actuel : téléchargements manuels fonctionnels, bibliothèque en cours de
constitution dans `C:\Users\rmore\Musique\`. NAS + Navidrome pas encore déployés
(prévus dans le homelab). L'outil doit donc fonctionner en local pour l'instant,
tout en préparant la bascule NAS.

---

## Environnement

- **OS** : Windows, shell **PowerShell**
- **Python** : 3.10 actuellement — **à migrer vers 3.11+** (yt-dlp déprécie 3.10,
  certaines futures versions ne s'installeront plus). Le faire tôt dans le projet.
- **Dépendances système obligatoires** :
  - `ffmpeg` (conversion audio) — `winget install ffmpeg`
  - `deno` (runtime JS requis par YouTube anti-bot) — `irm https://deno.land/install.ps1 | iex`
- **Paquets Python** : `yt-dlp`, `scdl`, `spotdl` (via pip)

Installer / mettre à jour :
```powershell
pip install -U yt-dlp scdl spotdl --break-system-packages
```

---

## Rôle de chaque outil

| Source | Outil | Mécanique |
|---|---|---|
| YouTube / YT Music | `yt-dlp` | Télécharge directement le flux |
| SoundCloud | `scdl` | Télécharge directement le flux |
| Spotify | `spotdl` | Lit les métadonnées Spotify, télécharge l'audio via YouTube (utilise yt-dlp en interne) |
| Deezer | `deemix` | Contourne le DRM — **hors périmètre**, ne pas intégrer par défaut |

Ordre de préférence des sources : **yt-dlp / scdl** en premier (flux direct, meilleure
qualité, moins de risque) → **spotdl** en repli pour ce qui est introuvable ailleurs.

---

## Conventions à respecter absolument

### Arborescence de sortie (identique pour TOUS les outils)
```
Musique/
└── Artiste/
    └── Album/
        └── 01 - Titre.mp3
```

Templates équivalents selon l'outil :
- **yt-dlp** : `Musique\%(artist)s\%(album)s\%(track_number)s - %(title)s.%(ext)s`
- **spotdl** : `Musique\{artist}\{album}\{track-number} - {title}.{output-ext}`

Correspondance des champs :

| spotdl | yt-dlp | Rôle |
|---|---|---|
| `{artist}` | `%(artist)s` | Artiste |
| `{album}` | `%(album)s` | Album |
| `{track-number}` | `%(track_number)s` | N° de piste (album) |
| — | `%(playlist_index)s` | Position dans une playlist perso |
| `{title}` | `%(title)s` | Titre |

- Album officiel → `track_number`. Playlist perso → `playlist_index`.
- Utiliser des valeurs de repli yt-dlp pour éviter les dossiers `NA` :
  `%(album|Divers)s`, `%(track_number|0)s`.
- Un lien YouTube Music `OLAK5uy_...` = album officiel "Art Track" (bonnes métadonnées).

### Déduplication (règle d'or)
- **Toujours le même template `--output`/`-o`**, quelle que soit la source.
  yt-dlp et spotdl skippent un fichier déjà présent au **chemin exact**.
- Le doublon vient d'un template différent pour la même chanson → deux fichiers
  physiques distincts. À éviter par construction.
- yt-dlp : `--download-archive archive.txt` pour ne pas retélécharger les IDs déjà pris.
- Dédup a posteriori possible via `beets` + plugin `duplicates`.

### Playlists / .m3u
- spotdl `--m3u` **n'accepte pas** de template `{list-name}` : donner un nom fixe.
- Navidrome importe les `.m3u` au scan et recrée la playlist. Une fois importée
  et modifiée dans l'appli (Symfonium), ne PAS réécraser le `.m3u` avec spotdl.

---

## Options standard des commandes sous-jacentes

**yt-dlp (base commune)** :
```
-x --audio-format mp3 --audio-quality 0 --embed-thumbnail --add-metadata
```
(`--audio-quality 0` = meilleure qualité ; échelle inversée 0=max, 10=min. La qualité
reste plafonnée par la source YouTube ~128-160kbps.)

**scdl** : `--addtofile --original-art` (et `-f` pour les likes d'un profil).

---

## Pièges connus & fixes (IMPORTANT)

### 403 Forbidden sur yt-dlp
Récurrent : YouTube change ses protections, yt-dlp doit être re-patché. Symptôme :
miniature/titre OK mais flux audio en `HTTP Error 403`. Souvent le client
`android vr player` est bloqué. Fix, dans l'ordre :
1. `pip install -U yt-dlp --break-system-packages`
2. Si insuffisant, **nightly via pip** (le `yt-dlp --update-to nightly` NE marche PAS
   en install pip) : `pip install -U --pre "yt-dlp[default]" --break-system-packages`
3. Forcer un autre client :
   `--extractor-args "youtube:player_client=default,web,mweb"`

### Erreurs spotdl
- `AudioProviderError: YT-DLP download error` → yt-dlp interne obsolète →
  `pip install -U spotdl yt-dlp --break-system-packages`
- `Could not get client token` → souci token Spotify, souvent transitoire →
  relancer ; si persistant : `spotdl --generate-config`
- `LookupError: No results found` → aucun match YouTube → fallback manuel yt-dlp
  sur une URL trouvée à la main.

### Autres
- `ffprobe and ffmpeg not found` → ffmpeg absent.
- `No supported JavaScript runtime` → deno absent.

L'outil devrait **détecter et gérer ces erreurs proprement** (retry, message clair,
suggestion de fix) plutôt que de crasher.

---

## Design attendu de l'outil

Suggestions (à challenger, pas figées) :
- **CLI** en Python. Une commande unique qui prend une URL (ou un fichier de liste
  d'URLs) et détecte automatiquement la source (YouTube / YT Music / SoundCloud / Spotify)
  pour router vers le bon outil.
- Config centralisée (dossier de sortie, template, options) dans un fichier
  (`config.toml` ou `.env`) plutôt qu'en dur.
- Couche d'abstraction : une interface commune `download(url, dest)` avec une
  implémentation par backend (yt-dlp / scdl / spotdl).
- Gestion des erreurs récurrentes centralisée (retry + mise à jour auto + fallback client).
- Génération `.m3u` pour les playlists.
- Logs lisibles (succès / skip / échec par titre, résumé en fin de run).

Extension possible plus tard (déjà envisagée) : petite **UI web / PWA** + backend
FastAPI pour déclencher un téléchargement depuis le téléphone vers le NAS, puis
trigger d'un scan Navidrome (`/api/scan`). Sécurisé derrière WireGuard. **Phase 2**,
ne pas commencer par là.

---

## Roadmap suggérée

1. **Phase 0** : migrer Python 3.11+, scaffolder le projet (structure, config, deps).
2. **Phase 1** : CLI de base — une URL → bon backend → arborescence correcte.
3. **Phase 2** : gestion robuste des erreurs (403, retry, fallback), dédup, `.m3u`.
4. **Phase 3** : traitement par lot (fichier de liste d'URLs, plusieurs playlists).
5. **Phase 4 (option)** : backend FastAPI + UI web + intégration Navidrome/NAS.

---

## Préférences de code

- Python idiomatique, typé (type hints), testable.
- Pas de secrets en dur (token Spotify, chemins) → config / variables d'env.
- Code versionné proprement (ce projet a vocation à figurer sur le portfolio GitHub).
- Messages et logs en français, code/commentaires techniques en anglais.

---

## Rappel légal

Usage strictement personnel. yt-dlp/scdl sur contenu librement accessible = zone
tolérée mais contraire aux CGU des plateformes. spotdl = zone grise (contourne le
modèle Spotify via YouTube). deemix (contournement DRM) = hors périmètre du projet.
