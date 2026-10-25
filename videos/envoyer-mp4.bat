@echo off
chcp 65001 >nul
REM Se placer dans le dossier où se trouve ce .bat (le dépôt git)
cd /d "%~dp0"

echo Dossier : %cd%
echo.

echo === 1/5 git pull ===
git pull
if errorlevel 1 goto erreur

echo.
echo === 2/5 git lfs track "*.mp4" ===
git lfs track "*.mp4"
if errorlevel 1 goto erreur

echo.
echo === 3/5 git add . ===
git add .
if errorlevel 1 goto erreur

echo.
echo === 4/5 git commit ===
git diff --cached --quiet
if errorlevel 1 (
    git commit -m "Track MP4"
    if errorlevel 1 goto erreur
) else (
    echo Rien de nouveau à enregistrer, on passe au push.
)

echo.
echo === 5/5 git push origin HEAD ===
git push origin HEAD
if errorlevel 1 goto erreur

echo.
echo Terminé sans erreur.
pause
exit /b 0

:erreur
echo.
echo [ERREUR] La dernière commande a échoué : le script s'arrête ici.
pause
exit /b 1
