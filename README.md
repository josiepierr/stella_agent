````markdown
# 🚗 Stella -- Compagnon Mobilité Stellantis

Stella est un agent conversationnel IA conçu pour accompagner les conductrices Stellantis dans leurs usages quotidiens de mobilité.

Le projet a été réalisé dans le cadre du **Women in GenAI Hackathon 2026 -- Stellantis**.

---

# 🎯 Problématique

> Comment l’IA générative peut guider un programme de fidélisation qui rend l’entretien du véhicule plus simple, plus sûr et plus abordable pour les jeunes femmes, en transformant l’usage réel de leur voiture en recommandations et avantages personnalisés -- de la recharge intelligente aux remises sur les réparations, en passant par des accessoires ciblés et des services voyage & hôtellerie ?

---

# ✨ Fonctionnalités principales

Stella agit comme un véritable compagnon mobilité :

- 🔧 Assistance véhicule personnalisée
- ⚡ Recommandations de recharge
- 🎁 Avantages fidélité personnalisés
- 🏨 Suggestions partenaires Stellantis
- 📚 Recherche documentaire RAG
- 👨‍💼 Escalade vers conseiller humain
- 🎙️ Interaction vocale (STT + TTS)
- 👥 Gestion multi-conducteurs
- 📊 Dashboard ROI business

---

# 🧠 Architecture IA

Le système repose sur :

| Composant | Technologie |
|---|---|
| Agent conversationnel | Claude Sonnet (Anthropic) |
| Voix (STT/TTS) | OpenAI Whisper + TTS |
| RAG | ChromaDB |
| Frontend | Streamlit |
| Déploiement | Docker + Kubernetes |
| CI/CD | GitHub Actions |
| Hébergement | SSPCloud |

---

# 🏗️ Structure du projet

```bash
Stella_Agent/
│
├── agent/                 # Agent IA principal
├── assets/                # Vidéo et médias
├── data/                  # Données utilisateurs/véhicules
├── deployment/            # Kubernetes manifests
├── evaluation/            # Évaluation automatique
├── interface/             # Application Streamlit
├── rag/                   # Pipeline documentaire RAG
├── logs/                  # Logs sessions
│
├── dockerfile
├── requirements.txt
├── README.md
└── stella_roi_dashboard_credible.html
````

---

# 🖥️ Démo

## 🌐 Application déployée

```text
https://stella-pmakamwe.lab.sspcloud.fr
```

---

# 🎬 Onglets disponibles

## 1️⃣ Présentation

* vidéo courte de démonstration
* description des fonctionnalités

## 2️⃣ Démo Stella

* conversation IA temps réel
* mode vocal
* gestion multi-profils
* outils métier Stellantis

## 3️⃣ Dashboard ROI

* analyse économique
* projection coûts IA
* comparaison centre d’appels vs IA
* hypothèses business

---

# 🚀 Lancement local

## 1. Cloner le dépôt

```bash
git clone https://github.com/josiepierr/Stella_Agent.git
cd Stella_Agent
```

---

## 2. Créer l’environnement Python

```bash
python -m venv stella_env
```

### Windows

```bash
stella_env\Scripts\activate
```

### Linux / Mac

```bash
source stella_env/bin/activate
```

---

## 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## 4. Configurer les clés API

Créer un fichier `.env` :

```env
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
```

---

## 5. Lancer l’application

```bash
streamlit run interface/app.py
```

---

# 🐳 Docker

## Build local

```bash
docker build -t stella-agent .
```

## Run local

```bash
docker run -p 8501:8501 \
-e ANTHROPIC_API_KEY=xxx \
-e OPENAI_API_KEY=xxx \
stella-agent
```

---

# ☸️ Déploiement Kubernetes

## Déployer

```bash
kubectl apply -f deployment/
```

## Vérifier

```bash
kubectl get pods
kubectl get svc
kubectl get ingress
```

---

# 📈 Évaluation automatique

## Lancer l’évaluation

```bash
python evaluation/evaluate_agent.py
```

## Générer le rapport

```bash
python evaluation/generate_report.py
```

---

# 📊 Résultats actuels

| Métrique          | Valeur |
| ----------------- | ------ |
| Success rate      | 100%   |
| Avg score         | ~0.83  |
| Avg latency       | ~15s   |
| Avg cost          | ~0.03€ |
| Tool success rate | 100%   |

---

# 🔒 Sécurité & limites

Le système inclut :

* limitation des appels outils
* gestion erreurs API
* escalade humaine
* contrôle des coûts
* séparation conducteur actif / propriétaire

---

# 💡 Perspectives

Améliorations futures envisagées :

* mémoire conversationnelle longue
* compagnon lifestyle élargi
* recommandations contextuelles
* intégration temps réel véhicule connecté
* analytics utilisateurs
* personnalisation émotionnelle
* application mobile native

---

# 👥 Équipe

Les Fantatstiques 
Women in GenAI Hackathon 2026 -- Stellantis

Projet : Stella -- Compagnon Mobilité IA

---

# 📄 Licence

MIT License

```
```
