# ==============================================================================
# Les librairies utilisées
# ==============================================================================
import mysql.connector
from datetime import datetime
import csv
import subprocess
import traceback



# ==============================================================================
# Définition de la classe d'exception pour gérer les erreurs
# ==============================================================================
class ErreurBdd(BaseException):
    def __init__(self, code, message):
        super().__init__()
        self.code = code
        self.message = message



# ==============================================================================
# Définition de la classe
# ==============================================================================
class Bdd():


    # ==========================================================================
    # Méthodes de base pour faire fonctionner la classe
    # ==========================================================================

    def __init__(self, configuration):
        """Méthode constructeur pour initialiser l'objet
        @param aucun
        @return rien
        """
        # Autres attributs
        self.debug = True

        if self.debug == True:
            print("Bdd::__init__()")

        # Attributs de connexion à MySQL
        self.adresse = ""
        self.utilisateur = ""
        self.mot_de_passe = ""
        self.nom = ""
        self.configuration = configuration

        # Attributs de gestion de la connexion MySQL
        self.cnx = None
        self.cur = None



    def se_connecter(self):
        """Méthode pour se connecter à la base de données MySQL
        @param configuration
        @return rien
        @throw Exception Si erreur de connexion
        """
        if self.debug == True:
            print("Bdd::se_connecter()")

        try:
            """
            # Connexion au serveur MySQL (méthode classique)
            self.cnx = mysql.connector.connect(
                host = self.adresse,
                user = self.utilisateur,
                password = self.mot_de_passe,
                database = self.nom)
            if self.debug == True:
                print("  + objet Connection =>", self.cnx)
            """
            # Connexion au serveur MySQL (avec un pool de connexions)
            self.cnx = mysql.connector.connect(
                pool_name = "enduropool",
                pool_size = 10,
                **self.configuration)

            # Création d'un object Cursor pour effectuer les requêtes
            if self.cnx is not None and self.cnx.is_connected() == True:
                self.cur = self.cnx.cursor()
            else:
                raise ErreurBdd(0, "Pas de connexion pour créer le curseur")

        except mysql.connector.Error as erreur:
            print("EXCEPTION [mysql.connector.Error] dans Bdd::se_connecter() =>", erreur)
            print("  + traceback :", traceback.print_exc() )
            raise ErreurBdd(0, erreur)



    def se_deconnecter(self):
        """Méthode pour se déconnecter à la base de données MySQL
        @param aucun
        @return rien
        @throw Exception Si erreur de déconnexion
        """
        if self.debug == True:
            print("Bdd::se_deconnecter()")

        try:
            # Fermeture du Cursor
            if self.cur is not None:
                self.cur.close()

            # Fermeture de la Connexion
            if self.cnx is not None and self.cnx.is_connected() == True:
                self.cnx.close()

        except mysql.connector.Error as erreur:
            print("EXCEPTION [mysql.connector.Error] dans Bdd::se_deconnecter() =>", erreur)
            print("  + traceback :", traceback.print_exc() )
            raise ErreurBdd(0, erreur)



    def executer_requete_sql_en_lecture(self, requete_sql, parametres):
        """Méthodes pour executer une requête SQL SELECT
        @param requete_sql
        @param requete_sql
        @return tuples
        """
        if self.debug == True:
            print("Bdd::executer_requete_sql_en_lecture()")
            print("  + requête sql =>", requete_sql)
            print("  + paramètres =>", parametres)

        resultats = None
        try:
            # Connexion à la base de données
            self.se_connecter()

            # Execution de la requete SQL SELECT
            self.cur.execute(requete_sql, parametres)

            # Récupération des resultats sous forme de tuples
            resultats = self.cur.fetchall()

            # Déconnexion de la base de données
            self.se_deconnecter()

        except mysql.connector.Error as erreur:
            # On fait remonter l'erreur
            print("EXCEPTION [mysql.connector.Error] dans Bdd::executer_requete_sql_en_lecture()")
            print("  + message =", erreur)
            print("  + detail requete =", self.cur._last_executed)
            print("  + traceback :", traceback.print_exc() )
            raise ErreurBdd(0, erreur)

        except ErreurBdd as erreur:
            print("EXCEPTION [ErreurBdd] dans Bdd::executer_requete_sql_en_lecture() =>", erreur.message)
            print("  + traceback :", traceback.print_exc() )
            raise

        # On retourne les resultats
        return resultats



    def executer_requete_sql_en_ecriture(self, requete_sql, parametres):
        """Méthodes pour executer une requête SQL INSERT INTO, UPDATE, DELETE
        @param requete_sql
        @return tuples
        """
        if self.debug == True:
            print("Bdd::executer_requete_sql_en_ecriture()")
            print("  + requête sql =>", requete_sql)
            print("  + paramètres =>", parametres)

        resultat = 0
        try:
            # Connexion à la base de données
            self.se_connecter()

            # Execution de la requete SQL SELECT
            self.cur.execute(requete_sql, parametres)

            # Applications des changements
            self.cnx.commit()
            resultat = self.cur.lastrowid
            print("dans executer_requete_sql_en_ecriture() =>", resultat)

            # Déconnexion de la base de données
            self.se_deconnecter()

        except mysql.connector.Error as erreur:
            # Annulation des changements
            self.cnx.rollback()

            # Affichage de l'erreur
            print("EXCEPTION [mysql.connector.Error] dans Bdd::executer_requete_sql_en_ecriture()")
            print("  + message =", erreur)
            print("  + detail requete =", self.cur._last_executed)
            print("  + traceback :", traceback.print_exc() )

            # On fait remonter l'exception
            raise ErreurBdd(0, erreur)

        except ErreurBdd as erreur:
            print("EXCEPTION [ErreurBdd] dans Bdd::executer_requete_sql_en_ecriture() =>", erreur.message)
            print("  + traceback :", traceback.print_exc() )
            raise

        # On retourne le dernier id concerné par la requête
        return resultat


    def rechercher_inscrit(self, nom_inscrit, prenom_inscrit, classe_inscrit):
        """Méthodes pour rechercher l'élève avec son nom, prenom, classe
        @param nom, prenom, classe
        @return ...
        """
        if self.debug == True:
            print("Bdd::rechercher_inscrit()")

        #Recherche de la personne
        resultats = None
        parametres = (nom_inscrit, prenom_inscrit, classe_inscrit)
        requete_sql = """
        SELECT enduro.coureurs.nom, enduro.coureurs.prenom, enduro.coureurs.classe
        FROM enduro.coureurs
        WHERE enduro.coureurs.nom = %s
        AND enduro.coureurs.prenom = %s
        AND enduro.coureurs.classe = %s;"""

        #Éxécution de la requête
        resultats = self.executer_requete_sql_en_lecture(requete_sql, parametres)

        #Retourne le resultats
        return resultats


    def coureurs_inscription(self, nom_inscription, prenom_inscription, classe_inscription, parrainage_inscription):
        """Méthodes pour inscrire un élève avec son nom, prenom, classe, argent/tour
        @param nom, prenom, classe, parrainage
        @return ...
        """

        if self.debug == True:
            print("Bdd::coureurs_inscription()")

        #Inscription de l'élève
        resultats = None
        parametres = (nom_inscription, prenom_inscription, classe_inscription, parrainage_inscription)
        requete_sql = """
        INSERT INTO enduro.coureurs (nom, prenom, classe, parrainage)
        VALUES (%s, %s, %s, %s);"""

        #Éxécution de la requête
        resultats = self.executer_requete_sql_en_ecriture(requete_sql, parametres)

        #Retourne les resultats
        return resultats


    # ==========================================================================
    # Méthodes pour la partie administration
    # ==========================================================================

    def recuperer_courses_toutes(self):
        """Méthodes pour récupérer toutes les courses dans la bdd
        @param aucun
        @return tuples de la forme (id, date, active, nb_coureurs, nb_passages)
        """
        if self.debug == True:
            print("Bdd::recuperer_courses_toutes()")

        # Récupération de toutes les courses
        resultats = None
        parametres = ()
        requete_sql = """
            SELECT enduro.courses.id, enduro.courses.date, enduro.courses.nom, enduro.courses.active, enduro.courses.archive, COUNT(DISTINCT(enduro.coureurs.id)), COUNT(enduro.passages.id)
            FROM enduro.courses
            LEFT JOIN enduro.coureurs
            ON enduro.courses.id = enduro.coureurs.id_course_fk
            LEFT JOIN enduro.passages
            ON enduro.coureurs.id = enduro.passages.id_coureur_fk
            GROUP BY enduro.courses.id;"""

        # Exécution de la requête
        resultats = self.executer_requete_sql_en_lecture(requete_sql, parametres)

        # Retourne le resultat
        return resultats



    def recuperer_courses_recentes(self):
        """Méthodes pour récupérer les courses récentes (> aujourd'hui)
        @param aucun
        @return tuples de la forme (id, date, nb_coureurs)
        """
        if self.debug == True:
            print("Bdd::recuperer_courses_recentes()")

        # Récupération des courses récentes
        resultats = None
        parametres = ()
        requete_sql = """
            SELECT * FROM enduro.courses
            WHERE date >= DATE(NOW());"""

        # Exécution de la requête
        resultats = self.executer_requete_sql_en_lecture(requete_sql, parametres)

        # Retourne le resultat
        return resultats



    def ajouter_une_course(self, date_de_la_course, nom_de_la_course):
        """Méthode pour ajouter une nouvelle course
        @param date_de_la_course au format YYYY-MM-DD
        @param nom_de_la_course
        @return ...
        """
        if self.debug == True:
            print("Bdd::ajouter_une_course()")
            print("  + date_de_la_course =>", date_de_la_course)

        # Réinitialisation du statut de course active pour les autres
        resultats = None
        parametres = ()
        requete_sql = """
            UPDATE enduro.courses
            SET active = 0;"""
        resultats = self.executer_requete_sql_en_ecriture(requete_sql, parametres)

        # Ajout de la course par défaut active
        parametres = (date_de_la_course, nom_de_la_course)
        requete_sql = """
            INSERT INTO enduro.courses (date, nom, active)
            VALUES (%s, %s, 1);"""
        resultats = self.executer_requete_sql_en_ecriture(requete_sql, parametres)

        # Retourne le resultat
        return resultats



    def supprimer_une_course(self, id_course):
        """Méthode pour ajouter une nouvelle course
        @param date_de_la_course
        @return ...
        """
        if self.debug == True:
            print("Bdd::supprimer_une_course()")
            print("  + id_course =>", id_course)

        # Réinitialisation du statut de course active pour les autres
        resultats = None
        parametres = (id_course, )
        requete_sql = """
            DELETE FROM enduro.courses
            WHERE id=%s"""
        resultats = self.executer_requete_sql_en_ecriture(requete_sql, parametres)
        print("apres =", resultats)

        # Retourne le resultat
        return resultats



    def choisir_une_course(self, id_course):
        """Méthode pour choisir la course de référence
        @param date_de_la_course
        @return ...
        """
        if self.debug == True:
            print("Bdd::choisir_une_course()")
            print("  + id_course =>", id_course)

        # Réinitialisation du statut de course active pour les autres
        resultats = None
        parametres = ()
        requete_sql = """
            UPDATE enduro.courses
            SET active = 0;"""
        resultats = self.executer_requete_sql_en_ecriture(requete_sql, parametres)

        # Mise à jour pour la course sélectionnée
        parametres = (id_course, )
        requete_sql = """
            UPDATE enduro.courses
            SET active = 1
            WHERE id=%s"""
        resultats = self.executer_requete_sql_en_ecriture(requete_sql, parametres)

        # Retourne le resultat
        return resultats



    def archiver_une_course(self, id_course):
        """Méthode pour archiver une course (calcul stats + suppression coureurs/passages)
        @param id_course à archiver
        @return ...
        """
        if self.debug == True:
            print("Bdd::archiver_une_course()")
            print("  + id_course =>", id_course)

        # Comptage du nombre de coureurs, du nombre de tours effectués et de l'argent gagné
        resultats = None
        parametres = (id_course, )
        requete_sql = """
            SELECT COUNT(enduro.coureurs.id), SUM(enduro.coureurs.distance_totale), SUM((enduro.coureurs.distance_totale * enduro.coureurs.parrainage) + enduro.coureurs.forfait)
            FROM enduro.coureurs
            WHERE enduro.coureurs.id_course_fk = %s;"""
        resultats = self.executer_requete_sql_en_lecture(requete_sql, parametres)

        # Décodage des valeurs
        if resultats is not None and len(resultats[0]) == 3:
            nb_participants = resultats[0][0]
            tours_effectues = resultats[0][1]
            argent_recolte = resultats[0][2]

            # Mise à jour du status archive pour la course sélectionnée
            parametres = (nb_participants, tours_effectues, argent_recolte, id_course)
            requete_sql = """
                UPDATE enduro.courses
                SET archive = 1, active = 0, nb_participants = %s, tours_effectues = %s, argent_recolte = %s
                WHERE enduro.courses.id = %s"""
            resultats = self.executer_requete_sql_en_ecriture(requete_sql, parametres)

            # Suppression des coureurs et des passages associés
            parametres = (id_course, )
            requete_sql = """
                DELETE FROM enduro.coureurs
                WHERE enduro.coureurs.id_course_fk = %s"""
            resultats = self.executer_requete_sql_en_ecriture(requete_sql, parametres)

        # Retourne le resultat
        return resultats



    def recuperer_course_active(self):
        """Méthodes pour récupérer la course active
        @param aucun
        @return id de la course
        """
        if self.debug == True:
            print("Bdd::recuperer_course_active()")

        # Préparation de la requête, ses paramètres et son résultat
        resultats = None

        # Recherche de la course avec le statut active
        parametres = ()
        requete_sql = """
            SELECT * FROM enduro.courses
            WHERE active = 1;"""
        resultats = self.executer_requete_sql_en_lecture(requete_sql, parametres)

        # Retourne le resultat
        return resultats



    def recuperer_coureurs_de_la_course(self, id_course):
        """Méthodes pour récupérer les coureurs participant à une certaine course
        @param id_course à laquelle participent les coureurs
        @return tuples de la forme (id, nom, prenom, classe, code_barre, parraingenb_coureurs)
        """
        if self.debug == True:
            print("Bdd::recuperer_coureurs_de_la_course()")
            print("  + id_course =>", id_course)

        # Préparation de la requête, ses paramètres et son résultat
        resultats = None

        # Récupération des coureurs associés à la course
        parametres = (id_course, )
        requete_sql = """
            SELECT * FROM enduro.coureurs
            INNER JOIN enduro.courses
            ON enduro.courses.id = enduro.coureurs.id_course_fk
            WHERE enduro.courses.id = %s;"""
        resultats = self.executer_requete_sql_en_lecture(requete_sql, parametres)

        # Retourne le resultat
        return resultats



    def ajouter_coureurs_depuis_csv(self, fichier_csv, id_course):
        """Fonction pour importer un fichier CSV dans la table coureurs
        @param fichier_csv
        @param id_course
        @return ...
        """
        if self.debug == True:
            print("Bdd::ajouter_coureurs_depuis_csv()")
            print("  + fichier_csv =>", fichier_csv)
            print("  + id_course =>", id_course)
            #raise ErreurBdd(0, "bonjour")

        # Préparation resultats
        resultats = 0

        try:
            # Ouverture du fichier CSV
            with open(fichier_csv, newline='') as csvfile:
                #csvfile = open(fichier_csv, newline='')

                # Lecture des données du fichier
                coureurs = csv.reader(csvfile, delimiter=';', quotechar='|')
                print(coureurs)

                # Ajout ligne par ligne des anniversaires
                for ligne in coureurs:
                    # Préparation de la requête SQL
                    requete_sql = """
                        INSERT INTO coureurs
                        (nom, prenom, classe, code_barre, parrainage, forfait, id_course_fk)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);"""

                    # Préparation des données
                    parametres = (ligne[0], ligne[1], ligne[2], ligne[3], ligne[4], ligne[5], id_course)

                    # Exécution de la requête
                    resultats = self.executer_requete_sql_en_ecriture(requete_sql, parametres)

        except OSError as erreur:
            # On fait remonter l'exception
            raise ErreurBdd(erreur.errno, erreur.strerror)

        # Retourne le resultat
        return resultats



    def exporter_une_course(self, id_course):
        """Méthodes pour exporter une course dans un fichier CSV
        @param id_course de la course à exporter
        @return tuples de la forme (id, date, active, nb_coureurs, nb_passages)
        """
        if self.debug == True:
            print("Bdd::exporter_une_course()")
            print("  + id_course =>", id_course)

        # Récupération de toutes les courses
        resultats = None
        parametres = (id_course, )
        requete_sql = """
            SELECT enduro.coureurs.nom, enduro.coureurs.prenom, enduro.coureurs.classe, enduro.coureurs.meilleur_temps, enduro.coureurs.distance_totale
            FROM enduro.coureurs
            WHERE enduro.coureurs.id_course_fk = %s
            ORDER BY enduro.coureurs.nom ASC;"""

        # Exécution de la requête
        resultats = self.executer_requete_sql_en_lecture(requete_sql, parametres)

        # Retourne le resultat
        return resultats



    def exporter_une_course_dans_un_fichier_csv_et_html(self, chemin_vers_fichier_csv, chemin_complet_vers_downloads, id_course):
        """Méthodes pour exporter une course dans un fichier CSV
        @param chemin_vers_fichier_csv le chemin complet (dossier+fichier) vers le fichier CSV contenant les résultats de la course
        @param chemin_complet_vers_downloads pour la génération du PDF à partir du HTML
        @param id_course de la course à exporter
        @return chemin_vers_fichier_csv
        """
        if self.debug == True:
            print("Bdd::exporter_une_course_dans_un_fichier_csv_et_html()")
            print("  + id_course =>", id_course)

        # Récupération des paramètres de la course
        la_course = None
        parametres = (id_course, )
        requete_sql = """
            SELECT enduro.courses.date, enduro.courses.nom
            FROM enduro.courses
            WHERE enduro.courses.id = %s;"""
        la_course = self.executer_requete_sql_en_lecture(requete_sql, parametres)

        # Récupération de tous les coureurs de la course
        les_coureurs = None
        parametres = (id_course, )
        requete_sql = """
            SELECT enduro.coureurs.nom, enduro.coureurs.prenom, enduro.coureurs.classe, enduro.coureurs.meilleur_temps, enduro.coureurs.distance_totale, enduro.coureurs.parrainage, enduro.coureurs.forfait
            FROM enduro.coureurs
            WHERE enduro.coureurs.id_course_fk = %s
            AND enduro.coureurs.distance_totale > 0
            ORDER BY enduro.coureurs.nom ASC;"""
        les_coureurs = self.executer_requete_sql_en_lecture(requete_sql, parametres)


        # Récupération des statistiques globales de la course
        statistiques = None
        parametres = (id_course, )
        requete_sql = """
            SELECT SUM(enduro.coureurs.distance_totale), SUM((enduro.coureurs.parrainage * enduro.coureurs.distance_totale) + enduro.coureurs.forfait), COUNT(enduro.coureurs.id), COUNT(CASE WHEN enduro.coureurs.distance_totale > 0 THEN 1 END)
            FROM enduro.coureurs
            WHERE enduro.coureurs.id_course_fk = %s;"""
        statistiques = self.executer_requete_sql_en_lecture(requete_sql, parametres)


        # Récupération des coureurs les plus rapides
        resultats_temps = None
        parametres = (id_course, )
        requete_sql = """
            SELECT enduro.coureurs.nom, enduro.coureurs.prenom, enduro.coureurs.classe, enduro.coureurs.meilleur_temps
            FROM enduro.coureurs
            WHERE enduro.coureurs.id_course_fk = %s
            AND enduro.coureurs.meilleur_temps < 9000
            AND enduro.coureurs.meilleur_temps > 180
            ORDER BY enduro.coureurs.meilleur_temps ASC
            LIMIT 5;"""
        resultats_temps = self.executer_requete_sql_en_lecture(requete_sql, parametres)


        # Récupération des coureurs les plus endurants
        resultats_distance = None
        parametres = (id_course, )
        requete_sql = """
            SELECT enduro.coureurs.nom, enduro.coureurs.prenom, enduro.coureurs.classe, enduro.coureurs.distance_totale
            FROM enduro.coureurs
            WHERE enduro.coureurs.id_course_fk = %s
            ORDER BY enduro.coureurs.distance_totale DESC
            LIMIT 5;"""
        resultats_distance = self.executer_requete_sql_en_lecture(requete_sql, parametres)

        # Récupération des classes les plus rapides
        resultats_temps_classe = None
        parametres = (id_course, )
        requete_sql = """
            SELECT enduro.coureurs.classe, AVG(enduro.coureurs.meilleur_temps)
            FROM enduro.coureurs
            WHERE enduro.coureurs.id_course_fk = %s
            AND enduro.coureurs.meilleur_temps < 9000
            AND enduro.coureurs.meilleur_temps > 180
            GROUP BY enduro.coureurs.classe
            ORDER BY AVG(enduro.coureurs.meilleur_temps) ASC
            LIMIT 5;"""
        resultats_temps_classe = self.executer_requete_sql_en_lecture(requete_sql, parametres)

        # Récupération des classes les plus endurantes
        resultats_distance_classe = None
        parametres = (id_course, )
        requete_sql = """
            SELECT enduro.coureurs.classe, AVG(enduro.coureurs.distance_totale)
            FROM enduro.coureurs
            WHERE enduro.coureurs.id_course_fk = %s
            AND enduro.coureurs.distance_totale > 0
            GROUP BY enduro.coureurs.classe
            ORDER BY AVG(enduro.coureurs.distance_totale) DESC
            LIMIT 5;"""
        resultats_distance_classe = self.executer_requete_sql_en_lecture(requete_sql, parametres)

        # Récupération des classes les plus participantes (taux de participation)
        resultats_participation_classe = None
        parametres = (id_course, )
        requete_sql = """
            SELECT enduro.coureurs.classe,
            (COUNT(CASE WHEN enduro.coureurs.distance_totale > 0 THEN 1 END)*100 /
            COUNT(CASE WHEN enduro.coureurs.distance_totale >= 0 THEN 1 END) ) as taux,
            COUNT(CASE WHEN enduro.coureurs.distance_totale > 0 THEN 1 END) as participants,
            COUNT(enduro.coureurs.id) as inscrits
            FROM enduro.coureurs
            WHERE enduro.coureurs.id_course_fk = %s
            AND enduro.coureurs.classe != "..."
            GROUP BY enduro.coureurs.classe
            ORDER BY taux DESC, inscrits ASC
            LIMIT 5;"""
        resultats_participation_classe = self.executer_requete_sql_en_lecture(requete_sql, parametres)


        # Ecriture des résultats dans un fichier CSV
        fichier_csv = None
        fichier_html = None

        try:
            # Ouverture du fichier CSV
            with open(chemin_vers_fichier_csv, "w") as fichier_csv:

                # Parcours de chaque ligne des résultats et écriture dans le fichier CSV
                for un_coureur in les_coureurs:
                    meilleur_temps = "%02d:%02d" % (divmod(un_coureur[3], 60))
                    ligne = "%s;%s;%s;%s;%s;%s;%s\n" % (
                        un_coureur[0],     # nom
                        un_coureur[1],     # prenom
                        un_coureur[2],     # classe
                        meilleur_temps,    # meilleur temps
                        un_coureur[4],      # nombre de tours effectués
                        un_coureur[5],      # parrainage au tour
                        un_coureur[6]      # forfait = parrainage pour toute la course
                    )
                    fichier_csv.write(ligne)

            # Ouverture du fichier HTML
            chemin_vers_fichier_html = chemin_vers_fichier_csv + ".html"
            with open(chemin_vers_fichier_html, "w") as fichier_html:

                # Préparation de l'en-tête HTML
                fichier_html.write("<!DOCTYPE html><html lang=\"fr\"><head><meta charset=\"utf-8\" /><title>Résultats course ENDURO</title>")
                fichier_html.write("<link href=\"../css/bootstrap.min.css\" rel=\"stylesheet\" /></head>")
                fichier_html.write("<body><main role=\"main\" class=\"container\">")
                fichier_html.write("<img src=\"../images/logo_saint_andre.png\" /><br /><h1 class=\"text-center\">Résultats de la course ENDURO</h1>")
                fichier_html.write("<h3 class=\"text-center\">%s le %s</h3><br /><br />" % (la_course[0][1], la_course[0][0]) )

                # Création du tableau des statistiques de course
                fichier_html.write("<p class=\"card-text font-italic\">Statistiques globales de la course :</p>")
                fichier_html.write("<table class=\"table table-striped\"><thead class=\"thead-dark\"><tr><th>Nombre de participants</th><th>Distance totale</th><th>Argent récolté</th></tr></thead><tbody>")
                ligne = "<tr><td>%s coureurs sur %s personnes au total</td><td>%s tours</td><td>%.02f €</td></tr>" % (
                    statistiques[0][3],     # nombre de participants
                    statistiques[0][2],     # nombre de participants
                    statistiques[0][0],     # distance totale parcourue
                    float(statistiques[0][1])/100.0,     # argent récolté
                )
                fichier_html.write(ligne)
                fichier_html.write("</tbody></table><br />")

                # Création du tableau des coureurs les plus rapides
                fichier_html.write("<p class=\"card-text font-italic\">Les 5 coureurs les plus rapides :</p>")
                fichier_html.write("<table class=\"table table-striped\"><thead class=\"thead-dark\"><tr><th>Nom</th><th>Prénom</th><th>Classe</th><th>Meilleur temps</th></tr></thead><tbody>")
                for un_coureur in resultats_temps:
                    meilleur_temps = "%02d:%02d" % (divmod(un_coureur[3], 60))
                    ligne = "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
                        un_coureur[0],      # nom
                        un_coureur[1],      # prénom
                        un_coureur[2],      # classe
                        meilleur_temps,     # meilleur temps
                    )
                    fichier_html.write(ligne)
                fichier_html.write("</tbody></table><br />")

                # Création du tableau des coureurs les plus endurants
                fichier_html.write("<p class=\"card-text font-italic\">Les 5 coureurs les plus endurants :</p>")
                fichier_html.write("<table class=\"table table-striped\"><thead class=\"thead-dark\"><tr><th>Nom</th><th>Prénom</th><th>Classe</th><th>Distance parcourue</th></tr></thead><tbody>")
                for un_coureur in resultats_distance:
                    ligne = "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s tours</td></tr>" % (
                        un_coureur[0],      # nom
                        un_coureur[1],      # prénom
                        un_coureur[2],      # classe
                        un_coureur[3],      # distance parcourue
                    )
                    fichier_html.write(ligne)
                fichier_html.write("</tbody></table><br />")

                # Création du tableau des classes les plus participantes
                fichier_html.write("<p class=\"card-text font-italic\">Les 5 classes les plus participantes :</p>")
                fichier_html.write("<table class=\"table table-striped\"><thead class=\"thead-dark\"><tr><th>Classe</th><th>Taux de participation</th></tr></thead><tbody>")
                for une_classe in resultats_participation_classe:
                    ligne = "<tr><td>%s</td><td>%s %% (%s/%s)</td></tr>" % (
                        une_classe[0],     # classe
                        une_classe[1],     # taux de participation
                        une_classe[2],     # participants
                        une_classe[3],     # inscrits
                    )
                    fichier_html.write(ligne)
                fichier_html.write("</tbody></table><br />")

                # Création du tableau des classes les plus rapides
                fichier_html.write("<p class=\"card-text font-italic\">Les 5 classes les plus rapides (selon meilleur temps moyen) :</p>")
                fichier_html.write("<table class=\"table table-striped\"><thead class=\"thead-dark\"><tr><th>Classe</th><th>Meilleur temps moyen</th></tr></thead><tbody>")
                for une_classe in resultats_temps_classe:
                    meilleur_temps_moyen = "%02d:%02d" % (divmod(une_classe[1], 60))
                    ligne = "<tr><td>%s</td><td>%s</td></tr>" % (
                        une_classe[0],      # classe
                        meilleur_temps_moyen,     # meilleur temps
                    )
                    fichier_html.write(ligne)
                fichier_html.write("</tbody></table><br />")

                # Création du tableau des classes les plus endurantes
                fichier_html.write("<p class=\"card-text font-italic\">Les 5 classes les plus endurantes (selon distance totale moyenne parcourue) :</p>")
                fichier_html.write("<table class=\"table table-striped\"><thead class=\"thead-dark\"><tr><th>Classe</th><th>Distance totale moyenne</th></tr></thead><tbody>")
                for une_classe in resultats_distance_classe:
                    ligne = "<tr><td>%s</td><td>%s tours</td></tr>" % (
                        une_classe[0],       # classe
                        une_classe[1],       # distance totale moyenne
                    )
                    fichier_html.write(ligne)
                fichier_html.write("</tbody></table><br />")


                # Création du tableau de tous les coureurs
                fichier_html.write("<p class=\"card-text font-italic\">Liste des coureurs par ordre alphabétique :</p>")
                fichier_html.write("<table class=\"table table-striped\"><thead class=\"thead-dark\"><tr><th>Nom</th><th>Prénom</th><th>Classe</th><th>Meilleur temps</th><th>Nombre de tour(s)</th></tr></thead><tbody>")
                for un_coureur in les_coureurs:
                    meilleur_temps = "%02d:%02d" % (divmod(un_coureur[3], 60))
                    ligne = "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
                        un_coureur[0],     # nom
                        un_coureur[1],     # prenom
                        un_coureur[2],     # classe
                        meilleur_temps,     # meilleur temps
                        un_coureur[4]      # nombre de tours effectués
                    )

                    fichier_html.write(ligne)

                # Fin du fichier HTML
                fichier_html.write("</tbody></table></main></body></html>")
                fichier_html.close()

            # Conversion du fichier HTML en PDF
            # wkhtmltopdf resultats_course.csv.html resultats_course.pdf
            print("  + conversion HTML vers PDF => xvfb-run wkhtmltopdf fichier_source fichier_destination")
            subprocess.run([
                "xvfb-run",
                "wkhtmltopdf",
                "%s/resultats_course.csv.html" % chemin_complet_vers_downloads,
                "%s/resultats_course.pdf" % chemin_complet_vers_downloads])


        except OSError as erreur:
            # On fait remonter l'exception
            print("  + EXCEPTION [OSError] => ", erreur)
            raise ErreurBdd(erreur.errno, erreur.strerror)


        except subprocess.SubprocessError as erreur:
            # On fait remonter l'exception
            print("  + EXCEPTION [SubprocessError] => ", erreur)
            raise ErreurBdd(erreur.errno, erreur.strerror)


        # Retourne le nom de la course
        return la_course[0][1]



    def reinitialiser_les_passages(self, id_course):
        """Méthode pour effacer les passages de tests et mettre à jour les compteurs des coureurs
        @param id_course
        @return ...
        """
        if self.debug == True:
            print("Bdd::reinitialiser_les_passages()")
            print("  + id_course =>", id_course)

        # Effacement de tous les passages de la course
        resultats = None
        parametres = (id_course, )
        requete_sql = """
            DELETE enduro.passages
            FROM enduro.passages
            INNER JOIN enduro.coureurs
            ON enduro.passages.id_coureur_fk = enduro.coureurs.id
            WHERE enduro.coureurs.id_course_fk = %s;"""
        resultats = self.executer_requete_sql_en_ecriture(requete_sql, parametres)

        # Mise à jour des statistiques calculées des coureurs
        parametres = (id_course, )
        requete_sql = """
            UPDATE enduro.coureurs
            SET dernier_temps = 9999, meilleur_temps = 9999, distance_totale = 0
            WHERE enduro.coureurs.id_course_fk = %s"""
        resultats = self.executer_requete_sql_en_ecriture(requete_sql, parametres)

        # Retourne le resultat
        return resultats



    # ==========================================================================
    # Méthodes pour l'IHM web mise à jour en direct
    # ==========================================================================

    def recuperer_derniers_passages(self, id_course, nb_passages_max):
        """Méthodes pour récupérer les derniers passages
        @param id_course courue actuellement
        @param nb_passages à récupérer
        @return tuples de la forme (nom, prenom, classe, dernier_temps, distance_totale)
        """
        if self.debug == True:
            print("Bdd::recuperer_derniers_passages()")
            print("  + id_course =>", id_course)
            print("  + nb_passages_max =>", nb_passages_max)

        # Préparation de la requête, ses paramètres et son résultat
        resultats = None

        # Récupération des N derniers passages dans la course
        parametres = (id_course, nb_passages_max)
        requete_sql = """
            SELECT DISTINCT(enduro.coureurs.id), enduro.coureurs.nom, enduro.coureurs.prenom, enduro.coureurs.classe, enduro.coureurs.dernier_temps, enduro.coureurs.distance_totale, MAX(enduro.passages.id), enduro.passages.date
            FROM enduro.coureurs
            INNER JOIN enduro.passages
            ON enduro.coureurs.id = enduro.passages.id_coureur_fk
            WHERE enduro.coureurs.id_course_fk = %s
            AND enduro.passages.temps < 9000
            GROUP BY enduro.coureurs.id, enduro.coureurs.nom, enduro.coureurs.prenom, enduro.coureurs.classe, enduro.coureurs.dernier_temps, enduro.coureurs.distance_totale, enduro.passages.date
            ORDER BY MAX(enduro.passages.id) DESC
            LIMIT %s;"""
        resultats = self.executer_requete_sql_en_lecture(requete_sql, parametres)

        # Retourne le resultat
        return resultats



    def recuperer_derniers_passages_de_test(self, id_course, nb_passages_max):
        """Méthodes pour récupérer les derniers passages de test
        @param id_course courue actuellement
        @param nb_passages à récupérer
        @return tuples de la forme (date, nom, prenom, classe, dernier_temps, distance_totale, numero_raspberry)
        """
        if self.debug == True:
            print("Bdd::recuperer_derniers_passages()")
            print("  + id_course =>", id_course)
            print("  + nb_passages_max =>", nb_passages_max)

        # Préparation de la requête, ses paramètres et son résultat
        resultats = None

        # Récupération des N derniers passages dans la course
        parametres = (id_course, nb_passages_max)
        requete_sql = """
            SELECT enduro.passages.date, enduro.coureurs.nom, enduro.coureurs.prenom, enduro.coureurs.classe, enduro.coureurs.dernier_temps, enduro.coureurs.distance_totale, enduro.passages.numero_raspberry
            FROM enduro.courses
            INNER JOIN enduro.coureurs
            ON enduro.courses.id = enduro.coureurs.id_course_fk
            INNER JOIN enduro.passages
            ON enduro.coureurs.id = enduro.passages.id_coureur_fk
            WHERE enduro.courses.id = %s
            ORDER BY enduro.passages.id DESC
            LIMIT %s;"""
        resultats = self.executer_requete_sql_en_lecture(requete_sql, parametres)

        # Retourne le resultat
        return resultats



    def recuperer_dernieres_statistiques(self, id_course):
        """Méthodes pour récupérer les derniers passages
        @param id_course courue actuellement
        @return tuples de la forme (...)
        """
        if self.debug == True:
            print("Bdd::recuperer_dernieres_statistiques()")
            print("  + id_course =>", id_course)

        # Préparation de la requête, ses paramètres et son résultat
        resultats = None

        # Récupération des N derniers passages dans la course
        parametres = (id_course, )
        requete_sql = """
            SELECT SUM(enduro.coureurs.distance_totale), SUM((enduro.coureurs.parrainage * enduro.coureurs.distance_totale) + enduro.coureurs.forfait), COUNT(enduro.coureurs.id)
            FROM enduro.coureurs
            WHERE enduro.coureurs.id_course_fk = %s;"""
        resultats = self.executer_requete_sql_en_lecture(requete_sql, parametres)

        # Retourne le resultat
        return resultats



    def recuperer_meilleurs_coureurs(self, id_course):
        """Méthodes pour récupérer les meilleurs coureurs
        @param id_course courue actuellement
        @return tuples de la forme (...)
        """
        if self.debug == True:
            print("Bdd::recuperer_meilleurs_coureurs()")
            print("  + id_course =>", id_course)

        # Préparation des résultats vides
        resultats_temps = None
        resultats_distance = None

        # Récupération du meilleur temps d'un coureur
        parametres = (id_course, )
        requete_sql = """
            SELECT enduro.coureurs.nom, enduro.coureurs.prenom, enduro.coureurs.meilleur_temps
            FROM enduro.coureurs
            WHERE enduro.coureurs.id_course_fk = %s
            AND enduro.coureurs.meilleur_temps < 9000
            ORDER BY enduro.coureurs.meilleur_temps ASC
            LIMIT 1;"""
        resultats_temps = self.executer_requete_sql_en_lecture(requete_sql, parametres)

        # Récupération de la meilleure distance parcourue par un coureur
        parametres = (id_course, )
        requete_sql = """
            SELECT enduro.coureurs.nom, enduro.coureurs.prenom, enduro.coureurs.distance_totale
            FROM enduro.coureurs
            WHERE enduro.coureurs.id_course_fk = %s
            ORDER BY enduro.coureurs.distance_totale DESC
            LIMIT 1;"""
        resultats_distance = self.executer_requete_sql_en_lecture(requete_sql, parametres)

        # Retourne le resultat
        return resultats_temps, resultats_distance


    # ==========================================================================
    # Méthodes pour la recherche et l'historique (partie publique)
    # ==========================================================================
    def rechercher_coureurs_resultats(self, id_course, nom_coureur):
        """Méthodes pour rechercher les résultats d'un coureur dans une course
        @param id_course courue par le coureur
        @param nom_coureur qui a couru la course
        @return tuples de la forme (...)
        """
        if self.debug == True:
            print("Bdd::rechercher_coureurs_resultats()")
            print("  + id_course =>", id_course)
            print("  + nom_coureur =>", nom_coureur)

        # Préparation des résultats vides
        resultats_du_coureur = None

        # Récupération du meilleur temps d'un coureur
        parametres = (id_course, nom_coureur)
        requete_sql = """
            SELECT enduro.coureurs.nom, enduro.coureurs.prenom, enduro.coureurs.classe, enduro.coureurs.meilleur_temps, enduro.coureurs.distance_totale, ((enduro.coureurs.distance_totale * enduro.coureurs.parrainage) + enduro.coureurs.forfait)
            FROM enduro.coureurs
            WHERE enduro.coureurs.id_course_fk = %s
            AND enduro.coureurs.nom LIKE UPPER(%s);"""
        resultats_du_coureur = self.executer_requete_sql_en_lecture(requete_sql, parametres)

        # Retourne le resultat
        return resultats_du_coureur



    # ==========================================================================
    # Méthodes pour le serveur MQTT
    # ==========================================================================

    def ajouter_un_passage(self, id_course, code_barre, numero_raspberry, delai_de_garde):
        """Méthode pour ajouter un passage d'un coureur dans la course
        @param id_course de la course active en cours
        @param code_barre du coureur qui vient de passer
        @param numero_raspberry où le coureur a badgé
        @param delai_de_garde à respecter
        @return ...

        Etapes :
          1 - vérifier si le code-barre existe dans la table coureurs
                si oui, récupérer l'id du coureur
                si non, insérer un nouveau coureur INCO NNU
          2 - vérifier si il y a déjà eu un passage pour ce coureur (via id)
                si oui, récupérer la date du dernier passage
                        calculer la différence avec la date de ce passage
                        insérer un nouveau passage avec date, temps et id_coureur_fk
                        mettre à jour table coureur : meilleur temps et total distance
                si non, insérer un nouveau passage avec date, temps=9999 et id_coureur_fk
          3 - récupérer/calculer les informations à renvoyer au raspberry par MQTT
                * nom
                * prénom
                * classe
                * numéro du tour (ou nombre de tours effectués)
                * meilleur temps
                * temps moyen
                * temps du dernier tour bouclé
                * argent récolté

        Méthodes disponibles :
            1 - id_coureur, nouveau_coureur = recuperer_ou_ajouter_un_coureur(id_course, code_barre)
            2 - id_passage, duree_dernier_tour = recuperer_et_ajouter_un_passage(id_coureur, numero_raspberry, delai_de_garde)
            2bis - mettre_a_jour_statistiques_coureur(id_coureur, duree_dernier_tour)
            3 - statistiques = recuperer_donnees_passage_du_coureur(id_coureur, duree_dernier_tour)

        Significations pour la variable code_etat retournée aux postes clients IHM.
        Si = 0, alors le passage a bien été enregistré pour un coureur existant dans la bdd, sinon chaque bit représente :
            xxxx xxxB => le coureur badgeait pour la première fois si B=1
            xxxx xxBx => le coureur n'existait pas dans la bdd si B=1
            xxxx xBxx => le délai de garde n'a pas été respecté si B=1
            xxxx Bxxx => une exception ErreurBdd a été levée si B=1
            xxxB xxxx => une exception Exception a été levée si B=1
        """
        # Affichage des paramètres si besoin
        if self.debug == True:
            print("Bdd::ajouter_un_passage()")
            print("  + id_course =>", id_course)
            print("  + code_barre =>", code_barre)
            print("  + numero_raspberry =>", numero_raspberry)
            print("  + delai_de_garde =>", delai_de_garde)

        # Variables
        code_etat = 0

        try:
            # Récupération ou ajout d'un coureur
            id_coureur, nouveau_coureur = self.recuperer_ou_ajouter_un_coureur(id_course, code_barre)

            # Récupération et ajout d'un passage
            id_passage, duree_dernier_tour = self.recuperer_et_ajouter_un_passage(id_coureur, numero_raspberry, delai_de_garde)

            #  Mise à jour des stats d'un coureur
            self.mettre_a_jour_statistiques_coureur(id_coureur, duree_dernier_tour)

            # Récupération des données et statistiques d'un coureur et de son passage
            donnees_passage = self.recuperer_donnees_passage_du_coureur(id_coureur, duree_dernier_tour)

            if self.debug == True:
                print("APRES APPELS FONCTIONS, AVANT CODE_ETAT")
                print("  + id_coureur =", id_coureur)
                print("  + nouveau_coureur =", nouveau_coureur)
                print("  + id_passage =", id_passage)
                print("  + duree_dernier_tour =", duree_dernier_tour)
                print("  + donnees_passage =", donnees_passage)

            # On fixe le code_etat pour informer le poste lecteur de l'état du passage avec le badge
            if duree_dernier_tour > 9000:
                code_etat += 1  # Le coureur badge pour la première fois et est donc dans son premier tour
            if nouveau_coureur == True:
                code_etat += 2  # Le coureur n'existe pas dans la bdd, il est ajouté sous un faux nom
            if id_passage == 0:
                code_etat += 4  # Le délai de garde n'est pas respecté

        except ErreurBdd as erreur:
            if self.debug == True:
                print("  + EXCEPTION ErreurBdd =>", erreur)
            code_etat += 8
            raise erreur

        except Exception as erreur:
            if self.debug == True:
                print("  + EXCEPTION Exception =>", erreur)
            code_etat += 16
            raise erreur

        # On retourne le résultat
        return donnees_passage, code_etat



    def recuperer_ou_ajouter_un_coureur(self, id_course, code_barre):
        """Méthode pour récupérer ou ajouter un coureur à la course
        @param id_course de la course active en cours
        @param code_barre du coureur
        @return ...
        """
        if self.debug == True:
            print("Bdd::recuperer_ou_ajouter_un_coureur()")
            print("  + id_course =>", id_course)
            print("  + code_barre =>", code_barre)

        resultats = None
        id_coureur = 0
        nouveau_coureur = None

        # Recherche si il existe un coureur avec ce code-barre ?
        parametres = (id_course, code_barre)
        requete_sql = """
            SELECT enduro.coureurs.id, enduro.coureurs.nom, enduro.coureurs.prenom
            FROM enduro.coureurs
            INNER JOIN enduro.courses
            ON enduro.courses.id = enduro.coureurs.id_course_fk
            WHERE enduro.courses.id = %s
            AND enduro.coureurs.code_barre = %s;"""
        resultats = self.executer_requete_sql_en_lecture(requete_sql, parametres)


        # Si le coureur existe on le retourne, sinon on l'ajoute dans la bdd
        if resultats:
            print("  + Coureur existant =>", resultats[0][0])
            id_coureur = resultats[0][0]
            nouveau_coureur = False
        else:
            print("  + Coureur inexistant")

            # Ajout d'un coureur inconnu dans la bdd
            parametres = ("INCO", "NNU", "...", code_barre, id_course)
            requete_sql = """
                INSERT INTO enduro.coureurs (nom, prenom, classe, code_barre, id_course_fk)
                VALUES (%s, %s, %s, %s, %s);"""
            id_coureur = self.executer_requete_sql_en_ecriture(requete_sql, parametres)
            nouveau_coureur = True


        # On retourne l'id du coureur et si il est nouveau ou pas
        return id_coureur, nouveau_coureur



    def recuperer_et_ajouter_un_passage(self, id_coureur, numero_raspberry, delai_de_garde):
        """Méthode pour récupérer et ajouter un passage d'un coureur
        @param id_coureur qui vient d'effectuer un passage
        @param numero_raspberry où le coureur à badgé
        @param delai_de_garde entre 2 passages
        @return id_passage qui vient d'être inséré dans la bdd
        """
        if self.debug == True:
            print("Bdd::recuperer_et_ajouter_un_passage()")
            print("  + id_coureur =>", id_coureur)
            print("  + numero_raspberry =>", numero_raspberry)
            print("  + delai_de_garde =>", delai_de_garde)

        # Variables résultats
        resultats = None
        id_passage = -1
        duree_tour_en_s = 9999
        respect_delai_de_garde = None


        # Recherche si il existe déjà un passage
        parametres = (id_coureur, )
        requete_sql = """
            SELECT enduro.passages.id, enduro.passages.date
            FROM enduro.passages
            WHERE enduro.passages.id_coureur_fk = %s
            ORDER BY enduro.passages.id DESC
            LIMIT 1;"""
        resultats = self.executer_requete_sql_en_lecture(requete_sql, parametres)
        if self.debug == True:
            print("  + resultats =>", resultats)


        # Si il y a déjà un passage on fait le calcul avant d'insérer pour vérifier le délai de garde
        if resultats:
            id_passage = resultats[0][0]
            ancienne_date = resultats[0][1]
            nouvelle_date = datetime.now()
            duree_tour = nouvelle_date - ancienne_date
            duree_tour_en_s = duree_tour.total_seconds()
            if self.debug == True:
                print("  + passage existant =>", nouvelle_date, " - ", ancienne_date, " = ", duree_tour_en_s)
        else:
            nouvelle_date = datetime.now()
            duree_tour_en_s = 9999
            if self.debug == True:
                print("  + passage inexistant, donc premier passage au départ => 9999")


        # Vérification du respect du delai de garde avant l'ajout d'un nouveau passage pour le coureur
        if duree_tour_en_s > delai_de_garde:
            parametres = (nouvelle_date.strftime("%Y-%m-%d %H:%M:%S"), numero_raspberry, duree_tour_en_s, id_coureur)
            requete_sql = """
                INSERT INTO enduro.passages (date, numero_raspberry, temps, id_coureur_fk)
                VALUES (%s, %s, %s, %s);"""
            id_passage = self.executer_requete_sql_en_ecriture(requete_sql, parametres)
            if self.debug == True:
                print("  + ajout d'un nouveau passage =>", id_passage)
        else:
            id_passage = 0
            if self.debug == True:
                print("  + delai de garde non respecté =>", duree_tour_en_s, " < ", delai_de_garde)


        # On retourne l'id du passage ajouté, la durée du dernier tour effectué et si le délai de garde a été respecté
        return id_passage, duree_tour_en_s



    def mettre_a_jour_statistiques_coureur(self, id_coureur, temps_dernier_tour):
        """Méthode pour récupérer et ajouter un passage d'un coureur
        @param id_coureur qui vient d'effectuer un passage
        @return ...
        """
        if self.debug == True:
            print("Bdd::mettre_a_jour_statistiques_coureur()")
            print("  + id_coureur =>", id_coureur)
            print("  + temps_dernier_tour =>", temps_dernier_tour)

        # Variables résultats
        resultats = None
        meilleur_temps = 9999


        # Récupération du meilleur temps et de la distance parcourue pour ce coureur
        parametres = (id_coureur, )
        requete_sql = """
            SELECT MIN(enduro.passages.temps), COUNT(enduro.passages.id)
            FROM enduro.passages
            WHERE enduro.passages.id_coureur_fk = %s;"""
        resultats = self.executer_requete_sql_en_lecture(requete_sql, parametres)
        if self.debug == True:
            print("  + resultats =>", resultats)
        meilleur_temps = resultats[0][0]
        distance_totale = resultats[0][1] - 1 # car le premier passage est le départ et pas un tour

        if self.debug == True:
            print("  + meilleur_temps =>", meilleur_temps)
            print("  + distance_totale =>", distance_totale)


        # Si il y a un meilleur temps, c'est à dire au moins un tour effectué par le coureur
        if meilleur_temps < 9999 and distance_totale > 0:

            parametres = (temps_dernier_tour, meilleur_temps, distance_totale, id_coureur)
            requete_sql = """
                UPDATE enduro.coureurs
                SET dernier_temps = %s, meilleur_temps = %s, distance_totale = %s
                WHERE enduro.coureurs.id = %s;"""
            id_coureur = self.executer_requete_sql_en_ecriture(requete_sql, parametres)



    def recuperer_donnees_passage_du_coureur(self, id_coureur, duree_dernier_tour):
        """Méthode pour récupérer les données d'un passage d'un coureur
        @param id_coureur qui vient d'effectuer un passage
        @param duree_dernier_tour en secondes
        @return un tuple (voir détails ci-dessous)
            * nom
            * prénom
            * classe
            * numéro du tour (ou nombre de tours effectués)
            * meilleur temps
            * temps moyen
            * temps du dernier tour bouclé
            * argent récolté

        """
        if self.debug == True:
            print("Bdd::recuperer_donnees_passage_du_coureur()")
            print("  + id_coureur =>", id_coureur)
            print("  + duree_dernier_tour =>", duree_dernier_tour)

        # Variables résultats
        resultats = None

        # Récupération du meilleur temps et de la distance parcourue pour ce coureur
        parametres = (id_coureur, id_coureur)
        requete_sql = """
            SELECT enduro.coureurs.nom, enduro.coureurs.prenom, enduro.coureurs.classe, COUNT(enduro.passages.id), MIN(enduro.passages.temps), ROUND(AVG(enduro.passages.temps)), enduro.coureurs.parrainage, enduro.coureurs.forfait
            FROM enduro.coureurs
            INNER JOIN enduro.passages
            ON enduro.coureurs.id = enduro.passages.id_coureur_fk
            WHERE enduro.coureurs.id = %s
            AND enduro.passages.id_coureur_fk = %s
            AND enduro.passages.temps < 9000;"""
        resultats = self.executer_requete_sql_en_lecture(requete_sql, parametres)
        if self.debug == True:
            print("  + resultats =>", resultats)

        # Préparation de la réponse
        donnees_passage = (
            resultats[0][0],
            resultats[0][1],
            resultats[0][2],
            resultats[0][3],
            resultats[0][4],
            resultats[0][5],
            duree_dernier_tour,
            resultats[0][6]*resultats[0][3] + resultats[0][7])

        return donnees_passage






# ==============================================================================
# Tests unitaires
# ==============================================================================
if __name__ == "__main__":

    """
    # Création et initialisation de la classe Bdd (méthode classique)
    print("Bdd::__init__()")
    bdd = Bdd()
    bdd.adresse = "localhost"
    bdd.utilisateur = "enduroadm"
    bdd.mot_de_passe = "enduropwd"
    bdd.nom = "enduro"
    """

    # Création et initialisation de la classe Bdd (avec pool de connexions)
    print("Bdd::__init__()")
    configuration = {}
    configuration["host"] = "localhost"
    configuration["user"] = "enduroadm"
    configuration["password"] = "enduropwd"
    configuration["database"] = "enduro"
    bdd = Bdd(configuration)

    #
    # Tests admin courses
    #
    try:
        # Récupération de toutes les courses
        for i in range(0, 100):
            print("Bdd::recuperer_courses_toutes()")
            print(bdd.recuperer_courses_toutes())

        # Récupération des courses
        #print("Bdd::recuperer_courses_recentes()")
        #print(bdd.recuperer_courses_recentes())

        # Suppression d'une course
        #print("Bdd::supprimer_une_course()")
        #print(bdd.supprimer_une_course(7))

        # Choix de la course active
        #print("Bdd::choisir_une_course()")
        #print(bdd.choisir_une_course(3))

        # Affichage de la course active
        #print("Bdd::recuperer_course_active()")
        #print(bdd.recuperer_course_active())

        # Affichage de la course active
        #print("Bdd::recuperer_coureurs_de_la_course()")
        #print(bdd.recuperer_coureurs_de_la_course(1))

        # Importation des coureurs depuis un fichier CSV
        #print("Bdd::ajouter_coureurs_depuis_csv()")
        #bdd.ajouter_coureurs_depuis_csv("./static/uploads/test.csv", 3)

        # Affichage de la course active
        #print("Bdd::reinitialiser_les_passages()")
        #print(bdd.reinitialiser_les_passages(3))



    except ErreurBdd as erreur:
        print("Exception ErreurBdd relevée dans __main__")
        print("  + code =>", erreur.code)
        print("  + message =>", erreur.message)
        print("  + traceback :", traceback.print_exc() )

    except:
        print("Exception inconnue relevée dans __main__")
        print("  + traceback :", traceback.print_exc() )



    """
    #
    # Tests CSV
    #

    # Importation des coureurs depuis un fichier CSV
    print("Bdd::ajouter_coureurs_depuis_csv()")
    bdd.ajouter_coureurs_depuis_csv("./static/uploads/coureurs01.csv", 2)
    """

    #print("Bdd::exporter_une_course_dans_un_fichier_csv()")
    #bdd.exporter_une_course_dans_un_fichier_csv_et_html("./static/downloads/resultats_course.csv", "/home/etudiant/projet_enduro/enduro_2018/enduro_git/serveur_central/static/downloads", 1)

    """
    #
    # Tests de l'ajout d'un passage d'un coureur (étape par étape)
    #

    # Récupérer/ajouter un coureur dans la base de données
    id_course = 2
    id_coureur = 14
    code_barre = 9999140
    delai_de_garde = 30

    #print("Bdd::recuperer_ou_ajouter_un_coureur()")
    #id_coureur, nouveau = bdd.recuperer_ou_ajouter_un_coureur(id_course, code_barre)
    #print("  id_coureur =", id_coureur)
    #print("  nouveau =", nouveau)

    # Récupérer/ajouter un coureur dans la base de données
    #print("Bdd::recuperer_et_ajouter_un_passage()")
    #id_passage, duree_tour = bdd.recuperer_et_ajouter_un_passage(id_coureur, delai_de_garde)
    #print("  id_passage =", id_passage)
    #print("  duree_tour =", duree_tour)

    # Mettre à jour les statistiques du coureur et de la course
    #print("Bdd::mettre_a_jour_statistiques_coureur()")
    #bdd.mettre_a_jour_statistiques_coureur(id_coureur)
    #print("Bdd::mettre_a_jour_statistiques_course()")
    #mettre_a_jour_statistiques_course(id_course)

    # Récupérer les données du passage d'un coureur
    #print("Bdd::recuperer_donnees_passage_du_coureur()")
    #print(bdd.recuperer_donnees_passage_du_coureur(id_coureur, id_course))
    """


    """
    #
    # Tests de l'ajout d'un passage d'un coureur (tout en un)
    #

    # Paramètres du test
    id_course = 2
    code_barre = 9999140
    numero_raspberry = 1
    delai_de_garde = 30

    # Ajouter un passage
    print("Bdd::ajouter_un_passage()")
    print(bdd.ajouter_un_passage(id_course, code_barre, numero_raspberry, delai_de_garde))
    """


    #
    # Tests récupération des données pour la page direct de l'IHM
    #
    """
    id_course = 1
    print("Bdd::recuperer_derniers_passages()")
    print(bdd.recuperer_derniers_passages(id_course, 5))

    #print("Bdd::recuperer_dernieres_statistiques()")
    #print(bdd.recuperer_dernieres_statistiques(id_course))

    #print("Bdd::recuperer_meilleurs_coureurs()")
    #print(bdd.recuperer_meilleurs_coureurs(id_course))
    """

    #
    # Tests de la recherche d'un coureur dans une course
    #
    """
    id_course = 1
    nom_coureur = "begood"

    print("Bdd::rechercher_coureurs_resultats()")
    print(bdd.rechercher_coureurs_resultats(id_course, nom_coureur))
    """
