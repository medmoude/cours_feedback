from flask import Flask, render_template, redirect, request, flash
from flask_mysqldb import MySQL

app = Flask(__name__)

app.secret_key = "medmoud"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "admin"
app.config["MYSQL_DB"] = "feedback_cours"
mysql = MySQL(app)


@app.route("/")
def index():
    return render_template("home.html")


# Route d'inscription
@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        matricule = request.form["matricule"]
        nom = request.form["nom"]
        prenom = request.form["prenom"]
        email = request.form["email"]
        code_dep = request.form["code_dep"]
        mot_de_pass = request.form["mot_de_pass"]
        confirm_mot_de_pass = request.form["confirm_mot_de_pass"]  # Corrected variable name

        # Verification manual
        if not matricule or not nom or not prenom or not email or not code_dep or not mot_de_pass or not confirm_mot_de_pass:
            flash('Tous les champs sont obligatoires !', 'error')
            return render_template("signup.html")

        if confirm_mot_de_pass != mot_de_pass:
            flash("Les mots de passe ne correspondent pas", "error")
            return render_template("signup.html")

        if len(mot_de_pass) < 6:
            flash("Le mot de passe doit comporter au moins 6 caractères.", "error")
            return render_template("signup.html")

        # Is the matricule valid?
        cur = mysql.connection.cursor()  # Fixed cursor method typo
        cur.execute("SELECT * FROM etudiants WHERE matricule = %s", (matricule,))
        matricule_e = cur.fetchone()
        if matricule_e:
            flash("Cette matricule existe déjà", "error")
            return render_template("signup.html")

        # Is the email valid?
        cur.execute("SELECT * FROM etudiants WHERE email = %s", (email,))
        email_e = cur.fetchone()
        if email_e:
            flash("L'email est déjà enregistré !", "error")
            return render_template("signup.html")



        cur.execute("""
        INSERT INTO etudiants (matricule, nom, prenom, email, mot_de_pass, code_dep) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """,(matricule, nom, prenom, email, mot_de_pass, code_dep))
        mysql.connection.commit()

        # Successful signup
        flash("Inscription réussie ! Vous pouvez maintenant vous connecter", "success")
        return render_template("login.html")

    return render_template('signup.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        mot_de_pass = request.form["mot_de_pass"]

        if not email or not mot_de_pass:
            flash('Tous les champs sont obligatoires !', 'error')
            return render_template("login.html")

        # Verify if the email and password exist
        cur = mysql.connection.cursor()
        cur.execute("SELECT email, mot_de_pass FROM etudiants WHERE email = %s AND mot_de_pass = %s",
                    (email, mot_de_pass))
        user = cur.fetchone()
        cur.close()

        if user:
            return redirect("/")
        else:
            flash("Email ou mot de passe incorrect", "error")
            return render_template("login.html")
    return render_template("login.html")


@app.route("/formulaire_cours/<cours_code>", )
def formulaire_cours(cours_code):
    cur = mysql.conection.cursor()
    cur.execute("")
    data = cur.fetchall()
    cur.close()

if __name__ == "__main__":
    app.run(debug=True)

