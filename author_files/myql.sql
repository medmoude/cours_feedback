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

CREATE TABLE annee_universitaire (
id_annee_univ INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
lib_annee_univ VARCHAR(255) NOT NULL
) AUTO_INCREMENT = 2024 ; 

CREATE TABLE etudiants (
matricule INT NOT NULL ,
nom_prenom VARCHAR (100) NOT NULL,
email VARCHAR (100) NOT NULL,
mot_de_pass VARCHAR(255) NOT NULL,
code_dep INT NOT NULL,
id_annee_univ INT NOT NULL,
PRIMARY KEY(matricule, id_annee_univ),
FOREIGN KEY (code_dep) REFERENCES departement(code_dep),
FOREIGN KEY (id_annee_univ) REFERENCES annee_universitaire(id_annee_univ)
);

CREATE TABLE section (
id_section INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
lib_section VARCHAR(255) NOT NULL,
id_annee_univ INT NOT NULL,
FOREIGN KEY (id_annee_univ) REFERENCES annee_universitaire(id_annee_univ)
);

CREATE TABLE question (
id_question INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
lib_question VARCHAR(255) NOT NULL,
id_section INT NOT NULL,
FOREIGN KEY (id_section) REFERENCES section(id_section)
);

CREATE TABLE reponse (
id_reponse INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
lib_reponse VARCHAR(255) NOT NULL,
poids_reponse INT NOT NULL,
id_question INT NOT NULL,
FOREIGN KEY (id_question) REFERENCES question(id_question)
);

CREATE TABLE images (
id_image INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
nom_image VARCHAR(255) NOT NULL,
chemin_image VARCHAR(255) NOT NULL,
date_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
matricule INT NOT NULL,
FOREIGN KEY (matricule) REFERENCES etudiants(matricule)
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

INSERT INTO annee_universitaire (lib_annee_univ) VALUES
("2024-2025"),
("2025-2026"),
("2026-2027"),
("2027-2028"),
("2028-2029"),
("2029-2030"),
("2030-2031"),
("2031-2032"),
("2032-2033"),
("2033-2034")
;

-- cours insrtions
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

-- inserting the students 

-- L1 Insert
INSERT INTO etudiants (matricule, nom_prenom, email, mot_de_pass, code_dep, id_annee_univ) VALUES
(23602, 'Aichatou Mohamed Vall El Hacen', '23602@isms.esp.mr', 'Q7r8S9t0', 1, 2024),
(23616, 'Nouha Mohamed Tolba', '23616@isms.esp.mr', 'Y5z6A7b8', 1, 2024),
(23620, 'Zeinabou Mohamed El Mokhetar', '23620@isms.esp.mr', 'K7l8M9n0', 1, 2024),
(23629, 'Fatimetou Zahra Mohameden Bany', '23629@isms.esp.mr', 'Z1x2C3v4', 1, 2024),
(23631, 'Mohamed Ould Bou Zemragui', '23631@isms.esp.mr', 'B5n6M7k8', 1, 2024),
(23638, 'Mohamed Abdellahi Mahfoudh Taleb Ebeidi', '23638@isms.esp.mr', 'V3b4N5m6', 1, 2024),
(23650, 'Ahmed Baba Mohamed Lemin Mohamdhen Hamdi', '23650@isms.esp.mr', 'L7k8J9h0', 1, 2024),
(23653, 'Vatimetou Abdellahi Mouhameden', '23653@isms.esp.mr', 'T5r6E7w8', 1, 2024),
(23663, 'Mohamedou Bounene Cheikh', '23663@isms.esp.mr', 'R4t5Y6u7', 1, 2024),
(24601, 'Zeinebou Mohamed Yahye Mohamed Vall', '24601@isms.esp.mr', 'F3v4C5b6', 1, 2024),
(24602, 'Aboubakry Aliou N\'Diaye', '24602@isms.esp.mr', 'E7w8R9t0', 1, 2024),
(24603, 'Aichetou Mohamed Imijine', '24603@isms.esp.mr', 'P5o6I7u8', 1, 2024),
(24604, 'Vala Mohamed El ghawth', '24604@isms.esp.mr', 'A1s2D3f4', 1, 2024),
(24606, 'Nour Dine Mohamedou El Atigh', '24606@isms.esp.mr', 'H7j8K9l0', 1, 2024),
(24607, 'Fatimata Alassane Djigo', '24607@isms.esp.mr', 'Z9x8C7v6', 1, 2024),
(24608, 'Zoubeir Aliene Mreizig', '24608@isms.esp.mr', 'Y5u6I7o8', 1, 2024),
(24609, 'Zeinebou Mohamed Salem Sidi El vally', '24609@isms.esp.mr', 'W3e4R5t6', 1, 2024),
(24610, 'Nasra Abderrahmane Moussa', '24610@isms.esp.mr', 'Q7r8T9y0', 1, 2024),
(24611, 'Ahmedou Mohamedou Ahmed El mamy', '24611@isms.esp.mr', 'U5i6O7p8', 1, 2024),
(24612, 'Mohamed Lemine Cheikh El Kassem', '24612@isms.esp.mr', 'I7u8O9p0', 1, 2024),
(24613, 'Aicha Abdellahi Mohamed', '24613@isms.esp.mr', 'T4y5U6i7', 1, 2024),
(24614, 'Amy Mohamed Abderrahmane Soueilim', '24614@isms.esp.mr', 'R3e4W5q6', 1, 2024),
(24615, 'Mariem Bilal Youba', '24615@isms.esp.mr', 'E7r8T9y0', 1, 2024),
(24616, 'Sid\'El Moctar Ely Ely Mby Taleb', '24616@isms.esp.mr', 'O5i6U7y8', 1, 2024),
(24617, 'Sidi\'Ahmed Mohamed Abdellahi Taleb Ahmed', '24617@isms.esp.mr', 'M9l8K7j6', 1, 2024),
(24618, 'Saidou Hamidou Djam', '24618@isms.esp.mr', 'P7o8I9u0', 1, 2024),
(24619, 'Mohamed Cheikh Hamahoullah Mohamed Be', '24619@isms.esp.mr', 'A4s5D6f7', 1, 2024),
(24620, 'El Megboule Mohamed Aguerem', '24620@isms.esp.mr', 'C6v7B8n9', 1, 2024),
(24621, 'Mohamed Boubacar Sow', '24621@isms.esp.mr', 'J8k9L7m6', 1, 2024),
(24622, 'El Hasne Mohamed Lemine Namou', '24622@isms.esp.mr', 'N5m6L7k8', 1, 2024),
(24623, 'Taleb Amar Elhadj Beibacar', '24623@isms.esp.mr', 'Y3t4U5r6', 1, 2024),
(24625, 'Mohamed Salem Mohamed Behah', '24625@isms.esp.mr', 'F7d8G9h0', 1, 2024),
(24626, 'Oum El Mouminine Mohamed Yahya El Belli', '24626@isms.esp.mr', 'H9j8K7l6', 1, 2024),
(24627, 'Rim Mohamed Lemine Loudaa', '24627@isms.esp.mr', 'X5c6V7b8', 1, 2024),
(24628, 'Aichetou Vadhila Abdellahi Salem', '24628@isms.esp.mr', 'Z4x5C6v7', 1, 2024),
(24629, 'Rajil Maleck Matala', '24629@isms.esp.mr', 'O7p8I9u0', 1, 2024),
(24630, 'Moussa Abdoulaye N\'Dongo', '24630@isms.esp.mr', 'A1s2F3g4', 1, 2024),
(24631, 'Sidi Mohamed Mohamed Lemine Lehbib', '24631@isms.esp.mr', 'L9k8J7h6', 1, 2024),
(24632, 'Oumar Samba Camara', '24632@isms.esp.mr', 'V3b4N5m6', 1, 2024),
(24633, 'Ahmed Mohamed Cheikh Teguedi', '24633@isms.esp.mr', 'Y6t7U8r9', 1, 2024),
(24634, 'Vatimetou Mohamed Salem Daoud', '24634@isms.esp.mr', 'T4y5E6w7', 1, 2024),
(24635, 'Dah Mohamed Mahmoud', '24635@isms.esp.mr', 'P8o9I7u6', 1, 2024),
(24636, 'Zeinabou Ahmedou Cherif H\'Mah Allah', '24636@isms.esp.mr', 'R5t6Y7u8', 1, 2024),
(24637, 'Chourva Habibe Mened', '24637@isms.esp.mr', 'K9j8L7m6', 1, 2024),
(24638, 'Dileita Mohameden Nah', '24638@isms.esp.mr', 'F3g4H5j6', 1, 2024),
(24639, 'Vatimetou Mohamed Naji Lemrabott', '24639@isms.esp.mr', 'B7n8V9c0', 1, 2024),
(24640, 'Fatimetou Ahmed Lehbib', '24640@isms.esp.mr', 'O6i7U8p9', 1, 2024),
(24641, 'Aminetou Hachem Bougueyah', '24641@isms.esp.mr', 'A1d2F3g4', 1, 2024),
(24642, 'Oum El Benine Mohamed Abdrrahmane Ahmed', '24642@isms.esp.mr', 'H7j8L9k0', 1, 2024),
(24643, 'Ahmedou Elhassan Mohamedou', '24643@isms.esp.mr', 'F9v8C7b6', 1, 2024),
(24644, 'Fatimata Bouh Mohamed', '24644@isms.esp.mr', 'T5q6Y7u8', 1, 2024),
(24645, 'El Mokhtar El Hamdi Mohamed M\'Ahmed Sidi', '24645@isms.esp.mr', 'Q1r2T3u4', 1, 2024),
(24646, 'Baba Hailatou Mohamed Salem', '24646@isms.esp.mr', 'A8z7B9v0', 1, 2024),
(24647, 'Mohamedou Ould Mohameden', '24647@isms.esp.mr', 'M6k7P8o9', 1, 2024),
(24648, 'Siham Mohamed Salem Lahlou', '24648@isms.esp.mr', 'R2e3W4t5', 1, 2024),
(24649, 'Mohamed Ould Mohameden Ould Sidi', '24649@isms.esp.mr', 'T9g8F7h6', 1, 2024),
(24650, 'Mariem Ahmed Ould Mohameden', '24650@isms.esp.mr', 'S6h7U8j9', 1, 2024),
(24651, 'Seynabou Mariem Mohamed Lamine', '24651@isms.esp.mr', 'F9h8J7g6', 1, 2024),
(24652, 'Ahmedou Ould Mohamed Moulaye El Mejdoub', '24652@isms.esp.mr', 'N7v8W9z0', 1, 2024),
(24653, 'Oumoulkheiri Mohamed Salem Sidi', '24653@isms.esp.mr', 'Z9x8C7v6', 1, 2024),

-- L2 SDID
(23605, 'Abderrahmane Mohamedou Bou Elvali', '23605@isms.esp.mr', 'P2a3S4b5', 2, 2024),
(23607, 'Bamby Doro Thiam', '23607@isms.esp.mr', 'D6e7F8g9', 2, 2024),
(23609, 'Adde Cheikh H''Meyid', '23609@isms.esp.mr', 'H0i1J2k3', 2, 2024),
(23612, 'Lalle Baba El Arby', '23612@isms.esp.mr', 'L4m5N6o7', 2, 2024),
(23614, 'M''Barka Mhamed Rara Joughdane', '23614@isms.esp.mr', 'Q8r9S0t1', 2, 2024),
(23618, 'Mohamed Mahmoud Yaghoub El Jelelani', '23618@isms.esp.mr', 'U2v3W4x5', 2, 2024),
(23623, 'Yahya Cheikh Mohamed Mahfoud Vahvou', '23623@isms.esp.mr', 'Y6z7A8b9', 2, 2024),
(23626, 'Fatimata Abdoulaye Ba', '23626@isms.esp.mr', 'C0d1E2f3', 2, 2024),
(23634, 'Souckeyna El Ghoutoub Essedat', '23634@isms.esp.mr', 'G4h5I6j7', 2, 2024),
(23635, 'Sidi Amar Cheikh Mohamed El Hafedh Ahmedou', '23635@isms.esp.mr', 'K8l9M0n1', 2, 2024),
(23636, 'Aly Sidi Mohamed Mohamed Ahmed', '23636@isms.esp.mr', 'O2p3Q4r5', 2, 2024),
(23637, 'Cheikhna El Vagha Sid''Amine', '23637@isms.esp.mr', 'S6t7U8v9', 2, 2024),
(23639, 'Mohamed El Hacen El Bar Jeyid', '23639@isms.esp.mr', 'W0x1Y2z3', 2, 2024),
(23642, 'Naji Mohamed Lemine Jed Oumou', '23642@isms.esp.mr', 'A4b5C6d7', 2, 2024),
(23644, 'Mohamed Hmetou Rajel', '23644@isms.esp.mr', 'E8f9G0h1', 2, 2024),
(23647, 'Mouhamed Yahye Mohamed Abdellahi Tajer', '23647@isms.esp.mr', 'I2j3K4l5', 2, 2024),
(23651, 'Vatimetou Abdellahi Daghana', '23651@isms.esp.mr', 'M6n7O8p9', 2, 2024),
(23654, 'Oumoukelthoum Souleymane Souleymane', '23654@isms.esp.mr', 'Q0r1S2t3', 2, 2024),
(23656, 'Hindou Bebay Boubi', '23656@isms.esp.mr', 'U4v5W6x7', 2, 2024),
(23657, 'Memmy Bedi Ahmedhou ould Zeyad', '23657@isms.esp.mr', 'Y8z9A0b1', 2, 2024),
(23658, 'Mohamed Moutar', '23658@isms.esp.mr', 'C2d3E4f5', 2, 2024),

-- L2 SEA
(22640, 'Mohamed vall Mohamedou', '22640@isms.esp.mr', 'P2q3R4s5', 3, 2024),
(23603, 'Zeinebou Mohamed Lemine Ennahoui', '23603@isms.esp.mr', 'T6u7V8w9', 3, 2024),
(23604, 'Mohamedou Bemba Cheikh Elya', '23604@isms.esp.mr', 'X0y1Z2a3', 3, 2024),
(23606, 'Mohamed Mohamed Lemin Ahmed', '23606@isms.esp.mr', 'B4c5D6e7', 3, 2024),
(23610, 'El Hadrami Cheikh Saleck Abdellahi', '23610@isms.esp.mr', 'F8g9H0i1', 3, 2024),
(23613, 'Mariem Mohamed Salem Mohamed El Abd', '23613@isms.esp.mr', 'J2k3L4m5', 3, 2024),
(23615, 'Hbib Mohamed Abatty', '23615@isms.esp.mr', 'N6o7P8q9', 3, 2024),
(23621, 'Zeinebou Oumar Moulaye Idriss', '23621@isms.esp.mr', 'R0s1T2u3', 3, 2024),
(23622, 'Ahmedou Baba Ebnou', '23622@isms.esp.mr', 'V4w5X6y7', 3, 2024),
(23624, 'Nenny Zeidan Beida', '23624@isms.esp.mr', 'Z8a9B0c1', 3, 2024),
(23625, 'Zeinebou Cheikh Sidi Ahmed El Bekaye M''Bareck', '23625@isms.esp.mr', 'D2e3F4g5', 3, 2024),
(23627, 'Aicha Mohamed El Moctar Lehbib', '23627@isms.esp.mr', 'H6i7J8k9', 3, 2024),
(23630, 'Henani Mohamed Hanany', '23630@isms.esp.mr', 'L0m1N2o3', 3, 2024),
(23632, 'Moulaye Ahmed El Yezid El Araby', '23632@isms.esp.mr', 'P4q5R6s7', 3, 2024),
(23641, 'Mama Cheikh Sidi Hamou', '23641@isms.esp.mr', 'T8u9V0w1', 3, 2024),
(23645, 'Abdellahi Mohamed Tiyeb Abdalla', '23645@isms.esp.mr', 'X2y3Z4a5', 3, 2024),
(23646, 'Abdallahi Isselmou Khiar Ntajou', '23646@isms.esp.mr', 'B6c7D8e9', 3, 2024),
(23648, 'Mohamed Abdellahi Mohemd El Moktar Abd Dayem', '23648@isms.esp.mr', 'F0g1H2i3', 3, 2024),
(23649, 'Fatma Babe Ahmed Wehne', '23649@isms.esp.mr', 'J4k5L6m7', 3, 2024),
(23655, 'Aichetou TAleb Mouhamed Jeyid', '23655@isms.esp.mr', 'N8o9P0q1', 3, 2024),
(23659, 'Khadijetou Mohamed Meouloud Abdouli', '23659@isms.esp.mr', 'R2s3T4u5', 3, 2024),
(23660, 'Cheikhna MahfoudNA Ahmed Jiddou', '23660@isms.esp.mr', 'V6w7X8y9', 3, 2024),
(23662, 'Khaled Mohamed Abdellahi Beidech', '23662@isms.esp.mr', 'Z0a1B2c3', 3, 2024),


-- L3 (this is only L3 SEA)
(21305, 'Zekerya Ethmane Sow', '21305@isms.esp.mr', 'A1b2C3d4', 5, 2024),
(22601, 'Bilghisse El Hadramy Ahmed Deida', '22601@isms.esp.mr', 'E5f6G7h8', 5, 2024),
(22602, 'Hademine Mohamed Khyar', '22602@isms.esp.mr', 'I9j0K1l2', 5, 2024),
(22604, 'Alassane Samba Cissoko', '22604@isms.esp.mr', 'M3n4O5p6', 5, 2024),
(22607, 'Ahmed Bechir Wodhane', '22607@isms.esp.mr', 'Q7r8S9t0', 5, 2024),
(22608, 'Sidati Mohamed El Ghadhi', '22608@isms.esp.mr', 'U1v2W3x4', 5, 2024),
(22610, 'Mohamed Nouh Bechir Oubeid', '22610@isms.esp.mr', 'Y5z6A7b8', 5, 2024),
(22611, 'Mohamed Cheikh Ahmed Oumar', '22611@isms.esp.mr', 'C9d0E1f2', 5, 2024),
(22612, 'Sid\'Ahmed Mohamed Mohamed Abbe', '22612@isms.esp.mr', 'G3h4I5j6', 5, 2024),
(22613, 'Ahmed Salem Ennour Ahaymed', '22613@isms.esp.mr', 'K7l8M9n0', 5, 2024),
(22614, 'Isselmou Mohamed Leghdhef Beyah', '22614@isms.esp.mr', 'O1p2Q3r4', 5, 2024),
(22615, 'El Ghaliya Sid\'Ahmed Ely Tem', '22615@isms.esp.mr', 'S5t6U7v8', 5, 2024),
(22616, 'Sida Said Mane', '22616@isms.esp.mr', 'W9x0Y1z2', 5, 2024),
(22617, 'El Jouneid Moussa Belal', '22617@isms.esp.mr', 'A3b4C5d6', 5, 2024),
(22618, 'Mariem Abdellahi Edda', '22618@isms.esp.mr', 'E7f8G9h0', 5, 2024),
(22619, 'Mamouye Dian Dianifaba', '22619@isms.esp.mr', 'I1j2K3l4', 5, 2024),
(22620, 'Mouadh Ahmed Mahmoud Mohamed Mouftah', '22620@isms.esp.mr', 'M5n6O7p8', 5, 2024),
(22621, 'Mariem Mohmeden Ana', '22621@isms.esp.mr', 'Q9r0S1t2', 5, 2024),
(22623, 'Oum El Vadly Mohamed Salem Boullah', '22623@isms.esp.mr', 'U3v4W5x6', 5, 2024),
(22624, 'Lareibiya Amar Bakar', '22624@isms.esp.mr', 'Y7z8A9b0', 5, 2024),
(22625, 'Abdel Khader Mohamed Vadel Abd El Kader', '22625@isms.esp.mr', 'C1d2E3f4', 5, 2024),
(22626, 'Mohamedene Ahmed Babah', '22626@isms.esp.mr', 'G5h6I7j8', 5, 2024),
(22627, 'Khadijetou Mohamed Salem Sidi Baba', '22627@isms.esp.mr', 'K9l0M1n2', 5, 2024),
(22630, 'Mohamed Abdellahi Cheikh Ahmed El Waghf', '22630@isms.esp.mr', 'O3p4Q5r6', 5, 2024),
(22631, 'Ahmed Chrif Cheikh Sid\'Ahmed Ahmed Maouloud', '22631@isms.esp.mr', 'S7t8U9v0', 5, 2024),
(22632, 'Mamoudou Djibril Ba', '22632@isms.esp.mr', 'W1x2Y3z4', 5, 2024),
(22633, 'Sidi Baccar Mohamed Ehmame', '22633@isms.esp.mr', 'A5b6C7d8', 5, 2024),
(22634, 'Mohamed Mahmoud Mohamed El Atigh', '22634@isms.esp.mr', 'E9f0G1h2', 5, 2024),
(22635, 'El Hafedh Cheikhany Mohamed Saleh', '22635@isms.esp.mr', 'I3j4K5l6', 5, 2024),
(22636, 'Mohamed Bechire Adberahmann', '22636@isms.esp.mr', 'M7n8O9p0', 5, 2024),
(22637, 'Mohamed El Moctar Mohamed Mohamadou', '22637@isms.esp.mr', 'Q1r2S3t4', 5, 2024),
(22638, 'Mohamed Sid\'Ahmed Mohamed Abd', '22638@isms.esp.mr', 'U5v6W7x8', 5, 2024),
(22639, 'Meimouna Baba Cheikh Sidiya', '22639@isms.esp.mr', 'Y9z0A1b2', 5, 2024);




#select from all tables (show the data)
SELECT * FROM niveau;
SELECT * FROM departement;
SELECT * FROM semestre;
SELECT * FROM cours ORDER BY code_sem;
SELECT * FROM etudiants order by code_dep;
SELECT * FROM evaluer;
SELECT * FROM images;
SELECT * FROM images WHERE matricule = 23602 ORDER BY date_upload desc;


#showing students relevant courses 
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
  

SELECT matricule, nom_prenom, email, intitulé_dep
FROM etudiants 
JOIN departement ON etudiants.code_dep = departement.code_dep
WHERE etudiants.email = '23618@isms.esp.mr';


SELECT ROUND(AVG(evaluation), 2) AS avg_evaluation, intitulé_cours 
FROM evaluer 
JOIN cours ON evaluer.cours_code = cours.cours_code
GROUP BY intitulé_cours;

DESC etudiants;