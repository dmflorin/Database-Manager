import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox, font
from datetime import datetime

# Function to test whether the database exists on the server or not
def check_credentials(database, cursor): 
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    for db in databases:
        if db[0] == database:
            return True
    return False

# Function to verify username and password
def check_login(user, password, cursor): 
    cursor.execute("SELECT * FROM utilizatori")
    credentials = cursor.fetchall()
    for credit in credentials:
        if credit[1] == user: 
            if credit[2] == password:
                return True
    return False

# Function to close connections
def close_connection(conn, cursor):
    cursor.close()
    conn.close()

# Function for connecting to the database
def connect_to_db(host, user, password, database):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        return conn, cursor
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Could not connect to MySQL: {str(err)}")
        exit()

# Function to retrieve table names from MySQL database
def fetch_table_names(cursor):
    try:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        return [table[0] for table in tables]  # Returns a list of table names
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"An error occurred: {err}")

# Function to retrieve all data from a table
def fetch_table_data(table_name, cursor):
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [i[0] for i in cursor.description]  # Extract column names
    return columns, rows

# Function to perform SQL query based on user selection
def fetch_data(cursor, selected_columns, table_name):
    if not selected_columns:
        messagebox.showwarning("Warning", "Please select at least one column.")
        return
    else:
        try:
            columns_str = ', '.join(selected_columns)
            query = f"SELECT {columns_str} FROM {table_name}"
            cursor.execute(query)
            results = cursor.fetchall()
            return results
        except Exception as e:
            messagebox.showerror("Error", f"Query error: {str(e)}")
            return []

# Function to get table columns
def get_columns(cursor, table_name):
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    columns = cursor.fetchall()
    return [col[0] for col in columns]

# Function to generate dynamic checkboxes
def create_checkboxes(root, columns, columns_vars):
    row = 0
    for col_name in columns:
        var = tk.IntVar()
        columns_vars[col_name] = var
        tk.Checkbutton(root, text=col_name.capitalize(), variable=var).grid(row=row, column=0, sticky='w', padx=10, pady=5)
        row += 1

# Function to adjust column width in TreeView
def adjust_column_width(treeview):
    tree_font = font.Font(family="TkDefaultFont")
    for col in treeview['columns']:
        max_width = tree_font.measure(treeview.heading(col, 'text'))
        for item in treeview.get_children():
            text = treeview.item(item, 'values')[treeview['columns'].index(col)]
            max_width = max(max_width, tree_font.measure(text))
        treeview.column(col, width=max_width + 10)

# Function to populate the second TreeView (display table data)
def display_table_data(table_name, right_tree, cursor):
    try:
        columns, rows = fetch_table_data(table_name, cursor)
        right_tree.delete(*right_tree.get_children())
        right_tree.column("#0", width=0, stretch=tk.NO)
        right_tree["columns"] = columns
        for col in columns:
            right_tree.heading(col, text=col)
            right_tree.column(col, anchor='w', stretch=tk.NO)
        for row in rows:
            right_tree.insert("", "end", values=row)
        adjust_column_width(right_tree)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"An error occurred: {err}")

# Function to display query results
def display_results(right_tree, rows, columns):
    try:
        right_tree.delete(*right_tree.get_children())
        right_tree.column("#0", width=0, stretch=tk.NO)
        right_tree["columns"] = columns
        for col in columns:
            right_tree.heading(col, text=col)
            right_tree.column(col, anchor='w', stretch=tk.NO)
        for row in rows:
            right_tree.insert("", "end", values=row)
        adjust_column_width(right_tree)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"An error occurred: {err}")

# Function that handles double-click on a table
def on_double_click(event, tree, right_tree, cursor, table_name):
    selected_item = tree.selection()[0]  # Get the selected item
    table_name[0] = tree.item(selected_item, "text")
    display_table_data(table_name[0], right_tree, cursor)  # Display data in the right widget

# Function to select an item
def select(tree):
    selected_item = tree.selection()[0]
    table_name = tree.item(selected_item, "text")
    print(table_name)

# Function to populate TreeView with table names
def populate_treeview(tree, table_names):
    for table_name in table_names:
        tree.insert('', 'end', text=table_name)

# Function to create the select query interface
def create_gui_select(root, main_tree, tree, cursor):
    root_select = tk.Toplevel(root)
    root_select.title("Database Query")
    root_select.geometry("400x400")
    selected_item = main_tree.selection()[0]
    table_name = main_tree.item(selected_item, "text")
    columns_vars = {}
    columns = get_columns(cursor, table_name)
    create_checkboxes(root_select, columns, columns_vars)
    
    # Function called when the query button is pressed
    def on_query():
        selected_columns = [col for col, var in columns_vars.items() if var.get() == 1]
        results = fetch_data(cursor, selected_columns, table_name)
        display_results(tree, results, selected_columns)
        root_select.destroy()
    
    query_button = ttk.Button(root_select, text="Show Data", command=on_query)
    query_button.grid(row=len(columns), column=0, padx=10, pady=10)

#Functie pentru crearea interfetei de insert
def create_gui_insert(root, main_tree, cursor):
    root_insert = tk.Toplevel(root)
    root_insert.title("Insert Data into Database")
    root_insert.geometry("400x400")

    selected_item = main_tree.selection()[0]
    table_name = main_tree.item(selected_item, "text")

    columns = get_columns(cursor, table_name)

    entry_widgets = {}

    for i, column in enumerate(columns):
        label = ttk.Label(root_insert, text=column)
        label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
        
        entry_var = tk.StringVar()
        entry = ttk.Entry(root_insert, textvariable=entry_var)
        entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
        
        entry_widgets[column] = entry_var

    def on_insert():
        values = {col: var.get() for col, var in entry_widgets.items()}
        
        insert_data(cursor, table_name, values)
        
        root_insert.destroy()

    insert_button = ttk.Button(root_insert, text="Insert Data", command=on_insert)
    insert_button.grid(row=len(columns), column=0, columnspan=2, padx=10, pady=20)


def insert_data(cursor, table_name, values):
    try :
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['%s'] * len(values))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        print(query)
        cursor.execute(query, list(values.values()))
        cursor.execute(f"commit")
    except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la interogare: {str(e)}")

#Functie pentru crearea interfetei de update
def create_gui_update(root, main_tree, table_name, columns, cursor):
    root_update = tk.Toplevel(root)
    root_update.title("Update Data in Database")
    root_update.geometry("500x500")

    check_vars = {}
    entry_widgets = {}

    id_label = ttk.Label(root_update, text="Enter the ID (or key) to update:")
    id_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    id_var = tk.StringVar()
    id_entry = ttk.Entry(root_update, textvariable=id_var)
    id_entry.grid(row=0, column=1, padx=10, pady=5)

    for i, column in enumerate(columns, start=1):
        check_var = tk.BooleanVar()
        check = ttk.Checkbutton(root_update, text=column, variable=check_var)
        check.grid(row=i, column=0, padx=10, pady=5, sticky="w")
        check_vars[column] = check_var

        entry_var = tk.StringVar()
        entry = ttk.Entry(root_update, textvariable=entry_var)
        entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
        entry_widgets[column] = entry_var

    def on_update():
        selected_columns = {col: var.get() for col, var in check_vars.items() if var.get()}
        if not selected_columns:
            messagebox.showerror("Error", "Please select at least one column to update.")
            return

        id_value = id_var.get()
        if not id_value:
            messagebox.showerror("Error", "Please enter the ID (or key) of the row to update.")
            return

        set_clauses = []
        values = []
        for column, entry_var in entry_widgets.items():
            if check_vars[column].get():
                set_clauses.append(f"{column} = %s")
                values.append(entry_var.get())

        set_clause = ", ".join(set_clauses)
        query = f"UPDATE {table_name} SET {set_clause} WHERE {columns[0]} = %s"
        values.append(id_value) 

        try:
            cursor.execute(query, values)
            cursor.execute("COMMIT")
            messagebox.showinfo("Success", "Data updated successfully!")
            root_update.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error while updating data: {str(e)}")

    update_button = ttk.Button(root_update, text="Update Data", command=on_update)
    update_button.grid(row=len(columns) + 1, column=0, columnspan=2, padx=10, pady=20)

def delete_selected_row(tree, cursor, table_name, column_names, root):
    # Verificăm dacă există un element selectat
    selected_item = tree.selection()
    if not selected_item:
        # Dacă nu este nimic selectat, deschidem o fereastră pentru a specifica criteriile de ștergere
        open_delete_dialog(tree, cursor, table_name, column_names, root)
        return

    try:
        # Presupunem că ID-ul rândului este stocat în primul atribut (coloană) al Treeview
        row_id = tree.item(selected_item[0])["values"][0]  # Primul element din "values" este ID-ul în baza de date
        
        # Șterge din baza de date folosind ID-ul selectat
        delete_query = f"DELETE FROM {table_name} WHERE id = %s"
        cursor.execute(delete_query, (row_id,))
        cursor.execute("commit")

        # Șterge rândul și din Treeview
        tree.delete(selected_item[0])
        messagebox.showinfo("Succes", "Rândul a fost șters cu succes.")
        
    except Exception as e:
        messagebox.showerror("Eroare", f"A apărut o eroare la ștergerea rândului: {e}")

def open_delete_dialog(tree, cursor, table_name, column_names, root):
    # Creăm o nouă fereastră de tip Toplevel
    dialog = tk.Toplevel(root)
    dialog.title("Ștergere rând specific")
    
    # Dictionar pentru a stoca câmpurile de intrare
    entries = {}

    # Creăm un Label și un Entry pentru fiecare coloană
    for idx, col in enumerate(column_names):
        ttk.Label(dialog, text=col).grid(row=idx, column=0, padx=5, pady=5)
        entry = ttk.Entry(dialog)
        entry.grid(row=idx, column=1, padx=5, pady=5)
        entries[col] = entry  # Adăugăm entry-ul în dicționar pentru acces ușor

    # Buton pentru a confirma ștergerea
    ttk.Button(dialog, text="Șterge", command=lambda: delete_row_with_criteria(entries, cursor, table_name)).grid(row=len(column_names), column=0, columnspan=2, pady=10)

def delete_row_with_criteria(entries, cursor, table_name):
    # Construim criteriile de ștergere pe baza valorilor introduse
    criteria = []
    values = []

    for col, entry in entries.items():
        value = entry.get()
        if value:  # Adăugăm doar dacă există o valoare introdusă
            criteria.append(f"{col} = %s")
            values.append(value)

    if not criteria:
        messagebox.showwarning("Eroare", "Introduceți cel puțin un criteriu pentru ștergere.")
        return

    # Construim interogarea SQL pentru ștergere
    delete_query = f"DELETE FROM {table_name} WHERE " + " AND ".join(criteria)
    print(delete_query)

    try:
        # Executăm interogarea
        cursor.execute(delete_query, tuple(values))
        
        if cursor.rowcount == 0:
            messagebox.showinfo("Informație", "Nu s-a găsit niciun rând care să corespundă criteriilor specificate.")
        else:
            messagebox.showinfo("Succes", f"Rânduri șterse cu succes: {cursor.rowcount}")
        
        cursor.execute("commit")
    except Exception as e:
        messagebox.showerror("Eroare", f"A apărut o eroare la ștergerea rândului: {e}")
    
# Functie pentru crearea interfetei bazei de date
def create_gui(main, conn, cursor):
    main.withdraw()
    root = tk.Toplevel(main)
    root.title("Baza de date")
    root.state("zoomed")
    #root.resizable(False, False)

    # Creăm un Treeview pentru a afișa numele tabelelor
    tree = ttk.Treeview(root)
    tree.heading("#0", text="Tabele", anchor='w')

    # Treeview pentru afișarea datelor din tabelul selectat
    right_tree = ttk.Treeview(root)

    # Creează un scrollbar orizontal
    h_scrollbar = ttk.Scrollbar(root, orient='horizontal', command=right_tree.xview)
    right_tree.configure(xscrollcommand=h_scrollbar.set)

    buttons_frame = ttk.Frame(root)
    buttons_frame.grid(row=1, column=1, padx=10, pady=5)

    select_button = tk.Button(buttons_frame, text="Select", command= lambda : create_gui_select(root, tree, right_tree, cursor))
    select_button.pack(side='left', padx=5, pady= 5)

    insert_button = tk.Button(buttons_frame, text="Insert", command= lambda : create_gui_insert(root, tree, cursor))
    insert_button.pack(side='left', padx=5, pady= 5)
    
    # Folosim grid și poziționăm cele două treeviews una lângă alta
    tree.grid(row=0, rowspan=3, column=0, sticky='nsw')  # Coloana din stânga pentru tabele
    right_tree.grid(row=0, column=1, sticky='nsew')  # Coloana din dreapta pentru datele tabelului
    h_scrollbar.grid(row=2, column=1, sticky='ew')  # Scrollbar-ul orizontal sub right_tree


    # Configurăm ferestrele să se extindă când redimensionăm
    root.grid_columnconfigure(0, minsize=200)
    root.grid_columnconfigure(1, weight=1)  # Coloana din dreapta să fie mai largă
    root.grid_rowconfigure(0, weight=1)

    # Preluăm numele tabelelor din baza de date
    table_names = fetch_table_names(cursor)

    # Populăm Treeview-ul cu numele tabelelor
    populate_treeview(tree, table_names)

    nume_tabel = [""]

    # Legăm evenimentul de dublu click pe un element din Treeview-ul de tabele
    tree.bind("<Double-1>", lambda event: on_double_click(event, tree, right_tree, cursor, nume_tabel))

    delete_button = tk.Button(buttons_frame, text="Delete", command= lambda : delete_selected_row(right_tree, cursor, nume_tabel[0], get_columns(cursor, nume_tabel[0]), root))
    delete_button.pack(side='left', padx=5, pady= 5)

    update_button = tk.Button(buttons_frame, text="Update", command= lambda : create_gui_update(root, right_tree, nume_tabel[0], get_columns(cursor, nume_tabel[0]), cursor))
    update_button.pack(side='left', padx=5, pady= 5)

    back_button1 = tk.Button(buttons_frame, text="Back", command= lambda : back_function(root, main))
    back_button1.pack(side='left', padx=5, pady= 5)

    def on_closing():
        #close_connection(conn, cursor)
        root.destroy()
        main.deiconify()
        main.state('zoomed')
    
    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()

def back_function(root, main) :
    root.destroy()
    main.deiconify()
    main.state('zoomed')


def login(main, username, password, database):
    
    conn, cursor = connect_to_db("localhost", "root", "password", "login")

    if  check_login(username, password, cursor) and check_credentials(database, cursor):
        close_connection(conn, cursor)
        conn, cursor = connect_to_db("localhost", "root", "password", database)
        messagebox.showinfo("Login Successful", "Welcome!")
        main.withdraw()
        create_window(main, conn, cursor)
        close_connection(conn, cursor)
        
    else:
        conn.close()
        cursor.close()
        messagebox.showerror("Login Failed", "Invalid database or login credentials!")

# Functie pentru creearea primului query
def functie_1(main, conn, cursor):
    
    root = tk.Toplevel(main)
    root.title("Afisare Sali")
    root.minsize(width=300, height=300)
    
    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)
    
    cursor.execute("SELECT DISTINCT locatie FROM Sali")
    locations = [row[0] for row in cursor.fetchall()]  # Convertim rezultatele într-o listă
    
    
    # Variabila asociată dropdown-ului
    selected_location = tk.StringVar()
    selected_location.set(locations[0])  # Setăm o valoare implicită (prima din listă)
    
    # Etichetă și dropdown
    location_label = tk.Label(frame, text="Selectează locația:", bg='lightblue')
    location_label.grid(row=0, columnspan=2, pady=10)
    
    location_dropdown = tk.OptionMenu(frame, selected_location, *locations)
    location_dropdown.grid(row=1, columnspan=2, pady=10)
    
    def on_submit(event = None) :
        
        location = selected_location.get()
        print(location)
        query = f"""
        SELECT e.denumire AS Eveniment, e.data_eveniment AS Data, s.nume_sala AS 'Nume Sala', s.locatie as Zona 
        FROM Evenimente e 
        JOIN Sali s ON e.id_sala = s.id_sala 
        WHERE s.locatie = '{location}';
        """
        root.destroy()
        create_treeview_with_query_results(main, query, conn, cursor)
        
    submit_button = tk.Button(frame, text="Submit", command = on_submit)
    submit_button.grid(row=2, columnspan=2, pady=20)
    #messagebox.showinfo("Buton 1", "Ați apăsat butonul 1!")

# Functie pentru creearea celui de al doilea query
def functie_2(main, conn, cursor):
    query = """
        SELECT nume_furnizor as 'Nume furnizor', nume_serviciu as 'Nume Serviciu', descriere_serviciu as Descriere, pret_serviciu as Pret 
	    FROM Furnizori f 
	    JOIN Servicii s on f.id_furnizor = s.id_furnizor;
    """
    create_treeview_with_query_results(main, query, conn, cursor)
    #messagebox.showinfo("Buton 2", "Ați apăsat butonul 2!")

# Functie pentru creearea celui de al treilea query
def functie_3(main, conn, cursor):
    query = """
        SELECT SUM(s.pret_pe_zi) as 'Incasari totale'
	    FROM sali s 
	    JOIN evenimente e ON s.id_sala = e.id_sala;
    """
    create_treeview_with_query_results(main, query, conn, cursor)
    #messagebox.showinfo("Buton 3", "Ați apăsat butonul 3!")

# Functie pentru creearea celui de al patrulea query
def functie_4(main, conn, cursor):
    root = tk.Toplevel(main)
    root.title("Afisare Sali")
    
    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)
    
    # Entry pentru an
    year_label = tk.Label(frame, text="Introduceți anul:", bg='lightblue')
    year_label.grid(row=2, column=0, pady=5)
    
    year_entry = tk.Entry(frame)
    year_entry.grid(row=2, column=1, pady=5)
    
    # Entry pentru lună
    month_label = tk.Label(frame, text="Introduceți luna (1-12):", bg='lightblue')
    month_label.grid(row=3, column=0, pady=5)
    
    month_entry = tk.Entry(frame)
    month_entry.grid(row=3, column=1, pady=5)
    
    # Funcția apelată la apăsarea butonului Submit
    def submit_query(event = None):
        year = year_entry.get().strip()    # Obținem anul introdus
        month = month_entry.get().strip()  # Obținem luna introdusă
        
        # Validare de bază pentru an și lună
        if not year.isdigit() or not month.isdigit() or not (1 <= int(month) <= 12):
            tk.messagebox.showerror("Eroare", "Introduceți un an valid și o lună între 1 și 12.")
            return
        
        query = f"""
            SELECT Evenimente.denumire, Evenimente.data_eveniment, Clienti.nume
	        FROM Evenimente
	        JOIN Clienti ON Evenimente.id_client = Clienti.id_client
	        WHERE YEAR(Evenimente.data_eveniment) = {year} AND MONTH(Evenimente.data_eveniment) = {month};
        """
        
        # Executăm funcția pentru a afișa rezultatele
        root.destroy()
        create_treeview_with_query_results(main, query, conn, cursor)
    
    # Butonul Submit
    submit_button = tk.Button(frame, text="Submit", command=submit_query)
    submit_button.grid(row=4, columnspan=2, pady=20)
    #messagebox.showinfo("Buton 4", "Ați apăsat butonul 4!")

# Functie pentru creearea celui de al cincelea query
def functie_5(main, conn, cursor):
    query = """
        SELECT e.denumire AS Eveniment, GROUP_CONCAT(f.nume_furnizor ORDER BY f.nume_furnizor SEPARATOR ', ') AS Furnizori
	    FROM evenimente e
	    JOIN evenimente_furnizori ef ON e.id_eveniment = ef.id_eveniment
	    JOIN furnizori f ON ef.id_furnizor = f.id_furnizor
	    GROUP BY e.id_eveniment, e.denumire;
    """
    create_treeview_with_query_results(main, query, conn, cursor)
    #messagebox.showinfo("Buton 5", "Ați apăsat butonul 5!")

# Functie pentru creearea celui de al saselea query
def functie_6(main, conn, cursor):
    query = """
       SELECT c.nume AS Client, c.telefon as Telefon, s.nume_sala as 'Nume Sala', e.denumire as Eveniment, e.data_eveniment as Data
	    FROM Clienti c
	    JOIN Evenimente e ON c.id_client = e.id_client
	    JOIN Sali s ON e.id_sala = s.id_sala;
    """
    create_treeview_with_query_results(main, query, conn, cursor)
    #messagebox.showinfo("Buton 6", "Ați apăsat butonul 6!")

# Functie pentru creearea celui de al saptelea query
def functie_7(main, conn, cursor):
    query = """
        SELECT nume as 'Nume Client'
        FROM Clienti 
        JOIN evenimente on Clienti.id_client = evenimente.id_client
        JOIN sali on evenimente.id_sala = sali.id_sala
        WHERE pret_pe_zi > (
            SELECT AVG(pret_pe_zi)
            FROM Sali
        );
    """
    create_treeview_with_query_results(main, query, conn, cursor)
    #messagebox.showinfo("Buton 7", "Ați apăsat butonul 7!")

# Functie pentru creearea celui de al optulea query
def functie_8(main, conn, cursor):
    query = """
        SELECT nume_furnizor as 'Nume Furnizor'
        FROM Furnizori
        JOIN evenimente_furnizori on evenimente_furnizori.id_furnizor = furnizori.id_furnizor
        JOIN evenimente on evenimente_furnizori.id_eveniment = evenimente.id_eveniment
        WHERE data_eveniment > ANY(
            SELECT data_eveniment
            FROM Evenimente
        );
    """
    create_treeview_with_query_results(main, query, conn, cursor)
    #messagebox.showinfo("Buton 8", "Ați apăsat butonul 8!")

# Functie pentru creearea celui de al noualea query
def functie_9(main, conn, cursor):
    query = """
        SELECT c.nume as Client, e.denumire AS Eveniment, s.pret_pe_zi as Pret
        FROM Clienti c
        JOIN Evenimente e ON c.id_client = e.id_client
        JOIN Sali s ON e.id_sala = s.id_sala
        WHERE s.pret_pe_zi = (
            SELECT MAX(pret_pe_zi)
            FROM Sali
        );
    """
    create_treeview_with_query_results(main, query, conn, cursor)
    #messagebox.showinfo("Buton 9", "Ați apăsat butonul 9!")

# Functie pentru creearea celui de al zecelea query
def functie_10(main, conn, cursor):
    root = tk.Toplevel(main)
    root.title("Afișare săli disponibile")
    
    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)
    
    # Etichetă și Entry pentru introducerea datei
    date_label = tk.Label(frame, text="Introduceți data (YYYY-MM-DD):", bg='lightblue')
    date_label.grid(row=0, column=0, pady=5)
    
    date_entry = tk.Entry(frame)
    date_entry.grid(row=0, column=1, pady=5)
    
    # Funcția care construiește query-ul și afișează rezultatele
    def submit_query():
        date = date_entry.get().strip()  # Obține data din Entry
        
        # Validare simplă pentru formatul datei
        try:
            # Încearcă să convertești șirul într-un obiect datetime
            valid_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            # Dacă formatul este greșit, afișează eroare
            messagebox.showerror("Eroare", "Data introdusă nu este validă. Folosiți formatul YYYY-MM-DD.")
            return
        
        query = f"""
            SELECT nume_sala as 'Nume Sala'
            FROM Sali
            WHERE id_sala NOT IN (
                SELECT id_sala
                FROM Evenimente
                WHERE data_eveniment = '{date}'
            );
        """
        
        # Apelează funcția de creare Treeview cu query-ul construit
        root.destroy()
        create_treeview_with_query_results(main, query, conn, cursor)
        
    
    # Buton pentru Submit
    submit_button = tk.Button(frame, text="Submit", command=submit_query)
    submit_button.grid(row=1, columnspan=2, pady=10)

    #messagebox.showinfo("Buton 10", "Ați apăsat butonul 10!")

#functie pentru crearea ferestrei principale
def create_window(main, conn, cursor):
    # Crearea ferestrei principale
    window = tk.Toplevel(main)
    window.title("Gestionare Sali Evenimente")
    window.state("zoomed") # Setează dimensiunea ferestrei
    
    frame = tk.Frame(window, bg='lightblue', height=600, width=600, bd=2, relief='raised')
    frame.place(in_=window, anchor='center', relx=.5, rely=.5)
    
    frameWindow = tk.Frame(frame, bg='lightblue')
    frameWindow.place(in_=frame, anchor='center', relx=.5, rely=.5)
    
    frameWindow.grid_columnconfigure(0, minsize=50)
    frameWindow.grid_columnconfigure(1, minsize=50)
    frameWindow.grid_columnconfigure(2, minsize=50)
    frameWindow.grid_columnconfigure(3, minsize=50)
    frameWindow.grid_rowconfigure(5, minsize=50)
    
   # Crearea fiecărui buton separat
    button1 = tk.Button(frameWindow, text="Afisare Locatii cu Evenimente", command= lambda : functie_1(window, conn, cursor))
    button1.grid(row=0, column=0, padx=10, pady=5)

    button2 = tk.Button(frameWindow, text="Afisare Servicii", command=lambda : functie_2(window, conn, cursor))
    button2.grid(row=1, column=0, padx=10, pady=5)

    button3 = tk.Button(frameWindow, text="Incasari Totale", command=lambda : functie_3(window, conn, cursor))
    button3.grid(row=2, column=0, padx=10, pady=5)

    button4 = tk.Button(frameWindow, text="Afisare Evenimente", command=lambda : functie_4(window, conn, cursor))
    button4.grid(row=3, column=0, padx=10, pady=5)

    button5 = tk.Button(frameWindow, text="Evenimente si lista furnizori", command=lambda : functie_5(window, conn, cursor))
    button5.grid(row=4, column=0, padx=10, pady=5)

    button6 = tk.Button(frameWindow, text="Info eveniment", command=lambda : functie_6(window, conn, cursor))
    button6.grid(row=0, column=3, padx=10, pady=5)

    button7 = tk.Button(frameWindow, text="Clienti cu evenimente peste medie", command=lambda : functie_7(window, conn, cursor))
    button7.grid(row=1, column=3, padx=10, pady=5)

    button8 = tk.Button(frameWindow, text="Furnizori utilizati recent", command=lambda : functie_8(window, conn, cursor))
    button8.grid(row=2, column=3, padx=10, pady=5)

    button9 = tk.Button(frameWindow, text="Top Client", command=lambda : functie_9(window, conn, cursor))
    button9.grid(row=3, column=3, padx=10, pady=5)

    button10 = tk.Button(frameWindow, text="Sali disponibile pentru o data anume", command=lambda : functie_10(window, conn, cursor))
    button10.grid(row=4, column=3, padx=10, pady=5)

    button11 = tk.Button(frameWindow, text="Baza de Date", command = lambda : create_gui(window, conn, cursor))
    button11.grid(row=6, columnspan=4, padx=10, pady=5)

        
    def on_closing():
        close_connection(conn, cursor)
        main.destroy()
    
    window.protocol("WM_DELETE_WINDOW", on_closing)

    window.mainloop()

def create_treeview_with_query_results(main, query, conn, cursor):
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        window = tk.Toplevel(main)
        window.title("Database OUTPUT")
        window.geometry("500x500")
        
        style = ttk.Style(window)

        style.configure("Treeview.Heading", background="red", foreground="black", font=("Arial", 10, "bold"))
                
        tree = ttk.Treeview(window, columns=columns, show="headings")
        tree.pack(fill=tk.BOTH, expand=True)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor=tk.CENTER) 
        
        for row in rows:
            tree.insert("", tk.END, values=row)
        
        #scrollbar = ttk.Scrollbar(window, orient=tk.VERTICAL, command=tree.yview)
        #tree.configure(yscroll=scrollbar.set)
        #scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def on_close():
            window.destroy()
        
        window.protocol("WM_DELETE_WINDOW", on_close)
        window.mainloop()
    
def create_main() :
    main = tk.Tk()
    main.title("Login")

    screen_width = main.winfo_screenwidth()
    screen_height = main.winfo_screenheight()

    mainWidth = int (screen_width / 2)
    mainHeight = int (screen_height / 2)


    x_offset = (screen_width / 2) - (mainWidth / 2)
    y_offset = (screen_height / 2) - (mainHeight / 2)

    main.geometry(f"{mainWidth}x{mainHeight}+{int(x_offset)}+{int(y_offset)}")
    main.minsize(400, 400)
    main.state('zoomed')

    frameMain = tk.Frame(main, bg='lightblue', height=400, width=400, bd=2, relief='raised')
    frameMain.place(in_=main, anchor='center', relx=.5, rely=.5)

    frame = tk.Frame(bg='lightblue',)
    #frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)
    #frame.pack(expand=True, fill="both", padx=20, pady=20)  # Add padding around the frame
    frame.place(in_=frameMain, anchor='center', relx=.5, rely=.5)


    # Username label and entry
    database_label = tk.Label(frame, text="Database:", bg='lightblue')
    database_entry = tk.Entry(frame)

    username_label = tk.Label(frame, text="Username:", bg='lightblue')
    username_entry = tk.Entry(frame)

    # Password label and entry
    password_label = tk.Label(frame, text="Password:", bg='lightblue')
    password_entry = tk.Entry(frame, show="*")
    password_entry.bind('<Return>', login);

    database_label.grid(row=0, columnspan=2, sticky="", pady=5, padx=10)
    database_entry.grid(row=1, columnspan=2, pady=5, padx=10)

    username_label.grid(row=2, columnspan=2, sticky="", pady=5, padx=10)
    username_entry.grid(row=3, columnspan=2, pady=5, padx=10)

    password_label.grid(row=4, columnspan=2, sticky="", pady=5, padx=10)
    password_entry.grid(row=5, columnspan=2, pady=5, padx=10)
    
    def on_login(event = None):
            database = database_entry.get()
            username = username_entry.get()
            password = password_entry.get()
            login(main, username, password, database)
    # Login button
    login_button = tk.Button(frame, text="Login", command = on_login)
    login_button.grid(row=6, columnspan=2, pady=20)
    
    password_entry.bind('<Return>', on_login)

    main.mainloop()

# Apelăm funcția pentru a porni aplicația
create_main() 