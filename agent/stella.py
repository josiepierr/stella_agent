"""
stella.py
Moteur principal de l'agent Stella.
Gère la boucle conversation : appel LLM → détection tool use → exécution → réponse finale.
"""

import json
import os
import time
from dotenv import load_dotenv
import anthropic

from prompts import build_system_prompt
from tools import TOOLS_DEFINITION, execute_tool

# Chargement des variables d'environnement
load_dotenv()

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────

MODEL = "claude-sonnet-4-5"
MAX_TOKENS = 1024
MAX_TOOL_ITERATIONS = 5  # Sécurité : max 5 appels de tools par tour


# ──────────────────────────────────────────────
# CHARGEMENT DU PROFIL UTILISATRICE
# ──────────────────────────────────────────────

def _load_json(filename: str) -> dict | list:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filepath = os.path.join(base_dir, "data", filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_user_profile(user_id: str) -> tuple[dict, dict]:
    """
    Charge le profil utilisatrice et son véhicule.

    Returns:
        tuple: (user dict, vehicle dict)
    """
    users = _load_json("users.json")
    vehicles = _load_json("vehicles.json")

    user = next((u for u in users["users"] if u["user_id"] == user_id), None)
    vehicle = next((v for v in vehicles["vehicles"] if v["user_id"] == user_id), None)

    if not user or not vehicle:
        raise ValueError(f"Profil introuvable pour user_id={user_id}")

    return user, vehicle


# ──────────────────────────────────────────────
# CLASSE PRINCIPALE — StellaAgent
# ──────────────────────────────────────────────

class StellaAgent:
    """
    Agent conversationnel Stella.
    Maintient l'historique de conversation et gère la boucle tool use.
    """

    def __init__(self, user_id: str):
        """
        Initialise l'agent pour une utilisatrice donnée.

        Args:
            user_id: identifiant de l'utilisatrice (ex: "U001")
        """
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.user_id = user_id
        self.user, self.vehicle = load_user_profile(user_id)
        self.system_prompt = build_system_prompt(self.user, self.vehicle)
        self.conversation_history = []

        # Métriques pour l'évaluation des coûts (Phase 4)
        self.metrics = {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_tool_calls": 0,
            "total_turns": 0,
            "session_start": time.time()
        }

        print(f"[STELLA] Agent initialisé pour {self.user['prenom']} ({user_id})")

    # ──────────────────────────────────────────
    # MÉTHODE PRINCIPALE — chat()
    # ──────────────────────────────────────────

    def chat(self, user_message: str) -> str:
        """
        Traite un message utilisatrice et retourne la réponse de Stella.
        Gère automatiquement la boucle tool use.

        Args:
            user_message: message de l'utilisatrice en langage naturel

        Returns:
            str: réponse finale de Stella
        """
        # Ajout du message à l'historique
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        self.metrics["total_turns"] += 1
        iterations = 0

        # ── BOUCLE AGENT ──
        while iterations < MAX_TOOL_ITERATIONS:
            iterations += 1

            # Appel à l'API Claude
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=self.system_prompt,
                tools=TOOLS_DEFINITION,
                messages=self.conversation_history
            )

            # Mise à jour des métriques tokens
            self.metrics["total_input_tokens"] += response.usage.input_tokens
            self.metrics["total_output_tokens"] += response.usage.output_tokens

            # ── CAS 1 : Réponse finale (pas de tool use) ──
            if response.stop_reason == "end_turn":
                final_response = self._extract_text(response)
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })
                return final_response

            # ── CAS 2 : L'agent veut utiliser un ou plusieurs tools ──
            elif response.stop_reason == "tool_use":

                # Ajout de la réponse assistant à l'historique
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })

                # Exécution de tous les tools demandés
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        self.metrics["total_tool_calls"] += 1
                        tool_name = block.name
                        tool_input = block.input

                        print(f"[TOOL] {tool_name}({tool_input})")

                        # Exécution du tool
                        result = execute_tool(tool_name, tool_input)

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, ensure_ascii=False, indent=2)
                        })

                # Ajout des résultats à l'historique
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })

            # ── CAS 3 : Arrêt inattendu ──
            else:
                return "Je rencontre une difficulté technique. Un conseiller Stellantis peut t'aider directement."

        # Sécurité : trop d'itérations
        return "Je vais te connecter à un conseiller pour t'aider au mieux."

    # ──────────────────────────────────────────
    # MÉTHODES UTILITAIRES
    # ──────────────────────────────────────────

    def _extract_text(self, response) -> str:
        """Extrait le texte de la réponse Claude."""
        for block in response.content:
            if hasattr(block, "text"):
                return block.text
        return ""

    def reset_conversation(self):
        """Réinitialise l'historique de conversation (nouvelle session)."""
        self.conversation_history = []
        print(f"[STELLA] Conversation réinitialisée pour {self.user['prenom']}")

    def get_metrics(self) -> dict:
        """
        Retourne les métriques de la session.
        Utilisé pour la Phase 4 — analyse des coûts.
        """
        duration = time.time() - self.metrics["session_start"]

        # Calcul du coût estimé (tarifs Claude Sonnet 4 au 05/05/2026)
        # Input : $3 / 1M tokens | Output : $15 / 1M tokens
        cost_input = (self.metrics["total_input_tokens"] / 1_000_000) * 3
        cost_output = (self.metrics["total_output_tokens"] / 1_000_000) * 15
        cost_total = cost_input + cost_output

        return {
            "user_id": self.user_id,
            "prenom": self.user["prenom"],
            "duree_session_sec": round(duration, 1),
            "nb_tours_conversation": self.metrics["total_turns"],
            "nb_appels_tools": self.metrics["total_tool_calls"],
            "tokens_input": self.metrics["total_input_tokens"],
            "tokens_output": self.metrics["total_output_tokens"],
            "tokens_total": self.metrics["total_input_tokens"] + self.metrics["total_output_tokens"],
            "cout_estime_usd": round(cost_total, 6),
            "cout_estime_eur": round(cost_total * 0.92, 6),
        }

    def get_conversation_summary(self) -> str:
        """
        Génère un résumé de la conversation pour l'escalade humaine (T4).
        """
        if not self.conversation_history:
            return "Aucun échange enregistré."

        messages_texte = []
        for msg in self.conversation_history:
            if isinstance(msg["content"], str):
                role = "Utilisatrice" if msg["role"] == "user" else "Stella"
                messages_texte.append(f"{role}: {msg['content'][:200]}")

        return " | ".join(messages_texte[-6:])  # Derniers 6 échanges


# ──────────────────────────────────────────────
# TEST EN LIGNE DE COMMANDE
# ──────────────────────────────────────────────

if __name__ == "__main__":
    """
    Test rapide de l'agent en mode terminal.
    Usage : python stella.py
    """
    print("\n" + "="*50)
    print("   STELLA — Agent Mobilité Stellantis")
    print("   Test en ligne de commande")
    print("="*50)

    # Choix du profil
    print("\nChoisir un profil de test :")
    print("  1. Camille (U001) — Citroën C3, voyant actif")
    print("  2. Sofia   (U002) — Peugeot e-208, batterie faible")
    print("  3. Inès    (U003) — Jeep Avenger, anniversaire véhicule")

    choix = input("\nProfil [1/2/3] : ").strip()
    user_ids = {"1": "U001", "2": "U002", "3": "U003"}
    user_id = user_ids.get(choix, "U001")

    # Initialisation de l'agent
    agent = StellaAgent(user_id=user_id)

    print(f"\n[Stella est prête. Tape 'quit' pour quitter, 'metrics' pour voir les coûts]\n")

    # Boucle de conversation
    while True:
        user_input = input("Toi : ").strip()

        if user_input.lower() == "quit":
            print("\n[Métriques finales de session]")
            metrics = agent.get_metrics()
            for k, v in metrics.items():
                print(f"  {k}: {v}")
            break

        if user_input.lower() == "metrics":
            metrics = agent.get_metrics()
            for k, v in metrics.items():
                print(f"  {k}: {v}")
            continue

        if not user_input:
            continue

        response = agent.chat(user_input)
        print(f"\nStella : {response}\n")