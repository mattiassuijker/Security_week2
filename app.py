import os.path
import sys
import csv
from flask_bcrypt import Bcrypt
from flask_bcrypt import check_password_hash
from flask import Flask, render_template, session, flash, jsonify, request, redirect, send_file
from cryptography.fernet import Fernet
from lib.tablemodel import DatabaseModel
from lib.demodatabase import create_demo_database
from flask_session import Session


# This demo glues a random database and the Flask framework. If the database file does not exist,
# a simple demo dataset will be created.
LISTEN_ALL = "0.0.0.0"
FLASK_IP = LISTEN_ALL
FLASK_PORT = 81
FLASK_DEBUG = True

app = Flask(__name__)
bcrypt = Bcrypt(app)
# This command creates the "<application directory>/databases/testcorrect_vragen.db" path
DATABASE_FILE = os.path.join(app.root_path, 'databases', 'testcorrect_vragen.db')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Check if the database file exists. If not, create a demo database
if not os.path.isfile(DATABASE_FILE):
    print(f"Could not find database {DATABASE_FILE}, creating a demo database.")
    create_demo_database(DATABASE_FILE)
dbm = DatabaseModel(DATABASE_FILE)

# Main route that shows a list of tables in the database
# Note the "@app.route" decorator. This might be a new concept for you.
# It is a way to "decorate" a function with additional functionality. You
# can safely ignore this for now - or look into it as it is a really powerful
# concept in Python.

class PasswordManager:
    def __init__(self):
        self.key = None
        self.password_file = None
        self.password_dict = {}

    def create_key(self, path):
        self.key = Fernet.generate_key()
        with open(path, 'wb') as f:
            f.write(self.key)
            
    def load_key(self, path):
        with open(path, 'rb') as f:
            self.key = f.read()

    def load_password_file(self,path):
        self.password_file = path

        with open(path, 'r') as f:
            for line in f:
                site, encrypted = line.split(":")
                self.password_dict[site] = Fernet(self.key).decrypt(encrypted.encode())
                

@app.route("/")
def index():
    tables = dbm.get_table_list()
    return render_template("home.html", table_list=tables, database_file=DATABASE_FILE, type=session.get("type"))



@app.route("/create_question")
def create_page():
    rows_leerdoelen = dbm.get_table_content(table_name = 'leerdoelen')
    rows_auteurs = dbm.get_table_content(table_name = 'auteurs')
    return render_template("create.html", leerdoelen=rows_leerdoelen[0],auteurs=rows_auteurs[0])
    
@app.route('/create_question/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        question = request.form['vraag']
        leerdoel = request.form['leerdoel']
        auteur = request.form['auteur']
        if not question:
            return render_template('create.html')
        else:
            dbm.create_vraag(question, leerdoel, auteur)

    return table_content(table_name='vragen')


@app.route("/create_user")
def create_page2():
    rows_type = dbm.get_table_content(table_name = 'users')
    return render_template("user.html", type=rows_type[0],)
    
@app.route('/create_user/', methods=('GET', 'POST'))
def user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        type = request.form['type']
        #encpass = bcrypt.generate_password_hash(password)
        if not type:
            return render_template('users.html')
        else:
            dbm.create_user(username, password, type)

    return table_content(table_name='users')    

@app.route("/inlog")
def inlog_page():
    tables = dbm.get_table_list()
    return render_template("inlog.html", table_list=tables, database_file=DATABASE_FILE)

@app.route("/inlog/", methods=('GET', 'POST'))
def inlog():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if dbm.login(username, password) == False:
            return redirect("/inlog")
        else:
            level = dbm.login(username, password)
            session["type"] = level
    return redirect("/")

@app.route("/logout")
def logout():
    session["type"] = 0
    return redirect("/")

@app.route("/csv/<table_name>")
def data_to_csv(table_name=None):
    # Connect to the database and retrieve the data
    data = dbm.get_table_content(table_name)
    print(data[0])
    # Open the CSV file in write mode
    csvfile = open('data.csv', 'w', newline='')

    # Create a CSV writer object
    writer = csv.writer(csvfile)

    # Write the data to the CSV file
    for row in data[0]:
        writer.writerow(row)
    
    # Close the CSV file
    csvfile.close()
    return redirect("/")
    
@app.route('/download')
def download_csv():
  return send_file('data.csv', mimetype='text/csv')

# The table route displays the content of a table
@app.route("/table_details/<table_name>",  methods=['GET', 'POST'])
def table_content(table_name=None):
    if not table_name:
        return "Missing table name", 400  # HTTP 400 = Bad Request
    else:
        print(session.get("type"))
        rows, column_names = dbm.get_table_content(table_name)
        leerdoelen = dbm.alle_leerdoelen()
        return render_template(
            "table_details.html", rows=rows, columns=column_names, table_name=table_name, leerdoelen=leerdoelen, type=session.get("type")
        )

@app.route("/wijzigen", methods=['POST', 'GET'])
def wijzig_table():
    dbm.change_table_row(request.form.get('vraag'), request.form.get('id'))
    if request.method == "POST":
        return redirect("/table_details/vragen", code=302)

@app.route("/wijzigenleerdoel", methods=['POST', 'GET'])
def wijzig_leerdoel_table():
    dbm.change_leerdoel_table_row(request.form.get('vraag'), request.form.get('id'), request.form.get('leerdoel'))
    if request.method == "POST":
        return redirect("/table_details/vragen", code=302)

@app.route("/wijzigmedewerker", methods=['POST', 'GET'])
def wijzig_medewerker():
    dbm.change_medewerker_table_row(request.form.get('medewerker'), request.form.get('medewerkerid'))
    if request.method == "POST":
        return redirect("/table_details/auteurs", code=302)

@app.route("/verwijder", methods=['POST', 'GET'])
def delete_table():
    dbm.delete_table_row(request.form.get('id'))
    if request.method == "POST":
        return redirect("/table_details/vragen", code=302)

@app.route('/alle-gegevens', methods=['GET', 'POST'])
def alle_gegevens():
    table_name = 'vragen'
    query = 'alles'
    rows, column_names = dbm.alles_table_row()
    return render_template("mistakes.html", query=query, rows=rows, columns=column_names, table_name=table_name, type=session.get("type"))

@app.route('/alle-auteurs', methods=['GET', 'POST'])
def alle_auteurs():
    table_name = 'auteurs'
    query = 'auteurs'
    rows, column_names = dbm.auteurs_table_row()
    return render_template("mistakes.html", query=query, rows=rows, columns=column_names, table_name=table_name, type=session.get("type"))

@app.route('/html-fouten', methods=['GET', 'POST'])
def html_fouten():
    table_name = 'vragen'
    query = 'html'
    rows, column_names = dbm.html_table_row()
    return render_template("mistakes.html", query=query, rows=rows, columns=column_names, table_name=table_name, type=session.get("type"))

@app.route('/medewerker-fout', methods=['GET', 'POST'])
def medewerker_fout():
    table_name = 'auteurs'
    query = 'medewerker'
    rows, column_names = dbm.medewerker_table_row()
    return render_template("mistakes.html", query=query, rows=rows, columns=column_names, table_name=table_name, type=session.get("type"))

@app.route('/geen-leerdoel', methods=['GET', 'POST'])
def geen_leerdoel():
    table_name = 'vragen'
    query = 'leerdoel'
    leerdoelen = dbm.alle_leerdoelen()
    rows, column_names = dbm.leerdoel_table_row()
    return render_template("mistakes.html", leerdoelen=leerdoelen, rows=rows, query=query, columns=column_names, table_name=table_name, type=session.get("type"))

#404 error pagina
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host=FLASK_IP, port=FLASK_PORT, debug=FLASK_DEBUG)