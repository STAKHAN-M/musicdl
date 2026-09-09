# musicdl installer for Windows.
# Installs prerequisites (uv, ffmpeg, deno, git if needed) via winget,
# then runs uv sync. Designed for non-devs: run from the cloned repo dir.
#
# Usage from an elevated or normal PowerShell:
#   Set-ExecutionPolicy -Scope Process Bypass -Force
#   .\install.ps1

$ErrorActionPreference = "Stop"

function Test-Cmd($cmd) {
    return $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue)
}

function Install-Winget($id, $label) {
    Write-Host "-> Installation $label"
    winget install --id=$id -e `
        --accept-source-agreements --accept-package-agreements
}

# ---------------------------------------------------------------------------
# 0. Sanity : winget doit exister
# ---------------------------------------------------------------------------
if (-not (Test-Cmd winget)) {
    Write-Host "!! winget introuvable. Mets a jour Windows (Store -> App Installer)"
    Write-Host "   ou installe App Installer depuis le Microsoft Store."
    exit 1
}

Write-Host "==> Verification des prerequis..."
Write-Host ""

# ---------------------------------------------------------------------------
# 1. Prerequis systeme via winget
# ---------------------------------------------------------------------------
if (-not (Test-Cmd git)) {
    Install-Winget "Git.Git" "git"
} else {
    Write-Host "-> git deja installe"
}

if (-not (Test-Cmd uv)) {
    Install-Winget "astral-sh.uv" "uv"
} else {
    Write-Host "-> uv deja installe"
}

if (-not (Test-Cmd ffmpeg)) {
    Install-Winget "Gyan.FFmpeg" "ffmpeg"
} else {
    Write-Host "-> ffmpeg deja installe"
}

if (-not (Test-Cmd deno) -and -not (Test-Cmd node)) {
    Install-Winget "DenoLand.Deno" "deno"
} else {
    Write-Host "-> runtime JS deja disponible"
}

Write-Host ""

# ---------------------------------------------------------------------------
# 2. Refresh PATH pour ce processus (winget ajoute au PATH utilisateur,
#    mais ce shell garde son ancien PATH tant qu'il n'est pas relance)
# ---------------------------------------------------------------------------
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [Environment]::GetEnvironmentVariable("Path", "User")

if (-not (Test-Cmd uv)) {
    Write-Host "!! uv installe mais pas encore dans le PATH."
    Write-Host "   Ferme cette fenetre PowerShell, ouvres-en une nouvelle,"
    Write-Host "   puis relance : .\install.ps1"
    exit 1
}

# ---------------------------------------------------------------------------
# 3. Sync du projet
# ---------------------------------------------------------------------------
Write-Host "==> uv sync --extra spotify"
uv sync --extra spotify

Write-Host ""
Write-Host "OK. Lance : uv run musicdl"
Write-Host ""
Write-Host "Astuce : si ffmpeg ou deno viennent d'etre installes, ouvre un"
Write-Host "NOUVEAU terminal PowerShell avant le premier lancement pour que"
Write-Host "le PATH soit rafraichi."
