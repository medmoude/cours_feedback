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
nom VARCHAR (50) NOT NULL,
prenom VARCHAR (50) NOT NULL,
email VARCHAR (50) NOT NULL,
num_telephone VARCHAR (8) NOT NULL,
code_dep INT NOT NULL,
FOREIGN KEY (code_dep) REFERENCES departement(code_dep)
);


CREATE TABLE cours (
cours_code VARCHAR(10) NOT NULL PRIMARY KEY,
intitulé_cours VARCHAR(50) NOT NULL,
code_sem INT NOT NULL,
FOREIGN KEY (code_sem) REFERENCES semestre(sem_code)
);

CREATE TABLE evaluer (
evaluation INT NOT NULL ,
commentaire TEXT NOT NULL,
matricule INT NOT NULL ,
cours_code INT NOT NULL,
FOREIGN KEY(matricule) REFERENCES etudiants(mtricule),
FOREIGN KEY(cours_code) REFERENCES cours(cours_code)

);