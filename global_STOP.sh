#!/bin/bash
# Port definieren
PORT=8191  # Passe den Port an, den du überprüfen möchtest
# Prozesse beenden, die den Port verwenden
echo "Suche Prozesse auf Port $PORT..."
lsof -ti tcp:$PORT | xargs -r kill -9
echo "Alle Prozesse auf Port $PORT wurden beendet."