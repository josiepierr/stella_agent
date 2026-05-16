"""
tools.py
Les 8 tools de Stella — fonctions Python qui simulent
les appels aux bases de données et services Stellantis.

Version robuste Streamlit / hackathon :
- RAG chargé paresseusement et mis en cache
- pas de crash si ChromaDB n'est pas encore indexée
- validation des entrées tools
- résultats RAG limités pour réduire latence/coût
- erreurs homogènes et non bloquantes
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from functools import lru_cache
from math import atan2, cos, radians, sin, sqrt
from typing import Any

# ──────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stella_tools")


# ──────────────────────────────────────────────
# CHEMINS PROJET
# ──────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHROMA_PATH = os.path.join(BASE_DIR, "rag", "chroma_db")
COLLECTION_NAME = "stellantis_docs"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


# ──────────────────────────────────────────────
# CHARGEMENT DES DONNÉES SIMULÉES
# ──────────────────────────────────────────────

@lru_cache(maxsize=16)
def _load_json(filename: str) -> dict | list:
    """Charge un fichier JSON depuis le dossier data/ avec cache."""
    filepath = os.path.join(DATA_DIR, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Fichier introuvable : {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _validate_user(user_id: str) -> None:
    """Valide rapidement l'identifiant utilisateur attendu par les tools."""
    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("user_id invalide ou vide")
    if not user_id.startswith("U"):
        raise ValueError(f"Format user_id invalide : {user_id}")


def _get_user(user_id: str) -> dict | None:
    data = _load_json("users.json")
    return next((u for u in data.get("users", []) if u.get("user_id") == user_id), None)


def _get_vehicle_by_user(user_id: str) -> dict | None:
    data = _load_json("vehicles.json")
    return next((v for v in data.get("vehicles", []) if v.get("user_id") == user_id), None)


def _safe_get(mapping: dict, key: str, default: Any = None) -> Any:
    return mapping.get(key, default) if isinstance(mapping, dict) else default


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcule la distance en km entre deux points GPS."""
    radius_earth_km = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return radius_earth_km * 2 * atan2(sqrt(a), sqrt(1 - a))


# Coordonnées approximatives des villes pour simuler la géolocalisation.
VILLES_COORDS = {
    "lyon": (45.7640, 4.8357),
    "bordeaux": (44.8378, -0.5792),
    "paris": (48.8566, 2.3522),
    "marseille": (43.2965, 5.3698),
    "toulouse": (43.6047, 1.4442),
}


def _coords_for_location(location: str | None) -> tuple[float, float]:
    if not location:
        return VILLES_COORDS["paris"]
    return VILLES_COORDS.get(location.strip().lower(), VILLES_COORDS["paris"])


# ──────────────────────────────────────────────
# INITIALISATION RAG PARESSEUSE
# ──────────────────────────────────────────────

@lru_cache(maxsize=1)
def _get_rag_collection():
    """
    Initialise ChromaDB seulement au moment du premier appel RAG.
    Cela évite de faire planter Streamlit si la base n'est pas encore construite.
    """
    try:
        import chromadb
        from chromadb.utils import embedding_functions

        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        return client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_function,
        )
    except Exception as e:
        logger.warning("RAG indisponible : %s", e)
        return None


# ──────────────────────────────────────────────
# TOOL 1 — get_vehicle_status
# ──────────────────────────────────────────────

def get_vehicle_status(user_id: str) -> dict:
    """Retourne l'état complet du véhicule lié à l'utilisatrice."""
    _validate_user(user_id)

    vehicle = _get_vehicle_by_user(user_id)
    if not vehicle:
        return {"error": f"Aucun véhicule trouvé pour l'utilisatrice {user_id}"}

    return {
        "marque": vehicle.get("marque"),
        "modele": vehicle.get("modele"),
        "annee": vehicle.get("annee"),
        "motorisation": vehicle.get("motorisation"),
        "kilometrage_actuel": vehicle.get("kilometrage_actuel"),
        "prochaine_revision_km": vehicle.get("prochaine_revision_km"),
        "km_avant_revision": vehicle.get("km_avant_revision"),
        "voyants_actifs": vehicle.get("voyants_actifs", []),
        "niveau_carburant_pct": vehicle.get("niveau_carburant_pct"),
        "niveau_batterie_pct": vehicle.get("niveau_batterie_pct"),
        "niveau_batterie_hybride_pct": vehicle.get("niveau_batterie_hybride_pct"),
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
    """Génère une recommandation d'entretien personnalisée."""
    _validate_user(user_id)

    vehicle = _get_vehicle_by_user(user_id)
    user = _get_user(user_id)
    if not vehicle or not user:
        return {"error": "Utilisatrice ou véhicule introuvable"}

    voyants = vehicle.get("voyants_actifs", []) or []
    km_avant = vehicle.get("km_avant_revision", 9999) or 9999
    niveau_connaissance = user.get("niveau_connaissance_auto", "intermediaire")

    if voyants and any(v.get("urgence") == "immediate" for v in voyants):
        urgence = "immediate"
    elif voyants or km_avant < 2000:
        urgence = "moyenne"
    elif km_avant < 5000:
        urgence = "planifier"
    else:
        urgence = "aucune"

    if urgence == "immediate":
        explication = (
            "Un voyant important s'est allumé. Pour ta sécurité, je te recommande "
            "de ne pas rouler et de contacter directement un garage agréé aujourd'hui."
            if niveau_connaissance == "debutante"
            else "Voyant d'urgence actif. Intervention requise avant tout trajet."
        )
    elif urgence == "moyenne":
        if voyants:
            explication = voyants[0].get("explication_simple", "Un contrôle est recommandé prochainement.")
        else:
            explication = (
                f"Ta révision approche dans {km_avant} km. C'est le bon moment pour la planifier "
                "et éviter les mauvaises surprises."
            )
    elif urgence == "planifier":
        explication = (
            f"Tu as encore {km_avant} km avant ta prochaine révision. "
            "Tu peux déjà prendre rendez-vous pour avoir le créneau de ton choix."
        )
    else:
        explication = "Ton véhicule est en bonne santé : rien d'urgent à signaler."

    offers_data = _load_json("offers.json")
    offre_applicable = None
    for offer in offers_data.get("offers", []):
        trigger_ok = offer.get("declencheur") in [
            "prochaine_revision_proche",
            "voyant_pression_pneu_actif",
        ]
        persona_ok = user.get("persona_type") in offer.get("personas_cibles", []) or "all" in offer.get("personas_cibles", [])
        if trigger_ok and persona_ok:
            offre_applicable = offer
            break

    partenaires = _load_json("partners.json")
    garage = None
    for p in partenaires.get("partners", []):
        if p.get("type") == "garage_agree" and vehicle.get("marque") in p.get("marques_acceptees", []):
            garage = p
            break

    first_voyant = voyants[0] if voyants else {}

    return {
        "urgence": urgence,
        "explication": explication,
        "action_recommandee": first_voyant.get("action_recommandee", "Planifier une révision"),
        "fourchette_prix": garage.get("tarif_revision_estime", "sur devis") if garage else "sur devis",
        "garage_recommande": {
            "nom": garage.get("nom"),
            "adresse": garage.get("adresse"),
            "note": garage.get("note_client"),
            "prochain_rdv": garage.get("disponibilite_rdv"),
            "lien_rdv": garage.get("lien_rdv"),
        } if garage else None,
        "offre_disponible": offre_applicable is not None,
        "offre": {
            "titre": offre_applicable.get("titre"),
            "valeur": offre_applicable.get("valeur"),
            "conditions": offre_applicable.get("conditions"),
            "expiration": offre_applicable.get("expiration"),
            "points_gagnes": offre_applicable.get("points_gagnes"),
        } if offre_applicable else None,
    }


# ──────────────────────────────────────────────
# TOOL 3 — get_charging_recommendation
# ──────────────────────────────────────────────

def get_charging_recommendation(user_id: str, location: str, destination: str = None) -> dict:
    """Recommande des bornes de recharge selon la position et la batterie."""
    _validate_user(user_id)

    vehicle = _get_vehicle_by_user(user_id)
    if not vehicle:
        return {"error": "Véhicule introuvable"}

    if vehicle.get("motorisation") == "thermique":
        return {"error": "Ce service concerne uniquement les véhicules électriques ou hybrides rechargeables."}

    niveau_batterie = vehicle.get("niveau_batterie_pct", 50) or 50
    autonomie = vehicle.get("autonomie_restante_km", 100) or 100

    if niveau_batterie < 20:
        urgence_recharge = "critique"
        message_urgence = f"Batterie à {niveau_batterie} %. Recharge rapide recommandée."
    elif niveau_batterie < 40:
        urgence_recharge = "recommandee"
        message_urgence = f"Batterie à {niveau_batterie} % ({autonomie} km restants). Recharge prochainement recommandée."
    else:
        urgence_recharge = "optionnelle"
        message_urgence = f"Batterie à {niveau_batterie} % ({autonomie} km restants). Pas d'urgence."

    coords_user = _coords_for_location(location)

    partenaires = _load_json("partners.json")
    bornes = []
    for p in partenaires.get("partners", [])[:100]:
        if p.get("type") == "borne_recharge" and p.get("disponible", False):
            dist = _haversine_km(coords_user[0], coords_user[1], p.get("latitude"), p.get("longitude"))
            bornes.append({
                "partner_id": p.get("partner_id"),
                "nom": p.get("nom"),
                "adresse": p.get("adresse"),
                "ville": p.get("ville"),
                "distance_km": round(dist, 1),
                "puissance_kw": p.get("puissance_kw"),
                "temps_charge_estime_min": p.get("temps_charge_estime_min"),
                "tarif_kwh": p.get("tarif_kwh"),
                "compatible_free2move": p.get("compatible_free2move", False),
                "disponible": p.get("disponible", False),
            })

    bornes.sort(key=lambda x: x["distance_km"])
    bornes_proches = bornes[:3]

    recommandation = None
    if bornes_proches:
        b = bornes_proches[0]
        recommandation = (
            f"La borne la plus proche est {b['nom']} à {b['distance_km']} km. "
            f"Charge estimée : {b.get('temps_charge_estime_min', 'N/A')} min jusqu'à 80 %."
        )

    return {
        "niveau_batterie_pct": niveau_batterie,
        "autonomie_restante_km": autonomie,
        "urgence_recharge": urgence_recharge,
        "message_urgence": message_urgence,
        "destination": destination,
        "bornes_proches": bornes_proches,
        "recommandation": recommandation,
        "compatible_free2move_charge": any(b.get("compatible_free2move") for b in bornes_proches),
    }


# ──────────────────────────────────────────────
# TOOL 4 — get_offers
# ──────────────────────────────────────────────

def get_offers(user_id: str, category: str = "all") -> list:
    """Retourne les offres personnalisées filtrées par pertinence."""
    _validate_user(user_id)

    user = _get_user(user_id)
    vehicle = _get_vehicle_by_user(user_id)
    if not user or not vehicle:
        return []

    category = category or "all"
    offers_data = _load_json("offers.json")
    persona = user.get("persona_type", "")
    motorisation = vehicle.get("motorisation", "")
    marque = vehicle.get("marque", "")
    km_avant = vehicle.get("km_avant_revision", 9999) or 9999
    voyants = vehicle.get("voyants_actifs", []) or []
    anniversaire = vehicle.get("anniversaire_vehicule_dans_jours")

    offres_pertinentes = []

    for offer in offers_data.get("offers", []):
        if category != "all" and offer.get("categorie") != category:
            continue
        if persona not in offer.get("personas_cibles", []) and "all" not in offer.get("personas_cibles", []):
            continue
        if motorisation not in offer.get("motorisation_cible", []) and "all" not in offer.get("motorisation_cible", []):
            continue
        if marque not in offer.get("marques_cibles", []) and "all" not in offer.get("marques_cibles", []):
            continue

        score = 0.5
        declencheur = offer.get("declencheur", "")

        if declencheur == "prochaine_revision_proche" and km_avant < 2000:
            score = 0.95
        elif declencheur == "voyant_pression_pneu_actif" and any(v.get("code") == "pression_pneu" for v in voyants):
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
            "offer_id": offer.get("offer_id"),
            "titre": offer.get("titre"),
            "description": offer.get("description"),
            "categorie": offer.get("categorie"),
            "valeur": offer.get("valeur"),
            "conditions": offer.get("conditions"),
            "expiration": offer.get("expiration"),
            "points_gagnes": offer.get("points_gagnes", 0),
            "score_pertinence": score,
        })

    offres_pertinentes.sort(key=lambda x: x["score_pertinence"], reverse=True)
    return offres_pertinentes[:5]


# ──────────────────────────────────────────────
# TOOL 5 — get_loyalty_dashboard
# ──────────────────────────────────────────────

def get_loyalty_dashboard(user_id: str) -> dict:
    """Retourne le tableau de bord fidélité complet."""
    _validate_user(user_id)

    user = _get_user(user_id)
    if not user:
        return {"error": "Utilisatrice introuvable"}

    points = user.get("points_fidelite", 0) or 0
    niveau = user.get("niveau_fidelite", "Bronze")

    niveaux = {
        "Bronze": {"seuil": 0, "prochain": "Argent", "seuil_prochain": 300},
        "Argent": {"seuil": 300, "prochain": "Or", "seuil_prochain": 700},
        "Or": {"seuil": 700, "prochain": "Platine", "seuil_prochain": 1500},
        "Platine": {"seuil": 1500, "prochain": None, "seuil_prochain": None},
    }

    niveau_info = niveaux.get(niveau, niveaux["Bronze"])
    seuil_prochain = niveau_info.get("seuil_prochain")
    points_manquants = max(0, seuil_prochain - points) if seuil_prochain else None

    avantages = [
        {"titre": "Lavage offert", "points_requis": 200, "deja_debloque": points >= 200, "description": "Lavage intérieur/extérieur dans le réseau partenaire"},
        {"titre": "Contrôle technique -15€", "points_requis": 350, "deja_debloque": points >= 350, "description": "Valable dans les centres partenaires"},
        {"titre": "Révision -30%", "points_requis": 700, "deja_debloque": points >= 700, "description": "Sur la prochaine révision complète en réseau agréé"},
        {"titre": "Weekend offert Free2move", "points_requis": 1200, "deja_debloque": points >= 1200, "description": "2 nuits dans un hôtel partenaire Free2move"},
    ]

    historique = []
    for session in user.get("historique_sessions", []):
        for action in session.get("actions_declenchees", []):
            historique.append({
                "date": session.get("date"),
                "action": action,
                "points": "+50",
            })

    return {
        "prenom": user.get("prenom"),
        "points_actuels": points,
        "niveau": niveau,
        "prochain_niveau": niveau_info.get("prochain"),
        "points_pour_niveau_suivant": points_manquants,
        "avantages": avantages,
        "avantages_disponibles": [a for a in avantages if a["deja_debloque"]],
        "historique_recent": historique[-3:] if historique else [],
        "prochain_gain": "Passe ta prochaine révision et gagne 150 points !",
    }


# ──────────────────────────────────────────────
# TOOL 6 — get_partners
# ──────────────────────────────────────────────

def get_partners(location: str, type_partenaire: str, marque_vehicule: str = None) -> list:
    """Trouve les partenaires pertinents selon la localisation et le besoin."""
    if not type_partenaire:
        return []

    coords_user = _coords_for_location(location)
    partenaires_data = _load_json("partners.json")
    resultats = []

    for p in partenaires_data.get("partners", [])[:100]:
        if p.get("type") != type_partenaire:
            continue

        if type_partenaire == "garage_agree" and marque_vehicule:
            if marque_vehicule not in p.get("marques_acceptees", []):
                continue

        dist = _haversine_km(coords_user[0], coords_user[1], p.get("latitude"), p.get("longitude"))

        resultats.append({
            "partner_id": p.get("partner_id"),
            "nom": p.get("nom"),
            "adresse": p.get("adresse"),
            "ville": p.get("ville"),
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

    resultats.sort(key=lambda x: x["distance_km"])
    return resultats[:3]


# ──────────────────────────────────────────────
# TOOL 7 — search_stellantis_docs
# ──────────────────────────────────────────────

@lru_cache(maxsize=64)
def search_stellantis_docs(query: str, marque: str = None, categorie_doc: str = None) -> list:
    """Recherche sémantique dans la base RAG ChromaDB."""
    if not query or len(query.strip()) < 3:
        return []

    collection = _get_rag_collection()
    if collection is None:
        return [{
            "contenu": "La base documentaire Stellantis n'est pas disponible. Lance d'abord python rag/indexer.py.",
            "source": "RAG indisponible",
            "titre": "Base documentaire non initialisée",
            "url": "",
            "marque": marque or "Stellantis",
            "categorie": categorie_doc or "general",
            "score_similarite": 0,
        }]

    where = {}
    if marque:
        where["marque"] = marque
    if categorie_doc and categorie_doc != "all":
        where["categorie"] = categorie_doc

    try:
        results = collection.query(
            query_texts=[query.strip()],
            n_results=3,
            where=where if where else None,
        )
    except Exception as e:
        logger.warning("Erreur requête RAG : %s", e)
        return [{
            "contenu": "La recherche documentaire est temporairement indisponible.",
            "source": "Erreur ChromaDB",
            "titre": "Erreur technique RAG",
            "url": "",
            "marque": marque or "Stellantis",
            "categorie": categorie_doc or "general",
            "score_similarite": 0,
        }]

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    formatted_results = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        score = round(1 - float(dist), 3)
        if score < 0.35:
            continue

        formatted_results.append({
            "contenu": (doc or "")[:1500],
            "source": meta.get("source", "Document Stellantis"),
            "titre": meta.get("titre", "Document Stellantis"),
            "url": meta.get("url", ""),
            "marque": meta.get("marque", "Stellantis"),
            "categorie": meta.get("categorie", "general"),
            "score_similarite": score,
        })

    if not formatted_results:
        return [{
            "contenu": "Aucun extrait suffisamment pertinent n'a été trouvé dans la documentation indexée.",
            "source": "Base documentaire Stellantis",
            "titre": "Aucun résultat pertinent",
            "url": "",
            "marque": marque or "Stellantis",
            "categorie": categorie_doc or "general",
            "score_similarite": 0,
        }]

    return formatted_results


# ──────────────────────────────────────────────
# TOOL 8 — escalate_to_human
# ──────────────────────────────────────────────

def escalate_to_human(user_id: str, reason: str, conversation_summary: str) -> dict:
    """Déclenche l'escalade vers un conseiller humain."""
    _validate_user(user_id)

    user = _get_user(user_id)
    prenom = user.get("prenom", "la cliente") if user else "la cliente"

    messages = {
        "insatisfaction": "Je transmets notre échange à un conseiller Stellantis. Il reviendra vers toi très rapidement avec une solution.",
        "urgence_securite": "Pour ta sécurité, je te mets immédiatement en contact avec notre équipe d'assistance. Reste en ligne.",
        "hors_capacite": "Cette question dépasse mes capacités actuelles. Je te connecte avec un expert Stellantis qui pourra t'aider.",
        "demande_explicite": "Bien sûr. Je te mets en contact avec un conseiller. Il aura tout le contexte de notre échange.",
    }

    reason = reason if reason in messages else "hors_capacite"
    message = messages[reason]
    conversation_summary = conversation_summary or "Résumé indisponible."

    escalade_log = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "prenom": prenom,
        "raison": reason,
        "resume_conversation": conversation_summary,
    }
    logger.info("[ESCALADE] %s", escalade_log)

    return {
        "escalade_confirmee": True,
        "canal": "chat_live",
        "temps_attente_estime_min": min(8, max(2, len(conversation_summary) // 120)),
        "conseiller_disponible": True,
        "message_transition": message,
        "reference_dossier": f"STL-{user_id}-{datetime.now().strftime('%Y%m%d%H%M')}",
    }


# ──────────────────────────────────────────────
# REGISTRE DES TOOLS
# ──────────────────────────────────────────────

TOOLS_DEFINITION = [
    {
        "name": "get_vehicle_status",
        "description": "Récupère l'état complet du véhicule : kilométrage, voyants actifs, niveau d'énergie, prochaine révision, garantie.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Identifiant unique de l'utilisatrice, ex: U001"},
            },
            "required": ["user_id"],
        },
    },
    {
        "name": "get_maintenance_recommendation",
        "description": "Génère une recommandation d'entretien personnalisée selon l'état du véhicule et le profil utilisatrice.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Identifiant unique de l'utilisatrice"},
            },
            "required": ["user_id"],
        },
    },
    {
        "name": "get_charging_recommendation",
        "description": "Recommande des bornes de recharge proches selon la ville et le niveau de batterie. Réservé aux véhicules électriques ou hybrides.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Identifiant unique de l'utilisatrice"},
                "location": {"type": "string", "description": "Ville ou position actuelle de l'utilisatrice"},
                "destination": {"type": "string", "description": "Destination du trajet, optionnel"},
            },
            "required": ["user_id", "location"],
        },
    },
    {
        "name": "get_offers",
        "description": "Retourne les offres et remises personnalisées selon le profil, le véhicule et le contexte.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Identifiant unique de l'utilisatrice"},
                "category": {
                    "type": "string",
                    "description": "Catégorie d'offres souhaitée",
                    "enum": ["entretien", "accessoires", "voyage", "recharge", "fidelite", "service", "all"],
                },
            },
            "required": ["user_id"],
        },
    },
    {
        "name": "get_loyalty_dashboard",
        "description": "Retourne le tableau de bord fidélité : points, niveau, avantages disponibles et historique récent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Identifiant unique de l'utilisatrice"},
            },
            "required": ["user_id"],
        },
    },
    {
        "name": "get_partners",
        "description": "Trouve les partenaires proches : garages agréés, bornes de recharge, hôtels, centres de contrôle technique.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Ville ou position de l'utilisatrice"},
                "type_partenaire": {
                    "type": "string",
                    "description": "Type de partenaire recherché",
                    "enum": ["garage_agree", "borne_recharge", "hotel", "centre_ct"],
                },
                "marque_vehicule": {"type": "string", "description": "Marque du véhicule pour filtrer les garages, optionnel"},
            },
            "required": ["location", "type_partenaire"],
        },
    },
    {
        "name": "search_stellantis_docs",
        "description": "Recherche dans la documentation officielle Stellantis : stratégie software, STLA Brain, SmartCockpit, Mobilisights, Free2move Charge, CloudMade, API véhicule connecté, électrification.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Question en langage naturel"},
                "marque": {"type": "string", "description": "Filtrer par marque Stellantis, optionnel"},
                "categorie_doc": {
                    "type": "string",
                    "description": "Type de document, optionnel",
                    "enum": ["software", "software_strategy", "ai_personalisation", "data_vehicle", "recharge", "api", "general", "official_pdf", "all"],
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "escalate_to_human",
        "description": "Transfère la conversation vers un conseiller humain en cas d'insatisfaction, urgence sécurité, demande explicite ou limite de capacité.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Identifiant unique de l'utilisatrice"},
                "reason": {
                    "type": "string",
                    "description": "Motif de l'escalade",
                    "enum": ["insatisfaction", "urgence_securite", "hors_capacite", "demande_explicite"],
                },
                "conversation_summary": {"type": "string", "description": "Résumé de la conversation pour le conseiller"},
            },
            "required": ["user_id", "reason", "conversation_summary"],
        },
    },
]


# ──────────────────────────────────────────────
# DISPATCHER — exécute un tool par son nom
# ──────────────────────────────────────────────

def execute_tool(tool_name: str, tool_input: dict) -> dict | list:
    """Exécute un tool par son nom avec les paramètres fournis."""
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

    if tool_input is None:
        tool_input = {}

    try:
        logger.info("[TOOL CALL] %s | input=%s", tool_name, tool_input)
        return tools_map[tool_name](**tool_input)
    except Exception as e:
        logger.exception("Erreur lors de l'exécution du tool %s", tool_name)
        return {"error": f"Erreur lors de l'exécution de {tool_name} : {str(e)}"}
