"""
tools.py
Les 8 tools de Stella — fonctions Python qui simulent
les appels aux bases de données et services Stellantis.
"""

import json
import os
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
import chromadb
from chromadb.utils import embedding_functions


# ──────────────────────────────────────────────
# INITIALISATION RAG GLOBALE
# ──────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(BASE_DIR, "rag", "chroma_db")

EMBEDDING_FUNCTION = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

CHROMA_CLIENT = chromadb.PersistentClient(path=CHROMA_PATH)

RAG_COLLECTION = CHROMA_CLIENT.get_collection(
    name="stellantis_docs",
    embedding_function=EMBEDDING_FUNCTION
)


# ──────────────────────────────────────────────
# CHARGEMENT DES DONNÉES SIMULÉES
# ──────────────────────────────────────────────

def _load_json(filename: str) -> dict | list:
    """Charge un fichier JSON depuis le dossier data/"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filepath = os.path.join(base_dir, "data", filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_user(user_id: str) -> dict | None:
    data = _load_json("users.json")
    for user in data["users"]:
        if user["user_id"] == user_id:
            return user
    return None


def _get_vehicle_by_user(user_id: str) -> dict | None:
    data = _load_json("vehicles.json")
    for vehicle in data["vehicles"]:
        if vehicle["user_id"] == user_id:
            return vehicle
    return None


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    """Calcule la distance en km entre deux points GPS."""
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


# Coordonnées approximatives des villes pour simuler la géolocalisation
VILLES_COORDS = {
    "lyon":     (45.7640, 4.8357),
    "bordeaux": (44.8378, -0.5792),
    "paris":    (48.8566, 2.3522),
    "marseille":(43.2965, 5.3698),
    "toulouse": (43.6047, 1.4442),
}


# ──────────────────────────────────────────────
# TOOL 1 — get_vehicle_status
# ──────────────────────────────────────────────

def get_vehicle_status(user_id: str) -> dict:
    """
    Retourne l'état complet du véhicule lié à l'utilisatrice.
    C'est le premier tool appelé à chaque session.
    """
    vehicle = _get_vehicle_by_user(user_id)
    if not vehicle:
        return {"error": f"Aucun véhicule trouvé pour l'utilisatrice {user_id}"}

    return {
        "marque": vehicle["marque"],
        "modele": vehicle["modele"],
        "annee": vehicle["annee"],
        "motorisation": vehicle["motorisation"],
        "kilometrage_actuel": vehicle["kilometrage_actuel"],
        "prochaine_revision_km": vehicle["prochaine_revision_km"],
        "km_avant_revision": vehicle["km_avant_revision"],
        "voyants_actifs": vehicle.get("voyants_actifs", []),
        "niveau_carburant_pct": vehicle.get("niveau_carburant_pct"),
        "niveau_batterie_pct": vehicle.get("niveau_batterie_pct"),
        "autonomie_restante_km": vehicle.get("autonomie_restante_km"),
        "derniere_visite_reseau": vehicle.get("derniere_visite_reseau"),
        "contrat_entretien": vehicle.get("contrat_entretien", False),
        "garantie_active": vehicle.get("garantie_active", False),
        "garantie_expiration": vehicle.get("garantie_expiration"),
        "anniversaire_vehicule_dans_jours": vehicle.get("anniversaire_vehicule_dans_jours"),
    }


# ──────────────────────────────────────────────
# TOOL 2 — get_maintenance_recommendation
# ──────────────────────────────────────────────

def get_maintenance_recommendation(user_id: str) -> dict:
    """
    Génère une recommandation d'entretien personnalisée
    selon l'état du véhicule et le profil de l'utilisatrice.
    """
    vehicle = _get_vehicle_by_user(user_id)
    user = _get_user(user_id)
    if not vehicle or not user:
        return {"error": "Utilisatrice ou véhicule introuvable"}

    voyants = vehicle.get("voyants_actifs", [])
    km_avant = vehicle.get("km_avant_revision", 9999)
    niveau_connaissance = user.get("niveau_connaissance_auto", "intermediaire")

    # Détermination de l'urgence
    if voyants and any(v.get("urgence") == "immediate" for v in voyants):
        urgence = "immediate"
    elif voyants or km_avant < 2000:
        urgence = "moyenne"
    elif km_avant < 5000:
        urgence = "planifier"
    else:
        urgence = "aucune"

    # Explication adaptée au niveau
    if urgence == "immediate":
        if niveau_connaissance == "debutante":
            explication = "Un voyant important s'est allumé. Pour ta sécurité, je te recommande de ne pas rouler " \
                         "et de contacter directement un garage agréé aujourd'hui."
        else:
            explication = "Voyant d'urgence actif. Intervention requise avant tout trajet."
    elif urgence == "moyenne":
        if voyants:
            v = voyants[0]
            explication = v.get("explication_simple", "Un contrôle est recommandé prochainement.")
        else:
            explication = f"Ta révision approche (dans {km_avant} km). C'est le bon moment pour la planifier " \
                         f"et éviter les mauvaises surprises."
    elif urgence == "planifier":
        explication = f"Tu as encore {km_avant} km avant ta prochaine révision, mais c'est le bon moment " \
                     f"pour prendre rendez-vous et avoir le créneau de ton choix."
    else:
        explication = "Ton véhicule est en bonne santé ! Rien d'urgent à signaler."

    # Recherche de l'offre de remise applicable
    offers_data = _load_json("offers.json")
    offre_applicable = None
    for offer in offers_data["offers"]:
        if offer.get("declencheur") in ["prochaine_revision_proche", "voyant_pression_pneu_actif"] \
        and (user.get("persona_type") in offer.get("personas_cibles", []) or "all" in offer.get("personas_cibles", [])):
            offre_applicable = offer
            break

    # Recherche du garage le plus proche
    partenaires = _load_json("partners.json")
    garage = None
    for p in partenaires["partners"]:
        if p["type"] == "garage_agree" and vehicle["marque"] in p.get("marques_acceptees", []):
            garage = p
            break

    return {
        "urgence": urgence,
        "explication": explication,
        "action_recommandee": voyants[0].get("action_recommandee", "Prendre rendez-vous en atelier") if voyants else "Planifier une révision",
        "fourchette_prix": garage.get("tarif_revision_estime", "sur devis") if garage else "sur devis",
        "garage_recommande": {
            "nom": garage["nom"],
            "adresse": garage["adresse"],
            "note": garage["note_client"],
            "prochain_rdv": garage["disponibilite_rdv"],
            "lien_rdv": garage["lien_rdv"]
        } if garage else None,
        "offre_disponible": offre_applicable is not None,
        "offre": {
            "titre": offre_applicable["titre"],
            "valeur": offre_applicable["valeur"],
            "conditions": offre_applicable["conditions"],
            "expiration": offre_applicable["expiration"],
            "points_gagnes": offre_applicable["points_gagnes"]
        } if offre_applicable else None
    }


# ──────────────────────────────────────────────
# TOOL 3 — get_charging_recommendation
# ──────────────────────────────────────────────

def get_charging_recommendation(user_id: str, location: str, destination: str = None) -> dict:
    """
    Recommande des bornes de recharge selon la position et le niveau de batterie.
    Uniquement pour véhicules électriques et hybrides rechargeables.
    """
    vehicle = _get_vehicle_by_user(user_id)
    if not vehicle:
        return {"error": "Véhicule introuvable"}

    if vehicle["motorisation"] == "thermique":
        return {"error": "Ce tool ne s'applique qu'aux véhicules électriques ou hybrides rechargeables."}

    niveau_batterie = vehicle.get("niveau_batterie_pct", 50)
    autonomie = vehicle.get("autonomie_restante_km", 100)

    # Urgence selon niveau batterie
    if niveau_batterie < 20:
        urgence_recharge = "critique"
        message_urgence = f"⚡ Batterie à {niveau_batterie}% ! Il est temps de recharger rapidement."
    elif niveau_batterie < 40:
        urgence_recharge = "recommandee"
        message_urgence = f"Batterie à {niveau_batterie}% ({autonomie} km restants). Je te recommande de recharger prochainement."
    else:
        urgence_recharge = "optionnelle"
        message_urgence = f"Batterie à {niveau_batterie}% ({autonomie} km restants). Pas d'urgence."

    # Localisation de l'utilisatrice
    loc_lower = location.lower()
    coords_user = VILLES_COORDS.get(loc_lower, VILLES_COORDS.get("paris"))

    # Recherche des bornes proches
    partenaires = _load_json("partners.json")
    bornes = []
    for p in partenaires["partners"]:
        if p["type"] == "borne_recharge" and p.get("disponible", False):
            dist = _haversine_km(
                coords_user[0], coords_user[1],
                p["latitude"], p["longitude"]
            )
            bornes.append({
                "partner_id": p["partner_id"],
                "nom": p["nom"],
                "adresse": p["adresse"],
                "distance_km": round(dist, 1),
                "puissance_kw": p["puissance_kw"],
                "temps_charge_estime_min": p["temps_charge_estime_min"],
                "tarif_kwh": p["tarif_kwh"],
                "compatible_free2move": p.get("compatible_free2move", False),
                "disponible": p["disponible"]
            })

    # Tri par distance
    bornes.sort(key=lambda x: x["distance_km"])
    bornes_proches = bornes[:3]

    # Recommandation principale
    recommandation = None
    if bornes_proches:
        b = bornes_proches[0]
        recommandation = f"La borne la plus proche est '{b['nom']}' à {b['distance_km']} km. " \
                        f"Charge estimée : {b['temps_charge_estime_min']} min pour 80%."

    return {
        "niveau_batterie_pct": niveau_batterie,
        "autonomie_restante_km": autonomie,
        "urgence_recharge": urgence_recharge,
        "message_urgence": message_urgence,
        "bornes_proches": bornes_proches,
        "recommandation": recommandation,
        "compatible_free2move_charge": any(b["compatible_free2move"] for b in bornes_proches)
    }


# ──────────────────────────────────────────────
# TOOL 4 — get_offers
# ──────────────────────────────────────────────

def get_offers(user_id: str, category: str = "all") -> list:
    """
    Retourne les offres personnalisées filtrées par pertinence
    selon le profil utilisatrice, son véhicule et le contexte.
    """
    user = _get_user(user_id)
    vehicle = _get_vehicle_by_user(user_id)
    if not user or not vehicle:
        return []

    offers_data = _load_json("offers.json")
    persona = user.get("persona_type", "")
    motorisation = vehicle.get("motorisation", "")
    marque = vehicle.get("marque", "")
    km_avant = vehicle.get("km_avant_revision", 9999)
    voyants = vehicle.get("voyants_actifs", [])
    anniversaire = vehicle.get("anniversaire_vehicule_dans_jours")

    offres_pertinentes = []

    for offer in offers_data["offers"]:
        # Filtre catégorie
        if category != "all" and offer["categorie"] != category:
            continue

        # Filtre persona
        if persona not in offer.get("personas_cibles", []) and "all" not in offer.get("personas_cibles", []):
            continue

        # Filtre motorisation
        if motorisation not in offer.get("motorisation_cible", []) and "all" not in offer.get("motorisation_cible", []):
            continue

        # Filtre marque
        if marque not in offer.get("marques_cibles", []) and "all" not in offer.get("marques_cibles", []):
            continue

        # Calcul score pertinence selon déclencheur
        score = 0.5
        declencheur = offer.get("declencheur", "")

        if declencheur == "prochaine_revision_proche" and km_avant < 2000:
            score = 0.95
        elif declencheur == "voyant_pression_pneu_actif" and any(v["code"] == "pression_pneu" for v in voyants):
            score = 1.0
        elif declencheur == "batterie_faible" and vehicle.get("niveau_batterie_pct", 100) < 30:
            score = 0.95
        elif declencheur == "anniversaire_vehicule" and anniversaire is not None and anniversaire <= 3:
            score = 1.0
        elif declencheur == "changement_saison":
            score = 0.7
        elif declencheur == "deplacement_detecte":
            score = 0.65
        elif declencheur == "fin_de_mois":
            score = 0.6

        offres_pertinentes.append({
            "offer_id": offer["offer_id"],
            "titre": offer["titre"],
            "description": offer["description"],
            "categorie": offer["categorie"],
            "valeur": offer["valeur"],
            "conditions": offer["conditions"],
            "expiration": offer["expiration"],
            "points_gagnes": offer["points_gagnes"],
            "score_pertinence": score
        })

    # Tri par score décroissant
    offres_pertinentes.sort(key=lambda x: x["score_pertinence"], reverse=True)
    return offres_pertinentes[:5]  # Maximum 5 offres


# ──────────────────────────────────────────────
# TOOL 5 — get_loyalty_dashboard
# ──────────────────────────────────────────────

def get_loyalty_dashboard(user_id: str) -> dict:
    """
    Retourne le tableau de bord fidélité complet de l'utilisatrice.
    """
    user = _get_user(user_id)
    if not user:
        return {"error": "Utilisatrice introuvable"}

    points = user.get("points_fidelite", 0)
    niveau = user.get("niveau_fidelite", "Bronze")

    # Définition des niveaux et seuils
    niveaux = {
        "Bronze": {"seuil": 0,    "prochain": "Argent", "seuil_prochain": 300},
        "Argent": {"seuil": 300,  "prochain": "Or",     "seuil_prochain": 700},
        "Or":     {"seuil": 700,  "prochain": "Platine","seuil_prochain": 1500},
        "Platine":{"seuil": 1500, "prochain": None,     "seuil_prochain": None},
    }

    niveau_info = niveaux.get(niveau, niveaux["Bronze"])
    points_manquants = None
    if niveau_info["seuil_prochain"]:
        points_manquants = niveau_info["seuil_prochain"] - points

    # Avantages disponibles selon les points
    avantages = [
        {
            "titre": "Lavage offert",
            "points_requis": 200,
            "deja_debloque": points >= 200,
            "description": "Lavage intérieur/extérieur dans tout réseau agréé"
        },
        {
            "titre": "Contrôle technique -15€",
            "points_requis": 350,
            "deja_debloque": points >= 350,
            "description": "Valable dans les centres Dekra et Autovision partenaires"
        },
        {
            "titre": "Révision -30%",
            "points_requis": 700,
            "deja_debloque": points >= 700,
            "description": "Sur la prochaine révision complète en réseau agréé"
        },
        {
            "titre": "Weekend offert Free2move",
            "points_requis": 1200,
            "deja_debloque": points >= 1200,
            "description": "2 nuits dans un hôtel partenaire Free2move"
        }
    ]

    # Historique depuis les sessions
    historique = []
    for session in user.get("historique_sessions", []):
        for action in session.get("actions_declenchees", []):
            historique.append({
                "date": session["date"],
                "action": action,
                "points": "+50"
            })

    return {
        "prenom": user.get("prenom"),
        "points_actuels": points,
        "niveau": niveau,
        "prochain_niveau": niveau_info["prochain"],
        "points_pour_niveau_suivant": points_manquants,
        "avantages": avantages,
        "avantages_disponibles": [a for a in avantages if a["deja_debloque"]],
        "historique_recent": historique[-3:] if historique else [],
        "prochain_gain": f"Passe ta prochaine révision et gagne 150 points !"
    }


# ──────────────────────────────────────────────
# TOOL 6 — get_partners
# ──────────────────────────────────────────────

def get_partners(location: str, type_partenaire: str, marque_vehicule: str = None) -> list:
    """
    Trouve les partenaires pertinents selon la localisation et le besoin.
    """
    loc_lower = location.lower()
    coords_user = VILLES_COORDS.get(loc_lower, VILLES_COORDS.get("paris"))

    partenaires_data = _load_json("partners.json")
    resultats = []

    for p in partenaires_data["partners"]:
        # Filtre type
        if p["type"] != type_partenaire:
            continue

        # Filtre marque pour les garages
        if type_partenaire == "garage_agree" and marque_vehicule:
            if marque_vehicule not in p.get("marques_acceptees", []):
                continue

        # Calcul distance
        dist = _haversine_km(
            coords_user[0], coords_user[1],
            p["latitude"], p["longitude"]
        )

        resultats.append({
            "partner_id": p["partner_id"],
            "nom": p["nom"],
            "adresse": p["adresse"],
            "ville": p["ville"],
            "distance_km": round(dist, 1),
            "note_client": p.get("note_client"),
            "telephone": p.get("telephone"),
            "disponibilite_rdv": p.get("disponibilite_rdv"),
            "horaires": p.get("horaires"),
            "services": p.get("services", []),
            "lien_rdv": p.get("lien_rdv"),
            "borne_recharge_parking": p.get("borne_recharge_parking"),
            "prix_nuit_base": p.get("prix_nuit_base"),
            "remise_free2move_pct": p.get("remise_free2move_pct"),
        })

    # Tri par distance
    resultats.sort(key=lambda x: x["distance_km"])
    return resultats[:3]


# ──────────────────────────────────────────────
# TOOL 7 — search_stellantis_docs
# ──────────────────────────────────────────────

def search_stellantis_docs(query: str, marque: str = None, categorie_doc: str = None) -> list:
    """
    Recherche sémantique dans la base RAG ChromaDB.
    """
    try:

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        chroma_path = os.path.join(base_dir, "rag", "chroma_db")

        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )

        collection = RAG_COLLECTION

        where = {}
        if marque:
            where["marque"] = marque
        if categorie_doc and categorie_doc != "all":
            where["categorie"] = categorie_doc

        results = collection.query(
            query_texts=[query],
            n_results=5,
            where=where if where else None
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        return [
            {
                "contenu": doc,
                "source": meta.get("source", "Document Stellantis"),
                "titre": meta.get("titre", "Document Stellantis"),
                "url": meta.get("url", ""),
                "marque": meta.get("marque", "Stellantis"),
                "categorie": meta.get("categorie", "general"),
                "score_similarite": round(1 - dist, 3)
            }
            for doc, meta, dist in zip(documents, metadatas, distances)
        ]

    except Exception as e:
        return [
            {
                "contenu": f"Erreur RAG : {str(e)}",
                "source": "Erreur ChromaDB",
                "marque": marque or "Stellantis",
                "categorie": categorie_doc or "general",
                "score_similarite": 0
            }
        ]

# ──────────────────────────────────────────────
# TOOL 8 — escalate_to_human
# ──────────────────────────────────────────────

def escalate_to_human(user_id: str, reason: str, conversation_summary: str) -> dict:
    """
    Déclenche l'escalade vers un conseiller humain.
    En production : intégration CRM Stellantis.
    En simulation : retourne une confirmation fictive.
    """
    user = _get_user(user_id)
    prenom = user.get("prenom", "la cliente") if user else "la cliente"

    # Mapping des raisons vers des messages appropriés
    messages = {
        "insatisfaction": f"Je transmets notre échange à un conseiller Stellantis. "
                         f"Il reviendra vers toi très rapidement avec une solution.",
        "urgence_securite": f"Pour ta sécurité, je te mets immédiatement en contact "
                           f"avec notre équipe d'assistance. Reste en ligne.",
        "hors_capacite": f"Cette question dépasse mes capacités actuelles. "
                        f"Je te connecte avec un expert Stellantis qui pourra t'aider.",
        "demande_explicite": f"Bien sûr ! Je te mets en contact avec un conseiller. "
                            f"Il aura tout le contexte de notre échange."
    }

    message = messages.get(reason, messages["hors_capacite"])

    # Log de l'escalade (en production : appel CRM)
    escalade_log = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "prenom": prenom,
        "raison": reason,
        "resume_conversation": conversation_summary
    }
    print(f"[ESCALADE] {escalade_log}")  # En production : envoi au CRM

    return {
        "escalade_confirmee": True,
        "canal": "chat_live",
        "temps_attente_estime_min": 3,
        "conseiller_disponible": True,
        "message_transition": message,
        "reference_dossier": f"STL-{user_id}-{datetime.now().strftime('%Y%m%d%H%M')}"
    }


# ──────────────────────────────────────────────
# REGISTRE DES TOOLS (pour l'API Claude)
# ──────────────────────────────────────────────

TOOLS_DEFINITION = [
    {
        "name": "get_vehicle_status",
        "description": "Récupère l'état complet du véhicule de l'utilisatrice : kilométrage, voyants actifs, niveau d'énergie, prochaine révision.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Identifiant unique de l'utilisatrice"}
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "get_maintenance_recommendation",
        "description": "Génère une recommandation d'entretien personnalisée selon l'état du véhicule et le profil de l'utilisatrice.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Identifiant unique de l'utilisatrice"}
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "get_charging_recommendation",
        "description": "Recommande des bornes de recharge proches selon la position et le niveau de batterie. Uniquement pour véhicules électriques ou hybrides.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Identifiant unique de l'utilisatrice"},
                "location": {"type": "string", "description": "Ville ou position actuelle de l'utilisatrice"},
                "destination": {"type": "string", "description": "Destination du trajet (optionnel)"}
            },
            "required": ["user_id", "location"]
        }
    },
    {
        "name": "get_offers",
        "description": "Retourne les offres et remises personnalisées selon le profil, le véhicule et le contexte de l'utilisatrice.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Identifiant unique de l'utilisatrice"},
                "category": {
                    "type": "string",
                    "description": "Catégorie d'offres souhaitée",
                    "enum": ["entretien", "accessoires", "voyage", "recharge", "fidelite", "service", "all"]
                }
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "get_loyalty_dashboard",
        "description": "Retourne le tableau de bord fidélité : points, niveau, avantages disponibles et historique.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Identifiant unique de l'utilisatrice"}
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "get_partners",
        "description": "Trouve les partenaires Stellantis proches : garages agréés, bornes de recharge, hôtels partenaires.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Ville ou position de l'utilisatrice"},
                "type_partenaire": {
                    "type": "string",
                    "description": "Type de partenaire recherché",
                    "enum": ["garage_agree", "borne_recharge", "hotel", "centre_ct"]
                },
                "marque_vehicule": {"type": "string", "description": "Marque du véhicule pour filtrer les garages (optionnel)"}
            },
            "required": ["location", "type_partenaire"]
        }
    },
    {
        "name": "search_stellantis_docs",
        "description": "Recherche dans la documentation officielle Stellantis : stratégie software, STLA Brain, SmartCockpit, Mobilisights, Free2move Charge, CloudMade, API véhicule connecté, électrification.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Question en langage naturel"},
                "marque": {"type": "string", "description": "Filtrer par marque Stellantis (optionnel)"},
                "categorie_doc": {
                    "type": "string",
                    "description": "Type de document (optionnel)",
                    "enum": ["software", "software_strategy", "ai_personalisation", "data_vehicle", "recharge", "api", "general", "official_pdf", "all"]
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "escalate_to_human",
        "description": "Transfère la conversation vers un conseiller humain Stellantis en cas d'insatisfaction, urgence ou demande explicite.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Identifiant unique de l'utilisatrice"},
                "reason": {
                    "type": "string",
                    "description": "Motif de l'escalade",
                    "enum": ["insatisfaction", "urgence_securite", "hors_capacite", "demande_explicite"]
                },
                "conversation_summary": {"type": "string", "description": "Résumé de la conversation pour le conseiller"}
            },
            "required": ["user_id", "reason", "conversation_summary"]
        }
    }
]


# ──────────────────────────────────────────────
# DISPATCHER — exécute un tool par son nom
# ──────────────────────────────────────────────

def execute_tool(tool_name: str, tool_input: dict) -> dict | list:
    """
    Exécute un tool par son nom avec les paramètres fournis.
    Appelé par la boucle agent dans stella.py.
    """
    tools_map = {
        "get_vehicle_status": get_vehicle_status,
        "get_maintenance_recommendation": get_maintenance_recommendation,
        "get_charging_recommendation": get_charging_recommendation,
        "get_offers": get_offers,
        "get_loyalty_dashboard": get_loyalty_dashboard,
        "get_partners": get_partners,
        "search_stellantis_docs": search_stellantis_docs,
        "escalate_to_human": escalate_to_human,
    }

    if tool_name not in tools_map:
        return {"error": f"Tool inconnu : {tool_name}"}

    try:
        return tools_map[tool_name](**tool_input)
    except Exception as e:
        return {"error": f"Erreur lors de l'exécution de {tool_name} : {str(e)}"}