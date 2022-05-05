from flask import render_template, flash, Blueprint, url_for, session, current_app, Response, jsonify
from bdd import Bdd, ErreurBdd
from werkzeug.utils import secure_filename
from datetime import timedelta, datetime
import os
import json
import sys
bpMG = Blueprint ( 'bpMG', __name__ )
configuration = {}
bdd = Bdd(configuration)
#num = current_app.config


def formater_temps(temps_en_secondes):
	"""Fonction pour formater un nombre de secondes xxx en mm:ss
	@param nombre de secondes à formater
	@return une chaîne de caractères de la forme mm:ss
	"""
	return "%02d:%02d" % (divmod(temps_en_secondes, 60))



def formater_argent(argent_en_cents):
	"""Fonction pour formater un nombre de cents d'euros en euros
	@param nombre de cents à formater
	@return une chaîne de caractères de la forme xxx.xx
	"""
	return "%.02f" % (float(argent_en_cents) / 100.0)


@bpMG.route('/direct')
def afficher_classement_direct():
	"""Fonction pour gérer la page du classement en direct
	@param Aucun
	@return Le template
	"""
	return render_template('public_classement_direct.html')
@bpMG.route('/direct/toutes')
def recuperer_dernieres_informations():
	"""Fonction pour générer depuis la base de données les statistiques et les derniers passages
	@param Aucun
	@return Les données en JSON
	"""
	# Préparation des variables résultats
	dernieres_stats = None
	meilleur_en_temps = None
	meilleur_en_distance = None
	informations = {}


	# Récupération de l'id de la course active
	if "id_course_active" not in session:
		try:
			course_active = bdd.recuperer_course_active()
			session["id_course_active"] = course_active[0][0]
		except ErreurBdd as erreur:
			informations["erreur"] = "Une erreur est survenue (%s)" % erreur.message
			return jsonify(informations)


	# Récupération des statistiques globales et les meilleurs coureurs de la course
	try:
		dernieres_stats = bdd.recuperer_dernieres_statistiques(session["id_course_active"])
		meilleur_en_temps, meilleur_en_distance = bdd.recuperer_meilleurs_coureurs(session["id_course_active"])
		informations["erreur"] = ""
	except ErreurBdd as erreur:
		flash("Une erreur est survenue (%s)" % erreur.message, "danger")
		informations["erreur"] = "Une erreur est survenue (%s)" % erreur.message
		return jsonify(informations)
	print(dernieres_stats)
	#print(meilleur_en_temps)
	#print(meilleur_en_distance)


	# Récupération de toutes les courses dans la bdd
	derniers_passages = None
	try:
		derniers_passages = bdd.recuperer_derniers_passages(session["id_course_active"], current_app.config["DIRECT_MAX_PASSAGES"])
		#print(derniers_passages)
	except ErreurBdd as erreur:
		flash("Une erreur est survenue (%s)" % erreur.message, "danger")
	print(derniers_passages)


	# Préparation des données statistiques dans un dictionnaire
	if dernieres_stats and len(dernieres_stats[0]) == 3:
		informations["distance_totale"] = dernieres_stats[0][0]
		informations["argent_total"] = formater_argent(dernieres_stats[0][1])
		informations["nb_coureurs"] = dernieres_stats[0][2]
	else:
		informations["distance_totale"] = "????"
		informations["argent_total"] = "????"
		informations["nb_coureurs"] = "????"

	if meilleur_en_temps and len(meilleur_en_temps[0]) == 3:
		informations["coureur_rapide_nom"] = meilleur_en_temps[0][0]
		informations["coureur_rapide_prenom"] = meilleur_en_temps[0][1]
		informations["coureur_rapide_temps"] = formater_temps(meilleur_en_temps[0][2])
	else:
		informations["coureur_rapide_nom"] = "???"
		informations["coureur_rapide_prenom"] = "???"
		informations["coureur_rapide_temps"] = "??:??"

	if meilleur_en_distance and len(meilleur_en_distance[0]) == 3 and meilleur_en_distance[0][2] > 0:
		informations["coureur_endurant_nom"] = meilleur_en_distance[0][0]
		informations["coureur_endurant_prenom"] = meilleur_en_distance[0][1]
		informations["coureur_endurant_tours"] = meilleur_en_distance[0][2]
	else:
		informations["coureur_endurant_nom"] = "???"
		informations["coureur_endurant_prenom"] = "???"
		informations["coureur_endurant_tours"] = "???"
	


	# Préparation des derniers passages dans un tableau ajouté ensuite au dictionnaire
	les_passages = []
	if derniers_passages is not None:
		for un_passage in derniers_passages:
			un_passage_dict = {}
			un_passage_dict["date"] = un_passage[7]
			un_passage_dict["nom"] = un_passage[1]
			un_passage_dict["prenom"] = un_passage[2]
			un_passage_dict["classe"] = un_passage[3]
			un_passage_dict["temps"] = formater_temps(un_passage[4])
			un_passage_dict["distance"] = un_passage[5]
			un_passage_dict["numero_raspberry"] = un_passage[6]
			les_passages.append(un_passage_dict)

	informations["derniers_passages"] = les_passages
	print("=== VERSION DICT PYTHON ===", informations)

	# Transformation du dictionnaire Python en JSON
	def convertisseur(donnee):
		if isinstance(donnee, datetime):
			return donnee.__str__()
		if isinstance(donnee, decimal.Decimal):
			return donnee.__str__()
	informations_en_json = json.dumps(informations, default=convertisseur)
	#print("=== VERSION JSON ===", informations_en_json)


	# On retourne le JSON au jQuery de la page publique direct
	return Response(informations_en_json, mimetype='application/json')




