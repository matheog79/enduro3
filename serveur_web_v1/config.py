"""
@brief Fichier de configuration de l'application
@author David SALLE
@date 29/03/2017
@version 0.1
@licence GPL3
"""


class Config(object):
    """Classe pour centraliser différents paramètres de configuration
    """

    # Quand le mode DEBUG est activé, les programmes produisent des logs en console
    # qui donnent des informations sur le déroulement des opérations, par contre
    # cela peut réduire les performances des programmes
    DEBUG = True

    # Identifiants (login + password) permettant d'entrer dans la partie
    # administration de l'application web (http://127.0.0.1/administration)
    ADMIN_LOGIN = "admin"
    ADMIN_PASSWORD = "p4ssw0rd"

    # Nombre de passages maximum affichés sur la page de suivi en direct de la course
    DIRECT_MAX_PASSAGES = 10

    # Délai de garde en secondes entre 2 passages d'un même badge
    DELAI_DE_GARDE = 30

    # Nom du fichier CSV de secours
    FICHIER_CSV_SECOURS = "./passages_course_enduro.csv"

    # Paramètres pour accéder à la base de données hébergée sur un serveur
    # MySQL (ou MariaDB)
    BDD_HOST = "10.231.1.189"
    BDD_NAME = "enduro"
    BDD_USER_IHM = "matheo"
    BDD_PASSWORD_IHM = "matheo"

    # Identifiants pour accéder au réseau MQTT (TODO: pas encore utilisé)
    BDD_USER_MQTT = "enduromqtt"
    BDD_PASSWORD_MQTT = "enduropwd"

    # Chemin vers le dossier où est téléversé le fichier CSV avant d'être inséré
    # dans la base de données (normalement ne pas y toucher)
    CHEMIN_VERS_UPLOADS_CSV = "./static/uploads"

    # Chemin vers le dossier contenant les résultats de la course en CSV et HTML
    # (normalement ne pas y toucher)
    CHEMIN_VERS_DOWNLOADS_CSV = "./static/downloads"
    FICHIER_RESULTATS_CSV = "resultats_course.csv"
    CHEMIN_COMPLET_VERS_DOWNLOADS = "/var/www/enduro/static/downloads"

    # Phrase secrète utilisée pour crypter les sessions
    PHRASE_SECRETE = "Allez cham01s !?! ... (ou pas)"



class DevelopmentConfig(Config):
    """Classe pour centraliser différents paramètres de configuration
    lors de la phase de développement
    """
    pass
