#!/bin/bash
# Port definieren
PORT=8191  
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
IP=$(ifconfig en0 | grep "inet " | awk '{print $2}')
GREEN="\033[0;32m"
RESET="\033[0m"
echo -e "${GREEN}Server wird gestartet. Erreichbar unter: http://$IP:$PORT${RESET}"
echo "Starte Python-Anwendung..."
gunicorn -w 11 -b 0.0.0.0:$PORT app:app  --access-logfile - --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
