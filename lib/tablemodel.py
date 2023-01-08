from multiprocessing import connection
from cryptography.fernet import Fernet
from flask_bcrypt import Bcrypt
from flask_bcrypt import check_password_hash
from flask import Flask, render_template, session, flash, jsonify, request, redirect
import os
import sqlite3
import locale


app = Flask(__name__)
bcrypt = Bcrypt(app)
class DatabaseModel:
    """This class is a wrapper around the sqlite3 database. It provides a simple interface that maps methods
    to database queries. The only required parameter is the database file."""

    def __init__(self, database_file):
        self.database_file = database_file
        if not os.path.exists(self.database_file):
            raise FileNotFoundError(f"Could not find database file: {database_file}")

    # Using the built-in sqlite3 system table, return a list of all tables in the database
    def get_table_list(self):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        return tables
        
    def create_vraag(self, question,leerdoel, auteur):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM vragen ORDER BY id DESC LIMIT 1")
        char = cursor.fetchall()
        list = char[0]
        id = list[0] + 1
        cursor.execute(f"INSERT INTO vragen (id, leerdoel,vraag, auteur) VALUES ('{id}', '{leerdoel}', '{question}', '{auteur}')")
        conn.commit()
        return 

    # in de function create_user word een wachtwoord gemaakt en die wordt ook gelijkt encrypted door encpass
    # en met de library bcrypt
    def create_user(self, user,password, type):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()
        id = 3
        encpass = bcrypt.generate_password_hash(password).decode()
        password = encpass
        cursor.execute(f"INSERT INTO users (id, username,password,type) VALUES ('{id}', '{user}', '{encpass}', '{type}')")
        conn.commit()
        return 
    # De login functie zorgt ervoor dat er ingelogd kan worden en met de if statement wordt er nagekeken of 
    # de encrypted wachtwoord overeen komt met en ingevoerde wachtwoord van de user.
    def login(self, username, password):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM users WHERE username='{username}'")
        level_block = cursor.fetchone()
        if not level_block or not bcrypt.check_password_hash(level_block[2], password):
            return False
        else:
            return level_block[0]


    # Given a table name, return the rows and column names
    def get_table_content(self, table_name):
        cursor = sqlite3.connect(self.database_file).cursor()
        if (table_name == 'vragen'):
            cursor.execute(f"SELECT vragen.id, leerdoelen.leerdoel, vragen.vraag, voornaam || ' ' || achternaam AS auteurnaam FROM vragen LEFT JOIN leerdoelen ON vragen.leerdoel = leerdoelen.id LEFT JOIN auteurs ON vragen.auteur = auteurs.id LIMIT 70")
        else:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 40")
        # An alternative for this 2 var approach is to set a sqlite row_factory on the connection
        table_headers = [column_name[0] for column_name in cursor.description]
        table_content = cursor.fetchall()
                
        # Note that this method returns 2 variables!
        return table_content, table_headers

    def delete_table_row(self, id):
        connection = sqlite3.connect(self.database_file)
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM vragen WHERE id = '{id}' ")
        connection.commit()
        cursor.close()

    def change_table_row(self, vraag, id):
        connection = sqlite3.connect(self.database_file)
        cursor = connection.cursor()
        cursor.execute(f"UPDATE vragen SET vraag = '{vraag}' WHERE id = '{id}' ")
        connection.commit()
        cursor.close()

    def html_table_row(self):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(f"SELECT vragen.id, leerdoelen.leerdoel, vragen.vraag, voornaam || ' ' || achternaam AS auteurnaam FROM vragen LEFT JOIN leerdoelen ON vragen.leerdoel = leerdoelen.id LEFT JOIN auteurs ON vragen.auteur = auteurs.id WHERE vraag LIKE '%<%' OR vraag LIKE '%>%'")
        table_headers = [column_name[0] for column_name in cursor.description]
        table_content = cursor.fetchall()
        return table_content, table_headers

    def medewerker_table_row(self):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(f"SELECT * FROM auteurs WHERE medewerker NOT IN (0, 1)")
        table_headers = [column_name[0] for column_name in cursor.description]
        table_content = cursor.fetchall()
        return table_content, table_headers

    def leerdoel_table_row(self):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(f"SELECT vragen.id, leerdoelen.leerdoel, vragen.vraag, voornaam || ' ' || achternaam AS auteurnaam FROM vragen LEFT JOIN leerdoelen ON vragen.leerdoel = leerdoelen.id LEFT JOIN auteurs ON vragen.auteur = auteurs.id WHERE vragen.leerdoel IS NULL OR ''")
        table_headers = [column_name[0] for column_name in cursor.description]
        table_content = cursor.fetchall()
        return table_content, table_headers

    def alles_table_row(self):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(f"SELECT vragen.id, leerdoelen.leerdoel, vragen.vraag, voornaam || ' ' || achternaam AS auteurnaam FROM vragen LEFT JOIN leerdoelen ON vragen.leerdoel = leerdoelen.id LEFT JOIN auteurs ON vragen.auteur = auteurs.id LIMIT 70")
        table_headers = [column_name[0] for column_name in cursor.description]
        table_content = cursor.fetchall()
        return table_content, table_headers

    def auteurs_table_row(self):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(f"SELECT * FROM auteurs")
        table_headers = [column_name[0] for column_name in cursor.description]
        table_content = cursor.fetchall()
        return table_content, table_headers

    def alle_leerdoelen(self):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(f"SELECT id, leerdoel FROM leerdoelen")
        leerdoelen = cursor.fetchall()
        return leerdoelen

    def change_leerdoel_table_row(self, vraag, id, leerdoel):
        connection = sqlite3.connect(self.database_file)
        cursor = connection.cursor()
        cursor.execute(f"UPDATE vragen SET vraag = '{vraag}', leerdoel = '{leerdoel}' WHERE id = '{id}' ")
        connection.commit()
        cursor.close()

    def change_medewerker_table_row(self, medewerker, id):
        connection = sqlite3.connect(self.database_file)
        cursor = connection.cursor()
        cursor.execute(f"UPDATE auteurs SET medewerker = '{medewerker}' WHERE id = '{id}' ")
        connection.commit()
        cursor.close()


