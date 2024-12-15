#Write your sql code here 

CREATE DATABASE feedback_cours;
USE feedback_cours;

CREATE TABLE niveau (
code_niv INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
intitulé_niv VARCHAR(50) NOT NULL
);

CREATE TABLE departement (
code_dep INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
intitulé_dep VARCHAR(50) NOT NULL,
code_niv INT NOT NULL,
FOREIGN KEY (code_niv) REFERENCES niveau(code_niv)
);

CREATE TABLE semestre (
code_sem INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
intitulé_sem VARCHAR(50) NOT NULL,
code_niv INT NOT NULL,
FOREIGN KEY (code_niv) REFERENCES niveau(code_niv)
);

CREATE TABLE etudiants (
matricule INT NOT NULL PRIMARY KEY,
nom VARCHAR (100) NOT NULL,
prenom VARCHAR (100) NOT NULL,
email VARCHAR (50) NOT NULL,
mot_de_pass VARCHAR(50) NOT NULL,
code_dep INT NOT NULL,
FOREIGN KEY (code_dep) REFERENCES departement(code_dep)
);


CREATE TABLE cours (
cours_code VARCHAR(10) NOT NULL PRIMARY KEY,
intitulé_cours VARCHAR(255) NOT NULL,
code_sem INT NOT NULL,
FOREIGN KEY (code_sem) REFERENCES semestre(code_sem)
);

CREATE TABLE evaluer (
evaluation INT NOT NULL ,
commentaire TEXT NOT NULL,
matricule INT NOT NULL ,
cours_code VARCHAR(50) NOT NULL,
PRIMARY KEY(matricule, cours_code),
FOREIGN KEY(matricule) REFERENCES etudiants(matricule),
FOREIGN KEY(cours_code) REFERENCES cours(cours_code)

);

#Insertion des données 
INSERT INTO niveau (intitulé_niv) VALUES
("L1"), ("L2"), ("L3");

INSERT INTO departement (intitulé_dep, code_niv) VALUES
("Tronc commun",1),
("SDID L2", 2),
("SEA L2", 2),
("SDID L3", 3),
("SEA L3", 3);

INSERT INTO semestre (intitulé_sem, code_niv) VALUES
("S1", 1),
("S2", 1),
("S3", 2),
("S4", 2),
("S5", 3),
("S6", 3);

INSERT INTO cours (cours_code, intitulé_cours, code_sem) VALUES 
-- Semester 1
("ST11", "analyse I", 1),
("ST12", "algèbre I", 1),
("ST21", "statistique descriptive", 1),
("ST22", "calcul des probabilités", 1),
("HE31", "économie générale", 1),
("HE32", "macro-économie", 1),
("ST41", "informatique, bureautique et TIC", 1),
("ST42", "introduction aux logiciels statistiques", 1),
("HE51", "anglais", 1),
("HE52", "TE - prise de note, dissertation, exposé", 1),
("HE53", "développement du projet professionnel", 1),

-- Semester 2
("ST61", "analyse II", 2),
("ST62", "algèbre II", 2),
("ST71", "théorie des probabilités", 2),
("ST72", "séries temporelles", 2),
("HE81", "comptabilité nationale", 2),
("HE82", "micro-économie", 2),
("HE83", "analyse financière", 2),
("ST91", "programmation Python", 2),
("ST92", "projet logiciels statistiques", 2),
("HE101", "anglais", 2),
("HE102", "TE - compte rendu, note de synthèse, rapport technique", 2),
("HE103", "développement du projet professionnel", 2),

-- SDID
-- Semester 3
("ST111", "statistique inférentielle", 3),
("ST112", "analyse des données", 3),
("SDID113", "économétrie", 3),
("SDID121", "méthodes numériques", 3),
("SDID122", "recherche opérationnelle", 3),
("ST131", "technologie Web et Mobile", 3),
("ST132", "bases de données", 3),
("SDID133", "systèmes d'exploitation", 3),
("HE141", "anglais", 3),
("HE142", "TE - débats, animation, PowerPoint", 3),

-- Semester 4
("SDID151", "logiciel R", 4),
("SDID152", "Python avancé", 4),
("SDID153", "projet intégrateur I", 4),
("HE161", "anglais", 4),
("HE162", "TE - conduite de réunion, coaching", 4),
("HE163", "développement du projet professionnel", 4),

-- semester 5
("SDID171", "business intelligence", 5),
("SDID172", "big data", 5),
("SDID173", "deep learning", 5),
("SDID181", "projet intégrateur II", 5),
("SDID182", "introduction à la sécurité informatique", 5),
("ST191", "système d'information", 5),
("ST192", "bases de données avancées", 5),
("HE201", "anglais", 5),
("HE202", "TE - rédaction administrative", 5),
("HE203", "développement du projet professionnel", 5),

-- SEA
-- Semester 3

("SEA113", "statistiques sectorielles", 3),
("SEA114", "statistiques démographiques", 3),
("SEA121", "économie du développement", 3),
("SEA122", "politique monétaire", 3),
("SEA123", "projet : études économiques", 3),

-- Semester 4
("SEA151", "enquêtes sociologiques", 4),
("SEA152", "mesures de la pauvreté et conditions de vie des ménages", 4),
("SEA153", "économétrie I", 4),


-- semester 5
("SEA171", "logiciels d'enquête", 5),
("SEA172", "sondage", 5),
("SEA181", "introduction aux big data", 5),
("SEA182", "suivi évaluation des ODD", 5),
("SEA183", "économétrie II", 5),
("SEA211", "Organisation des systèmes statistiques", 5),
("SEA212", "Management", 5),
("SEA213", "Management", 5)
;


SELECT * FROM niveau;
SELECT * FROM departement;
SELECT * FROM semestre;
SELECT * FROM cours ORDER BY code_sem;
SELECT * FROM etudiants ;
SELECT * FROM evaluer;

        
SELECT cours_code, intitulé_cours
FROM etudiants
JOIN departement ON etudiants.code_dep = departement.code_dep
JOIN niveau ON departement.code_niv = niveau.code_niv
JOIN semestre ON niveau.code_niv = semestre.code_niv
JOIN cours ON semestre.code_sem = cours.code_sem
WHERE etudiants.matricule = 23615 
  AND (
	niveau.intitulé_niv = 'L1'  -- Filter for L1 level students
    -- If student is from SEA, exclude courses starting with SDID
    OR
    (departement.intitulé_dep LIKE 'SEA%' AND cours.cours_code NOT LIKE 'SDID%')
    -- If student is from SDID, exclude courses starting with SEA
    OR
    (departement.intitulé_dep LIKE 'SDID%' AND cours.cours_code NOT LIKE 'SEA%')
  );
  
  
  SELECT matricule, nom, prenom, email, intitulé_dep
  FROM etudiants 
  JOIN departement ON etudiants.code_dep = departement.code_dep
  WHERE etudiants.matricule = 23618;
  ;
