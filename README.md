Ticketverkauf-System Schulparty HSG 2025

Before first run:

		cd /path/to/Ticketverkauf
		
create a virtual environment:

		python3 -m venv venv_Ticketverkauf
activate it
		source /venv/bin/activate
install required modules
		pip install -r Requirements.txt
		
To start the production server run HostDeploySP.sh, might want to adjust gunicorn workers.
For testing and development use testhost.sh 



