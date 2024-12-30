from flask import Flask, render_template, redirect, request, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
import pandas as pd
import openpyxl
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
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  

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


# the main route
@app.route("/")
def index():
    if not user_logged_in():
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
        return render_template("index.html", cours=cours_sem_impaire, evaluated_courses=evaluated_courses)
    else:
        return render_template("index.html", cours=cours_sem_paire, evaluated_courses=evaluated_courses)



# Login route
@app.route("/login", methods=["POST", "GET"])
def login():
    if user_logged_in():
        return redirect(url_for('index'))

    if request.method == "POST":
        email = request.form["email"]
        mot_de_pass = request.form["mot-de-pass"]

        if not email or not mot_de_pass:
            flash('Tous les champs sont obligatoires !', 'error')
            return render_template("login.html")
        
        if email == "admin" and mot_de_pass == "admin":
            session['admin_id'] = 'admin'
            return redirect('visualisation')

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
                flash("login succée", "success")
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
    else:
        return "vous ne pouvez pas accédez cette page"


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
    return "vous ne pouvez pas accéder ce profile"

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
    
    return "Vous ne pouvez pas accédez cette page"


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


@app.route('/questionnaire')
def questionnaire():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM question")
    questions = cur.fetchall()
    return render_template('questionnaire.html', questions = questions)


@app.route('/modifier_question<question_id>')
def modifier_questionnaire(question_id):
    cur = mysql.connection.cursor()
    cur.execute("")
    mysql.connection.commit()
    cur.close()
    return render_template('modifier_question.html')


@app.route('/ajouter_question', methods = ['POST', 'GET'])
def ajouter_question():
    if request.method == "POST":
        question = request.form['question']
        reponseA = request.form['reponse-A']
        reponseB = request.form['reponse-B']
        reponseC = request.form['reponse-C']
        reponseD = request.form['reponse-D']

        cur = mysql.connection.cursor()
        query = ""
        cur.execute()
        mysql.connection.commit()
        cur.close()
        return render_template('questionnaire.html')

    return render_template('ajouter_question.html')



@app.route('/ajouter_promotion', methods=['GET', 'POST']) 
def ajouter_promotion():
    if request.method == 'POST':

        if 'promotion-file' not in request.files:
            flash('Aucun fichier trouvé', 'error') 
            return redirect(request.url)

        file = request.files['promotion-file']
    
        if file.filename == '':
            flash('Aucun fichier sélectionné', 'error')  
            return redirect(request.url)

        if file and file.filename.endswith('.xlsx'):
            promotion_data = pd.read_excel(file, sheet_name=None)  # sheet_name=None charge toutes les feuilles sous forme de dictionnaire

            for sheet_name, df in promotion_data.items():
                
                for index, row in df.iterrows():
                    matricule = row.get('matricule', None)
                    nom_prenom = row.get('nom_prenom', None)
                    email = row.get('email', None)
                    mot_de_pass = row.get('mot_de_pass', None)
                    code_dep = row.get('code_dep', None)
                    id_annee_univ = row.get('id_annee_univ', None)

                    # Insérer les données dans la base de données MySQL (vous pouvez aussi insérer dans différentes tables en fonction du nom de la feuille)
                    cursor = mysql.connection.cursor()
                    query = """
                            INSERT INTO etudiants (matricule, nom_prenom, email, mot_de_pass, code_dep, id_annee_univ) 
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """
                    cursor.execute(query, (matricule, nom_prenom, email, mot_de_pass, code_dep, id_annee_univ))
                    mysql.connection.commit()
                    cursor.close()

            flash('Fichier téléchargé avec succès et données insérées', 'success')
            return redirect(url_for('visualisation'))  

    # Rendre le template HTML pour l'upload
    return render_template('ajouter_promotion.html')


@app.route('/ajouter_image', methods=['GET', 'POST'])
def ajouter_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('Aucun image trouvé', 'error') 
            return redirect(url_for('profile', user_id = session['user_id']))

        file = request.files['image']
        
        if file.filename == '':
            flash('Aucun image sélectionné', 'error')
            return redirect(url_for('profile', user_id = session['user_id']))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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
            flash("Type d'image non autorisé", 'error')
            return redirect(url_for('profile', user_id = session['user_id']))

    return render_template('profile.html')  


if __name__ == "__main__":
    app.run(debug=True)
