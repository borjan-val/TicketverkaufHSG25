#!/bin/bash
pkill Python
cd /Users/can/Desktop/Ticketverkauf
source venv/bin/activate
IP=$(ifconfig en0 | grep "inet " | awk '{print $2}')
GREEN="\033[0;32m"
RESET="\033[0m"
echo -e "${GREEN}Server wird gestartet. Erreichbar unter: http://$IP:8191${RESET}"
gunicorn -w 11 -b 0.0.0.0:8191 app:app  --access-logfile - --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'