@echo off
REM ============================================================
REM  KI-Malbuch-Generator  -  Start-All
REM
REM  Diese Datei gehoert eine Ebene UEBER die App, also nach:
REM      C:\KI-Malbuch-Generator\start-all.bat
REM
REM  Erwartete Ordnerstruktur:
REM      C:\KI-Malbuch-Generator\
REM         |-- Fooocus-API\        (REST-Dienst, Port 8888)
REM         |-- malbuch-generator\  (diese App,   Port 5010)
REM         \-- start-all.bat       (diese Datei)
REM
REM  Liegen die Ordner woanders, einfach die Pfade unten anpassen.
REM ============================================================

title KI-Malbuch-Generator

REM --- Pfade (bei Bedarf auf absolute Pfade aendern) ---
set "ROOT=%~dp0"
set "FOOOCUS_API_DIR=%ROOT%Fooocus-API"
set "APP_DIR=%ROOT%malbuch-generator"

echo ============================================================
echo  KI-Malbuch-Generator wird gestartet ...
echo ============================================================
echo.

REM --- 1) Fooocus-API (REST, Port 8888) in eigenem Fenster ---
if exist "%FOOOCUS_API_DIR%\main.py" (
    echo [1/2] Starte Fooocus-API  ^(Port 8888^) ...
    start "Fooocus-API" /D "%FOOOCUS_API_DIR%" cmd /k "if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) & python main.py"
) else (
    echo [Hinweis] Fooocus-API wurde hier nicht gefunden:
    echo           "%FOOOCUS_API_DIR%"
    echo           Ohne Fooocus-API koennen keine Bilder erzeugt werden.
    echo           Einrichtung siehe malbuch-generator\README.md
    echo.
)

REM --- Fooocus-API einen Vorsprung geben (laedt Modelle) ---
echo       Warte kurz, bis Fooocus-API hochfaehrt ...
timeout /t 8 >nul

REM --- 2) Malbuch-App (Port 5010) in eigenem Fenster ---
if exist "%APP_DIR%\start.bat" (
    echo [2/2] Starte Malbuch-Generator  ^(Port 5010^) ...
    start "Malbuch-Generator" /D "%APP_DIR%" cmd /k "start.bat"
) else (
    echo [Fehler] malbuch-generator\start.bat nicht gefunden unter:
    echo          "%APP_DIR%"
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Es wurden zwei Fenster geoeffnet:
echo    - Fooocus-API        (laedt beim ersten Mal die Modelle)
echo    - Malbuch-Generator  -> http://127.0.0.1:5010
echo.
echo  Tipp: In der App oben rechts wird es gruen "Fooocus verbunden",
echo  sobald Fooocus-API fertig geladen hat (kann 1-2 Min dauern).
echo.
echo  Dieses Fenster kann jetzt geschlossen werden.
echo ============================================================
timeout /t 10 >nul
