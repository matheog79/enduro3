from flask import render_template, flash, Blueprint, url_for
bpMG = Blueprint ( 'bpMG', __name__ )

@bpMG.route('/direct')
def afficher_classement_direct():
	"""Fonction pour gérer la page du classement en direct
	@param Aucun
	@return Le template
	"""
	return render_template('public_classement_direct.html')

