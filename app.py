from flask import Flask, render_template, redirect, request, flash
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "cours_feedback"
mysql = MySQL(app)

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/signup", methods = ["POST"])
def signup():
    if request.method == "POST":
        matricule = request.form["matricule"]
        nom = request.form["nom"]
        prenom = request.form["prenom"]
        email = request.form["email"]
        telephone = request.form["telephone"]
        niveau = request.form["niveau"]
        mot_de_pass = request.form["mot_de_pass"]
        rep_mot_de_pass = request.form["mot_de_pass"]

        if not matricule or not nom or not prenom or not email or not telephone or not niveau or not mot_de_pass or not rep_mot_de_pass:
            flash("obligatoire de remplire toute les fields!", "error")
            return render_template("signup.html")

        if rep_mot_de_pass != mot_de_pass:
            flash("mots de passe ne sont pas égaux!")
            return render_template("signup.html")

        if len(mot_de_pass < 6):
            flash("le mot de pass doit avoir 6 charachteres!", "erreur")
            return render_template("signup.html")


        #est-ce que la matricule est valable ?
        cur = mysql.connection.curso()
        cur.execute("SELECT * FROM etudiants WHERE matricule = %s ", (matricule))
        matricule_e = cur.fetchone()
        if matricule_e :
            flash("cette matricule existe déja!", "erreur")
            cur.close()
            return render_template("signup.html")

        #est-ce-que l'email est valable ?
        cur.execute("SELECT * FROM etudiants WHERE email = %s ", (email))
        email_e = cur.fetchone()
        if email_e:
            flash("email est utilisé !", "erreur")
            cur.close()
            return render_template("signup.html")

        #est-ce-que le numéro de telephone  est valable ?
        cur.execute("SELECT * FROM etudiants WHERE num_telephone = %s ", (telephone))
        telephone_e =  cur.fetchone()
        if telephone_e:
            flash("le numéro du telephone est utilisé", "erreur")
            cur.close()
            return render_template("signup.html")

        



        return render_template("login.html")

@app.route("/login", methods = ["request"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        mot_de_pass = request.form["mot_de_pass"]

        return render_template("home.html")

@app.route("/formulaire_cours/<cours_code>", )
def formulaire_cours(cours_code):
    cur = mysql.conection.cursor()
    cur.execute("")
    data = cur.fetchall()
    cur.close()