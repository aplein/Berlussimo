@echo off
REM ============================================================
REM  KI-Malbuch-Generator - Start-All
REM
REM  Diese Datei gehoert in den Malbuch-Ordner, also z. B.:
REM      C:\Fooocus\KI-Malbuch-Generator\start-all.bat
REM
REM  Erwartete Struktur:
REM      C:\Fooocus\KI-Malbuch-Generator\           (App: app.py, start.bat, .venv)
REM      C:\Fooocus\KI-Malbuch-Generator\Fooocus-API\ (REST-Dienst: main.py, venv)
REM
REM  Ein Doppelklick startet Fooocus-API (Port 8888) UND die
REM  Malbuch-App (Port 5010) in je einem eigenen Fenster.
REM ============================================================

title KI-Malbuch-Generator

set "ROOT=%~dp0"
set "FOOOCUS_API_DIR=%ROOT%Fooocus-API"

echo ============================================================
echo  KI-Malbuch-Generator wird gestartet ...
echo ============================================================
echo.

REM --- 1) Fooocus-API (Port 8888) in eigenem Fenster ---
if exist "%FOOOCUS_API_DIR%\main.py" (
    echo [1/2] Starte Fooocus-API  ^(Port 8888^) ...
    start "Fooocus-API" /D "%FOOOCUS_API_DIR%" cmd /k ".\venv\Scripts\python.exe main.py"
) else (
    echo [Hinweis] Fooocus-API nicht gefunden unter:
    echo           %FOOOCUS_API_DIR%
    echo           Ohne Fooocus-API koennen keine Bilder erzeugt werden.
    echo.
)

REM --- Fooocus-API einen Vorsprung geben (laedt beim 1. Mal das Modell) ---
echo       Warte, bis Fooocus-API hochfaehrt ...
timeout /t 8 >nul

REM --- 2) Malbuch-App (Port 5010) in eigenem Fenster ---
if exist "%ROOT%start.bat" (
    echo [2/2] Starte Malbuch-Generator  ^(Port 5010^) ...
    start "Malbuch-Generator" /D "%ROOT%" cmd /k "start.bat"
) else if exist "%ROOT%app.py" (
    echo [2/2] Starte Malbuch-Generator  ^(Port 5010^) ...
    start "Malbuch-Generator" /D "%ROOT%" cmd /k ".venv\Scripts\python.exe app.py"
) else if exist "%ROOT%malbuch-generator\start.bat" (
    echo [2/2] Starte Malbuch-Generator  ^(Port 5010^) ...
    start "Malbuch-Generator" /D "%ROOT%malbuch-generator" cmd /k "start.bat"
) else (
    echo [Fehler] Weder start.bat noch app.py in "%ROOT%" gefunden.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Zwei Fenster wurden geoeffnet:
echo    - Fooocus-API        ^(laedt beim 1. Start das Modell, 1-2 Min^)
echo    - Malbuch-Generator  -^> http://127.0.0.1:5010
echo.
echo  In der App wird es oben rechts gruen, sobald Fooocus-API
echo  fertig geladen hat. Dieses Fenster kann geschlossen werden.
echo ============================================================
timeout /t 10 >nul
