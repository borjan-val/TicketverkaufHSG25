Ticketverkauf-System Schulparty HSG 2025

Before first run:

		cd /path/to/Ticketverkauf
		
create a virtual environment:

		python3 -m venv venv_Ticketverkauf
activate it
		source /venv/bin/activate
install required modules
		pip install -r Requirements.txt
		
To start the production server run HostDeploySP.sh or

	PORT=8191
	SCRIPT_DIR=$(dirname "$(realpath "$0")")
	echo "Wechsle in das Verzeichnis: $SCRIPT_DIR"
	cd "$SCRIPT_DIR"
	source venv/bin/activate
	gunicorn -w 11 -b 0.0.0.0:$PORT app:app  --access-logfile - --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

might want to adjust GUnicorn workers to machine.
For testing and development use testhost.sh 



