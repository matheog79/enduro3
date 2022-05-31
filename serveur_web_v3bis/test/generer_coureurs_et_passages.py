"""
Fichier pour générer N coureurs dans un fichier CSV
@author Sallé David
@date 26/10/2018
@version 0.1
"""

# Librairies utilisées
from random import randint


"""
# Paramètres de la generation
nom_fichier_csv = "coureurs03.csv"
nb_coureurs = 1500

# Ouverture du fichier CSV
fichier_csv = open(nom_fichier_csv, "w")

# Ajout de coureurs non random
ligne = "BEGOOD;JOHNNY;SNIR3;9999140;1000\n"
fichier_csv.write(ligne)


# Boucle de génération
for i in range(0, nb_coureurs):
    parrainage = randint(9, 999)
    ligne = "NOM%04d;PRENOM%04d;CLASSE%02d;%07d;%03d\n" % (i, i, i%99, i, parrainage)
    fichier_csv.write(ligne)

# Fermeture du fichier CSV
fichier_csv.close()
"""


# Paramètres de la generation
nom_fichier_sql = "dump_bdd_26102018.db"
nb_coureurs = 1500
nb_passages = 6000

# Tableaux pour stocker temporairement les données
les_coureurs = []
les_passages = []


# Ouverture du fichier CSV
fichier_sql = open(nom_fichier_sql, "w")


# Génération des données pour les coureurs
for i in range(1, nb_coureurs+1):
    parrainage = randint(9, 999)
    les_coureurs.append([i, 9999, 9999, 0, parrainage])


# Génération des données pour les passages qui doivent modifier les données des coureurs
pas_encore_passe = []
pas_encore_passe = list( range(1, nb_coureurs) )
for i in range(1, nb_passages+1):
    # Choix aléatoire d'un id de coureur
    id_coureur = randint(1, nb_coureurs-1)

    # Si premier tour alors temps_tour = 9999 sinon aléatoire et incrémentation nombre de tours
    if id_coureur in pas_encore_passe:
        temps_tour = 9999
        pas_encore_passe.remove(id_coureur)
    else:
        temps_tour = randint(200, 1500)
        les_coureurs[id_coureur][3] += 1

    # Mise à jour du dernier temps du coureur
    les_coureurs[id_coureur][1] = temps_tour

    # Mise à jour de son meilleur temps
    if temps_tour < les_coureurs[id_coureur][2]:
        les_coureurs[id_coureur][2] = temps_tour

    les_passages.append([i, id_coureur+1, temps_tour])


#print(les_coureurs)
#print(les_passages)

# Ajout de coureurs non random
fichier_sql.write("--\n-- Les coureurs\n--\n")

# Boucle de génération de requête SQL à écrire dans le fichier
for i in range(1, nb_coureurs+1):
    if i == 1:
        ligne = "INSERT INTO coureurs VALUES (%d,'BEGOOD','Johnny','SNIR3',9999140,%03d,5000,%04d,%04d,%d,1);\n" % (i, les_coureurs[i-1][4], les_coureurs[i-1][1], les_coureurs[i-1][2], les_coureurs[i-1][3])
    else:
        ligne = "INSERT INTO coureurs VALUES (%d,'NOM%04d','Prenom%04d','CLASSE%02d',%07d,%03d,0,%04d,%04d,%d,1);\n" % (i, i, i, i%99, i, les_coureurs[i-1][4], les_coureurs[i-1][1], les_coureurs[i-1][2], les_coureurs[i-1][3])
    fichier_sql.write(ligne)


# Boucle de génération des passages
fichier_sql.write("\n--\n-- Les passages\n--\n")

for i in range(1, nb_passages+1):
    ligne = "INSERT INTO passages VALUES (%d,'2018-10-21 09:00:00',%d,%d,%d);\n" % (i, (les_passages[i-1][0]%3)+1, les_passages[i-1][2], les_passages[i-1][1])
    fichier_sql.write(ligne)


# Fermeture du fichier CSV
fichier_sql.close()
