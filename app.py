from flask import Flask, render_template, request, jsonify
import json
import os
import re
import unicodedata

app = Flask(__name__)

MOT_DE_PASSE = "LVD-2026"

with open("faq.json", "r", encoding="utf-8") as f:
    faq = json.load(f)

with open("vehicules.json", "r", encoding="utf-8") as f:
    vehicules = json.load(f)

def normaliser(texte):
    texte = texte.lower()
    texte = unicodedata.normalize("NFD", texte)
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    return texte

def contient_mot_entier(message, mot_cle):
    message = normaliser(message)
    mot_cle = normaliser(mot_cle)
    pattern = r"(^|[^a-zA-Z0-9])" + re.escape(mot_cle) + r"([^a-zA-Z0-9]|$)"
    return re.search(pattern, message) is not None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/verifier-mdp", methods=["POST"])
def verifier_mdp():
    mdp = request.json["password"]
    return jsonify({"success": mdp == MOT_DE_PASSE})

@app.route("/chat", methods=["POST"])
def chat():
    message = request.json["message"]

    for item in faq:
        for mot in item["mots_cles"]:
            if contient_mot_entier(message, mot):
                return jsonify({"reply": item["reponse"]})

    return jsonify({
        "reply": "Je n'ai pas compris votre question. Pouvez-vous reformuler ou contacter le loueur directement ?"
    })

@app.route("/devis", methods=["POST"])
def devis():
    data = request.json

    voiture = data["voiture"].lower()
    jours = int(data["jours"])
    livraison = data["livraison"].lower()

    if voiture not in vehicules:
        return jsonify({"error": "Véhicule introuvable."})

    vehicule = vehicules[voiture]

    prix_location = vehicule["prix_jour"] * jours
    prix_livraison = 20 if livraison == "oui" else 0
    total = prix_location + prix_livraison
    acompte = total / 2
    reste = total - acompte

    devis_texte = f"""
DEVIS PERSONNALISÉ

Véhicule : {vehicule["nom"]}
Durée : {jours} jour(s)

Prix location : {prix_location} €
Livraison : {prix_livraison} €

Total : {total} €

Caution : {vehicule["caution"]} €
Kilométrage inclus : {vehicule["kilometrage"]}

Acompte : {acompte:.0f} €
Reste à payer : {reste:.0f} €
"""

    return jsonify({"devis": devis_texte})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)