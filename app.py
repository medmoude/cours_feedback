from flask import Flask, render_template, redirect, request, url_for, flash, session, jsonify, make_response
from flask_mysqldb import MySQL
from MySQLdb._exceptions import IntegrityError
from datetime import datetime
import pandas as pd
import openpyxl
import time
import re
import os 
from werkzeug.utils import secure_filename
import string
import secrets 


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
    return 'admin_id' in session and 'annee_univ' in session

#generate a random password
def generate_password(length=8):
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(length))

    return password

#validate annee universitaire
def validate_annee_universitaire(annee_universitaire):
    pattern = r"^\d{4}-\d{4}$"
    
    if not re.match(pattern, annee_universitaire):
        return False
    
    try:
        start_year, end_year = map(int, annee_universitaire.split('-'))
        if start_year < end_year and (end_year - start_year == 1):
            return True
        else:
            return False
    except ValueError:
        return False



####################################
        ### USER ROUTES ###
####################################

# the main route
@app.route("/")
def index():
    if user_logged_in():
        
        #traitement des semestres impaires
        cur = mysql.connection.cursor()
        query_sem_impaire = """
        SELECT cours_code, intitulé_cours
        FROM etudiants
        JOIN departement ON etudiants.intitulé_dep = departement.intitulé_dep
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
        JOIN departement ON etudiants.intitulé_dep = departement.intitulé_dep
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
            return render_template("index.html", cours=cours_sem_impaire, evaluated_courses=evaluated_courses)
        else:
            return render_template("index.html", cours=cours_sem_paire, evaluated_courses=evaluated_courses)
        
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
            cur = mysql.connection.cursor()
            cur.execute("SELECT lib_annee_univ FROM annee_universitaire")
            annees = cur.fetchall()
            session['admin_id'] = 'admin'
            return render_template('promp_annee_univ.html', annees = annees)

        # Verify if the email of the user exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT matricule, nom_prenom, email, mot_de_pass, lib_annee_univ FROM etudiants WHERE email = %s ",
                    (email,))
        user = cur.fetchone()

        if user:
            #verify the password
            if mot_de_pass == user[3]:
                session["user_id"] = user[0]  # Store matricule in session
                session["user_nom_prenom"] = user[1]
                session["annee_univ"] = user[4]
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
    session.pop("annee_univ", None)
    session.pop("user_nom_prenom", None)
    return redirect(url_for('login'))


#Logout route (admin)
@app.route("/logout_admin")
def logout_admin():
    session.pop("admin_id", None)
    session.pop("annee_univ", None)
    session.pop("annees_univs", None)
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
                        SELECT matricule, nom_prenom , email, etudiants.intitulé_dep
                        FROM etudiants 
                        JOIN departement ON etudiants.intitulé_dep = departement.intitulé_dep
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

            cur.execute("SELECT * FROM section WHERE lib_annee_univ = %s ", (session['annee_univ'],))
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
            
            notes = []  
            ponderations = [] 
            percentages = []  
            commentaires = [] 
            
            
            for key, value in request.form.items():
                if key.startswith("question_"):
                    question_id = key.split('_')[1]
                    score = int(value)  
                    
                    ponderation_key = f"some_ponderation_{question_id}"
                    ponderation_value = int(request.form.get(ponderation_key, 0))  # Default to 0 if not found
                    
                    if ponderation_value > 0:
                        percentage = (score / ponderation_value) * 100
                    else:
                        percentage = 0
                    
                    notes.append(score)
                    ponderations.append(ponderation_value)
                    percentages.append(percentage)
                    print(f"{key}: Score = {score}, Ponderation = {ponderation_value}, Percentage = {percentage}%")
                
                elif key.startswith("commentaire_"):
                    
                    commentaire_text = value
                    commentaires.append(commentaire_text)
            
            total_score = sum(notes)
            total_ponderation = sum(ponderations)
            
            if total_ponderation > 0:
                total_percentage = (total_score / total_ponderation) * 100
            else:
                total_percentage = 0
            
            
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO evaluer (evaluation, matricule, cours_code, lib_annee_univ) 
                VALUES (%s, %s, %s, %s)
            """, (total_percentage, matricule, cours_code, session['annee_univ'])) 
            mysql.connection.commit()

            for commentaire in commentaires:
                cur.execute("""
                    INSERT INTO commentaire (lib_commentaire, matricule, cours_code)
                    VALUES (%s, %s, %s) 
                """, (commentaire, matricule, cours_code))
            mysql.connection.commit()

            cur.close()

            return redirect(url_for('index')) 
        else:
            return redirect(url_for('login'))
    return redirect(url_for('login'))

    

######################################
       ### ADMIN ROUTES ###
######################################
@app.route("/visualisation")
def visualisation():
    if admin_logged_in():
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT intitulé_cours, ROUND(AVG(evaluation), 1) AS avg_evaluation 
            FROM evaluer 
            JOIN cours ON evaluer.cours_code = cours.cours_code 
            WHERE lib_annee_univ = %s
            GROUP BY intitulé_cours;
        """, (session['annee_univ'],))
        evaluation_data = cur.fetchall()

        #fetch the data of the selected year 
        cur.execute("SELECT * FROM annee_universitaire WHERE lib_annee_univ = %s ",(session['annee_univ'],))
        annee = cur.fetchone()
        cur.close()

        return render_template('visualisation.html', evaluation_data = evaluation_data, annee = annee)
    
    return redirect(url_for('login'))


@app.route('/chart-data')
def chart_data():
    if admin_logged_in():
        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT c.intitulé_cours, ROUND(AVG(ev.evaluation), 0) AS pourcentage
            FROM evaluer ev
            JOIN cours c ON ev.cours_code = c.cours_code
            WHERE lib_annee_univ = %s
            GROUP BY c.intitulé_cours
        """, (session['annee_univ'],))
        chart_data = cur.fetchall()
        cur.close()

        # Convert data to JSON for chart rendering
        return jsonify(chart_data)
    
    return redirect(url_for('login'))


@app.route('/questionnaire')
def questionnaire():
    if admin_logged_in():
        cur = mysql.connection.cursor()
        cur.execute("""
                    SELECT id_question, lib_question
                    FROM question 
                    JOIN section ON question.id_section = section.id_section 
                    WHERE lib_annee_univ = %s ;
                    """, (session['annee_univ'],))
        questions = cur.fetchall()

        #fetch the data of the selected year 
        cur.execute("SELECT * FROM annee_universitaire WHERE lib_annee_univ = %s ",(session['annee_univ'],))
        annee = cur.fetchone()
        cur.close()
        return render_template('questionnaire.html', questions=questions , annee = annee)
    
    return redirect(url_for('login'))


@app.route('/ajouter_question', methods=['GET', 'POST'])
def ajouter_question():
    if admin_logged_in():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM annee_universitaire WHERE lib_annee_univ = %s ", (session['annee_univ'],))
        annee = cur.fetchone()

        if request.method == "POST":
            # Fetch the main question, its section ID, and type
            question = request.form['question']
            type_question = request.form['type']
            section_id = request.form['section']

            # Determine if responses are required based on question type
            response_required = True if type_question != 'textarea' else False

            # Insert the question into the database
            cur.execute("INSERT INTO question (lib_question, id_section, type_question, reponse_required) VALUES (%s, %s, %s, %s)", 
                        (question, section_id, type_question, response_required))
            mysql.connection.commit()
            question_id = cur.lastrowid

            # If responses are required (not a textarea), insert them
            if response_required:
                responses = []
                some_pond_question = []
                
                for key, value in request.form.items():
                    if key.startswith('reponse-'):
                        response = request.form[key]
                        ponderation_key = f'ponderation-{key.split("-")[1]}'
                        ponderation = request.form.get(ponderation_key, 0)
                        responses.append((response, ponderation))

                # Insert responses into the database
                for response, ponderation in responses:
                    cur.execute("INSERT INTO reponse (lib_reponse, poids_reponse, id_question) VALUES (%s, %s, %s)", 
                                (response, ponderation, question_id))
                mysql.connection.commit()

            return redirect(url_for('questionnaire'))

        # Fetch all sections for the dropdown
        cur.execute("SELECT id_section, lib_section FROM section WHERE lib_annee_univ = %s ", (session['annee_univ'],))
        sections = cur.fetchall()
        cur.close()

        return render_template('ajouter_question.html', sections=sections, annee = annee)

    return redirect(url_for('login'))


@app.route('/modifier_question/<int:question_id>', methods=['GET', 'POST'])
def modifier_question(question_id):
    if admin_logged_in():
        cur = mysql.connection.cursor()

        if request.method == "POST":
            new_question = request.form['question']
            section = request.form['section']
            type_question = request.form['type']

            # Determine if responses are required based on question type
            response_required = True if type_question != 'textarea' else False

            # Update the question text, section, and type
            cur.execute("UPDATE question SET lib_question = %s, id_section = %s, type_question = %s, reponse_required = %s WHERE id_question = %s", 
                        (new_question, section, type_question, response_required, question_id))
            mysql.connection.commit()

            # If responses are required (not a textarea), update them
            if response_required:
                responses = []
                for key in request.form:
                    if key.startswith('reponse-'):
                        response = request.form[key]
                        ponderation_key = f'ponderation-{key.split("-")[1]}'
                        ponderation = request.form.get(ponderation_key, 0)
                        responses.append((response, ponderation))

                # Fetch the current response IDs
                cur.execute("SELECT id_reponse FROM reponse WHERE id_question = %s", (question_id,))
                existing_response_ids = cur.fetchall()

                c = 0
                for response, ponderation in responses:
                    if c < len(existing_response_ids):
                        # Update existing responses
                        response_id = existing_response_ids[c][0]
                        cur.execute("UPDATE reponse SET lib_reponse = %s, poids_reponse = %s WHERE id_reponse = %s", 
                                    (response, ponderation, response_id))
                    else:
                        # Insert new responses if there are more
                        cur.execute("INSERT INTO reponse (lib_reponse, poids_reponse, id_question) VALUES (%s, %s, %s)", 
                                    (response, ponderation, question_id))
                    mysql.connection.commit()
                    c += 1

            else:
                # If it's a textarea, ensure no responses are included (optional, can be left empty)
                pass

            cur.close()
            return redirect(url_for('questionnaire'))

        # Fetch the current question and responses for editing
        cur.execute("SELECT * FROM question WHERE id_question = %s", (question_id,))
        question = cur.fetchone()

        cur.execute("SELECT lib_reponse, poids_reponse FROM reponse WHERE id_question = %s", (question_id,))
        responses = cur.fetchall()

        # Fetch all sections for the dropdown
        cur.execute("SELECT id_section, lib_section FROM section WHERE lib_annee_univ = %s ",(session['annee_univ'],))
        sections = cur.fetchall()

        #fetch the data of the selected year 
        cur.execute("SELECT * FROM annee_universitaire WHERE lib_annee_univ = %s ",(session['annee_univ'],))
        annee = cur.fetchone()
        cur.close()

        return render_template('modifier_question.html', question=question, responses=responses, sections=sections, annee = annee)

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


@app.route('/ajouter_section', methods = ['GET', 'POST'])
def ajouter_section():
    if admin_logged_in():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM section WHERE lib_annee_univ = %s ",(session['annee_univ'],))
        sections = cur.fetchall()
        sections_list = [i[1] for i in sections]

        cur.execute("SELECT * FROM annee_universitaire ORDER BY lib_annee_univ DESC ")
        annees = cur.fetchall()

        if request.method == 'POST':
            new_section = request.form['new_section']
            
            #verify if the input exists and have a text in it 
            if new_section and new_section.strip() != '' :
                #don't allow the admin to add an existing section
                if new_section not in sections_list:
                    cur.execute("INSERT INTO section (lib_section, lib_annee_univ) VALUES (%s, %s)",
                                (new_section, session['annee_univ'] ))
                    mysql.connection.commit()
                    cur.close()
                    return redirect(url_for('parametres'))
                else: 
                    flash('la section existe déjà !', 'error')
                    return render_template('parametres.html', sections = sections, sections_list = sections_list)
            
        return render_template('parametres.html', sections = sections, sections_list = sections_list)
    
    return(redirect(url_for('login')))


@app.route('/modifier_section_informations/<id_section>')
def modifier_section_informations(id_section):
    if admin_logged_in():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM section WHERE id_section = %s ", (id_section,))
        section = cur.fetchone()

        #fetch the data of the selected year 
        cur.execute("SELECT * FROM annee_universitaire WHERE lib_annee_univ = %s ",(session['annee_univ'],))
        annee = cur.fetchone()
        cur.close()
        return render_template('modifier_section.html', section = section, annee = annee)
    
    return redirect(url_for('login'))


@app.route('/modifier_section/<id_section>', methods = ['GET', 'POST'])
def modifier_section(id_section):
    if admin_logged_in():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM section WHERE lib_annee_univ = %s ",(session['annee_univ'],))
        sections = cur.fetchall()
        sections_list = [i[1] for i in sections]
        
        cur.execute("SELECT lib_section FROM section WHERE id_section = %s", (id_section,))
        current_section_name = cur.fetchone()[0]

        if request.method == 'POST':
            lib_section = request.form['lib_section'].strip()

            if lib_section == '':
                flash("La sélection ne peut pas être vide !", "error")
                return redirect(url_for('modifier_section_informations', id_section=id_section))

            if lib_section != current_section_name and lib_section in sections_list:
                flash("le nom de la section existe déjà !", "error")
                return redirect(url_for('modifier_section_informations', id_section=id_section))

            cur.execute("UPDATE section SET lib_section = %s WHERE id_section = %s", (lib_section, id_section))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('ajouter_section'))

        return redirect(url_for('modifier_section_informations', id_section=id_section))
    return redirect(url_for('login'))


@app.route('/supprimer_section/<id_section>')
def supprimer_section(id_section):
    if admin_logged_in():
        cur = mysql.connection.cursor()
        cur.execute("DELETE from section WHERE id_section = %s ", (id_section,))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('parametres'))
    
    return redirect(url_for('login'))


@app.route('/ajouter_promotion', methods=['GET', 'POST'])
def ajouter_promotion():
    if admin_logged_in():
        cur = mysql.connection.cursor()
        query = """
                SELECT matricule, nom_prenom, email, etudiants.intitulé_dep, etudiants.lib_annee_univ 
                FROM etudiants 
                JOIN departement ON etudiants.intitulé_dep = departement.intitulé_dep
                JOIN annee_universitaire ON etudiants.lib_annee_univ = annee_universitaire.lib_annee_univ
                WHERE etudiants.lib_annee_univ = %s
                ORDER BY code_dep ASC;
                """
        cur.execute(query, (session['annee_univ'],))
        etudiants = cur.fetchall()
        #fetching the data of the current year 
        cur.execute("SELECT * FROM annee_universitaire WHERE lib_annee_univ = %s ",(session['annee_univ'],))
        annee = cur.fetchone()

        #fetch les départements pour ajouter un étudiant
        cur.execute("SELECT intitulé_dep FROM departement")
        departements = cur.fetchall()
        cur.close()

        if request.method == 'POST' :
            if 'promotion-file' not in request.files:
                flash('Aucun fichier trouvé', 'error')
                return render_template('ajouter_promotion.html', etudiants=etudiants, annee = annee, departements = departements)

            file = request.files['promotion-file']

            if file.filename == '':
                flash('Aucun fichier sélectionné', 'error')
                return render_template('ajouter_promotion.html', etudiants=etudiants, annee = annee, departements = departements)

            if file and file.filename.endswith('.xlsx'):
                try:
                    promotion_data = pd.read_excel(file, sheet_name=None)
                except Exception as e:
                    flash('Le fichier Excel est corrompu ou invalide', 'error')
                    return render_template('ajouter_promotion.html', etudiants=etudiants, annee = annee, departements = departements)

                for sheet_name, df in promotion_data.items():
                    required_columns = ['matricule', 'nom_prenom', 'email', 'intitulé_dep']
                    if not all(col in df.columns for col in required_columns):
                        flash('Le fichier Excel est manquant de certaines colonnes obligatoires', 'error')
                        return render_template('ajouter_promotion.html', etudiants=etudiants, annee = annee, departements = departements)
                    

                    for index, row in df.iterrows():
                        matricule = row.get('matricule', None)
                        nom_prenom = row.get('nom_prenom', None)
                        email = row.get('email', None)
                        mot_de_pass = generate_password(8)
                        intitulé_dep = row.get('intitulé_dep', None)

                        try:
                            cur = mysql.connection.cursor()
                            query = """
                                    INSERT INTO etudiants (matricule, nom_prenom, email, mot_de_pass, intitulé_dep, lib_annee_univ) 
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                    """
                            cur.execute(query, (matricule, nom_prenom, email, mot_de_pass, intitulé_dep, session['annee_univ']))
                            mysql.connection.commit()
                            cur.close()
                            
                        except IntegrityError:
                            flash('Cette promotion existe déjà', 'error')
                            return render_template('ajouter_promotion.html', etudiants=etudiants, annee = annee, departements = departements)
                flash('Fichier téléchargé avec succès et données insérées', 'success')
                return redirect(url_for('ajouter_promotion'))
            else:
                flash('Seuls les fichiers Excel sont acceptables', 'error')

        return render_template('ajouter_promotion.html', etudiants=etudiants, annee = annee, departements = departements)

    return redirect(url_for('login'))


@app.route("/ajouter_etudiant", methods = ['POST', 'GET'])
def ajouter_etudiant():
    if admin_logged_in():
        cur = mysql.connection.cursor()
        cur.execute("SELECT matricule FROM etudiants WHERE lib_annee_univ = %s ",(session['annee_univ'],))
        etudiants = [int(i[0]) for i in cur.fetchall()]
        if request.method == 'POST':
            matricule = request.form['matricule'].strip()
            matricule = int(matricule)
            nom_prenom = request.form['nom_prenom'].strip()
            intitule_dep = request.form['intitule_dep']

            if matricule in etudiants:
                flash ("L'étudiant existe déjà! ", 'error')
                return redirect(url_for('ajouter_promotion'))
            
            email = str(matricule) + "@isms.esp.mr"
            mot_de_pass = generate_password(8)
            lib_annee_univ = session['annee_univ']

            cur.execute("""
                        INSERT INTO etudiants (matricule, nom_prenom, email, mot_de_pass, intitulé_dep, lib_annee_univ)
                        VALUES(%s, %s, %s, %s, %s, %s)
                        """,(matricule, nom_prenom, email, mot_de_pass, intitule_dep, lib_annee_univ))
            mysql.connection.commit()
            cur.close()
            flash("Les données de l'étudiant·e ont été enregistrées correctement", 'success')
            return redirect(url_for('ajouter_promotion'))
        
    return redirect(url_for('login'))


@app.route("/envoyer_formulaire" , methods = ['GET', 'POST'])
def envoyer_formulaire():
    if admin_logged_in():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM departement ")
        departements = cur.fetchall()


        cur.execute("SELECT * FROM annee_universitaire WHERE lib_annee_univ = %s ", (session['annee_univ'],))
        annee = cur.fetchone()
        
        etudiants_info = []

        if request.method == 'POST':
            departements_selectionnees = request.form.getlist('departement')
            cur.execute("""SELECT email, mot_de_pass, intitulé_dep FROM etudiants WHERE intitulé_dep IN %s
                        ORDER BY intitulé_dep;""", (departements_selectionnees,))
            etudiants_info = cur.fetchall()
        cur.close()
        return render_template('envoyer_formulaire.html', departements = departements, etudiants_info = etudiants_info, annee = annee)

    return redirect(url_for('login'))


@app.route("/parametres", methods = ['POST', 'GET'])
def parametres():
    if admin_logged_in():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM annee_universitaire")
        annees = cur.fetchall()
        cur.execute("SELECT * FROM section WHERE lib_annee_univ = %s ",(session['annee_univ'],))
        sections = cur.fetchall()

        #fetch the data of the selected year 
        cur.execute("SELECT * FROM annee_universitaire WHERE lib_annee_univ = %s ",(session['annee_univ'],))
        annee = cur.fetchone()
        cur.close()
        return render_template("parametres.html", annees = annees, sections = sections, annee = annee)
    
    return redirect(url_for('login'))


@app.route("/promp_annee_univ", methods = ['POST', 'GET'])
def promp_annee_univ():
    if 'admin_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT lib_annee_univ FROM annee_universitaire")
        annees = cur.fetchall()
        if request.method == 'POST':
            annee_univ = request.form['annee_univ']
            session['annee_univ'] = annee_univ
            session['annees_univs'] = annees
            return redirect(url_for('visualisation'))

    return redirect(url_for('login'))
      

@app.route("/creer_promp_annee_univ", methods = ['POST', 'GET'])
def creer_promp_annee_univ():
    if 'admin_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT lib_annee_univ FROM annee_universitaire")
        annees = cur.fetchall()
        list_annees = [i[0] for i in annees]
        
        if request.method == 'POST':
            nouvelle_annee = request.form['nouvelle_annee'].strip()
            
            if not validate_annee_universitaire(nouvelle_annee):
                flash('invalid année universitaire', 'error')
                return render_template('promp_annee_univ.html', annees = annees)

            if nouvelle_annee in list_annees:
                flash("L'année universitaire existe! ", "error")
                return render_template('promp_annee_univ.html', annees = annees)
            
            id_annee_univ = nouvelle_annee.split("-")[0]
            
            cur.execute("""
                        INSERT INTO annee_universitaire (id_annee_univ, lib_annee_univ, status_annee_univ)
                        VALUES(%s, %s , %s)
                        """
                        ,(int(id_annee_univ), nouvelle_annee, 'Actif'))
            mysql.connection.commit()

            #fetching annees again to store them in session
            cur.execute("SELECT lib_annee_univ FROM annee_universitaire")
            annees = cur.fetchall()
            cur.close()
            session['annee_univ'] = nouvelle_annee
            session['annees_univs'] = annees
            
            return redirect(url_for('visualisation'))
        
    return redirect(url_for('login'))
    

@app.route("/creer_annee_univ", methods=['POST', 'GET'])
def creer_annee_univ():
    if admin_logged_in():
        cur = mysql.connection.cursor()
        cur.execute("SELECT lib_annee_univ FROM annee_universitaire")
        annees = cur.fetchall()

        list_annees = [annee[0] for annee in annees]

        if request.method == 'POST':
            nouvelle_annee = request.form['nouvelle_annee']
            if not validate_annee_universitaire(nouvelle_annee):
                flash('invalid année universitaire', 'error')
                return redirect(url_for('parametres'))
            
            seuil = request.form['seuil']
            id_annee_univ = nouvelle_annee.split("-")[0]

            if not nouvelle_annee or not seuil:
                flash("tous les champs sont obligatoires", 'error')
                return redirect(url_for('parametres'))
            
            if nouvelle_annee in list_annees:
                flash("L'année universitaire existe!", "error")
                return redirect('parametres')

            cur.execute("""
                        INSERT INTO annee_universitaire (id_annee_univ, lib_annee_univ, seuil_annee_univ, status_annee_univ)
                        VALUES(%s, %s , %s, %s)
                        """, (int(id_annee_univ), nouvelle_annee, seuil, 'Actif'))
            mysql.connection.commit()
            
            #fetching annees again to store them in session
            cur.execute("SELECT lib_annee_univ FROM annee_universitaire")
            annees = cur.fetchall()
            cur.close()
            session['annees_univs'] = annees
            flash("L'année universitaire a été créée avec succès", "success")
            return redirect(url_for('parametres'))
        
    return redirect(url_for('login'))


@app.route("/modifier_annee_univ_info/<int:id_annee_univ>")
def modifier_annee_univ_info(id_annee_univ):
    if admin_logged_in():
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_annee_univ, lib_annee_univ, seuil_annee_univ FROM annee_universitaire WHERE id_annee_univ = %s ",(id_annee_univ,))
        annee = cur.fetchone()

        #fetch the data of the selected year 
        cur.execute("SELECT * FROM annee_universitaire WHERE lib_annee_univ = %s ",(session['annee_univ'],))
        current_annee = cur.fetchone()
        cur.close()
        return render_template('modifier_annee.html', annee = annee, current_annee = current_annee)
    
    return redirect(url_for('login'))


@app.route("/modifier_annee_univ/<int:id_annee_univ>", methods=['POST', 'GET'])
def modifier_annee_univ(id_annee_univ):
    if admin_logged_in():
        cur = mysql.connection.cursor()
        cur.execute("SELECT lib_annee_univ FROM annee_universitaire")
        list_annees = [i[0] for i in cur.fetchall()]
        if request.method == 'POST':
            annee = request.form['annee']
            if not validate_annee_universitaire(annee):
                flash('invalid année universitaire', 'error')
                return redirect(url_for('modifier_annee_univ_info', id_annee_univ = id_annee_univ))
            
            seuil = request.form['seuil']
            if not annee or not seuil:
                flash("L'année et la seuil ne peuvent pas être vide!", "error")
                return redirect(url_for('modifier_annee_univ_info', id_annee_univ = id_annee_univ))

            cur.execute("SELECT lib_annee_univ FROM annee_universitaire WHERE lib_annee_univ = %s ", (annee,))
            annee_modifiee = cur.fetchone()[0]
            print("modifiée ", annee_modifiee)
            if annee in list_annees[0] and annee != annee_modifiee:
                flash("L'année universitaire existe déjà. Veuillez en choisir une autre.", "error")
                return redirect(url_for('modifier_annee_univ_info', id_annee_univ=id_annee_univ))

            cur.execute("""
                UPDATE annee_universitaire 
                SET lib_annee_univ = %s, seuil_annee_univ = %s 
                WHERE id_annee_univ = %s
            """, (annee, seuil, id_annee_univ))
            mysql.connection.commit()

            #fetching annees again to store them in session
            cur.execute("SELECT lib_annee_univ FROM annee_universitaire")
            annees = cur.fetchall()
            session['annees_univs'] = annees
            flash("L'année universitaire a été mise à jour avec succès.", "success")
            return redirect(url_for('parametres'))

        cur.close()
        return redirect(url_for('parametres'))
    
    return redirect(url_for('login'))


@app.route("/supprimer_annee_univ/<int:id_annee_univ>")
def supprimer_annee_univ(id_annee_univ):
    if admin_logged_in():
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM annee_universitaire WHERE id_annee_univ = %s ",(id_annee_univ,))
        mysql.connection.commit()
        cur.execute("SELECT lib_annee_univ FROM annee_universitaire ")
        annees = cur.fetchall()
        
        #if there still some years go back to parametres otherwise go to login
        if len(annees) != 0:
            list_annees = [i[0] for i in annees]
            session['annee_univ'] = list_annees[0]
            session['annees_univs'] = annees
            return redirect(url_for('parametres'))
        else:
            return redirect(url_for('logout_admin'))
        
    return redirect(url_for('login'))


@app.route("/archiver_ou_unarchiver_anne_univ/<int:id_annee_univ>", methods = ['POST', 'GET'])
def archiver_ou_unarchiver_anne_univ(id_annee_univ):
    if admin_logged_in():
        if request.method == 'POST':
            status = request.form['status']
            cur = mysql.connection.cursor()
            cur.execute("""UPDATE annee_universitaire SET status_annee_univ = %s WHERE id_annee_univ = %s """
                        ,(status, id_annee_univ))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('parametres'))
    
    return redirect(url_for('login'))


@app.route("/changer_annee_univ", methods=['POST', 'GET'])
def changer_annee_univ():
    if admin_logged_in():
        if request.method == 'POST':
            annee = request.form['annee']
            print(annee)
            if annee:
                session['annee_univ'] = annee
            else:
                flash("Veuillez sélectionner une année universitaire", 'error')
        return redirect(url_for('parametres'))
    
    return redirect(url_for('login'))




if __name__ == "__main__":
    app.run(debug=True)