"""
scraper.py
Récupère les documents publics des sites Stellantis
et les sauvegarde en fichiers texte pour indexation RAG.

Usage : python scraper.py
"""

import requests
from bs4 import BeautifulSoup
import os
import json
import time
import shutil

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs_stellantis")
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# URLs à scraper par marque et catégorie
SOURCES = [
    # ── Citroën
    {
        "marque": "Citroën",
        "categorie": "fiche_technique",
        "titre": "Citroën C3 — Fiche technique et caractéristiques",
        "url": "https://www.citroen.fr/vehicules-neufs/citroën-c3.html",
        "source_type": "official_public"
    },
    {
        "marque": "Citroën",
        "categorie": "entretien",
        "titre": "Citroën — Services et entretien",
        "url": "https://www.citroen.fr/services-citroen/entretien-vehicule.html",
        "source_type": "official_public"
    },
    {
        "marque": "Citroën",
        "categorie": "garantie",
        "titre": "Citroën — Garantie véhicule",
        "url": "https://www.citroen.fr/services-citroen/garantie.html",
        "source_type": "official_public"
    },
    # ── Peugeot
    {
        "marque": "Peugeot",
        "categorie": "fiche_technique",
        "titre": "Peugeot e-208 — Fiche technique électrique",
        "url": "https://www.peugeot.fr/vehicules-neufs/e-208.html",
        "source_type": "official_public"
    },
    {
        "marque": "Peugeot",
        "categorie": "entretien",
        "titre": "Peugeot — Services et entretien",
        "url": "https://www.peugeot.fr/services/entretien.html",
        "source_type": "official_public"
    },
    {
        "marque": "Peugeot",
        "categorie": "garantie",
        "titre": "Peugeot — Garantie et assistance",
        "url": "https://www.peugeot.fr/services/garantie.html",
        "source_type": "official_public"
    },
    # ── Jeep
    {
        "marque": "Jeep",
        "categorie": "fiche_technique",
        "titre": "Jeep Avenger — Caractéristiques techniques",
        "url": "https://www.jeep.fr/vehicules-neufs/avenger.html",
        "source_type": "official_public"
    },
    {
        "marque": "Jeep",
        "categorie": "garantie",
        "titre": "Jeep — Garantie et service après-vente",
        "url": "https://www.jeep.fr/services/garantie.html",
        "source_type": "official_public"
    },
    # ── Fiat
    {
        "marque": "Fiat",
        "categorie": "fiche_technique",
        "titre": "Fiat 500 — Caractéristiques et motorisations",
        "url": "https://www.fiat.fr/gamme/500.html",
        "source_type": "official_public"
    },
    # ── Free2move
    {
        "marque": "Free2move",
        "categorie": "cgu",
        "titre": "Free2move — Conditions générales d'utilisation",
        "url": "https://fr.free2move.com/fr/conditions-generales",
        "source_type": "official_public"
    },
    {
        "marque": "Free2move",
        "categorie": "entretien",
        "titre": "Free2move Charge — Recharge électrique",
        "url": "https://fr.free2move.com/fr/recharge",
        "source_type": "official_public"
    },
    # ── Stellantis groupe
    {
        "marque": "Stellantis",
        "categorie": "general",
        "titre": "Stellantis — À propos du groupe",
        "url": "https://www.stellantis.com/fr/groupe",
        "source_type": "official_public"
    },
    #
     {
        "marque": "Stellantis",
        "categorie": "software",
        "titre": "Stellantis — STLA Brain et STLA SmartCockpit",
        "url": "https://www.stellantis.com/en/innovation/intelligent-vehicles-software",
        "source_type": "official_public"
    },
    {
        "marque": "Mobilisights",
        "categorie": "data_vehicle",
        "titre": "Mobilisights — Données véhicule connecté",
        "url": "https://www.stellantis.com/en/news/press-releases/2024/january/empowering-customers-a-year-of-major-advances-in-mobilisights-mobility-data",
        "source_type": "official_public"
    },
    {
        "marque": "Free2move",
        "categorie": "recharge",
        "titre": "Free2move Charge — Écosystème de recharge",
        "url": "https://www.stellantis.com/en/news/press-releases/2023/june/charging-your-way-stellantis-launches-free2move-charge-to-make-it-easy-to-always-be-charged",
        "source_type": "official_public"
    },
    {
        "marque": "Stellantis",
        "categorie": "api",
        "titre": "Stellantis Developers — Connected Vehicle API",
        "url": "https://developers.stellantis.com/docs.html",
        "source_type": "official_public"
    },
    {
    "marque": "Stellantis",
    "categorie": "software_strategy",
    "titre": "Stellantis — Revenus software-enabled vehicles",
    "url": "https://www.stellantis.com/en/news/press-releases/2021/december/stellantis-targets-20-billion-in-incremental-annual-revenues-by-2030-driven-by-software-enabled-vehicles",
    "source_type": "official_public"
    },
    {
        "marque": "Stellantis",
        "categorie": "ai_personalisation",
        "titre": "Stellantis — CloudMade AI personalization",
        "url": "https://www.stellantis.com/en/news/press-releases/2024/january/stellantis-to-enhance-personalized-mobility-experience-with-acquisition-of-cloudmade-s-artificial-intelligence-technologies-and-ip",
        "source_type": "official_public"
    }
]

# ──────────────────────────────────────────────
# DOCUMENTS DE FALLBACK
# Utilisés si le scraping échoue (anti-bot, structure changée)
# Basés sur les informations publiques connues des marques
# ──────────────────────────────────────────────

FALLBACK_DOCS = [
    {
        "marque": "Citroën",
        "categorie": "fiche_technique",
        "titre": "Citroën C3 — Fiche technique complète",
        "contenu": """
Citroën C3 — Fiche technique officielle

MOTORISATIONS DISPONIBLES
- Pure Tech 83 ch (essence) : consommation mixte 5.2L/100km, émissions CO2 118g/km
- Pure Tech 110 ch (essence) : consommation mixte 5.4L/100km
- Blue HDi 100 ch (diesel) : consommation mixte 3.8L/100km, émissions CO2 102g/km

DIMENSIONS
- Longueur : 4,00 m | Largeur : 1,75 m | Hauteur : 1,48 m
- Volume coffre : 315 litres (extendable à 1150 L sièges rabattus)
- Poids à vide : 1050 à 1180 kg

PRESSION DES PNEUS RECOMMANDÉE (C3 thermique)
- Pneus standard 185/65 R15 : 2.3 bar avant, 2.1 bar arrière (à froid)
- Avec charge complète : 2.6 bar avant, 2.4 bar arrière
- Pneus 205/45 R17 : 2.5 bar avant, 2.3 bar arrière

ENTRETIEN RECOMMANDÉ
- Révision huile et filtres : tous les 20 000 km ou 1 an
- Remplacement filtres à air : tous les 40 000 km
- Remplacement bougies : tous les 60 000 km (essence)
- Contrôle freins : tous les 20 000 km
- Remplacement courroie de distribution : 150 000 km ou 10 ans

ÉQUIPEMENTS SÉRIE
- Aide au démarrage en côte
- Système multimédia avec écran tactile 7"
- Bluetooth et connexion smartphone
- Rétroviseurs électriques
- Climatisation manuelle (selon finition)

GARANTIE CITROËN
- Garantie constructeur : 2 ans kilométrage illimité
- Garantie anti-perforation carrosserie : 12 ans
- Assistance 24h/24 incluse pendant la période de garantie
- Extension de garantie disponible : jusqu'à 5 ans

RÉSEAU APRÈS-VENTE
- Plus de 700 points de service en France
- Prise en charge sous 48h pour entretien courant
- Pièces d'origine Citroën garanties 2 ans
"""
    },
    {
        "marque": "Citroën",
        "categorie": "entretien",
        "titre": "Citroën — Guide d'entretien et maintenance",
        "contenu": """
Citroën — Guide d'entretien officiel

PROGRAMME D'ENTRETIEN CITROËN

Révision annuelle ou 20 000 km (la première des deux échéances)
Comprend :
- Vidange huile moteur + remplacement filtre huile
- Vérification et remplacement filtre à air si nécessaire
- Contrôle et ajustement pression des pneus
- Contrôle niveau liquide de refroidissement, frein, direction
- Vérification état des balais d'essuie-glaces
- Diagnostic électronique complet
- Test batterie 12V
- Contrôle éclairage complet
Tarif indicatif réseau agréé : 180-250€ selon modèle

Révision intermédiaire 10 000 km
- Contrôle visuel général
- Vérification pression pneus
- Contrôle niveaux
Tarif indicatif : 80-120€

VOYANTS ET SIGNIFICATIONS
- Voyant pression pneus (pictogramme pneu avec point d'exclamation) :
  Un ou plusieurs pneus sont sous-gonflés. À corriger sous 48h maximum.
  Ne pas rouler à plus de 80 km/h avant correction.
  
- Voyant huile (pictogramme huilier rouge) :
  Pression huile insuffisante. ARRÊTER le véhicule immédiatement.
  Ne pas redémarrer avant vérification du niveau.

- Voyant température (thermomètre rouge) :
  Surchauffe moteur. Arrêter immédiatement, laisser refroidir.

- Voyant batterie (pictogramme pile) :
  Problème de charge alternateur. Consulter un technicien rapidement.

- Voyant service (clé ou tournevis) :
  Révision programmée échue. Prendre rendez-vous en atelier.

CONTRAT D'ENTRETIEN CITROËN
Citroën propose des forfaits entretien prépayés :
- Pack Entretien 2 ans : révisions à prix fixe bloqué
- Pack Entretien 4 ans : inclut pneus et freins
- Tarification mensuelle disponible à partir de 19€/mois
"""
    },
    {
        "marque": "Citroën",
        "categorie": "garantie",
        "titre": "Citroën — Conditions de garantie",
        "contenu": """
Citroën — Garantie constructeur

GARANTIE DE BASE
Durée : 2 ans à compter de la date de livraison, kilométrage illimité
Couvre : tous les défauts de matériaux et de fabrication
Exclusions : pièces d'usure normale (pneus, plaquettes de frein, disques, ampoules, balais)

GARANTIE ANTI-PERFORATION
Durée : 12 ans
Couvre : perforation de la carrosserie par corrosion de l'intérieur vers l'extérieur

ASSISTANCE 24h/24
Incluse pendant toute la durée de la garantie
Services inclus :
- Dépannage sur place si possible
- Remorquage vers le garage agréé le plus proche
- Véhicule de remplacement (selon contrat)
- Prise en charge hébergement si panne à plus de 50 km du domicile

EXTENSIONS DE GARANTIE
- Citroën Garantie + : extension jusqu'à 5 ans ou 100 000 km
- Peut être souscrite jusqu'à 6 mois après l'achat du véhicule neuf
- Inclut l'assistance routière étendue

CONDITIONS DE VALIDITÉ
- Respect du plan d'entretien constructeur
- Entretien effectué dans le réseau agréé Citroën ou PSA
- Utilisation de pièces d'origine Citroën
- Carnet d'entretien à jour et tamponné

DÉMARCHE EN CAS DE PANNE SOUS GARANTIE
1. Contacter le service Citroën Assistance : 0 800 00 24 24 (gratuit)
2. Ou se rendre directement au garage agréé le plus proche
3. Présenter le carnet de garantie et les justificatifs d'entretien
"""
    },
    {
        "marque": "Peugeot",
        "categorie": "fiche_technique",
        "titre": "Peugeot e-208 — Fiche technique électrique",
        "contenu": """
Peugeot e-208 — Fiche technique officielle véhicule électrique

MOTORISATION ÉLECTRIQUE
- Puissance : 115 kW (156 ch)
- Couple maximal : 260 Nm
- 0 à 100 km/h : 8.1 secondes
- Vitesse maximale : 150 km/h (bridée)

BATTERIE
- Capacité : 50 kWh (bruts) / 46 kWh (nets)
- Autonomie WLTP : jusqu'à 362 km (cycle mixte)
- Autonomie urbaine WLTP : jusqu'à 580 km
- Garantie batterie : 8 ans ou 160 000 km (maintien 70% capacité)
- Dégradation normale : environ 2-3% par an

RECHARGE
- Recharge AC (courant alternatif) : 11 kW max, 0-100% en ~5h30
- Recharge DC rapide (courant continu) : 100 kW max, 0-80% en 25 minutes
- Prise embarquée : Type 2 (AC) + CCS Combo (DC)
- Compatible avec toutes les bornes publiques européennes

NIVEAUX DE CHARGE ET RECOMMANDATIONS
- Charge quotidienne recommandée : maintenir entre 20% et 80%
- Charge complète (100%) : uniquement pour longs trajets
- Ne pas descendre régulièrement sous 10% : accélère la dégradation
- Température optimale de charge : 15°C à 25°C

DIMENSIONS
- Longueur : 4,06 m | Largeur : 1,75 m | Hauteur : 1,43 m
- Volume coffre : 311 litres
- Poids à vide : 1530 kg

ENTRETIEN SPÉCIFIQUE ÉLECTRIQUE
- Révision : tous les 2 ans ou 30 000 km (moins fréquent que thermique)
- Pas de vidange huile moteur
- Vérification freins régénératifs : tous les 60 000 km
- Remplacement liquide de frein : tous les 2 ans
- Vérification climatisation thermique batterie : annuelle
- Mise à jour logicielle : via réseau agréé ou OTA (Over The Air)
"""
    },
    {
        "marque": "Peugeot",
        "categorie": "garantie",
        "titre": "Peugeot — Garantie véhicule électrique",
        "contenu": """
Peugeot — Garantie constructeur véhicule électrique

GARANTIE VÉHICULE
Durée : 2 ans kilométrage illimité
Couvre : défauts de fabrication sur toutes les pièces mécaniques et électroniques

GARANTIE BATTERIE HAUTE TENSION
Durée : 8 ans ou 160 000 km
Condition : la capacité de la batterie ne descend pas sous 70%
Si la capacité descend sous 70% dans la période : remplacement ou réparation gratuite
Cette garantie est transférable en cas de revente du véhicule

GARANTIE ANTI-CORROSION
Durée : 12 ans (perforation de l'intérieur vers l'extérieur)

ASSISTANCE PEUGEOT
Disponible 24h/24, 7j/7, en France et en Europe
Numéro : 0 800 00 24 24
Services :
- Dépannage électrique (recharge d'urgence possible)
- Remorquage vers point de charge ou réseau agréé
- Mise à disposition d'un véhicule de remplacement thermique ou électrique

EXTENSIONS DE GARANTIE
Peugeot Garantie + : jusqu'à 5 ans ou 120 000 km
Inclut la couverture batterie étendue au-delà des 8 ans constructeur
"""
    },
    {
        "marque": "Jeep",
        "categorie": "fiche_technique",
        "titre": "Jeep Avenger — Fiche technique hybride",
        "contenu": """
Jeep Avenger — Fiche technique officielle

MOTORISATION HYBRIDE (version e-Hybrid)
- Moteur essence : 1.2L PureTech 100 ch
- Moteur électrique : 21 kW (28 ch) d'assistance
- Système mild-hybrid 48V
- Puissance combinée : 136 ch
- Couple : 230 Nm
- 0 à 100 km/h : 9.9 secondes
- Consommation mixte WLTP : 5.4L/100km
- Émissions CO2 : 123g/km

VERSION 100% ÉLECTRIQUE (Avenger BEV)
- Puissance : 115 kW (156 ch)
- Autonomie WLTP : 404 km
- Recharge rapide DC : 100 kW

DIMENSIONS
- Longueur : 4,08 m | Largeur : 1,78 m | Hauteur : 1,53 m
- Garde au sol : 200 mm
- Volume coffre : 355 litres

ÉQUIPEMENTS SÉRIE
- Système multimédia Uconnect 5 avec écran 10.25"
- Navigation connectée
- Chargeur à induction smartphone
- Caméra de recul
- Aide au stationnement avant/arrière
- Modes de conduite : Normal, Eco, Sport, Snow

ENTRETIEN HYBRIDE
- Révision : tous les 20 000 km ou 1 an
- Vidange huile moteur thermique : identique à un thermique classique
- Vérification système 48V : tous les 40 000 km
- Batterie hybride 48V : garantie 8 ans, peu de maintenance
- Freins régénératifs : s'usent moins vite (moins de friction)

GARANTIE JEEP
- Véhicule : 3 ans ou 100 000 km (meilleur que la moyenne du marché)
- Batterie hybride 48V : 8 ans ou 160 000 km
- Assistance 24h/24 incluse
"""
    },
    {
        "marque": "Free2move",
        "categorie": "cgu",
        "titre": "Free2move — Services et conditions d'utilisation",
        "contenu": """
Free2move — Plateforme de mobilité Stellantis

PRÉSENTATION DU SERVICE
Free2move est la solution de mobilité du groupe Stellantis.
Elle regroupe sur une seule application :
- Service de recharge électrique (Free2move Charge)
- Location courte durée
- Autopartage
- Stationnement dans les grandes villes
- Réservation d'hôtels partenaires

RÉSEAU FREE2MOVE CHARGE
- Plus de 175 000 bornes en France et en Europe
- Compatible avec tous les véhicules électriques (standard Type 2 et CCS)
- Facturation unifiée : une seule facture pour tous les opérateurs
- Application mobile pour localiser, réserver et payer
- Tarifs moyens : 0.35 à 0.55€/kWh selon la puissance et l'opérateur

ABONNEMENTS FREE2MOVE CHARGE
- Pass Recharge : accès illimité, facturation à l'usage
- Abonnement mensuel Standard : 7.99€/mois + tarifs réduits
- Abonnement mensuel Premium : 14.99€/mois + tarifs préférentiels
- Forfait Entreprise : facturation mensuelle unifiée pour les flottes

PROGRAMME DE FIDÉLITÉ
Le programme de points Free2move récompense chaque utilisation :
- Recharge sur réseau Free2move : points selon kWh rechargés
- Révision dans le réseau agréé : points selon montant
- Achat d'accessoires : points selon montant
- Parrainage : 200 points par filleul actif

PARTENAIRES HÔTELIERS
Free2move propose des tarifs négociés chez :
- Groupe Accor (Ibis, Novotel, Mercure) : -10 à -20%
- B&B Hotels : -15%
- Hôtels indépendants partenaires : -10%
Condition : réservation via l'application Free2move

DONNÉES ET CONFIDENTIALITÉ
Free2move collecte uniquement les données nécessaires au service :
- Données de géolocalisation : uniquement pendant les sessions de navigation
- Historique de recharge : conservé 3 ans
- Données de paiement : jamais stockées en clair (tokenisation)
- Droit à l'effacement : exercice possible via l'application ou par email
- Hébergement des données : serveurs en Europe (conformité RGPD)
"""
    },
    {
        "marque": "Stellantis",
        "categorie": "general",
        "titre": "Stellantis — Groupe automobile et marques",
        "contenu": """
Stellantis — Présentation du groupe

LE GROUPE STELLANTIS
Stellantis est né en janvier 2021 de la fusion entre PSA Group et Fiat Chrysler Automobiles.
C'est l'un des plus grands constructeurs automobiles mondiaux avec 14 marques.

LES 14 MARQUES DU GROUPE
Marques premium et de luxe : Maserati, Alfa Romeo, DS Automobiles
Marques généralistes Europe : Peugeot, Citroën, Opel/Vauxhall, Fiat, Lancia
Marques américaines : Jeep, Ram, Dodge, Chrysler
Marque commerciale : Abarth

PRÉSENCE EN FRANCE
Marques principales sur le marché français :
- Peugeot : leader historique, gamme complète thermique, hybride, électrique
- Citroën : confort et accessibilité, fort en véhicules utilitaires
- DS Automobiles : positionnement premium français, rival de BMW/Audi
- Jeep : SUV et tout-terrain, notoriété mondiale
- Fiat : citadines, marché des petits véhicules
- Opel : marché germanique et européen

STRATÉGIE ÉLECTRIQUE
Objectif Stellantis : 100% de ventes électriques en Europe d'ici 2030
Plateformes électriques : STLA Small, STLA Medium, STLA Large, STLA Frame
Technologie embarquée : STLA SmartCockpit (IA embarquée, connectivité avancée)
Partenariat données : Mobilisights (données véhicules connectés en temps réel)

ENGAGEMENT DÉVELOPPEMENT DURABLE
- Neutralité carbone pour l'ensemble du groupe d'ici 2038
- Réduction de 50% des émissions de CO2 d'ici 2030
- Programme de recyclage batteries en fin de vie
- Approvisionnement responsable en matières premières

SERVICE CLIENT STELLANTIS
- Application Free2move : point d'entrée unique pour tous les services mobilité
- Réseau après-vente : plus de 2 000 points de service en France
- Numéro d'assistance universel : 0 800 00 24 24 (gratuit, 24h/24)
- Programme de fidélisation : Free2move Points (commun à toutes les marques)
"""
    },
]


# ──────────────────────────────────────────────
# FONCTIONS DE SCRAPING
# ──────────────────────────────────────────────

def scrape_url(url: str) -> str | None:
    """Scrape une page avec Playwright, utile pour les sites chargés en JavaScript."""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent=HEADERS["User-Agent"],
                locale="fr-FR"
            )
            page.goto(url, wait_until="networkidle", timeout=30000)

            # Tentative accept cookies
            for label in ["Tout accepter", "Accepter", "Accept all", "I agree"]:
                try:
                    page.get_by_text(label, exact=False).click(timeout=2000)
                    break
                except Exception:
                    pass

            text = page.locator("body").inner_text(timeout=10000)
            browser.close()

        lines = [l.strip() for l in text.splitlines() if l.strip() and len(l.strip()) > 25]
        cleaned = "\n".join(lines[:250])

        return cleaned if len(cleaned) > 300 else None

    except Exception as e:
        print(f"  ⚠️  Erreur scraping {url}: {e}")
        return None


def save_document(doc: dict, content: str):
    safe_name = doc["titre"].lower()
    for char in " /\\:*?\"<>|'éèêëàâùûüîïç":
        safe_name = safe_name.replace(char, "_")
    safe_name = safe_name[:60] + ".json"

    filepath = os.path.join(OUTPUT_DIR, safe_name)

    data = {
        "marque": doc["marque"],
        "categorie": doc["categorie"],
        "titre": doc["titre"],
        "url": doc.get("url", "fallback"),
        "source_type": doc.get("source_type", "simulated_fallback"),
        "date_scraping": time.strftime("%Y-%m-%d"),
        "contenu": content,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filepath


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def run_scraper():
    print("\n" + "="*55)
    print("  STELLA — Constitution de la base documentaire RAG")
    print("="*55)
    print(f"\nDossier de sortie : {OUTPUT_DIR}\n")
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    saved = 0
    failed = 0

    # ── Étape 1 : tentative de scraping des URLs
    print("📥 Étape 1 — Scraping des sites officiels Stellantis...")
    for doc in SOURCES:
        print(f"  → {doc['marque']} | {doc['categorie']} | {doc['titre'][:45]}...")
        content = scrape_url(doc["url"])
        if content and len(content) > 300:
            filepath = save_document(doc, content)
            print(f"     ✅ Sauvegardé ({len(content)} caractères)")
            saved += 1
        else:
            print(f"     ⚠️  Scraping insuffisant — document ignoré")
            failed += 1
        time.sleep(1)  # Politesse serveur

    # ── Étape 2 : fallback pour les documents non récupérés
    USE_FALLBACKS = False

    if USE_FALLBACKS:
        print(f"\n📋 Étape 2 — Ajout des {len(FALLBACK_DOCS)} documents de fallback...")
        for doc in FALLBACK_DOCS:
            existing = [f for f in os.listdir(OUTPUT_DIR)
                        if doc["marque"].lower() in f and doc["categorie"].lower() in f]
            if existing:
                continue
            save_document(doc, doc["contenu"])

    # ── Résumé
    all_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".json")]
    print(f"✅ Base documentaire constituée :")
    print(f"   {saved} documents officiels sauvegardés")
    print(f"   {failed} URLs ignorées ou non exploitables")
    print(f"   {len(all_files)} documents disponibles pour le RAG")
    print(f"   Dossier : {OUTPUT_DIR}")


if __name__ == "__main__":
    run_scraper()