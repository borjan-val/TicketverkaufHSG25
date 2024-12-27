#!/usr/bin/env python3

from flask import Flask, request, render_template, redirect, url_for, send_file, session
import sqlite3
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
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
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, event
from sqlalchemy.orm import sessionmaker


app = Flask(__name__, template_folder='templates')
request_count = 0

logging.basicConfig(filename='app.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialisiere SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/can/Desktop/Ticketverkauf/datenbank.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "mysecret"
db = SQLAlchemy(app)

# Initialisiere Flask-Admin
admin = Admin(app, name='Admin Panel', template_mode='bootstrap4')

Base = declarative_base()
class Benutzer(db.Model):
    __tablename__ = 'benutzer'
    
    # Definiere die Spalten
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vorname = db.Column(db.String(80), nullable=False)
    nachname = db.Column(db.String(80), nullable=False)
    age_user = db.Column(db.Integer, nullable=False)
    jahrgang = db.Column(db.Integer, nullable=False)
    identifier = db.Column(db.String(120), unique=True, nullable=False)
    anmeldedatum = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Default für aktuelle Zeit
    bezahlt = db.Column(db.Boolean, default=False)
    scanned = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50), default='Gast', nullable=False)
    last_scantime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_address = db.Column(db.String(120), nullable=False)
    anmerkung = db.Column(db.Text, nullable = True)
    
    def __repr__(self):
        return f'<Benutzer {self.vorname} {self.nachname}>'
    
# Beispiel für die andere Klasse
class PayStateScanned(db.Model):
    __tablename__ = 'paystate_scanned'
    identifier = db.Column(db.ForeignKey("benutzer.identifier"), nullable=False, primary_key=True)
    vorname = db.Column(db.String(80), nullable=False)
    nachname = db.Column(db.String(80), nullable=False)
    age_user = db.Column(db.Integer, nullable=False)
    jahrgang = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    bezahlt = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<PayStateScanned {self.vorname} {self.nachname}>'
    
class PayStateView(ModelView):
    can_delete = False
    
# Die Statistik-Klasse
class Stats(db.Model):
    __tablename__ = 'stats'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    page = db.Column(db.String(80), nullable=False)
    count = db.Column(db.Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f'<Stats {self.page}>'

app.secret_key = secrets.token_hex(16)  # Sicherer Schlüssel für die Sessions

active_connections = 0  # Initialisierung der globalen Zählung

print("Templates-Verzeichnis:", os.path.abspath("templates"))

logging.debug("Debug message")
logging.info("Info message")
logging.warning("Warning message")
logging.error("Error message")
logging.critical("Critical message")

# überprüft Pfade
if os.path.exists("templates/index.html") and os.path.exists("templates/error.html") and os.path.exists("templates/confirmation.html"):
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
    personal_data = f"{formatted_number}{age_user}{jahrgang}="
    random_suffix =''.join(random.choice(random_charakters_bar) for _ in range(10))
    #bei range(10) gibt es 53,783,827,851,266,404,096 verschiedene kombinationen, für dekodierung über 3 Jahre
    return personal_data + random_suffix

def generate_unique_user_id(registration_number, age_user, jahrgang):
    while True:
        identifier = generate_user_id(registration_number, age_user, jahrgang)
        # Überprüfe, ob der identifier bereits existiert
        if not Benutzer.query.filter_by(identifier=identifier).first():
            break
    return identifier


## Neue Version mit SQLAlchemy:
#def add_user_to_db(vorname, nachname, age_user, jahrgang, identifier, ip_address):
#   new_user = Benutzer(
#       vorname=vorname,
#       nachname=nachname,
#       age_user=age_user,
#       jahrgang=jahrgang,
#       identifier=identifier,
#       ip_address=ip_address,
#       anmeldedatum=datetime.now()
#   )
#   db.session.add(new_user)
#   db.session.commit()
    
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
    
    
# Neue Version mit SQLAlchemy:
def increment_request_count():
    stat = db.session.query(Stats).filter_by(page="index").first()
    if stat:
        stat.count += 1
    else:
        stat = Stats(page="index", count=1)
        db.session.add(stat)
    db.session.commit()
    return stat.count


def init_db():
    # Setze den Anwendungskontext, um mit der Datenbank zu arbeiten
    with app.app_context():
        db.create_all()
        
        # Initialisiere 'stats' Tabelle mit Standardwerten, falls nicht vorhanden
        index_stat = db.session.query(Stats).filter_by(page="index").first()
        if not index_stat:
            index_stat = Stats(page="index", count=0)
            db.session.add(index_stat)
            db.session.commit()
            
        # Erstelle Verzeichnisse, falls nicht vorhanden
        os.makedirs('static/barcodes', exist_ok=True)

@app.before_request
def before_request():
    if 'active_connections' not in session:
        session['active_connections'] = 0
        
@app.after_request
def after_request(response):
    session['active_connections'] -= 1
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
    #    return render_template('error.html', error_code=403, error_message="Zugriff verweigert"), 403
        
        #vorhande zum testen:
       return render_template('index.html', ip_address=ip_address)
                                
#leitet bei Neustart zurück zur Startseite und cleared Einträge
@app.route('/restart', methods=['GET'])
def restart():
    try:
        ip_address = request.remote_addr
        
        # Update IP-Adresse des Benutzers auf 0, indem wir SQLAlchemy verwenden
        benutzer = Benutzer.query.filter_by(ip_address=ip_address).all()
        for user in benutzer:  # Entferne .items() und iteriere direkt
            user.ip_address = "0"  # Setze die IP-Adresse auf "0"
        
        db.session.commit()  # Änderungen in der Datenbank speichern
        
        return redirect(url_for('index'))
    except Exception as e:
        print(f"{bcolors.WARNING}Fehler beim Neustarten: {str(e)}{bcolors.ENDC}")
        return f"Ein Fehler ist aufgetreten: {str(e)}", 500
    
#blockiert Zugriff auf Barcode Dateien 
@app.route('/barcodes/<identifier>.png')
def get_barcode(identifier):
    user_agent = request.user_agent
    user_ip = request.remote_addr
    
    # Überprüfe, ob der Zugriff von einem mobilen Gerät kommt
    if user_agent.platform not in ['android', 'iphone', 'ipad']:
        error_message = "Seite nicht für Desktop verfügbar"
        return render_template('error.html', error_code=403, error_message=error_message), 403
    
    # Überprüfe, ob der Benutzer mit dem gegebenen Identifier existiert und ob die IP-Adresse übereinstimmt
    user = Benutzer.query.filter_by(identifier=identifier).first()
    if not user or user.ip_address != user_ip:
        error_message = "IP-Adresse passt nicht zum Benutzer"
        return render_template('error.html', error_code=403, error_message=error_message), 403
    
    # Überprüfe, ob die Barcode-Datei existiert
    barcode_path = os.path.join('static', 'barcodes', f"{identifier}.png")
    if not os.path.exists(barcode_path):
        error_message = "Der angeforderte Barcode existiert nicht"
        return render_template('error.html', error_code=404, error_message=error_message), 404
    
    # Sende die Barcode-Datei
    return send_file(barcode_path)

from datetime import datetime

@app.route('/submit', methods=['POST'])
def submit():
    try:
        print(f"Form Data: {request.form}")
        # Formulardaten abrufen und validieren
        age_user = request.form.get('age', '')
        jahrgang = request.form.get('jahrgang', '')
        vorname = request.form.get('vorname', '')
        nachname = request.form.get('nachname', '')
        
        # Validierung der Eingabewerte
        if not validate_name(vorname) or not validate_name(nachname):
            return render_template('error.html', error_message="Ungültiger Vorname oder Nachname! Nur Buchstaben und Leerzeichen sind erlaubt.")
        

        print(f"Type of form data: {type(request.form)}")
        
        # IP-Adresse des Benutzers ermitteln
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
        
        # Logging der empfangenen Daten
        print(f"{bcolors.OKGREEN}Empfangene Daten: Vorname={vorname}, Nachname={nachname}, Alter={age_user}, Jahrgang={jahrgang}, ip={ip_address}{bcolors.ENDC}")
        
        # Den aktuellen Zeitstempel für das Anmelde-Datum als datetime-Objekt
        current_timestamp = datetime.now()
        
        # Benutzer mit derselben IP überprüfen
        existing_user = Benutzer.query.filter_by(ip_address=ip_address).first()
        
        if existing_user:
            # Rückgabe der Bestätigungsseite für bestehenden Benutzer
            return render_template('confirmation.html', 
                                   vorname=existing_user.vorname, 
                                   nachname=existing_user.nachname, 
                                   age_user=existing_user.age_user, 
                                   jahrgang=existing_user.jahrgang, 
                                   identifier=existing_user.identifier,
                                   ip_address=existing_user.ip_address,
                                   id=existing_user.id,
                                   anmeldedatum=existing_user.anmeldedatum)
        
        # Anmeldungsnummer ermitteln
        registration_number = Benutzer.query.count() + 1
        
        # Neuen Benutzer erstellen
        identifier = generate_unique_user_id(registration_number, int(age_user), int(jahrgang))
        
        # Neuer Benutzer in der Datenbank speichern
        new_user = Benutzer(vorname=vorname, nachname=nachname, age_user=int(age_user), 
                            jahrgang=int(jahrgang), identifier=identifier, 
                            ip_address=ip_address, anmeldedatum=current_timestamp)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Barcode generieren (aufrufen einer Funktion)
        generate_barcode(identifier)
        
        # Bestätigungsseite für den neuen Benutzer rendern
        return render_template('confirmation.html', 
                               vorname=vorname, 
                               nachname=nachname, 
                               age_user=int(age_user), 
                               jahrgang=int(jahrgang), 
                               identifier=identifier,
                               ip_address=ip_address,     
                               anmeldedatum=current_timestamp,
                               id=new_user.id)
    
    except Exception as e:
        print(f"Fehler im submit-Handler: {str(e)}")
        return render_template("error.html", error_message="Ein unerwarteter Fehler ist aufgetreten. Bitte versuche es später erneut."), 500
    
# Füge Models zu Flask-Admin hinzu
admin.add_view(ModelView(Benutzer, db.session))
admin.add_view(ModelView(PayStateScanned, db.session))
admin.add_view(ModelView(Stats, db.session))

if __name__ == "__main__":
    if not os.path.exists('static'):
        os.makedirs('static')
    if not os.path.exists('static/barcodes'):
        os.makedirs('static/barcodes')
    # Initialisiere die Datenbank
    init_db()
    
    app.run(host="0.0.0.0", port=8191, debug=True)
