@echo off
REM Malbuch-Generator – Start unter Windows
REM Doppelklick genuegt. Beim ersten Start wird alles eingerichtet.

cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo [Fehler] Python wurde nicht gefunden.
    echo Bitte Python 3.10+ von https://www.python.org/downloads/ installieren
    echo und beim Setup "Add python.exe to PATH" anhaken.
    echo.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo Erstelle virtuelle Umgebung ...
    python -m venv .venv
)

call ".venv\Scripts\activate.bat"

echo Installiere / pruefe Abhaengigkeiten ...
python -m pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo.
echo ============================================================
echo  Malbuch-Generator laeuft auf:  http://127.0.0.1:5000
echo  (Fenster offen lassen. Zum Beenden: Strg+C)
echo ============================================================
echo.

REM Browser nach kurzer Wartezeit oeffnen
start "" /b cmd /c "timeout /t 2 >nul & start http://127.0.0.1:5000"

python app.py

pause
