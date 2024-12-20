#!/usr/bin/env python3

from flask import Flask, request, render_template, redirect, url_for, send_file, session
import sqlite3
import random
import os
import datetime
import time
from barcode.writer import ImageWriter
import secrets
import barcode
import threading
import logging
import re
from datetime import datetime


app = Flask(__name__, template_folder='templates')
request_count = 0
app.secret_key = secrets.token_hex(16)  # Sicherer Schlüssel für die Sessions

print("Templates-Verzeichnis:", os.path.abspath("templates"))
logging.debug("Debug message")
logging.info("Info message")
logging.warning("Warning message")
logging.error("Error message")
logging.critical("Critical message")

# überprüft Pfade
if print(os.path.exists("templates/index.html")) and print(os.path.exists("templates/error.html"))  == TRUE: # Soll True zurückgeben
    print("Template Pfade 'index' und 'error' vorhanden = TRUE")

#Zieht aktuelle Zeit für Insert in db
anmeldedatum = datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')
# Zeitstempel in Millisekunden
current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


def is_valid_name(name):
    return bool(re.match(r'^[A-Za-zÄäÖöÜüß-]+$', name))
def validate_name(name):
    # Regex für erlaubte Zeichen
    if re.match(r"^[a-zA-ZäöüßÄÖÜ\s-]+$", name):
        return True
    return False

@app.errorhandler(404)
def page_not_found(e):
    print(f"{bcolors.FAIL}Fehler 404 aufgetreten: {e}{bcolors.ENDC}")  # Fehlerprotokollierung
    return render_template('error.html', error_code=404, error_message="Seite nicht gefunden"), 404
@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_code=403, error_message="Zugriff verweigert"), 403
@app.errorhandler(400)
def bad_request_handler(e):
    return render_template('error.html', error_code=400, error_message="Ungültige Eingabe. Keine Sonderzeichen erlaubt."), 400
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, error_message="Interner Serverfehler"), 500
@app.errorhandler(Exception)
def handle_exception(e):
    # Allgemeiner Fehlerhandler für unerwartete Ausnahmen
    return render_template('error.html', error_code=500, error_message=str(e)), 500
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    OKPINK = '\033[95m'  
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ORANGE = '\033[38;5;214m'
random_charakters_bar = "qwertzuiopasdfghjklyxcvbnmQWERTZUIOPASDFGHJKLYXCVBNM1234567890!@#$%^&()-_=+[].,"
os.makedirs('static/tickets', exist_ok=True)
def count_registrations_with_ip():
    # Verbindung zur Datenbank herstellen
    conn = sqlite3.connect('datenbank.db')
    cursor = conn.cursor()
    
    # SQL-Abfrage, um die Anzahl der Zeilen mit nicht-NULL ip_address zu zählen
    cursor.execute("SELECT COUNT(*) FROM registrations WHERE ip_address IS NOT NULL")
    result = cursor.fetchone()
    
    # Anzahl der Anmeldungen mit gültiger IP-Adresse
    total_with_ip = result[0]
    
    # Schließe die Verbindung zur Datenbank
    conn.close()
    print(f"{bcolors.OKBLUE}Insgesamt {bcolors.ORANGE}{total_with_ip}{bcolors.OKBLUE} Anmeldungen mit gültiger IP-Adresse{bcolors.ENDC}")
def update_total_requests():
    # Gesamtzahl der Zugriffe in einer Datei speichern
    stats_dir = 'stats'
    if not os.path.exists(stats_dir):
        os.makedirs(stats_dir)
    stats_file = os.path.join(stats_dir, 'total_requests.txt')
    # Gesamtzahl der Zugriffe aus der Datei lesen
    total_requests = 0
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            total_requests = int(f.read().strip())
    # Gesamtzahl der Zugriffe erhöhen und wieder in die Datei speichern
    total_requests += 1
    with open(stats_file, 'w') as f:
        f.write(str(total_requests))
    return total_requests
# erstellt einzigartigen identifier für Person
def generate_user_id(registration_number, age_user, jahrgang):
    formatted_number = f"{registration_number:03d}"
    # Personendaten: Nummer, Alter und Klasse
    personal_data = f"{formatted_number}{age_user}{jahrgang}="
    # Generierung von x zufälligen Zeichen
    random_suffix =''.join(random.choice(random_charakters_bar) for _ in range(10))
    #bei range(10) gibt es 53,783,827,851,266,404,096 verschiedene kombinationen, für dekodierung über 3 Jahre
    return personal_data + random_suffix
def add_user_to_db(vorname, nachname, age_user, jahrgang, identifier, ip_address):
    conn = sqlite3.connect('datenbank.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO benutzer (
            vorname, nachname, age_user, jahrgang, identifier, anmeldedatum,
            ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (vorname, nachname, age_user, jahrgang, identifier, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
          ip_address))
    conn.commit()
    conn.close()
def generate_barcode(identifier):
    try:
        writer = ImageWriter()
        barcode_obj = barcode.get_barcode_class('code128')
        barcode_instance = barcode_obj(identifier, writer=writer)
        barcode_dir = os.path.join('static', 'barcodes')
        if not os.path.exists(barcode_dir):
            os.makedirs(barcode_dir)
        barcode_path = os.path.join(barcode_dir, f"{identifier}")
        barcode_instance.save(barcode_path)
        print(f"{bcolors.OKCYAN}Barcode erfolgreich gespeichert unter: {barcode_path}{bcolors.ENDC}")
        return barcode_path
    except Exception as e:
        print(f"{bcolors.WARNING}Fehler bei der Barcode-Erstellung: {e}{bcolors.ENDC}")
        return None
def init_stats_db():
    conn = sqlite3.connect('datenbank.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page TEXT NOT NULL,
            count INTEGER NOT NULL DEFAULT 0
        )
    ''')
    c.execute('INSERT OR IGNORE INTO stats (id, page, count) VALUES (1, "index", 0)')
    conn.commit()
    conn.close()
    
def increment_request_count():
    conn = sqlite3.connect('datenbank.db')
    c = conn.cursor()
    c.execute('UPDATE stats SET count = count + 1 WHERE page = "index"')
    c.execute('SELECT count FROM stats WHERE page = "index"')
    total_requests = c.fetchone()[0]
    conn.commit()
    conn.close()
    return total_requests

# Initialisierung der Statistik-Datenbank
init_stats_db()
def init_db():
    conn = sqlite3.connect('datenbank.db')
    c = conn.cursor()
    c.execute('''
    
        CREATE TABLE IF NOT EXISTS Benutzer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vorname TEXT NOT NULL,
            nachname TEXT NOT NULL,
            age_user INTEGER NOT NULL,
            jahrgang INTEGER NOT NULL,
            identifier TEXT UNIQUE NOT NULL,
            anmeldedatum DATETIME NOT NULL,
            bezahlt BOOLEAN NOT NULL DEFAULT 0,
            scanned INTEGER NOT NULL DEFAULT 0,
            category TEXT NOT NULL DEFAULT 'Gast',
            last_scantime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT NOT NULL
        );


        
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS PayState_scanned (
            identifier TEXT UNIQUE NOT NULL,
            vorname TEXT NOT NULL,
            nachname TEXT NOT NULL,
            category TEXT NOT NULL,
            bezahlt BOOLEAN NOT NULL DEFAULT 0
        );  
    ''')
    c.execute('''
        CREATE TRIGGER IF NOT EXISTS after_insert_on_PayState_scanned
        AFTER INSERT ON PayState_scanned
        FOR EACH ROW
        BEGIN
            UPDATE PayState_scanned
            SET
                vorname = (SELECT vorname FROM Benutzer WHERE Benutzer.identifier = NEW.identifier),
                nachname = (SELECT nachname FROM Benutzer WHERE Benutzer.identifier = NEW.identifier),
                category = (SELECT category FROM Benutzer WHERE Benutzer.identifier = NEW.identifier)
            WHERE identifier = NEW.identifier;
        END;
''')
    conn.commit()
    conn.close()
    if not os.path.exists('static/barcodes'):
        os.makedirs('static/barcodes')
init_db()

#zählt Zugriffe auf Seite
@app.before_request
def before_request():
    if not hasattr(active_connections, 'count'):
        active_connections.count = 0
    active_connections.count += 1
@app.after_request
def after_request(response):
    active_connections.count -= 1
    return response

#ruft bei mobilen Geräten index.html auf
@app.route('/')
def index():
    total_requests = increment_request_count()
    print(f"{bcolors.OKBLUE}Zugriffe auf Seite {bcolors.OKPINK}{total_requests}{bcolors.ENDC}")
    ip_address = request.remote_addr
    # Überprüfen, ob der User-Agent auf ein mobiles Gerät hinweist
    user_agent = request.user_agent.string.lower()
    is_mobile = "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent
    if is_mobile:
        return render_template('index.html', 
                               ip_address=ip_address)
    else:
        #regulärer Ausdruck zum blockieren von Desktop Zugriff
        return render_template('error.html', error_code=403, error_message="Zugriff verweigert"), 403
        
        #vorhande zum testen:
    #    return render_template('index.html', ip_address=ip_address)
                                
#leitet bei Neustart zurück zur Startseite und cleared Einträge
@app.route('/restart', methods=['GET'])
def restart():
    try:
        ip_address = request.remote_addr
        conn = sqlite3.connect('datenbank.db')
        c = conn.cursor()
        c.execute("UPDATE benutzer SET ip_address = ? WHERE ip_address = ?", (0, ip_address))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    except Exception as e:
        print(f"{bcolors.WARNING}Fehler beim Neustarten: {str(e)}{bcolors.ENDC}")
        return f"Ein Fehler ist aufgetreten: {str(e)}", 500
    
#blockiert Zugriff auf Barcode Dateien 
@app.route('/barcodes/<identifier>.png')
def get_barcode(identifier):
    user_agent = request.user_agent
    user_ip = request.remote_addr
    if user_agent.platform not in ['android', 'iphone', 'ipad']:
        error_message = "Seite nicht für Desktop verfügbar"
        return render_template('error.html', error_code=403, error_message=error_message), 403
    conn = sqlite3.connect('datenbank.db')
    c = conn.cursor()
    c.execute("SELECT ip_address FROM benutzer WHERE identifier = ?", (identifier,))
    result = c.fetchone()
    conn.close()
    session.clear()
    if not result or result[0] != user_ip:
        error_message = "IP-Adresse passt nicht zum Benutzer"
        return render_template('error.html', error_code=403, error_message=error_message), 403
    barcode_path = os.path.join('static', 'barcodes', f"{identifier}.png")
    if not os.path.exists(barcode_path):
        error_message = "Der angeforderte Barcode existiert nicht"
        return render_template('error.html', error_code=404, error_message=error_message), 404
    return send_file(barcode_path)

@app.route('/submit', methods=['POST'])
def submit():
    count_registrations_with_ip
    try:
        # Formulardaten abrufen und validieren
        vorname = request.form.get('vorname')
        nachname = request.form.get('nachname')
        age_user = request.form.get('age')
        jahrgang = request.form.get('jahrgang')
        
        
        # IP-Adresse des Benutzers ermitteln
        ip_address = request.remote_addr
    # Logging der empfangenen Daten
        print(f"{bcolors.OKGREEN}Empfangene Daten: Vorname={vorname}, Nachname={nachname}, Alter={age_user}, Jahrgang={jahrgang},ip={ip_address}{bcolors.ENDC}")
        # SQLite-Verbindung und Datenbankzugriff
        with sqlite3.connect('datenbank.db') as conn:
            c = conn.cursor()
            
            # Anmeldungsnummer ermitteln
            c.execute("SELECT COUNT(*) FROM benutzer")
            registration_number = c.fetchone()[0] + 1
            
            # Benutzer mit derselben IP prüfen
            c.execute("SELECT * FROM benutzer WHERE ip_address = ?", (ip_address,))
            existing_user = c.fetchone()
            
            if existing_user:
                return render_template('confirmation.html', 
                                        vorname=existing_user[1], 
                                        nachname=existing_user[2], 
                                        age_user=existing_user[3], 
                                        jahrgang=existing_user[4], 
                                        identifier=existing_user[5],
                                        ip_address=existing_user[6],
                                        id=existing_user[0],
                                        anmeldedatum=existing_user[7])
            
            # Neuen Benutzer erstellen
            identifier = generate_user_id(registration_number, int(age_user), int(jahrgang))
            c.execute("INSERT INTO benutzer (vorname, nachname, age_user, jahrgang, identifier, ip_address, anmeldedatum) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                (vorname, nachname, int(age_user), int(jahrgang), identifier, ip_address, current_timestamp))
            
            # Neu erstellten Benutzer abrufen
            c.execute("SELECT * FROM benutzer WHERE identifier = ?", (identifier,))
            new_user = c.fetchone()
            
            # Barcode generieren
        generate_barcode(identifier)
        
        # Bestätigungsseite rendern
        return render_template('confirmation.html', 
                                vorname=vorname, 
                                nachname=nachname, 
                                age_user=int(age_user), 
                                jahrgang=int(jahrgang), 
                                identifier=identifier,
                                ip_address=ip_address,     
                                anmeldedatum=anmeldedatum,
                                id=new_user[0])
    except Exception as e:
        print(f"Fehler im submit-Handler: {str(e)}")
        return render_template("error.html", error_message="Ein unerwarteter Fehler ist aufgetreten. Bitte versuche es später erneut."), 500
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8191, debug=False)
    if not os.path.exists('static'):
        os.makedirs('static')
    if not os.path.exists('static/barcodes'):
        os.makedirs('static/barcodes')
    # Initialisiere die Datenbank
    init_db()