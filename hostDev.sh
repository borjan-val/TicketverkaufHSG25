#!/bin/bash
# Port definieren
PORT=8191  # Passe den Port an, den du überprüfen möchtest
# Prozesse beenden, die den Port verwenden
echo "Suche Prozesse auf Port $PORT..."
lsof -ti tcp:$PORT | xargs -r kill -9
echo "Alle Prozesse auf Port $PORT wurden beendet."

# Verzeichnis des aktuellen Skripts ermitteln
SCRIPT_DIR=$(dirname "$(realpath "$0")")
echo "Wechsle in das Verzeichnis: $SCRIPT_DIR"
cd "$SCRIPT_DIR"

# Virtuelle Umgebung aktivieren
if [ -f venv/bin/activate ]; then
    echo "Aktiviere die virtuelle Umgebung..."
    source venv/bin/activate
else
    echo "Virtuelle Umgebung nicht gefunden!"
    exit 1
fi
echo "Starte Python-Anwendung..."
python3 app.py