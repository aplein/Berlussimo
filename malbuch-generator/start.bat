@echo off
REM Malbuch-Generator – Start unter Windows
REM Nutzt gezielt Python 3.10 (py -3.10), weil Fooocus & Co. darauf ausgelegt
REM sind. So entstehen keine kaputten Pakete (z. B. Pillow) durch neuere
REM Python-Versionen wie 3.14.
REM Doppelklick genuegt. Beim ersten Start wird alles eingerichtet.

cd /d "%~dp0"

REM --- Python 3.10 vorhanden? ---
py -3.10 --version >nul 2>nul
if errorlevel 1 (
    echo.
    echo [Fehler] Python 3.10 wurde nicht gefunden.
    echo Bitte Python 3.10 installieren von:
    echo   https://www.python.org/downloads/release/python-31011/
    echo Beim Setup "Add python.exe to PATH" anhaken, danach erneut starten.
    echo.
    pause
    exit /b 1
)

REM --- Virtuelle Umgebung MIT Python 3.10 anlegen (falls noch nicht da) ---
if not exist ".venv\Scripts\python.exe" (
    echo Erstelle virtuelle Umgebung mit Python 3.10 ...
    py -3.10 -m venv .venv
)

set "VENVPY=.venv\Scripts\python.exe"

echo Installiere / pruefe Abhaengigkeiten ...
"%VENVPY%" -m pip install --quiet --upgrade pip
"%VENVPY%" -m pip install --quiet -r requirements.txt

echo.
echo ============================================================
echo  Malbuch-Generator laeuft auf:  http://127.0.0.1:5010
echo  (Fenster offen lassen. Zum Beenden: Strg+C)
echo ============================================================
echo.

REM Browser nach kurzer Wartezeit oeffnen
start "" /b cmd /c "timeout /t 2 >nul & start http://127.0.0.1:5010"

"%VENVPY%" app.py

pause
