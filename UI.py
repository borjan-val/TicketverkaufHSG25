import tkinter as tk
from tkinter import ttk, messagebox, Tk
import sqlite3
from datetime import datetime


conn = sqlite3.connect('datenbank.db')
cursor = conn.cursor()  # Cursor erstellen

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'  # Gelb
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Funktion für die Verbindung zur Datenbank
# Funktion für die Verbindung zur Datenbank
def connect_to_db():
    global conn, cursor  # Globale Verbindung und Cursor
    try:
        if conn:
            conn.close()  # Falls eine alte Verbindung besteht, schließen
        conn = sqlite3.connect("datenbank.db")  # Neue Verbindung herstellen
        cursor = conn.cursor()  # Neuer Cursor für diese Verbindung
        cursor.execute("PRAGMA foreign_keys = ON;")  # Fremdschlüssel aktivieren
        status_label.config(text="Datenbank: Verbunden", fg="green")  # Status aktualisieren
        log_message("Erfolgreich mit der Datenbank verbunden.")
    except sqlite3.Error as e:
        status_label.config(text="Datenbank: Nicht verbunden", fg="red")  # Fehlerstatus
        log_message(f"Fehler bei der Verbindung zur Datenbank: {e}")
# Funktion, um Nachrichten in den Verlauf zu loggen
def log_message(message):
    # Konfiguriere den gelben Tag für Text
    log_area.tag_configure("warning", foreground="yellow")
    
    # Füge die Nachricht mit dem Tag 'warning' ein, um sie gelb darzustellen
    log_area.insert(tk.END, f"** Hinweis: {message} **\n", "warning")
    log_area.see(tk.END)

    
# Funktion, um nur die Daten für den aktuellen Identifier anzuzeigen und die Historie zu bewahren
def show_scanned_data(identifier):
    # Abrufen der Benutzerdaten für den aktuellen Identifier
    cursor.execute("SELECT vorname, nachname, age_user, jahrgang, category, bezahlt FROM PayState_scanned WHERE identifier = ?", (identifier,))
    result = cursor.fetchone()
    
    if result:
        vorname, nachname, age_user, jahrgang, category, bezahlt = result
        status = "Bezahlt" if bezahlt == 1 else "Nicht Bezahlt"
        # Neue Zeile in der Tabelle mit dem gescannten Identifier einfügen
        table.insert("", "0", values=(identifier, vorname, nachname, age_user, jahrgang, category, status))
        
        # Verlauf aktualisieren
        log_area.config(state="normal")
        log_area.insert("end", f"{identifier} - {status} (Gescannt)\n")
        log_area.config(state="disabled")
        log_message(f"Daten für Identifier '{identifier}' angezeigt.")
    else:
        log_message(f"Keine historischen Daten für Identifier '{identifier}' gefunden.")
    

    
def start_action():
    messagebox.showinfo("Info", "Start-Skript ausgeführt!")

def stop_action():
    messagebox.showinfo("Info", "Stopp-Skript ausgeführt!")

def toggle_mode():
    current_mode = mode_var.get()
    new_mode = "Einlass" if current_mode == "Verkauf" else "Verkauf"
    mode_var.set(new_mode)
    toggle_button.config(text=f"Modus: {new_mode}")

def show_info():
    messagebox.showinfo("Info", "Dies ist ein Ticketverkaufssystem!")

# Funktion, um Nachrichten in den Verlauf zu loggen
# Funktion, um Nachrichten in den Verlauf zu loggen
def log_message(message):
    log_area.config(state="normal")  # Stelle sicher, dass der Textbereich bearbeitbar ist
    log_area.insert(tk.END, message + "\n")
    log_area.config(state="disabled")  # Setze den Textbereich zurück in den 'disabled'-Zustand
    log_area.see(tk.END)  # Scrollen, um den neuesten Eintrag zu zeigen


# Hauptfenster
root = tk.Tk()
root.title("Ticketverkauf System")
root.geometry("800x600")

# Canvas oben rechts für das Symbol
canvas = tk.Canvas(root, width=50, height=50)
canvas.place(x=740, y=10)

# Funktion zum Ändern des Symbols
def update_status_symbol(status):
    canvas.delete("all")  # Entfernt das alte Symbol
    
    # Kreis zeichnen
    canvas.create_oval(10, 10, 40, 40, fill="lightgray", outline="black", width=2)
    
    if status == "green":  # Grüner Haken
        canvas.create_text(25, 25, text="✓", font=("Arial", 20, "bold"), fill="green")
    elif status == "red":  # Rotes X
        canvas.create_text(25, 25, text="X", font=("Arial", 20, "bold"), fill="red")
    else:  # Minus-Zeichen
        canvas.create_text(25, 25, text="-", font=("Arial", 20, "bold"), fill="black")
    
# Standardmäßig das Minuszeichen anzeigen (Verkaufsmodus)
update_status_symbol("none")

# Funktion für die Verbindung zur Datenbank
def connect_to_db():
    global conn, cursor  # Globale Verbindung und Cursor
    try:
        if conn:
            conn.close()  # Falls eine alte Verbindung besteht, schließen
        conn = sqlite3.connect("datenbank.db")  # Neue Verbindung herstellen
        cursor = conn.cursor()  # Neuer Cursor für diese Verbindung
        cursor.execute("PRAGMA foreign_keys = ON;")  # Fremdschlüssel aktivieren
        status_label.config(text="Datenbank: Verbunden", fg="green")  # Status aktualisieren
        log_message("Erfolgreich mit der Datenbank verbunden.")
    except sqlite3.Error as e:
        status_label.config(text="Datenbank: Nicht verbunden", fg="red")  # Fehlerstatus
        log_message(f"Fehler bei der Verbindung zur Datenbank: {e}")
        
def process_input(event=None):
    global cursor  # Sicherstellen, dass cursor global verwendet wird
    identifier = entry.get().strip()  # Eingabe aus dem Feld
    if not identifier:
        log_message("Keine Eingabe erkannt.")
        return
    
    # Überprüfen des Modus
    current_mode = mode_var.get()
    if current_mode == "Verkauf":
        # Im Verkaufsmodus: Bezahlstatus auf TRUE (1) setzen
        try:
            # Aktuelle Zeit holen
            last_scantime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Bezahlstatus auf TRUE setzen und last_scantime sowie scanned aktualisieren
            cursor.execute("""
                UPDATE Benutzer 
                SET bezahlt = 1, last_scantime = ?, scanned = 1
                WHERE identifier = ?
            """, (last_scantime, identifier))
            conn.commit()
            print(f"Hinweis: Bezahlstatus für '{identifier}' auf TRUE (1) gesetzt (Verkauf) und last_scantime aktualisiert.")
            
            # Abrufen der Benutzerdaten
            cursor.execute("SELECT vorname, nachname, category FROM benutzer WHERE identifier = ?", (identifier,))
            result = cursor.fetchone()
            
            if result:
                vorname, nachname, category = result
                
                # Überprüfen, ob der Identifier bereits in der PayState_scanned Tabelle vorhanden ist
                cursor.execute("SELECT * FROM PayState_scanned WHERE identifier = ?", (identifier,))
                existing_entry = cursor.fetchone()
                
                if existing_entry:
                    print(f"{bcolors.WARNING} Hinweis: Bereits bezahlt und Eintrag für Identifier '{identifier}' vorhanden {bcolors.ENDC}")
                else:
                    # Einfügen der Daten in die PayState_scanned Tabelle
                    cursor.execute("INSERT INTO PayState_scanned (identifier, vorname, nachname, category, bezahlt) VALUES (?, ?, ?, ?, ?)",
                                    (identifier, vorname, nachname, category, 1))
                    conn.commit()               
                    log_message(f"Daten für Identifier '{identifier}' in PayState_scanned eingetragen.")
                    
                # Daten für den aktuellen Identifier in der Tabelle anzeigen
                show_scanned_data(identifier)
            else:
                log_message(f"Keine Benutzerdaten für Identifier '{identifier}' gefunden.")
                
        except sqlite3.Error as e:
            log_message(f"Datenbankfehler beim Setzen des Bezahlstatus oder Einfügen der Daten: {e}")
            
    else:  # Wenn im Modus 'Einlass'
        try:
            cursor.execute("SELECT vorname, nachname, age_user, jahrgang, bezahlt FROM benutzer WHERE identifier = ?", (identifier,))
            result = cursor.fetchone()
            
            if result:
                vorname, nachname, age_user, jahrgang, bezahlt = result
                if bezahlt == 1:
                    status = "Bezahlt"
                    icon = "green"
                else:
                    status = "Nicht Bezahlt"
                    icon = "red"
                    
                # Daten in die Tabelle eintragen
                table.insert("", "end", values=(identifier, vorname, nachname, age_user, jahrgang, status))
                
                # Verlauf aktualisieren
                log_area.config(state="normal")
                log_area.insert("end", f"{identifier} - {status}\n")
                log_area.config(state="disabled")
                log_message(f"Daten für Identifier '{identifier}' abgerufen.")
            else:
                log_message(f"Keine Daten für Identifier '{identifier}' gefunden.")
                
        except sqlite3.Error as e:
            log_message(f"Datenbankfehler: {e}")
            
    # Eingabefeld leeren
    entry.delete(0, tk.END)
    
# Menüleiste
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
# Statussymbol für die Verbindung
status_label = tk.Label(root, text="Datenbank: Nicht verbunden", fg="red", font=("Arial", 10))
status_label.pack(pady=5)
file_menu.add_command(label="Datenbank verbinden", command=connect_to_db)
file_menu.add_separator()
file_menu.add_command(label="Beenden", command=root.quit)
menu_bar.add_cascade(label="Datei", menu=file_menu)

options_menu = tk.Menu(menu_bar, tearoff=0)
options_menu.add_command(label="Info", command=show_info)
menu_bar.add_cascade(label="Optionen", menu=options_menu)

root.config(menu=menu_bar)

# Eingabebereich
entry_label = tk.Label(root, text="Barcode Scannen:")
entry_label.pack(pady=10)

entry = tk.Entry(root, font=("Arial", 14))
entry.pack(pady=10)
# Das Eingabefeld wird auf die Funktion process_input gebunden
entry.bind("<Return>", process_input)

# Buttons für Aktionen
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

connect_button = tk.Button(root, text="Datenbank verbinden", command=connect_to_db)
connect_button.pack(pady=5)

start_button = tk.Button(button_frame, text="Start", command=start_action)
start_button.grid(row=0, column=1, padx=5)

stop_button = tk.Button(button_frame, text="Stopp", command=stop_action)
stop_button.grid(row=0, column=2, padx=5)

mode_var = tk.StringVar(value="Verkauf")
toggle_button = tk.Button(button_frame, text="Modus: Verkauf", command=toggle_mode)
toggle_button.grid(row=0, column=3, padx=5)

info_button = tk.Button(button_frame, text="Info", command=show_info)
info_button.grid(row=0, column=4, padx=5)

# Verlauf
log_label = tk.Label(root, text="Verlauf:")
log_label.pack(pady=5)

log_area = tk.Text(root, height=8, state="normal", wrap="word", bg="#2b2b2b", fg="white", font=("Courier", 10))
log_area.pack(padx=10, pady=5, fill="both")
log_area.tag_configure("warning", foreground="yellow")


# Tabelle
table_label = tk.Label(root, text="Daten:")
table_label.pack(pady=5)

columns = ("ID", "Vorname", "Nachname", "Alter", "Klasse", "Status", "Bezahlt")
table = ttk.Treeview(root, columns=columns, show="headings")


for col in columns:
    table.heading(col, text=col)
    table.column(col, width=120)

table.pack(pady=10, fill="both", expand=True)

# Start der Anwendung
root.mainloop()