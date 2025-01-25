from flask import Flask, render_template, redirect, request, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

app.config["MYSQL_HOST"] = os.getenv('MYSQL_HOST')
app.config["MYSQL_USER"] = os.getenv('MYSQL_USER')
app.config["MYSQL_PASSWORD"] = os.getenv('MYSQL_PASSWORD')
app.config["MYSQL_DB"] = os.getenv('MYSQL_DB')
mysql = MySQL(app)

def is_logged_in():
    return 'user_id' in session


# the main route
@app.route("/")
def index():
    if not is_logged_in():
        return redirect(url_for('login'))

    #traitement des semestres impaires
    cur = mysql.connection.cursor()
    query_sem_impaire = """
    SELECT cours_code, intitulé_cours
    FROM etudiants
    JOIN departement ON etudiants.code_dep = departement.code_dep
    JOIN niveau ON departement.code_niv = niveau.code_niv
    JOIN semestre ON niveau.code_niv = semestre.code_niv
    JOIN cours ON semestre.code_sem = cours.code_sem
    WHERE etudiants.matricule = %s
    AND semestre.code_sem IN (1, 3, 5)
    AND (
        niveau.intitulé_niv = 'L1'  -- Filter for L1 level students
        -- If student is from SEA, exclude courses starting with SDID
        OR
        (departement.intitulé_dep LIKE %s AND cours.cours_code NOT LIKE %s)
        OR
        -- If student is from SDID, exclude courses starting with SEA
        (departement.intitulé_dep LIKE %s AND cours.cours_code NOT LIKE %s)
    );
    """

    if session['user_id']:  # Ensure the user_id is set
        sea_pattern = "SEA%"
        sdid_pattern = "SDID%"
        
        cur.execute(query_sem_impaire, (session['user_id'], sea_pattern, "SDID%", sdid_pattern, "SEA%"))
        cours_sem_impaire = cur.fetchall()
    else:
        cours_sem_impaire = []

    #traitement des semestres paire
    query_sem_paire = """
    SELECT cours_code, intitulé_cours
    FROM etudiants
    JOIN departement ON etudiants.code_dep = departement.code_dep
    JOIN niveau ON departement.code_niv = niveau.code_niv
    JOIN semestre ON niveau.code_niv = semestre.code_niv
    JOIN cours ON semestre.code_sem = cours.code_sem
    WHERE etudiants.matricule = %s
    AND semestre.code_sem IN (2, 4, 6)
    AND (
        niveau.intitulé_niv = 'L1'  -- Filter for L1 level students
        -- If student is from SEA, exclude courses starting with SDID
        OR
        (departement.intitulé_dep LIKE %s AND cours.cours_code NOT LIKE %s)
        OR
        -- If student is from SDID, exclude courses starting with SEA
        (departement.intitulé_dep LIKE %s AND cours.cours_code NOT LIKE %s)
    );
    """

    if session['user_id']:  # Ensure the user_id is set
        sea_pattern = "SEA%"
        sdid_pattern = "SDID%"
        
        cur.execute(query_sem_paire, (session['user_id'], sea_pattern, "SDID%", sdid_pattern, "SEA%"))
        cours_sem_paire = cur.fetchall()
    else:
        cours_sem_paire = []
    

    # Get list of courses the student has already evaluated
    evaluated_courses = set()
    cur.execute("""
        SELECT cours_code FROM evaluer WHERE matricule = %s
    """, (session['user_id'],))
    for row in cur.fetchall():
        evaluated_courses.add(row[0])

    cur.close()
    
    mois = datetime.now().month
    if mois in [10, 11, 12, 1, 2]:
        return render_template("home.html", cours=cours_sem_impaire, evaluated_courses=evaluated_courses)
    else:
        return render_template("home.html", cours=cours_sem_paire, evaluated_courses=evaluated_courses)



# Login route
@app.route("/login", methods=["POST", "GET"])
def login():
    if is_logged_in():
        return redirect(url_for('index'))

    if request.method == "POST":
        email = request.form["email"]
        mot_de_pass = request.form["mot_de_pass"]

        if not email or not mot_de_pass:
            flash('Tous les champs sont obligatoires !', 'error')
            return render_template("login.html")

        # Verify if the email and password exist
        cur = mysql.connection.cursor()
        cur.execute("SELECT matricule, nom_prenom, email, mot_de_pass FROM etudiants WHERE email = %s AND mot_de_pass = %s ",
                    (email, mot_de_pass))
        user = cur.fetchone()

        if user:
            session["user_id"] = user[0]  # Store matricule (user_id) in session
            session["user_nom_prenom"] = user[1]
            flash("login succée", "success")
            return redirect(url_for("index"))

        else:
            flash("Email introuvable", "error")
            return render_template("login.html")
    return render_template("login.html")


# Logout route
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for('login'))


# Profile route
@app.route("/profile/<user_id>")
def profile(user_id):
    if is_logged_in():
        if user_id == str(session['user_id']):
            cur = mysql.connection.cursor()
            cur.execute("""
                        SELECT matricule, nom_prenom , email, intitulé_dep
                        FROM etudiants 
                        JOIN departement ON etudiants.code_dep = departement.code_dep
                        WHERE etudiants.matricule = %s ;
                    """, (user_id,))
            user_data = cur.fetchone()
            cur.close()
            return render_template("profile.html", user_data=user_data)
    return "vous ne pouvez pas accéder ce profile"


# Modifier Profile_rec route
@app.route('/modifier_profile_rec/<user_id>', methods=["GET", "POST"])
def modifier_profile_rec(user_id):
    if is_logged_in():
        if user_id == str(session['user_id']):
            cur1 = mysql.connection.cursor()
            cur1.execute("""
                    SELECT matricule, nom_prenom, email, intitulé_dep
                    FROM etudiants 
                    JOIN departement ON etudiants.code_dep = departement.code_dep
                    WHERE etudiants.matricule = %s ;
                """, (user_id,))
            user_data = cur1.fetchone()
            cur1.close()

            cur2 = mysql.connection.cursor()
            cur2.execute("SELECT * FROM departement ORDER BY code_niv")
            departements = cur2.fetchall()
            cur2.close()

            return render_template('modifier_profile_rec.html', user_data=user_data, departements=departements)
        else:
            return redirect(url_for('profile', user_id=user_id))
    return redirect(url_for('login'))


# Modifier Profile Save route
@app.route("/modifier_profile/<user_id>", methods = ["POST", "GET"])
def modifier_profile(user_id):
    if is_logged_in():
        if user_id == str(session['user_id']):
            ancien_matricule = request.form["ancien_matricule"]
            matricule = request.form["matricule"]
            nom = request.form["nom"]
            prenom = request.form["prenom"]
            ancien_email = request.form["ancien_email"]
            email = request.form["email"]
            code_dep = request.form["code_dep"]

            if (ancien_matricule != matricule) or (ancien_email != email) :

                cur = mysql.connection.cursor()
                cur.execute("""
                    SELECT * FROM etudiants WHERE matricule = %s OR email = %s;
                """, (matricule, email))
                user = cur.fetchone()
                cur.close()

                if user:
                    flash('Email ou matricule existe', 'error')
                    return redirect(url_for('modifier_profile_rec', user_id=user_id))
            else:
                cur = mysql.connection.cursor()
                cur.execute("""
                    UPDATE etudiants SET nom = %s, prenom = %s, email = %s, code_dep = %s
                    WHERE matricule = %s
                """, (nom, prenom, email, code_dep, matricule))

                mysql.connection.commit()
                cur.close()
                return redirect(url_for('profile', user_id=matricule))
    return "Vous ne pouvez pas modifier ce profile"

# Formulaire Cours route

@app.route("/formulaire_cours/<cours_code>")
def formulaire_cours(cours_code):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM cours WHERE cours_code = %s ", (cours_code,))
    cours = cur.fetchone()
    cur.close()

    return render_template("formulaire.html", cours_code=cours_code, cours = cours)


@app.route('/insert_formulaire/<cours_code>', methods = ["POST", "GET"])
def insert_formulaire(cours_code):
    if request.method == "POST":

        matricule = session['user_id']
        v_1 = int(request.form['preparation'])
        print(type(v_1))
        v_2 = int(request.form['aide_enseignant'])
        v_4 = int(request.form['methodes_enseignement'])
        v_5 = int(request.form['supports_ped'])
        v_6 = int(request.form['methode_evaluation'])
        v_7 = int(request.form['retours_clarite_utilite'])
        v_8 = int(request.form['Cours_organisation'])
        v_9 = int(request.form['Cours_benefices'])
        v_10 = int(request.form['efficacite_cours'])
        v_11= int(request.form['importance_utilite'])
        v_12= int(request.form['environnement'])
        v_13= int(request.form['statisfaction_des_objectifs'])
        v_14= int(request.form['recommendation'])
        v_15= int(request.form['exp_global'])
        commentaire = request.form['feedback']
        values = [v_1,v_2,v_4,v_5,v_6,v_7,v_8,v_9,v_10,v_11,v_12,v_13,v_14,v_15]
        note_final = sum(values)/len(values)

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO evaluer (matricule, cours_code, evaluation, commentaire) 
            VALUES (%s, %s, %s, %s)
        """, (matricule, cours_code, note_final, commentaire))
        mysql.connection.commit()
        return redirect(url_for('index'))


@app.route("/visualisation")
def visualisation ():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT intitulé_cours, AVG(evaluation) AS avg_evaluation 
        FROM evaluer 
        JOIN cours ON evaluer.cours_code = cours.cours_code
        GROUP BY intitulé_cours;
    """)
    evaluation_data = cur.fetchall()

    return render_template('visualisation.html', evaluation_data = evaluation_data)


@app.route('/chart-data')
def chart_data():
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT c.intitulé_cours, AVG(ev.evaluation) AS average_score
        FROM evaluer ev
        JOIN cours c ON ev.cours_code = c.cours_code
        GROUP BY c.intitulé_cours
    """)
    chart_data = cur.fetchall()
    cur.close()

    # Convert data to JSON for chart rendering
    return jsonify(chart_data)

if __name__ == "__main__":
    app.run(debug=True)
