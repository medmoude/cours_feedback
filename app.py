from flask import Flask, render_template, redirect, request, url_for, flash, session, jsonify, make_response
from flask_mysqldb import MySQL
from MySQLdb._exceptions import IntegrityError
from datetime import datetime
import pandas as pd
import openpyxl
import time
import os 
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "medmoud"

#mysql configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "admin"
app.config["MYSQL_DB"] = "feedback_cours"

#file uploads configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads' 
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}  

#initialize mysql
mysql = MySQL(app)


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


#check for login (user and admin)
def user_logged_in():
    return 'user_id' in session

def admin_logged_in():
    return 'admin_id' in session


@app.before_request
def set_end_time():
    if 'end_time' not in session:
        
        countdown_duration = 60 * 10
        session['end_time'] = time.time() + countdown_duration 



# the main route
@app.route("/")
def index():
    if user_logged_in():

        end_time = session['end_time']
        
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
        cur.execute("SELECT cours_code FROM evaluer WHERE matricule = %s ", (session['user_id'],))

        for row in cur.fetchall():
            evaluated_courses.add(row[0])

        cur.close()
        
        mois = datetime.now().month
        if mois in [10, 11, 12, 1, 2]:
            return render_template("index.html", cours=cours_sem_impaire, evaluated_courses=evaluated_courses, end_time=end_time)
        else:
            return render_template("index.html", cours=cours_sem_paire, evaluated_courses=evaluated_courses, end_time=end_time)
        
    return redirect(url_for('login'))


# Login route
@app.route("/login", methods=["POST", "GET"])
def login():

    if user_logged_in():
        return redirect(url_for('index'))
    
    if admin_logged_in():
        return redirect(url_for('visualisation'))

    if request.method == "POST":
        email = request.form["email"]
        mot_de_pass = request.form["mot-de-pass"]

        if not email or not mot_de_pass:
            flash('Tous les champs sont obligatoires !', 'error')
            return render_template("login.html")
        
        if email == "admin" and mot_de_pass == "admin":
            session['admin_id'] = 'admin'
            return redirect(url_for('visualisation'))

        # Verify if the email of the user exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT matricule, nom_prenom, email, mot_de_pass FROM etudiants WHERE email = %s ",
                    (email,))
        user = cur.fetchone()

        if user:
            #verify the password
            if mot_de_pass == user[3]:
                session["user_id"] = user[0]  # Store matricule (user_id) in session
                session["user_nom_prenom"] = user[1]
                return redirect(url_for("index"))
            else:
                flash('le mot de passe est incorrecte','error')
                return render_template("login.html")
            
        else:
            flash("Email introuvable", "error")
            return render_template("login.html")
        
    return render_template("login.html")


# Logout route (users)
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for('login'))

#Logout route (admin)
@app.route("/logout_admin")
def logout_admin():
    session.pop("admin_id", None)
    return redirect(url_for('login'))


#changer le mot de passe 
@app.route('/changer_mot_de_pass', methods = ['POST','GET'])
def changer_mot_de_pass():
    if user_logged_in():

        if request.method == "POST":
            actuel_mot_de_pass = request.form['actuel-mot-de-pass']
            nouveau_mot_de_pass = request.form['nouveau-mot-de-pass']
            conf_mot_de_pass = request.form['confirmer-mot-de-pass']

            cur = mysql.connection.cursor()
            query = "SELECT * FROM etudiants WHERE matricule = %s AND mot_de_pass = %s "
            cur.execute(query,(session['user_id'], actuel_mot_de_pass))
            user = cur.fetchone()
            if user:
                if nouveau_mot_de_pass == conf_mot_de_pass:
                    query = "UPDATE etudiants SET mot_de_pass = %s WHERE matricule = %s "
                    cur.execute(query,(nouveau_mot_de_pass, session['user_id']))
                    mysql.connection.commit()
                    flash('Le mot de passe a été changé avec succès', 'success')
                    
                else:
                    flash('Assurez-vous que les mots de passe correspondent', 'error')
                    return render_template('changer_mot_de_pass.html')

            else:
                flash('le mot de passe est incorrete', 'error')
                return render_template('changer_mot_de_pass.html')

        return render_template ('changer_mot_de_pass.html')
    
    return redirect(url_for('login'))


# Profile route
@app.route("/profile/<user_id>")
def profile(user_id):
    if user_logged_in():
        if user_id == str(session['user_id']):
            cur = mysql.connection.cursor()
            cur.execute("""
                        SELECT matricule, nom_prenom , email, intitulé_dep
                        FROM etudiants 
                        JOIN departement ON etudiants.code_dep = departement.code_dep
                        WHERE etudiants.matricule = %s ;
                    """, (user_id,))
            user_data = cur.fetchone()

            cur.execute("SELECT * FROM images WHERE matricule = %s ORDER BY date_upload DESC ", (session['user_id'],))
            image = cur.fetchone()
            cur.close()
            if image:
                return render_template("profile.html", user_data=user_data, image = image)
            else:
                return render_template("profile.html", user_data=user_data)

        else:
            return redirect(url_for('profile', user_id = session['user_id']))

    return redirect(url_for('login'))

@app.route('/ajouter_image', methods=['GET', 'POST'])
def ajouter_image():
    if user_logged_in():
        if request.method == 'POST':
            if 'image-file' not in request.files:
                flash('Aucun image trouvé', 'error') 
                return redirect(url_for('profile', user_id = session['user_id']))

            file = request.files['image-file']
            
            if file.filename == '':
                flash('Aucun image sélectionné', 'error')
                return redirect(url_for('profile', user_id = session['user_id']))

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace("\\", "/")
                file.save(file_path)  

                # Optionally, store the file path in the database
                cursor = mysql.connection.cursor()
                query = "INSERT INTO images (nom_image, chemin_image, matricule) VALUES (%s, %s, %s)"
                cursor.execute(query, (filename, file_path, session['user_id']))
                mysql.connection.commit()
                cursor.close()

                flash('Image téléchargée avec succès', 'success')  
                return redirect(url_for('profile', user_id = session['user_id'])) 

            else:
                flash("Type de fishier non autorisé", 'error')
                return redirect(url_for('profile', user_id = session['user_id']))

        return render_template('profile.html') 
    
    return redirect(url_for('login'))


# Formulaire Cours route
@app.route("/formulaire_cours/<cours_code>")
def formulaire_cours(cours_code):
    if user_logged_in():
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT * FROM cours WHERE cours_code = %s", (cours_code,))
            cours = cur.fetchone()

            cur.execute("SELECT * FROM section")
            sections = cur.fetchall()

            cur.execute("SELECT * FROM question")
            questions = cur.fetchall()

            cur.execute("SELECT * FROM reponse")
            reponses = cur.fetchall()
        finally:
            cur.close()

        return render_template("formulaire.html",
                                cours_code=cours_code,
                                cours=cours,
                                sections = sections,
                                questions = questions,
                                reponses = reponses)
    
    return redirect(url_for('login'))


@app.route('/insert_formulaire/<cours_code>', methods=["POST", "GET"])
def insert_formulaire(cours_code):
    if user_logged_in():
        if request.method == "POST":
            matricule = session['user_id']
            commentaire = request.form['feedback']

            notes = []
            for key, value in request.form.items():
                if key.startswith("question_"):
                    question_id = key.split("_")[1]
                    notes.append(value)

            somme = 0
            for i in notes :
                somme = somme + int(i)
            note_final = somme/len(notes)


            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO evaluer (matricule, cours_code, evaluation, commentaire) 
                VALUES (%s, %s, %s, %s)
            """, (matricule, cours_code, note_final, commentaire))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('index'))
    
    return redirect(url_for('login'))
    


# ADMIN routes 
@app.route("/visualisation")
def visualisation ():
    if admin_logged_in():
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT intitulé_cours, ROUND(AVG(evaluation), 2) AS avg_evaluation 
            FROM evaluer 
            JOIN cours ON evaluer.cours_code = cours.cours_code
            GROUP BY intitulé_cours;
        """)
        evaluation_data = cur.fetchall()

        return render_template('visualisation.html', evaluation_data = evaluation_data)
    
    return redirect(url_for('login'))


@app.route('/chart-data')
def chart_data():
    if admin_logged_in():
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
    
    return redirect(url_for('login'))


@app.route('/questionnaire')
def questionnaire():
    if admin_logged_in():
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_question, lib_question FROM question")
        questions = cur.fetchall()
        cur.close()
        return render_template('questionnaire.html', questions=questions)
    
    return redirect(url_for('login'))


@app.route('/ajouter_question', methods=['GET', 'POST'])
def ajouter_question():
    if admin_logged_in():
        cur = mysql.connection.cursor()

        if request.method == "POST":
            # Fetch the main question and its section ID
            question = request.form['question']
            section_id = request.form['section']

            # Fetch all responses and their ponderations dynamically
            for key, value in request.form.items():
                print(f"{key}: {value}")

                # Collect dynamic responses and ponderations
            responses = []
            for key in request.form:
                if key.startswith('reponse-'):
                    response = request.form[key]
                    ponderation_key = f'ponderation-{key.split("-")[1]}'
                    ponderation = request.form.get(ponderation_key, 0)
                    responses.append((response, ponderation))


            cur.execute("INSERT INTO question (lib_question, id_section) VALUES (%s, %s)", (question, section_id))
            mysql.connection.commit()
            question_id = cur.lastrowid 

            # Insert responses and ponderations into their respective table
            for response, ponderation in responses:
                cur.execute(
                    "INSERT INTO reponse (lib_reponse, poids_reponse, id_question) VALUES (%s, %s, %s)",
                    (response, ponderation, question_id))
            mysql.connection.commit()
            cur.close()

            return redirect(url_for('questionnaire'))

        # Fetch all sections for the dropdown
        cur.execute("SELECT id_section, lib_section FROM section")
        sections = cur.fetchall()
        cur.close()

        return render_template('ajouter_question.html', sections=sections)

    return redirect(url_for('login'))

@app.route('/modifier_question/<int:question_id>', methods=['GET', 'POST'])
def modifier_questionnaire(question_id):
    if admin_logged_in():
        cur = mysql.connection.cursor()
        if request.method == "POST":
            new_question = request.form['new_question']
            cur.execute("UPDATE question SET lib_question = %s WHERE id_question = %s", (new_question, question_id))
            mysql.connection.commit()

            section = request.form['section']
            cur.execute("update question set id_section = %s where id_question = %s",(section,question_id))
            mysql.connection.commit()

            cur.execute("SELECT lib_question , id_section FROM question WHERE id_question = %s", (question_id,))
            question = cur.fetchone()
            cur.close

            cur = mysql.connection.cursor()
            cur.execute("select  lib_reponse , poids_reponse from reponse WHERE id_question = %s", (question_id,))
            reponse = cur.fetchall()
            cur.close

            cur.connection.cursor()
            cur.execute("select * from section")
            sections = cur.fetchall()
            cur.close

            # Fetch all responses and their ponderations dynamically
            responses = []
            for key in request.form:
                if key.startswith('reponse-'):
                    response = request.form[key]
                    ponderation_key = f'ponderation-{key.split("-")[1]}'
                    ponderation = request.form.get(ponderation_key, 0)
                    responses.append((response, ponderation))

            cur.connection.cursor()
            cur.execute("select id_reponse from reponse where id_question = %s", (question_id,))
            ids = cur.fetchall()
            cur.close
            c = 0

            for i in responses :

                if c < len(ids):
                    lib_rep = i[0]
                    poid_rep = i[1]
                    cur.execute("update reponse set lib_reponse = %s , poids_reponse = %s where id_reponse = %s",
                                (lib_rep, poid_rep, ids[c]))
                    mysql.connection.commit()
                    c = c + 1

                else :
                    lib_rep = i[0]
                    poid_rep = i[1]
                    cur.execute("INSERT INTO reponse (lib_reponse, poids_reponse, id_question) VALUES (%s, %s, %s)",
                    (lib_rep, poid_rep, question_id))
                    mysql.connection.commit()


            return redirect(url_for('questionnaire'))


        cur.execute("SELECT lib_question , id_section FROM question WHERE id_question = %s", (question_id,))
        question = cur.fetchone()
        cur.close

        cur = mysql.connection.cursor()
        cur.execute("select  lib_reponse , poids_reponse from reponse WHERE id_question = %s",(question_id,))
        reponse = cur.fetchall()
        cur.close

        cur.connection.cursor()
        cur.execute("select * from section")
        sections = cur.fetchall()
        cur.close

        return render_template('modifier_question.html', question=question,reponses = reponse, sections = sections)

    return redirect(url_for('login'))

@app.route('/supprimer_question/<int:question_id>')
def supprimer_question(question_id):
    if admin_logged_in():
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM reponse WHERE id_question = %s", (question_id,))
        mysql.connection.commit()
        cur.execute("DELETE FROM question WHERE id_question = %s", (question_id,))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('questionnaire'))
    
    return redirect(url_for('login'))


@app.route('/ajouter_promotion', methods=['GET', 'POST'])
def ajouter_promotion():
    if admin_logged_in():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM annee_universitaire ORDER BY id_annee_univ ASC;")
        annees = cur.fetchall()

        # If the form is submitted via the 'select' dropdown
        if request.method == 'POST' and request.form.get('type-form') == 'select':
            session['annee_univ'] = request.form['annee_univ']
            return redirect(url_for('ajouter_promotion')) 

        # Check if 'annee_univ' is in session
        if 'annee_univ' in session:
            query = """
                    SELECT matricule, nom_prenom, email, etudiants.code_dep, intitulé_dep, lib_annee_univ 
                    FROM etudiants 
                    JOIN departement ON etudiants.code_dep = departement.code_dep
                    JOIN annee_universitaire ON etudiants.id_annee_univ = annee_universitaire.id_annee_univ
                    WHERE lib_annee_univ = %s
                    ORDER BY code_dep ASC;
                    """
            cur.execute(query, (session['annee_univ'],))
            etudiants = cur.fetchall()
            print("hhhh")

        else:
            query = """
                    SELECT matricule, nom_prenom, email, etudiants.code_dep, intitulé_dep, lib_annee_univ 
                    FROM etudiants 
                    JOIN departement ON etudiants.code_dep = departement.code_dep
                    JOIN annee_universitaire ON etudiants.id_annee_univ = annee_universitaire.id_annee_univ
                    WHERE lib_annee_univ = '2024-2025'
                    ORDER BY code_dep ASC;
                    """
            cur.execute(query)
            etudiants = cur.fetchall()
            
        cur.close()
            

        

        # If the form is submitted with the file (from file-form)
        if request.method == 'POST' and request.form.get('type-form') == 'file-upload':
            if 'promotion-file' not in request.files:
                flash('Aucun fichier trouvé', 'error')
                return render_template('ajouter_promotion.html', etudiants=etudiants, annees=annees)

            file = request.files['promotion-file']

            if file.filename == '':
                flash('Aucun fichier sélectionné', 'error')
                return render_template('ajouter_promotion.html', etudiants=etudiants, annees=annees)

            if file and file.filename.endswith('.xlsx'):
                try:
                    promotion_data = pd.read_excel(file, sheet_name=None)
                except Exception as e:
                    flash('Le fichier Excel est corrompu ou invalide', 'error')
                    return render_template('ajouter_promotion.html', etudiants=etudiants, annees=annees)

                for sheet_name, df in promotion_data.items():
                    required_columns = ['matricule', 'nom_prenom', 'email', 'mot_de_pass', 'code_dep', 'id_annee_univ']
                    if not all(col in df.columns for col in required_columns):
                        flash('Le fichier Excel est manquant de certaines colonnes obligatoires', 'error')
                        return render_template('ajouter_promotion.html', etudiants=etudiants, annees=annees)

                    for index, row in df.iterrows():
                        matricule = row.get('matricule', None)
                        nom_prenom = row.get('nom_prenom', None)
                        email = row.get('email', None)
                        mot_de_pass = row.get('mot_de_pass', None)
                        code_dep = row.get('code_dep', None)
                        id_annee_univ = row.get('id_annee_univ', None)

                        try:
                            cur = mysql.connection.cursor()
                            query = """
                                    INSERT INTO etudiants (matricule, nom_prenom, email, mot_de_pass, code_dep, id_annee_univ) 
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                    """
                            cur.execute(query, (matricule, nom_prenom, email, mot_de_pass, code_dep, id_annee_univ))
                            mysql.connection.commit()
                            cur.close()
                        except IntegrityError:
                            flash('Cette promotion existe déjà', 'error')
                            return render_template('ajouter_promotion.html', etudiants=etudiants, annees=annees)

                flash('Fichier téléchargé avec succès et données insérées', 'success')
                return render_template('ajouter_promotion.html', etudiants=etudiants, annees=annees)
            else:
                flash('Seuls les fichiers Excel sont acceptables', 'error')

        return render_template('ajouter_promotion.html', etudiants=etudiants, annees=annees)

    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)