from flask import Flask, request, render_template, session, flash, redirect, url_for, jsonify, Response, send_from_directory
from werkzeug.utils import secure_filename
from datetime import timedelta, datetime
import os
import json
import sys
#import psutil
import decimal
from bdd import Bdd, ErreurBdd
from enduro_MG import bpMG

# ==============================================================================
# Création/initialisation des objets Flask et Bdd
# ==============================================================================

# Bannière d'accueil
print("#####################################")
print("### Serveur WEB Flask Enduro v0.1 ###")
print("#####################################\n")

# Création et initialisation de l'application Flask
app = Flask(__name__)
app.register_blueprint(bpMG)
app.config.from_object("config.DevelopmentConfig")
app.secret_key = app.config["PHRASE_SECRETE"]

# Création et initialisation de la classe Bdd
configuration = {}
bdd = Bdd(configuration)

# ==============================================================================
# Définition des routes et fonctions associées (partie publique)
# ==============================================================================
@app.route('/')
@app.route('/accueil')
def afficher_accueil():
	"""Fonction pour gérer la page d'accueil
	@param Aucun
	@return Le template
	"""
	return render_template('public_accueil.html')

@app.route('/resultats')
def afficher_resultats():
	"""Fonction pour gérer la page du classement
	@param Aucun
	@return Le template
	"""
	return render_template('public_resultats.html')

@app.route('/direct')
def afficher_classement_direct():
	"""Fonction pour gérer la page du classement en direct
	@param Aucun
	@return Le template
	"""
	return render_template('public_classement_direct.html')

@app.route('/inscription')
def afficher_inscription():
	"""Fonction pour gérer les inscription
	@param Aucun
	@return le template
	"""
	return render_template('public_inscription.html')

@app.route('/inscription/modification')
def afficher_inscription_modification():
	"""Fonction pour gérer les inscription
	@param Aucun
	@return le template
	"""
	return render_template('public_inscription_etape3.html')

@app.route('/inscription/suppression')
def afficher_inscription_suppression():
	"""Fonction pour gérer les inscription
	@param Aucun
	@return le template
	"""
	return render_template('public_inscription_etape4.html')


@app.route('/credits')
def afficher_credits():
	"""Fonction pour afficher les crédits
	@param Aucun
	@return le template
	"""
	return render_template('public_credits.html')


@app.route('/inscription/recherche', methods=["POST"])
def recherche_inscrit():
	"""Fonction pour afficher l'étape 1 de l'inscription
	@param Aucun
	@return le template
	"""

	#Récupération de l'id de la course active 
	course = None
	course_active = None
	try:
		course = bdd.recuperer_course_active()
		course_active = course[0][0]
	except ErreurBdd as erreur:
		flash("Une erreur est survenue (%s)" % erreur, "danger")

	#Récupération des paramètres de la requête
	nom_inscrit = request.form["nom_inscrit"]
	prenom_inscrit = request.form["prenom_inscrit"]
	classe_inscrit = request.form["classe_inscrit"]
	deja_inscrit = True
	print("nom =>", nom_inscrit)
	print("prenom =>", prenom_inscrit)
	print("classe =>", classe_inscrit)
	print("id_course =>", course_active)

	#Envoie de la requête SQL
	deja_inscrit = None
	try:
		recherche_coureurs = bdd.rechercher_inscrit(nom_inscrit, prenom_inscrit, classe_inscrit, course_active)
		print(recherche_coureurs)
		if recherche_coureurs == []:
			deja_inscrit = False
		else:
			deja_inscrit = True

	except ErreurBdd as erreur:
		flash("Une erreur est survenue (%s)" % erreur, "danger")

	return render_template('public_inscription_etape2.html', deja_inscrit=deja_inscrit)


@app.route('/inscription/modification', methods=["POST"])
def inscription_modification():
	"""Fonction pour gérer la modification
	@param Aucun
	@return le template
	"""

	#Récupération de l'id de la course active 
	course = None
	course_active = None
	try:
		course = bdd.recuperer_course_active()
		course_active = course[0][0]
	except ErreurBdd as erreur:
		flash("Une erreur est survenue (%s)" % erreur, "danger")

	#Récupération des paramètre de la requête
	parrainage_modification = request.form["parrainage_modification"]
	nom_modification = request.form["nom_modification"]
	prenom_modification = request.form["prenom_modification"]
	classe_modification = request.form["classe_modification"]
	print("nom =>", nom_modification)
	print("prenom =>", prenom_modification)
	print("classe =>", classe_modification)
	print("parrrainage =>", parrainage_modification)
	print("id_course =>", course_active)

	#Envoie de la requête SQL
	try:
		modification_coureur = bdd.modifier_coureur(nom_modification, prenom_modification, classe_modification, parrainage_modification, course_active)
		print(modification_coureur)
		flash("Votre inscription à été modifié", "success")

	except ErreurBdd as erreur:
		flash("une erreur est survenue (%s)" % erreur, "danger")

	return render_template('public_inscription_etape3.html')



@app.route('/inscription/suppression', methods=["POST"])
def inscription_suppression():
	"""Fonction pour gérer les inscription
	@param Aucun
	@return le template
	"""

	#Récupération de l'id de la course active 
	course = None
	course_active = None
	try:
		course = bdd.recuperer_course_active()
		course_active = course[0][0]
	except ErreurBdd as erreur:
		flash("Une erreur est survenue (%s)" % erreur, "danger")

	#Récupératoin des paramètres de la requête
	nom_inscrit_supr = request.form["nom_inscrit_supr"]
	prenom_inscrit_supr = request.form["prenom_inscrit_supr"]
	classe_inscrit_supr = request.form["classe_inscrit_supr"]
	print("nom =>", nom_inscrit_supr)
	print("prenom =>", prenom_inscrit_supr)
	print("classe =>", classe_inscrit_supr)
	print("id_course =>", course_active)

	#Envoie de la requête SQL
	try:
		suppression_coureur = bdd.supprimer_coureur(nom_inscrit_supr, prenom_inscrit_supr, classe_inscrit_supr, course_active)
		print(suppression_coureur)
		flash("Votre inscription à été supprimée", "success")

	except ErreurBdd as erreur:
		flash("une erreur est survenue (%s)" % erreur, "danger")

	return render_template('public_inscription_etape4.html')


@app.route('/inscription', methods=["POST"])
def inscription():
	"""Fonction pour afficher l'inscription
	@param Aucun
	@return le template
	"""

	#Récupération de l'id de la course active 
	course = None
	course_active = None
	try:
		course = bdd.recuperer_course_active()
		course_active = course[0][0]
	except ErreurBdd as erreur:
		flash("Une erreur est survenue (%s)" % erreur, "danger")

	#Récupération des paramètres de la requête
	nom_inscription = request.form["nom_inscription"]
	prenom_inscription = request.form["prenom_inscription"]
	classe_inscription = request.form["classe_inscription"]
	parrainage_inscription = request.form["parrainage_inscription"]
	print("nom =>", nom_inscription)
	print("prenom =>", prenom_inscription)
	print("classe =>", classe_inscription)
	print("parrrainage =>", parrainage_inscription)
	print("id_course =>", course_active)

	#Envoie de la requête SQL
	try:
		coureurs_inscription_en_cours = bdd.coureurs_inscription(nom_inscription, prenom_inscription, classe_inscription, parrainage_inscription, course_active)
		print(coureurs_inscription_en_cours)
		flash("Vous êtes inscrit pour l'Enduro", "success")

	except ErreurBdd as erreur:
		flash("Une erreur est survenue (%s)" % erreur, "danger")
	
	return render_template('public_inscription_etape2.html')


# ==============================================================================
# Définition des routes et fonctions associées (partie tutoriel administration)
# ==============================================================================
@app.route('/administration/tutoriel/etape1')
def administrer_tutoriel_etape1():
	"""Fonction pour l'étape #1 du tutoriel d'administration
	@param Aucun
	@return template
	"""
	# Vérification de l'authentification et redirection si pas bon
	if "authentifie" not in session:
		flash("Vous devez vous authentifier pour accéder à cette page", "danger")
		return redirect(url_for("afficher_accueil_admin"))

	# On retourne les résultats intégrés au template
	return render_template('admin_tutoriel_etape1.html')


@app.route('/administration/tutoriel/etape2')
def administrer_tutoriel_etape2():
	"""Fonction pour l'étape #2 du tutoriel d'administration
	@param Aucun
	@return template
	"""
	# Vérification de l'authentification et redirection si pas bon
	if "authentifie" not in session:
		flash("Vous devez vous authentifier pour accéder à cette page", "danger")
		return redirect(url_for("afficher_accueil_admin"))

	# Récupération de toutes les courses dans la bdd
	try:
		les_courses = bdd.recuperer_courses_toutes()
		print(les_courses)
	except ErreurBdd as erreur:
		flash("Une erreur est survenue (%s)" % erreur, "danger")

	# On retourne les résultats intégrés au template
	return render_template('admin_tutoriel_etape2.html', les_courses=les_courses)



@app.route('/administration/tutoriel/etape3')
def administrer_tutoriel_etape3():
	"""Fonction pour l'étape #3 du tutoriel d'administration
	@param Aucun
	@return template
	"""
	# Vérification de l'authentification et redirection si pas bon
	if "authentifie" not in session:
		flash("Vous devez vous authentifier pour accéder à cette page", "danger")
		return redirect(url_for("afficher_accueil_admin"))

	# Récupération des courses récentes
	les_courses = None
	try:
		les_courses = bdd.recuperer_courses_recentes()
	except ErreurBdd as e:
		flash("Une erreur est survenue (%s)" % e, "danger")

	# On retourne le template
	return render_template('admin_tutoriel_etape3.html', les_courses=les_courses)


@app.route('/administration/tutoriel/etape4')
def administrer_tutoriel_etape4():
	"""Fonction pour l'étape #4 du tutoriel d'administration
	@param Aucun
	@return template
	"""
	# Vérification de l'authentification et redirection si pas bon
	if "authentifie" not in session:
		flash("Vous devez vous authentifier pour accéder à cette page", "danger")
		return redirect(url_for("afficher_accueil_admin"))

	# On retourne le template
	return render_template('admin_tutoriel_etape4.html')



@app.route('/administration/tutoriel/etape5')
def administrer_tutoriel_etape5():
	"""Fonction pour l'étape #6 du tutoriel d'administration
	@param Aucun
	@return template
	"""
	# Vérification de l'authentification et redirection si pas bon
	if "authentifie" not in session:
		flash("Vous devez vous authentifier pour accéder à cette page", "danger")
		return redirect(url_for("afficher_accueil_admin"))

	# Récupération de toutes les courses dans la bdd
	les_courses = None
	try:
		les_courses = bdd.recuperer_courses_toutes()
		print(les_courses)
	except ErreurBdd as erreur:
		flash("Une erreur est survenue (%s)" % erreur, "danger")

	# On retourne les résultats intégrés au template
	return render_template('admin_tutoriel_etape5.html', les_courses=les_courses)



@app.route('/administration/tutoriel/etape6')
def administrer_tutoriel_etape6():
	"""Fonction pour l'étape #7 du tutoriel d'administration
	@param Aucun
	@return template
	"""
	# Vérification de l'authentification et redirection si pas bon
	if "authentifie" not in session:
		flash("Vous devez vous authentifier pour accéder à cette page", "danger")
		return redirect(url_for("afficher_accueil_admin"))

	# On retourne les résultats intégrés au template
	return render_template('admin_tutoriel_etape6.html')

@app.route('/administration')
def afficher_accueil_admin():
	"""Fonction pour gérer la partie administration après authentification
	@param Aucun
	@return le template
	"""
	return render_template('admin_accueil.html')

@app.route("/administration/login", methods=["POST"])
def administrer_login():
	"""Fonction pour gérer l'authentification de la zone d'administration
	@param Aucun
	@return template + flash
	"""
    # Récupération des paramètres de la requête
	login = request.form["login"]
	password = request.form["password"]
	print("login    =>", login)
	print("password =>", password)

	# Appel de la fonction dédiée
	if login == app.config["ADMIN_LOGIN"] and password == app.config["ADMIN_PASSWORD"]:
		flash("Authentification réussie ... bonne visite !", "success")
		session["id_utilisateur"] = "admin"
		session["login"] = login
		session["authentifie"] = True
	else:
		flash("Authentification impossible. Vérifiez vos identifiants", "danger")

	# On redirige l'utilisateur vers la page d'accueil de l'administration
	return redirect(url_for("afficher_accueil_admin"))

@app.route("/administration/logout", methods=["POST"])
def administrer_logout():
	"""Fonction pour gérer la déconnexion de la zone d'administration
	@param Aucun
	@return rien
	"""
	# Mise à jour des variables de session
	session["id_utilisateur"] = 0
	session["login"] = ""
	session["authentifie"] = None
	session.pop('authentifie', None)

	# Et affichage d'un message de confirmation
	flash("Déconnexion réussie ... à bientôt !", "success")

	# On redirige l'utilisateur vers la page d'accueil
	return redirect(url_for("afficher_accueil_admin"))


@app.route('/direct/dernierstests')
def recuperer_derniers_passages_course_test():
	"""Fonction pour générer depuis la base de données les statistiques de la course
	@param Aucun
	@return Les données en JSON

	Format des données : (date, nom, prenom, classe, dernier_temps, distance_totale, numero_raspberry)
	"""
	# Récupération de l'id de la course active
	if "id_course_active" not in session:
		try:
			course_active = bdd.recuperer_course_active()
			session["id_course_active"] = course_active[0][0]
		except ErreurBdd as erreur:
			statistiques["erreur"] = "Une erreur est survenue (%s)" % erreur.message
			return jsonify(statistiques)

	# Récupération de toutes les courses dans la bdd
	derniers_passages = None
	try:
		derniers_passages = bdd.recuperer_derniers_passages_de_test(session["id_course_active"], 7)
		#print(derniers_passages)
	except ErreurBdd as erreur:
		flash("Une erreur est survenue (%s)" % erreur.message, "danger")

	# Préparation du dictionnaire
	les_passages = []
	if derniers_passages is not None:
		for un_passage in derniers_passages:
			un_passage_dict = {}
			un_passage_dict["date"] = un_passage[0]
			un_passage_dict["nom"] = un_passage[1]
			un_passage_dict["prenom"] = un_passage[2]
			un_passage_dict["classe"] = un_passage[3]
			un_passage_dict["temps"] = formater_temps(un_passage[4])
			un_passage_dict["distance"] = un_passage[5]
			un_passage_dict["numero_raspberry"] = un_passage[6]
			les_passages.append(un_passage_dict)

	def convertisseur(donnee):
	    if isinstance(donnee, datetime):
	        return donnee.__str__()
	derniers_passages_en_json = json.dumps(les_passages, default=convertisseur)
	print(derniers_passages_en_json)

	# Plutôt json.dumps que jsonify car erreur avec les tableaux
	return Response(derniers_passages_en_json, mimetype='application/json')


@app.route('/administration/courses')
def administrer_courses():
	"""Fonction pour afficher le courses
	@param Aucun
	@return template
	"""
	# Vérification de l'authentification et redirection si pas bon
	if "authentifie" not in session:
		flash("Vous devez vous authentifier pour accéder à cette page", "danger")
		return redirect(url_for("afficher_accueil_admin"))

	# Récupération de toutes les courses dans la bdd
	try:
		les_courses = bdd.recuperer_courses_toutes()
		print(les_courses)

	except ErreurBdd as erreur:
		flash("Une erreur est survenue (%s)" % erreur, "danger")

	return render_template('admin_courses.html', les_courses=les_courses)

@app.route('/administration/courses/ajouter', methods=["POST"])
def administrer_courses_ajouter():
	"""Fonction pour ajouter une nouvelle course
	@param Aucun
	@return template + flash
	"""
	# Vérification de l'authentification et redirection si pas bon
	if "authentifie" not in session:
		flash("Vous devez vous authentifier pour accéder à cette page", "danger")
		return redirect(url_for("afficher_accueil_admin"))

	# Variables
	resultats = None
	date_course_en_s = 0
	difference = 0

	# Récupération des informations du formulaire
	date_de_la_course = request.form["date_de_la_course"]
	nom_de_la_course = request.form["nom_de_la_course"]

	# Vérification si la date saisie est bien dans le futur
	date_course = "%s_23:59" % date_de_la_course
	print("date course =>", date_course)
	try:
		date_course_en_s = datetime.strptime(date_course, "%Y-%m-%d_%H:%M").timestamp()
	except ValueError as e:
		flash("Une erreur est survenue (Le format de date n'est pas correct)", "danger")

	aujourd_hui_en_s = datetime.today().timestamp()
	difference = date_course_en_s - aujourd_hui_en_s
	print(difference)

	if difference < 0:
		flash("Une erreur est survenue (La date choisie dans être dans le futur)", "danger")
	else:
		resultats = bdd.ajouter_une_course(date_de_la_course, nom_de_la_course)
		print(resultats)

	# Notification
	if resultats > 0:
		flash("La course %s a bien été ajoutée" % nom_de_la_course, "success")

	# On redirige l'utilisateur vers la page d'accueil
	return redirect(url_for("afficher_accueil_admin"))

@app.route('/administration/courses/supprimer/<int:id_course>')
def administrer_courses_supprimer(id_course):
	"""Fonction pour supprimer une course
	@param id_course de la course à supprimer
	@return template + flash
	"""
	# Vérification de l'authentification et redirection si pas bon
	if "authentifie" not in session:
		flash("Vous devez vous authentifier pour accéder à cette page", "danger")
		return redirect(url_for("administrer_accueil"))

	# Suppression de la course
	try:
		resultat = bdd.supprimer_une_course(id_course)
		flash("La course a bien été supprimée", "success")
	except ErreurBdd as erreur:
		flash("Une erreur est survenue (%s)" % erreur, "danger")

	# On redirige l'utilisateur vers la page d'accueil
	return redirect(url_for("administrer_tutoriel_etape2"))

@app.route('/administration/courses/choisir/<int:id_course>')
def administrer_courses_choisir(id_course):
	"""Fonction pour choisir la course de référence
	@param id_course de la course à sélectionner comme course de référence
	@return template + flash
	"""
	# Vérification de l'authentification et redirection si pas bon
	if "authentifie" not in session:
		flash("Vous devez vous authentifier pour accéder à cette page", "danger")
		return redirect(url_for("administrer_accueil"))

	try:
		resultat = bdd.choisir_une_course(id_course)
		session["id_course_active"] = id_course
		flash("La course a bien été choisie", "success")
	except ErreurBdd as e:
		flash("Une erreur est survenue (%s)" % e, "danger")

	# On redirige l'utilisateur vers la page d'accueil
	return redirect(url_for("administrer_tutoriel_etape2"))



@app.route('/administration/courses/archiver/<int:id_course>')
def administrer_courses_archiver(id_course):
	"""Fonction pour choisir la course à archiver (stats)
	@param id_course de la course à archiver
	@return template + flash
	"""
	# Vérification de l'authentification et redirection si pas bon
	if "authentifie" not in session:
		flash("Vous devez vous authentifier pour accéder à cette page", "danger")
		return redirect(url_for("administrer_accueil"))

	try:
		resultat = bdd.archiver_une_course(id_course)
		flash("La course a bien été archivée", "success")
	except ErreurBdd as e:
		flash("Une erreur est survenue (%s)" % e, "danger")

	# On redirige l'utilisateur vers la page d'accueil
	return redirect(url_for("administrer_tutoriel_etape6"))



@app.route('/administration/courses/exporter/<int:id_course>')
def administrer_courses_exporter(id_course):
	"""Fonction pour choisir la course à exporter en CSV
	@param id_course de la course à exporter
	@return template + flash
	"""
	# Vérification de l'authentification et redirection si pas bon
	if "authentifie" not in session:
		flash("Vous devez vous authentifier pour accéder à cette page", "danger")
		return redirect(url_for("administrer_accueil"))

	# Exportation des résultats de la course en HTML
	try:
		chemin_complet_csv = "%s/%s" % (app.config["CHEMIN_VERS_DOWNLOADS_CSV"], app.config["FICHIER_RESULTATS_CSV"])
		nom_course = bdd.exporter_une_course_dans_un_fichier_csv_et_html(chemin_complet_csv, app.config["CHEMIN_COMPLET_VERS_DOWNLOADS"], id_course)
		flash("La course %s a bien été exportée dans le fichier resulats_course.pdf" % nom_course, "success")
	except ErreurBdd as e:
		flash("Une erreur est survenue (%s)" % e, "danger")

	# On redirige l'utilisateur vers la page d'accueil
	return redirect(url_for("administrer_tutoriel_etape7"))

	# Export HTML
	# Exportation des résultats de la course en HTML
	try:
		les_coureurs = bdd.exporter_une_course(id_course)
		flash("La course a bien été exportée", "success")
	except ErreurBdd as e:
		flash("Une erreur est survenue (%s)" % e, "danger")

	# On redirige l'utilisateur vers la page d'accueil
	return render_template('admin_export.html', les_coureurs=les_coureurs, formater_temps=formater_temps)
	

@app.route('/administration/courses/reinitialiser/<int:id_course>')
def administrer_courses_reinitialiser(id_course):
	"""Fonction pour réinitialiser une course en supprimant ses passages et réinitialisant les stats des coureurs
	@param id_course de la course à réinitialiser
	@return template + flash
	"""
	# Vérification de l'authentification et redirection si pas bon
	if "authentifie" not in session:
		flash("Vous devez vous authentifier pour accéder à cette page", "danger")
		return redirect(url_for("administrer_accueil"))

	try:
		resultat = bdd.reinitialiser_les_passages(id_course)
		flash("La course a bien été réinitialisée", "success")
	except ErreurBdd as e:
		flash("Une erreur est survenue (%s)" % e, "danger")

	# On redirige l'utilisateur vers la page d'accueil
	return redirect(url_for("administrer_tutoriel_etape4"))

@app.route('/administration/coureurs')
def administrer_coureurs():
	"""Fonction pour afficher les coureurs
	@param Aucun
	@return template + flash
	"""
	# Vérification de l'authentification et redirection si pas bon
	if "authentifie" not in session:
		flash("Vous devez vous authentifier pour accéder à cette page", "danger")
		return redirect(url_for("afficher_accueil_admin"))

	try:
		# Récupération des courses récentes
		les_courses = bdd.recuperer_courses_recentes()
	except ErreurBdd as e:
		flash("Une erreur est survenue (%s)" % e, "danger")

	return render_template('admin_coureurs_import.html', les_courses=les_courses)

@app.route('/administration/coureurs/afficher', methods=["GET", "POST"])
def administrer_coureurs_afficher():
	"""Fonction pour afficher les coureurs
	@param id_course
	@return template + flash
	"""
	# Vérification de l'authentification et redirection si pas bon
	if "authentifie" not in session:
		flash("Vous devez vous authentifier pour accéder à cette page", "danger")
		return redirect(url_for("afficher_accueil_admin"))

	# Récupération de toutes les courses dans la bdd
	les_courses = bdd.recuperer_courses_toutes()

	# Selon la méthode HTTP on récupère (ou pas) les coureurs dans la BDD
	if request.method == "POST":
		# Récupération de la course concernée
		id_course = request.form["id_course"]

		# Et des coureurs qui y ont participés
		les_coureurs = bdd.recuperer_coureurs_de_la_course(id_course)
		print(les_coureurs)
	else:
		les_coureurs = ()

	return render_template('admin_coureurs_afficher.html', les_courses=les_courses, les_coureurs=les_coureurs)


@app.route('/resultats/<filename>')
def telecharger_fichier_pdf(filename):
	""" Fonction qui permet de télécharger un fichier PDF
	@param Aucun
	@return Le template
	"""
	return send_from_directory(
		app.config["CHEMIN_VERS_DOWNLOADS_CSV"],
		"resultats_course.pdf",
		mimetype="application/pdf",
		as_attachment=True,
		attachment_filename="resultats_course.pdf"
	)



@app.route('/resultats/<filename>')
def telecharger_fichier_csv(filename):
	""" Fonction qui permet de télécharger un fichier CSV
	@param Aucun
	@return Le template
	"""
	return send_from_directory(
		app.config["CHEMIN_VERS_DOWNLOADS_CSV"],
		"resultats_course.csv",
		mimetype='text/csv',
		as_attachment=True,
		attachment_filename="resultats_course.csv"
	)


@app.route("/administration/coureurs/importer", methods=["POST"])
def administrer_coureurs_importer():
	"""Fonction pour importer des coureurs depuis un fichier CSV
	@param Aucun
	@return template + flash
	"""
	# Vérification de l'authentification et redirection si pas bon
	if "authentifie" not in session:
		flash("Vous devez vous authentifier pour accéder à cette page", "danger")
		return redirect(url_for("administrer_accueil"))

	# Récupération de la course concernée
	if "id_course_active" not in session:
		flash("Vous n'avez pas sélectionné de course active à l'étape précédente", "danger")
		return redirect(url_for("administrer_tutoriel_etape2"))
	else:
		id_course = session["id_course_active"]

	# Vérification si le fichier a bien été envoyé
	if "fichier_csv" not in request.files:
		flash("Aucun fichier envoyé", "danger")
		return redirect(url_for("administrer_tutoriel_etape3"))

	# Récupération du fichier CSV
	fichier_csv = request.files["fichier_csv"]

	# Si l'utilisateur n'a pas sélectionné de fichier => envoi vide
	if fichier_csv.filename == "":
		flash("Aucun fichier sélectionné", "danger")
		return redirect(url_for("administrer_tutoriel_etape3"))

	if fichier_csv:
		# Enregistrement en local du fichier CSV
		nom_fichier_csv = secure_filename(fichier_csv.filename)
		chemin_vers_fichier_csv = os.path.join(app.config['CHEMIN_VERS_UPLOADS_CSV'], nom_fichier_csv)
		fichier_csv.save(chemin_vers_fichier_csv)

		# Enregistrement dans la base de données du contenu CSV
		try:
			resultat = bdd.ajouter_coureurs_depuis_csv(chemin_vers_fichier_csv, id_course)
			flash("Les coureurs ont bien été ajoutés depuis %s" % chemin_vers_fichier_csv, "success")
		except ErreurBdd as erreur:
			flash("Une erreur est survenue (%s)" % erreur.message, "danger")

	else:
		flash("Fichier CSV inexistant", "danger")
		return redirect(url_for("administrer_tutoriel_etape3"))

	# Redirection vers une autre route/URL
	return redirect(url_for("administrer_tutoriel_etape3"))


# ==============================================================================
# Lancement de l'application web
# ==============================================================================

if __name__ == '__main__':
	# use_reloader=False pour éviter de lancer 2 connexions à la bdd
    app.run(host ="0.0.0.0", debug=True, use_reloader=False, port=1664)
