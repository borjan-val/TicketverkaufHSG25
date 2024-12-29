> # THIS PROJECT IS INCOMPLETE AND HAS BEEN ABANDONED

# Ticket Sale System for HSG School Party 2025

This project is a web-based system for managing ticket sales for the HSG school party in 2025. It allows administrators to create events, manage tickets, and track sales, while attendees can conveniently purchase tickets online.

## Project Overview

The system provides an intuitive user interface for ticket sales and management. It is based on the Flask web framework and utilizes an SQLite database for data storage. Its key features include:

- Creating and managing events  
- Online ticket sales (local)  
- Participant data management  
- Generating sales reports  

### Useful Features

This system simplifies the ticket sale process for events, reduces administrative effort, and provides attendees with a convenient way to purchase tickets online.  

While designed for school parties, it can be repurposed for other events as it primarily facilitates in-person ticket sales.

---

## Getting Started

### Prerequisites

- Python 3.x  
- Virtualenv  
- SQLite  

---

## Installation

1. Clone the repository:

	```bash
	git clone https://github.com/your-username/Ticketverkauf.git
	cd Ticketverkauf
	```

2. Create a virtual environment:

	```bash
	python3 -m venv venv_Ticketverkauf
	```

3. Activate the virtual environment:

	- On Unix/MacOS:  

		```bash
		source venv_Ticketverkauf/bin/activate
		```

	- On Windows:  

		```bash
		venv_Ticketverkauf\Scripts\activate
		```

4. Install dependencies:

	```bash
	pip install -r requirements.txt
	```

---

### Setting Up the Database
( normally, running the application for the first time should initiallise the database and this step can be skipped. )
Run the following commands to initialize the database:

	```bash
	flask db init
	flask db migrate -m "Initial migration."
	flask db upgrade
	```
 ( normally, running the application for the first time should initiallise the database and this step can be skipped. )

---

### Starting the Application

- **In development mode:**

	```bash
	python3 app.py
	```

	The application will then be accessible at [http://127.0.0.1:8191](http://127.0.0.1:8191).

- **In production mode:**

	```bash
	PORT=8191
	SCRIPT_DIR=$(dirname "$(realpath "$0")")
	echo "Switching to directory: $SCRIPT_DIR"
	cd "$SCRIPT_DIR"
	source venv/bin/activate
	gunicorn -w 11 -b 0.0.0.0:$PORT app:app --access-logfile - --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
	```

	Adjust the number of workers (`-w`) according to your server's performance.

---

## Directory Structure

	```
	Ticketverkauf/
	├── static/
	│   ├── images/
	│   │   ├── Wallpaper/
	│   │   └── icons/
	│   ├── fonts/
	│   ├── favicon.ico
	│   └── barcode/
	├── templates/
	│   ├── index.html
	│   ├── confirmation.html
	│   ├── error.html
	│   └── admin/
	│       └── index.html
	├── venv_Ticketverkauf/
	├── requirements.txt
	├── README.md
	├── LICENSE.txt
	├── datenbank.db
	├── testhost.sh
	├── HostDeploySP.sh
	├── global_STOP
	└── app.py
	```

- `app`: Contains the application code.  
- `templates/`: Contains the HTML templates.  
- `venv_Ticketverkauf/`: Virtual environment.  
- `requirements.txt`: List of Python dependencies.  

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure that you run tests and update the documentation accordingly.

---

### License

This project is licensed under the GNU General Public License.

---

### Contact

If you have any questions or suggestions, please create a discussion in the repository.

**Thank you! 😊**
