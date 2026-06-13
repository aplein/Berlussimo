@echo off
REM ============================================================
REM  KI-Malbuch-Generator  -  Installation (setup.bat)
REM
REM  Diese Datei gehoert nach:  C:\KI-Malbuch-Generator\setup.bat
REM  (eine Ebene ueber den Ordner "malbuch-generator")
REM
REM  Richtet automatisch ein:
REM    - Python 3.10           (falls noch nicht vorhanden)
REM    - Fooocus-API           (REST-Dienst, Port 8888)
REM    - PyTorch passend zur GPU (NVIDIA = CUDA, sonst CPU)
REM    - Malbuch-App           (Port 5010)
REM
REM  Danach genuegt zum Starten ein Doppelklick auf start-all.bat
REM ============================================================

title KI-Malbuch-Generator - Installation

set "ROOT=%~dp0"
set "FOOOCUS_API_DIR=%ROOT%Fooocus-API"
set "APP_DIR=%ROOT%malbuch-generator"
set "PYVER=3.10.11"
set "PYURL=https://www.python.org/ftp/python/%PYVER%/python-%PYVER%-amd64.exe"
set "FAPI_URL=https://github.com/mrhan1993/Fooocus-API/archive/refs/heads/main.zip"

echo ============================================================
echo   KI-Malbuch-Generator  -  Installation
echo ============================================================
echo.
echo   Es werden mehrere GB heruntergeladen (Python, PyTorch, ...).
echo   Bitte etwas Geduld und das Fenster offen lassen.
echo.
pause

REM ---------- 1) Python 3.10 sicherstellen ----------
echo.
echo [1/5] Pruefe Python 3.10 ...
py -3.10 --version >nul 2>nul
if errorlevel 1 (
    echo       Python 3.10 nicht gefunden - lade Installer ...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri '%PYURL%' -OutFile \"$env:TEMP\python310.exe\""
    if errorlevel 1 ( echo [Fehler] Python-Download fehlgeschlagen. & pause & exit /b 1 )
    echo       Installiere Python 3.10 ...
    "%TEMP%\python310.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    py -3.10 --version >nul 2>nul
    if errorlevel 1 (
        echo [Fehler] Python 3.10 wird noch nicht erkannt.
        echo          Bitte den PC neu starten und setup.bat erneut ausfuehren.
        pause & exit /b 1
    )
)
for /f "delims=" %%v in ('py -3.10 --version') do echo       OK: %%v

REM ---------- 2) Fooocus-API holen ----------
echo.
echo [2/5] Pruefe Fooocus-API ...
if not exist "%FOOOCUS_API_DIR%\main.py" (
    echo       Lade Fooocus-API herunter ...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri '%FAPI_URL%' -OutFile \"$env:TEMP\fapi.zip\""
    if errorlevel 1 ( echo [Fehler] Fooocus-API-Download fehlgeschlagen. & pause & exit /b 1 )
    echo       Entpacke ...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -Path \"$env:TEMP\fapi.zip\" -DestinationPath '%ROOT%' -Force"
    for /d %%d in ("%ROOT%Fooocus-API-*") do move "%%d" "%FOOOCUS_API_DIR%" >nul
)
if not exist "%FOOOCUS_API_DIR%\main.py" ( echo [Fehler] Fooocus-API konnte nicht eingerichtet werden. & pause & exit /b 1 )
echo       OK

REM ---------- 3) venv + Requirements fuer Fooocus-API ----------
echo.
echo [3/5] Richte Python-Umgebung fuer Fooocus-API ein ...
if not exist "%FOOOCUS_API_DIR%\venv\Scripts\python.exe" (
    py -3.10 -m venv "%FOOOCUS_API_DIR%\venv"
)
set "FAPY=%FOOOCUS_API_DIR%\venv\Scripts\python.exe"
"%FAPY%" -m pip install --upgrade pip wheel
echo       Installiere Abhaengigkeiten (mehrere GB) ...
"%FAPY%" -m pip install -r "%FOOOCUS_API_DIR%\requirements.txt"
if errorlevel 1 ( echo [Fehler] Installation der Fooocus-API-Abhaengigkeiten fehlgeschlagen. & pause & exit /b 1 )

REM ---------- 4) PyTorch passend zur GPU ----------
echo.
echo [4/5] Installiere PyTorch ...
nvidia-smi >nul 2>nul
if errorlevel 1 (
    echo       Keine NVIDIA-GPU erkannt.
    echo       PyTorch bleibt in der CPU-Version - das ist sehr langsam.
    echo       Fooocus-API muss dann mit  --always-cpu  gestartet werden.
) else (
    echo       NVIDIA-GPU erkannt - installiere CUDA-Version (cu121) ...
    "%FAPY%" -m pip uninstall -y torch torchvision
    "%FAPY%" -m pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cu121
    if errorlevel 1 ( echo [Fehler] CUDA-PyTorch-Installation fehlgeschlagen. & pause & exit /b 1 )
)
"%FAPY%" -c "import torch; print('       CUDA verfuegbar:', torch.cuda.is_available())"

REM ---------- 5) Malbuch-App vorbereiten ----------
echo.
echo [5/5] Richte Malbuch-App ein ...
if exist "%APP_DIR%\requirements.txt" (
    if not exist "%APP_DIR%\.venv\Scripts\python.exe" (
        py -3.10 -m venv "%APP_DIR%\.venv"
    )
    "%APP_DIR%\.venv\Scripts\python.exe" -m pip install --upgrade pip >nul
    "%APP_DIR%\.venv\Scripts\python.exe" -m pip install -r "%APP_DIR%\requirements.txt"
    echo       OK
) else (
    echo       [Hinweis] Ordner "malbuch-generator" nicht neben dieser Datei gefunden.
    echo                 Bitte das malbuch-generator-ZIP nach "%ROOT%" entpacken
    echo                 und setup.bat danach erneut ausfuehren.
)

echo.
echo ============================================================
echo   Fertig!
echo.
echo   Starten ab jetzt mit Doppelklick auf:  start-all.bat
echo   (Beim ERSTEN Start laedt Fooocus-API noch das Bildmodell,
echo    ca. 6 GB - das passiert nur einmal.)
echo ============================================================
echo.
pause
