from multiprocessing import connection
import os
import sqlite3


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
        cursor.execute(f"SELECT * FROM vragen WHERE vraag LIKE '%<%' OR vraag LIKE '%>%'")
        table_headers = [column_name[0] for column_name in cursor.description]
        table_content = cursor.fetchall()
        return table_content, table_headers
