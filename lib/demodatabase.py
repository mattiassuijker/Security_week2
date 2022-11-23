import sqlite3
from sqlite3 import OperationalError


# This function creates a demo database given a filename.  The demo database contains
# a single table called 'demo' with three columns: id, name and email.
def create_demo_database(database_file):
    try:
        connection = sqlite3.connect(database_file)
    except OperationalError as e:
        print(f"Error opening database file {database_file}")
        raise e

    cursor = connection.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS demo (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, email TEXT)"
    )

    for pair in [
        ("Veysel", "Altinok", "v.k.altinok@hr.nl"),
        ("Diederik", "de Vries", "d.de.vries@hr.nl"),
        ("Mark", "Otting", "m.b.otting@hr.nl"),
    ]:
        cursor.execute(
            "INSERT INTO demo (first_name, last_name, email) VALUES (?, ?, ?)", pair
        )
    connection.commit()
    connection.close()
