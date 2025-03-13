import mysql.connector

# Conexiune la serverul MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password"  # Înlocuiește cu parola ta
)

cursor = conn.cursor()

# Crearea bazei de date
cursor.execute("CREATE DATABASE IF NOT EXISTS app")
cursor.execute("USE app")

# Crearea tabelelor
tables_sql = [
    """
    CREATE TABLE IF NOT EXISTS Clienti (
        id_client INT AUTO_INCREMENT PRIMARY KEY,
        nume VARCHAR(100),
        telefon VARCHAR(15),
        email VARCHAR(100),
        adresa VARCHAR(255)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Sali (
        id_sala INT AUTO_INCREMENT PRIMARY KEY,
        nume_sala VARCHAR(100),
        capacitate INT,
        locatie VARCHAR(255),
        pret_pe_zi DECIMAL(10, 2)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Evenimente (
        id_eveniment INT AUTO_INCREMENT PRIMARY KEY,
        denumire VARCHAR(100),
        data_eveniment DATE,
        id_client INT,
        id_sala INT,
        nr_invitați INT,
        CONSTRAINT fk_client FOREIGN KEY (id_client) REFERENCES Clienti(id_client),
        CONSTRAINT fk_sala FOREIGN KEY (id_sala) REFERENCES Sali(id_sala)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Furnizori (
        id_furnizor INT AUTO_INCREMENT PRIMARY KEY,
        nume_furnizor VARCHAR(100),
        tip_serviciu VARCHAR(100),
        contact_furnizor VARCHAR(100),
        telefon_furnizor VARCHAR(15)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Evenimente_Furnizori (
        id_eveniment INT,
        id_furnizor INT,
        PRIMARY KEY (id_eveniment, id_furnizor),
        CONSTRAINT fk_eveniment FOREIGN KEY (id_eveniment) REFERENCES Evenimente(id_eveniment),
        CONSTRAINT fk_furnizor FOREIGN KEY (id_furnizor) REFERENCES Furnizori(id_furnizor)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Servicii (
        id_serviciu INT AUTO_INCREMENT PRIMARY KEY,
        nume_serviciu VARCHAR(100),
        descriere_serviciu VARCHAR(255),
        pret_serviciu DECIMAL(10, 2),
        id_furnizor INT,
        CONSTRAINT fk_furnizor1 FOREIGN KEY (id_furnizor) REFERENCES Furnizori(id_furnizor)
    )
    """
]

for sql in tables_sql:
    cursor.execute(sql)

# Inserarea datelor
data_insert = [
    # Inserturi pentru Clienti
    """
    INSERT INTO Clienti (nume, telefon, email, adresa)
    VALUES 
    ('Ion Popescu', '0712345678', 'ion.popescu@example.com', 'Str. Principala, Nr. 1'),
    ('Maria Ionescu', '0723456789', 'maria.ionescu@example.com', 'Str. Lalelelor, Nr. 10'),
    ('George Marin', '0734567890', 'george.marin@example.com', 'Str. Libertatii, Nr. 5'),
    ('Ana Dumitru', '0745678901', 'ana.dumitru@example.com', 'Str. Garii, Nr. 20'),
    ('Vasile Luca', '0756789012', 'vasile.luca@example.com', 'Str. Soarelui, Nr. 15')
    """,
    # Inserturi pentru Sali
    """
    INSERT INTO Sali (nume_sala, capacitate, locatie, pret_pe_zi)
    VALUES 
    ('Sala Mare', 200, 'Centru', 1500.50),
    ('Sala Albastra', 100, 'Periferie', 800.00),
    ('Sala Verde', 150, 'Zona Industriala', 1200.75),
    ('Sala Eleganta', 300, 'Centru', 2000.00),
    ('Sala Business', 50, 'Centru', 500.00)
    """,
    # Inserturi pentru Furnizori
    """
    INSERT INTO Furnizori (nume_furnizor, tip_serviciu, contact_furnizor, telefon_furnizor)
    VALUES 
    ('Catering Premium', 'Catering', 'office@cateringpremium.com', '0765432109'),
    ('Florarie Luxury', 'Florist', 'luxury@florarie.com', '0754321098'),
    ('DJ Sound Pro', 'Muzica', 'contact@soundpro.com', '0743210987'),
    ('Decor Magic', 'Decorare', 'info@decormagic.com', '0732109876'),
    ('Photo Moments', 'Fotografie', 'contact@photomoments.com', '0721098765')
    """,
    # Inserturi pentru Evenimente
    """
    INSERT INTO Evenimente (denumire, data_eveniment, id_client, id_sala, nr_invitați)
    VALUES 
    ('Nunta Popescu', '2024-06-15', 1, 1, 150),
    ('Botez Ionescu', '2024-07-20', 2, 2, 100),
    ('Conferinta Tehnologica', '2024-09-10', 3, 5, 50),
    ('Aniversare Ana', '2024-08-01', 4, 3, 120),
    ('Lansare Carte', '2024-11-05', 5, 4, 75)
    """,
    # Inserturi pentru Evenimente_Furnizori
    """
    INSERT INTO Evenimente_Furnizori (id_eveniment, id_furnizor)
    VALUES 
    (1, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (4, 5)
    """,
    # Inserturi pentru Servicii
    """
    INSERT INTO Servicii (nume_serviciu, descriere_serviciu, pret_serviciu, id_furnizor)
    VALUES 
    ('Meniu Deluxe', 'Meniu complet cu 3 feluri de mâncare', 250.00, 1),
    ('Aranjamente Florale', 'Buchete personalizate pentru mese', 500.00, 2),
    ('DJ Profesional', 'Muzică pentru petrecere', 1500.00, 3),
    ('Decor Elegant', 'Decor modern pentru sală', 1000.00, 4),
    ('Album Foto', 'Album profesional cu poze de eveniment', 750.00, 5)
    """
]

# Executarea inserțiilor
for insert_sql in data_insert:
    cursor.execute(insert_sql)

# Crearea bazei de date pentru login corespunzator codului python
cursor.execute("CREATE DATABASE IF NOT EXISTS login")
cursor.execute("USE login")

# Crearea tabelei utilizatori
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS utilizatori (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user VARCHAR(100),
        password VARCHAR(100)
    ) 
    """
)

# Inserarea de user si parola pentru login root/password
cursor.execute( "INSERT INTO utilizatori VALUES ('root', 'password')")

conn.commit()

# Închidere conexiune
cursor.close()
conn.close()

print("Baza de date, tabelele și toate datele au fost inserate cu succes!")