"""Application web dynamique Bonjour

Ce tutoriel présente le framework (cadriciel) Flask qui permet de réaliser
des applications web dynamiques relativement simplement.

Cette première version minimaliste affiche simplement un message
"""

# Librairie(s) utilisée(s)
from flask import *
from datetime import datetime
from werkzeug.utils import secure_filename
from bdd import *
from PIL import Image
import os

bpPA = Blueprint('bpPA',__name__)


# Création de l'objet pour accéder à la base de données SQLite
bdd = Bdd("bdd/data.sqlite")


# Page pour afficher le formulaire de téléversement
@bpPA.route("/test-televersement")
def tester_televersement():
    return render_template("bonjour_televersement.html")

# Contrôleur pour récupérer le fichier téléversé
@bpPA.route("/televersement-fichier", methods=["POST"])
def televerser_fichier():
    # Récupération du fichier (si il est présent dans request)
    if "fichier" not in request.files:
        flash("Pas de fichier envoyé")
        return redirect("/test-televersement")
    fichier = request.files["fichier"]

    x = datetime.now()
    mystring = str(x)
    # Renommage du fichier s'il a un nom
    if fichier.filename == "":
        flash("Pas de nom au fichier envoyé")
        return redirect("/test-televersement")
    nom_fichier = secure_filename(mystring+".jpg")

    # Vérification de l'extension du fichier
    if nom_fichier.rsplit(".", 1)[1].lower() != "jpg":
        flash("Pas de nom au fichier envoyé")
        return redirect("/test-televersement")


    # Sinon, si tout est bon, on sauvegarde le fichier sur le serveur...
    fichier.save(f"static/photo/{nom_fichier}")
    flash(f"Félicitations, le fichier {nom_fichier} a bien été téléversé")

    # Va chercher l'image dans le dossier
    image = Image.open(f"static/photo/{nom_fichier}")
    image.show()

    width, height = image.size
    print(width, height)

    new_width = 1200
    new_height = 800

    # Permet de rendimensionner les photos
    resized_image = image.resize((new_width, new_height))
    print(resized_image.size)

    resized_image.save(f"static/photo/{nom_fichier}")
    """
	if fichier:
		# Enregistrement en local du fichier CSV
		chemin_vers_fichier_photo = os.path.join(current_app.config['CHEMIN_VERS_UPLOADS_PHOTO'], nom_fichier)
		fichier.save(chemin_vers_fichier_photo)

		# Enregistrement dans la base de données du contenu CSV
		try:
			resultat = bdd.ajouter_photos_depuis_jpg(chemin_vers_fichier_photo)
			flash("Les coureurs ont bien été ajoutés depuis %s" % chemin_vers_fichier_photo, "success")
		except ErreurBdd as erreur:
			flash("Une erreur est survenue (%s)" % erreur.message, "danger")

	else:
		flash("Fichier inexistant", "danger")
        """

    # ... et on redirige vers la page d'origine
    return redirect("/test-televersement")




# Page utilisant du CSS et une image
@bpPA.route("/test-css-img")
def tester_css_img():
    """Affiche un template contenant lié à un fichier CSS"""
    return render_template("bonjour_css_img.html")


# Lancement de l'application web et son serveur
# accessible à l'URL : http://127.0.0.1:1664
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1664, threaded=True, debug=True)

    