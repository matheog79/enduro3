#!/usr/bin/python3
"""
Serveur MQTT chargé de recevoir des passages et renvoyer les données associées
@author Sallé David
@date 18/10/2018
@version 0.2
"""

# ==============================================================================
# Les librairies utilisées
# ==============================================================================
from datetime import timedelta
from time import strftime, localtime
import paho.mqtt.client as mqtt
import traceback
from bdd import Bdd, ErreurBdd
from config import Config


# ==============================================================================
# Initialisations de la configuration et de la base de données
# ==============================================================================

try:
	# Bannière d'accueil
	print("################################")
	print("### Serveur MQTT Enduro v0.2 ###")
	print("################################\n")

	# Création et initialisation de la classe Config
	print(" => Initialisation de la configuration...")
	cfg = Config()
	delai_de_garde = cfg.DELAI_DE_GARDE

	# Création et initialisation de la classe Bdd
	print(" => Initialisation de la base de données...")
	configuration = {}
	configuration["host"] = cfg.BDD_HOST
	configuration["user"] = cfg.BDD_USER_MQTT
	configuration["password"] = cfg.BDD_PASSWORD_MQTT
	configuration["database"] = cfg.BDD_NAME
	bdd = Bdd(configuration)
	bdd.se_connecter()

	# Récupération de l'id de la course active
	print(" => Récupération de la course active...")
	course_active = bdd.recuperer_course_active()
	id_course = course_active[0][0]
	print("  + id_course =", id_course)

	# Ouverture du fichier CSV de secours
	print(" => Ouverture du fichier CSV de secours...")
	nom_fichier_csv_secours = cfg.FICHIER_CSV_SECOURS
	print("  + fichier_csv_secours =", nom_fichier_csv_secours)
	fichier_csv_secours = open(nom_fichier_csv_secours, "a")


except ErreurBdd as erreur:
    print(" => EXCEPTION [ErreurBdd] dans l'initialisation de la configuration et de la bdd !!!")
    print("  + details :", erreur)

except Exception as erreur:
    print(" => EXCEPTION [Exception] dans l'initialisation de la configuration et de la bdd !!!")
    print("  + details :", erreur)



# ==============================================================================
# Définitions des fonctions de callback MQTT
# ==============================================================================

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	"""Fonction de callback appelée automatiquement lors de la connexion MQTT
	(à la réception de CONNACK du serveur).
	Elle permet d'indiquer le résultat de la connexion
	"""
	try:
		print("  + Connexion au broker avec code =" + str(rc))
		if rc == 0:
			print("  + Connection successful")
		elif rc == 1:
			print("  + Connection refused – incorrect protocol version")
		elif rc == 2:
			print("  + Connection refused – invalid client identifier")
		elif rc == 3:
			print("  + Connection refused – server unavailable")
		elif rc == 4:
			print("  + Connection refused – bad username or password")
		elif rc == 5:
			print("  + Connection refused – not authorised")
		else:
			print("  + Currently unused")

		# Subscribing in on_connect() means that if we lose the connection and
		# reconnect then subscriptions will be renewed.
		client.subscribe("passages")
		client.subscribe("affichage")


	except Exception as erreur:
		print(" => EXCEPTION [Exception] dans on_connect() !!!")
		print("  + details :", erreur)



# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	"""Fonction de callback appelée automatiquement lorsque un message est reçu
	@param client
	@param userdata
	@param msg

	Significations pour la variable code_etat retournée aux postes clients IHM.
	Si = 0, alors le passage a bien été enregistré pour un coureur existant dans la bdd, sinon chaque bit représente :
	    xxxx xxxB => le coureur badgeait pour la première fois si B=1
	    xxxx xxBx => le coureur n'existait pas dans la bdd si B=1
	    xxxx xBxx => le délai de garde n'a pas été respecté si B=1
	    xxxx Bxxx => une exception ErreurBdd a été levée si B=1
	    xxxB xxxx => une exception Exception a été levée si B=1
	"""
	try:
		if msg.topic == "passages":
			# Décortiquage du message MQTT
			print("\n=============================================================")
			print(" => Nouveau message...")
			print("  + topic =", msg.topic)
			print("  + data =", msg.payload.decode("utf8"))
			message = msg.payload.decode("utf8").split(";")
			print("  + trame découpée =", message)
			numero_raspberry = message[0]
			print("  + raspberry =", numero_raspberry)
			code_barre = message[1]
			print("  + codebarre =", code_barre)
			print("  + heure =", message[2])

			# On ajoute le passage dans le fichier CSV de secours
			heure = strftime("%H:%M:%S", localtime() )
			ligne = "%s;%s;%s\n" % (heure, code_barre, numero_raspberry)
			fichier_csv_secours.write(ligne)

			# On ajoute le passage dans la bdd
			try:
				donnees_passage, code_etat = bdd.ajouter_un_passage(id_course, code_barre, numero_raspberry, delai_de_garde)
				print("  + donnees_passage =", donnees_passage)
				print("  + code_etat =", code_etat)

			except ErreurBdd as erreur:
				print("EXCEPTION dans Bdd::ajouter_un_passage() =>", erreur.message)

			# Correction des valeurs selon le code_etat
			if code_etat == 0:

				# Préparation trame à renvoyer
				trame = "%s;%d;%s;%s;%s;%d;%d;%d;%d;%.02f" % (
					numero_raspberry,	# numéro du Raspberry PI
					code_etat,			# code_etat (0=ok, 1=nouveau coureur, 2=delai de garde non respecté, 4=erreur bdd)
					donnees_passage[0],	# nom
					donnees_passage[1],	# prenom
					donnees_passage[2],	# classe
					donnees_passage[3], # nb_tours_effectues
					donnees_passage[4], # meilleur_temps
					donnees_passage[5], # temps_moyen
					donnees_passage[6], # temps_dernier_tour
					donnees_passage[7],	# argent_recolte
				)
			elif code_etat == 4:
				# Préparation trame à renvoyer
				trame = "%s;%d;%s;%s;%s;%d;%d;%d;%d;%.02f" % (
					numero_raspberry,	# numéro du Raspberry PI
					code_etat,			# code_etat (0=ok, 1=nouveau coureur, 2=delai de garde non respecté, 4=erreur bdd)
					donnees_passage[0],	# nom
					donnees_passage[1],	# prenom
					donnees_passage[2],	# classe
					donnees_passage[3], # nb_tours_effectues
					0, 					# meilleur_temps
					0, 					# temps_moyen
					donnees_passage[6],					# temps_dernier_tour
					donnees_passage[7],	# argent_recolte
				)
			else:
				# Préparation trame à renvoyer
				trame = "%s;%d;%s;%s;%s;%d;%d;%d;%d;%.02f" % (
					numero_raspberry,	# numéro du Raspberry PI
					code_etat,			# code_etat (0=ok, 1=nouveau coureur, 2=delai de garde non respecté, 4=erreur bdd)
					donnees_passage[0],	# nom
					donnees_passage[1],	# prenom
					donnees_passage[2],	# classe
					0,					# nb_tours_effectues
					0, 					# meilleur_temps
					0, 					# temps_moyen
					0,					# temps_dernier_tour
					donnees_passage[7],	# argent_recolte
				)

			# Envoi de la trame MQTT
			print(" => Envoi de la trame MQTT pour l'IHM")
			print("  + detail trame =", trame)
			resultat = client.publish("affichage", trame)
			print("  + resultat =", resultat)


	except Exception as erreur:
		print(" => EXCEPTION [Exception] dans on_message() !!!")
		print("  + details :", erreur)
		traceback.print_tb(err.__traceback__)



def on_publish(client, userdata, result):
	"""Fonction de callback appelée automatiquement lorsque qu'un message a
	été publié et qui indique comment s'est déroulée la publication
	"""
	try:
		# Affichage des détails de la publication d'un message MQTT
		print(" => on_publish")
		print("  + client", client)
		print("  + userdata", userdata)
		print("  + result", result)

	except Exception as erreur:
		print(" => EXCEPTION [Exception] dans on_publish() !!!")
		print("  + details :", erreur)



# ==============================================================================
# Lancement du serveur MQTT
# ==============================================================================

try:
	print(" => Initialisation du client MQTT et enregistrement des fonctions...")
	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message
	client.on_publish = on_publish

	print(" => Connexion au broker MQTT...")
	client.connect("127.0.0.1", 1883, 60)

	# Blocking call that processes network traffic, dispatches callbacks and
	# handles reconnecting.
	# Other loop*() functions are available that give a threaded interface and a
	# manual interface.
	print(" => En attente de messages MQTT...")
	client.loop_forever()

except Exception as erreur:
    print(" => EXCEPTION [Exception] dans l'initialisation de MQTT !!!")
    print("  + details :", erreur)


# Fermeture du fichier CSV
fichier_csv_secours.close()
