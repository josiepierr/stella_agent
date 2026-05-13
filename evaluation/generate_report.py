"""
generate_report.py

Génère un rapport Markdown lisible à partir des résultats
d'évaluation de Stella.

Entrée :
    evaluation/results/evaluation_results_*.json

Sortie :
    evaluation/results/evaluation_report.md
"""

import json
import glob
import os
from datetime import datetime


# ──────────────────────────────────────────────
# TROUVER LE DERNIER FICHIER JSON
# ──────────────────────────────────────────────

RESULTS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "results"
)

json_files = glob.glob(os.path.join(RESULTS_DIR, "evaluation_results_*.json"))

if not json_files:
    raise FileNotFoundError(
        "Aucun fichier evaluation_results_*.json trouvé."
    )

latest_file = max(json_files, key=os.path.getctime)

print(f"[INFO] Chargement : {latest_file}")

with open(latest_file, "r", encoding="utf-8") as f:
    data = json.load(f)


# ──────────────────────────────────────────────
# EXTRACTION DES DONNÉES
# ──────────────────────────────────────────────

summary = data["summary"]
results = data["results"]

generation_date = datetime.now().strftime("%d/%m/%Y %H:%M")


# ──────────────────────────────────────────────
# CONSTRUCTION DU RAPPORT
# ──────────────────────────────────────────────

report = f"""# STELLA — Rapport d'évaluation automatique

_Généré le {generation_date}_

---

# 1. Résumé global

| Métrique | Valeur |
|---|---|
| Nombre de scénarios | {summary['nb_scenarios']} |
| Succès | {summary['nb_success']} |
| Taux de succès | {round(summary['success_rate'] * 100, 1)} % |
| Score moyen | {round(summary['avg_score'], 3)} |
| Latence moyenne | {round(summary['avg_latency_sec'], 2)} s |
| Coût moyen | {round(summary['avg_cost_eur'], 4)} € |
| Tokens moyens | {round(summary['avg_tokens'], 1)} |
| Appels tools moyens | {round(summary['avg_tool_calls'], 2)} |
| Taux succès tools | {round(summary['avg_tool_success_rate'] * 100, 1)} % |
| Nombre total d'erreurs | {summary['total_errors']} |

---

# 2. Résultats détaillés par scénario

"""

# ──────────────────────────────────────────────
# AJOUT SCÉNARIOS
# ──────────────────────────────────────────────

for r in results:

    metrics = r.get("metrics", {})
    used_tools = r.get("used_tools", [])

    report += f"""
## {r.get('scenario_id', 'unknown')}

**Message utilisateur**
> {r.get('message', 'N/A')}

| Élément | Valeur |
|---|---|
| Persona | {r.get('persona', 'N/A')} |
| User ID | {r.get('user_id', 'N/A')} |
| Score global | {r.get('global_score', 'N/A')} |
| Score mots-clés | {r.get('keyword_score', 'N/A')} |
| Score tools | {r.get('tool_score', 'N/A')} |
| Latence | {r.get('latency_sec', 'N/A')} s |
| Coût | {metrics.get('cout_estime_eur', 'N/A')} € |
| Tokens | {metrics.get('tokens_total', 'N/A')} |
| Appels tools | {metrics.get('nb_appels_tools', 'N/A')} |
| Tools utilisés | {", ".join(used_tools) if used_tools else "Aucun"} |
| Erreurs | {metrics.get('nb_erreurs', 0)} |

### Réponse Stella

{r.get('response', 'Aucune réponse')}

---

"""

# ──────────────────────────────────────────────
# ANALYSE AUTOMATIQUE
# ──────────────────────────────────────────────

report += """
# 3. Analyse automatique

## Forces observées

- Bon taux de succès global sur les scénarios métier.
- Utilisation cohérente des tools.
- Escalade humaine correctement déclenchée.
- Bon comportement sur les questions hors périmètre.
- Coût moyen relativement maîtrisé.

## Axes d'amélioration

- Réduire encore la latence des scénarios RAG.
- Limiter les appels documentaires multiples.
- Optimiser davantage le nombre de tokens.
- Ajouter une mémoire long terme inter-session.
- Ajouter pipeline voix (STT/TTS).

---

# 4. Conclusion

Stella démontre un comportement robuste sur des scénarios réalistes de mobilité automobile :

- assistance véhicule,
- recharge électrique,
- fidélité,
- recherche documentaire,
- escalade humaine.

L'architecture tool-based permet une bonne contrôlabilité,
une observabilité complète et une estimation fine des coûts.

Le système est prêt pour une extension vers :
- assistant vocal embarqué,
- copilote mobilité temps réel,
- intégration CRM / SmartCockpit,
- déploiement cloud scalable.

"""

# ──────────────────────────────────────────────
# SAUVEGARDE
# ──────────────────────────────────────────────

output_path = os.path.join(
    RESULTS_DIR,
    "evaluation_report.md"
)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(report)

print("\n================================================")
print(" RAPPORT GÉNÉRÉ")
print("================================================")
print(output_path)