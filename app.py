from flask import Flask, render_template, redirect, request
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = ""
mysql = MySQL(app)

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/signup")
def signup():
    matricule = request.form["matricule"]
    nom = request.form["nom"]
    prenome = request.form["prenom"]
    email = request.form["email"]
    telephone = request.form["telephone"]
    niveua = request.form["niveau"]
    mot_de_pass = request.form["mot_de_pass"]

