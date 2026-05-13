"""
stella.py
Moteur principal de l'agent Stella.

Gère :
- la boucle conversationnelle Claude → tool use → exécution → réponse finale ;
- les métriques tokens/coûts ;
- la latence LLM ;
- le tracing des tools ;
- les logs de session pour évaluation et observabilité.
"""

import json
import os
import time
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
import anthropic

from prompts import build_system_prompt
from tools import TOOLS_DEFINITION, execute_tool


# ──────────────────────────────────────────────
# ENV
# ──────────────────────────────────────────────

load_dotenv()


# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────

MODEL = "claude-sonnet-4-5"
MAX_TOKENS = 1024
MAX_TOOL_ITERATIONS = 5

USD_TO_EUR = 0.92

# Tarifs Claude Sonnet utilisés pour estimation.
# À mettre à jour si les prix changent.
PRICE_INPUT_PER_MILLION = 3.0
PRICE_OUTPUT_PER_MILLION = 15.0


# ──────────────────────────────────────────────
# PATHS
# ──────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")


# ──────────────────────────────────────────────
# CHARGEMENT DONNÉES
# ──────────────────────────────────────────────

def _load_json(filename: str) -> dict | list:
    """Charge un fichier JSON depuis le dossier data/."""
    filepath = os.path.join(DATA_DIR, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Fichier introuvable : {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_user_profile(user_id: str) -> tuple[dict, dict]:
    """
    Charge le profil utilisatrice et son véhicule.

    Args:
        user_id: identifiant technique, par exemple U001.

    Returns:
        tuple(user, vehicle)
    """
    users = _load_json("users.json")
    vehicles = _load_json("vehicles.json")

    user = next((u for u in users["users"] if u["user_id"] == user_id), None)
    vehicle = next((v for v in vehicles["vehicles"] if v["user_id"] == user_id), None)

    if not user:
        raise ValueError(f"Utilisateur introuvable pour user_id={user_id}")

    if not vehicle:
        raise ValueError(f"Véhicule introuvable pour user_id={user_id}")

    return user, vehicle


# ──────────────────────────────────────────────
# SÉRIALISATION POUR LOGS
# ──────────────────────────────────────────────

def _safe_serialize(obj: Any) -> Any:
    """
    Rend les objets Anthropic sérialisables en JSON.
    Les blocs de messages Claude ne sont pas toujours des dicts natifs.
    """
    if obj is None:
        return None

    if isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, list):
        return [_safe_serialize(x) for x in obj]

    if isinstance(obj, dict):
        return {str(k): _safe_serialize(v) for k, v in obj.items()}

    # Objets Anthropic/Pydantic
    if hasattr(obj, "model_dump"):
        return _safe_serialize(obj.model_dump())

    if hasattr(obj, "__dict__"):
        return _safe_serialize(obj.__dict__)

    return str(obj)


# ──────────────────────────────────────────────
# CLASSE PRINCIPALE
# ──────────────────────────────────────────────

class StellaAgent:
    """
    Agent conversationnel Stella.

    Responsabilités :
    - maintenir l'historique de conversation ;
    - appeler Claude ;
    - exécuter les tools demandés ;
    - mesurer coûts, latences, erreurs ;
    - sauvegarder les logs de session.
    """

    def __init__(self, user_id: str, enable_logging: bool = True, verbose: bool = True):
        """
        Initialise l'agent pour une utilisatrice.

        Args:
            user_id: identifiant technique, par exemple U001.
            enable_logging: active/désactive les logs JSON.
            verbose: affiche les traces dans le terminal.
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY manquante. Vérifie ton fichier .env."
            )

        self.client = anthropic.Anthropic(api_key=api_key)

        self.user_id = user_id
        self.user, self.vehicle = load_user_profile(user_id)
        self.system_prompt = build_system_prompt(self.user, self.vehicle)

        self.conversation_history: list[dict] = []

        self.enable_logging = enable_logging
        self.verbose = verbose

        self.session_id = (
            f"{self.user_id}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        self.metrics = {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_tool_calls": 0,
            "total_turns": 0,
            "session_start": time.time(),

            # Observability
            "llm_latencies": [],
            "tool_history": [],
            "errors": [],
            "turn_history": [],
        }

        if self.verbose:
            print(f"[STELLA] Agent initialisé pour {self.user['prenom']} ({user_id})")

    # ──────────────────────────────────────────
    # MÉTHODE PRINCIPALE
    # ──────────────────────────────────────────

    def chat(self, user_message: str) -> str:
        """
        Traite un message utilisatrice.

        Args:
            user_message: message texte.

        Returns:
            Réponse finale de Stella.
        """
        if not user_message or not user_message.strip():
            return "Je n'ai pas reçu de message. Peux-tu reformuler ?"

        turn_start = time.time()

        self.conversation_history.append({
            "role": "user",
            "content": user_message.strip()
        })

        self.metrics["total_turns"] += 1

        turn_trace = {
            "turn": self.metrics["total_turns"],
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message.strip(),
            "tools_called": [],
            "llm_calls": [],
            "final_response": None,
            "success": False,
            "latency_sec": None,
        }

        iterations = 0

        try:
            while iterations < MAX_TOOL_ITERATIONS:
                iterations += 1

                llm_start = time.time()

                response = self.client.messages.create(
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                    system=self.system_prompt,
                    tools=TOOLS_DEFINITION,
                    messages=self.conversation_history
                )

                llm_latency = round(time.time() - llm_start, 3)
                self.metrics["llm_latencies"].append(llm_latency)

                input_tokens = getattr(response.usage, "input_tokens", 0)
                output_tokens = getattr(response.usage, "output_tokens", 0)

                self.metrics["total_input_tokens"] += input_tokens
                self.metrics["total_output_tokens"] += output_tokens

                turn_trace["llm_calls"].append({
                    "iteration": iterations,
                    "stop_reason": response.stop_reason,
                    "latency_sec": llm_latency,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                })

                # CAS 1 — Réponse finale
                if response.stop_reason == "end_turn":
                    final_response = self._extract_text(response)

                    self.conversation_history.append({
                        "role": "assistant",
                        "content": response.content
                    })

                    turn_trace["final_response"] = final_response
                    turn_trace["success"] = True
                    turn_trace["latency_sec"] = round(time.time() - turn_start, 3)

                    self.metrics["turn_history"].append(turn_trace)

                    if self.enable_logging:
                        self._save_session_log()

                    return final_response

                # CAS 2 — Tool use
                if response.stop_reason == "tool_use":
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": response.content
                    })

                    tool_results = []

                    for block in response.content:
                        if getattr(block, "type", None) != "tool_use":
                            continue

                        self.metrics["total_tool_calls"] += 1

                        tool_name = block.name
                        tool_input = block.input

                        if self.verbose:
                            print(f"[TOOL] {tool_name}({tool_input})")

                        tool_start = time.time()

                        tool_trace = {
                            "turn": self.metrics["total_turns"],
                            "iteration": iterations,
                            "tool": tool_name,
                            "input": tool_input,
                            "success": False,
                            "latency_sec": None,
                            "error": None,
                        }

                        try:
                            result = execute_tool(tool_name, tool_input)
                            tool_latency = round(time.time() - tool_start, 3)

                            tool_trace["success"] = True
                            tool_trace["latency_sec"] = tool_latency

                        except Exception as e:
                            result = {"error": str(e)}
                            tool_latency = round(time.time() - tool_start, 3)

                            tool_trace["success"] = False
                            tool_trace["latency_sec"] = tool_latency
                            tool_trace["error"] = str(e)

                            self.metrics["errors"].append({
                                "timestamp": datetime.now().isoformat(),
                                "type": "tool_error",
                                "tool": tool_name,
                                "error": str(e),
                            })

                        self.metrics["tool_history"].append(tool_trace)
                        turn_trace["tools_called"].append(tool_trace)

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, ensure_ascii=False, indent=2)
                        })

                    self.conversation_history.append({
                        "role": "user",
                        "content": tool_results
                    })

                    continue

                # CAS 3 — Stop reason inattendu
                error_msg = f"Stop reason inattendu : {response.stop_reason}"
                self.metrics["errors"].append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "unexpected_stop_reason",
                    "error": error_msg,
                })

                turn_trace["final_response"] = (
                    "Je rencontre une difficulté technique. "
                    "Un conseiller Stellantis peut t'aider directement."
                )
                turn_trace["success"] = False
                turn_trace["latency_sec"] = round(time.time() - turn_start, 3)
                self.metrics["turn_history"].append(turn_trace)

                if self.enable_logging:
                    self._save_session_log()

                return turn_trace["final_response"]

            # Trop d'itérations tools
            fallback = (
                "Je préfère te connecter à un conseiller Stellantis pour éviter "
                "de te donner une réponse incomplète."
            )

            self.metrics["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "type": "max_tool_iterations",
                "error": f"MAX_TOOL_ITERATIONS={MAX_TOOL_ITERATIONS} atteint",
            })

            turn_trace["final_response"] = fallback
            turn_trace["success"] = False
            turn_trace["latency_sec"] = round(time.time() - turn_start, 3)
            self.metrics["turn_history"].append(turn_trace)

            if self.enable_logging:
                self._save_session_log()

            return fallback

        except Exception as e:
            fallback = (
                "Je rencontre une difficulté technique. "
                "Je peux transférer la demande à un conseiller Stellantis."
            )

            self.metrics["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "type": "chat_error",
                "error": str(e),
            })

            turn_trace["final_response"] = fallback
            turn_trace["success"] = False
            turn_trace["latency_sec"] = round(time.time() - turn_start, 3)
            turn_trace["error"] = str(e)
            self.metrics["turn_history"].append(turn_trace)

            if self.enable_logging:
                self._save_session_log()

            if self.verbose:
                print(f"[ERROR] {e}")

            return fallback

    # ──────────────────────────────────────────
    # MÉTRIQUES
    # ──────────────────────────────────────────

    def get_metrics(self) -> dict:
        """
        Retourne les métriques de session.
        Utilisé par Streamlit, l'évaluation et la modélisation des coûts.
        """
        duration = time.time() - self.metrics["session_start"]

        input_tokens = self.metrics["total_input_tokens"]
        output_tokens = self.metrics["total_output_tokens"]

        cost_input = (input_tokens / 1_000_000) * PRICE_INPUT_PER_MILLION
        cost_output = (output_tokens / 1_000_000) * PRICE_OUTPUT_PER_MILLION
        cost_total_usd = cost_input + cost_output

        llm_latencies = self.metrics["llm_latencies"]
        tool_history = self.metrics["tool_history"]

        successful_tools = [t for t in tool_history if t.get("success")]
        failed_tools = [t for t in tool_history if not t.get("success")]

        avg_llm_latency = (
            sum(llm_latencies) / len(llm_latencies)
            if llm_latencies else 0
        )

        tool_latencies = [
            t["latency_sec"]
            for t in tool_history
            if isinstance(t.get("latency_sec"), (int, float))
        ]

        avg_tool_latency = (
            sum(tool_latencies) / len(tool_latencies)
            if tool_latencies else 0
        )

        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "prenom": self.user["prenom"],

            "duree_session_sec": round(duration, 1),
            "nb_tours_conversation": self.metrics["total_turns"],

            "nb_appels_tools": self.metrics["total_tool_calls"],
            "nb_tools_success": len(successful_tools),
            "nb_tools_failed": len(failed_tools),
            "tool_success_rate": round(
                len(successful_tools) / len(tool_history),
                3
            ) if tool_history else 1.0,

            "tokens_input": input_tokens,
            "tokens_output": output_tokens,
            "tokens_total": input_tokens + output_tokens,

            "cout_estime_usd": round(cost_total_usd, 6),
            "cout_estime_eur": round(cost_total_usd * USD_TO_EUR, 6),

            "avg_llm_latency_sec": round(avg_llm_latency, 3),
            "avg_tool_latency_sec": round(avg_tool_latency, 3),
            "nb_erreurs": len(self.metrics["errors"]),

            "tool_history": self.metrics["tool_history"],
            "errors": self.metrics["errors"],
        }

    # ──────────────────────────────────────────
    # UTILITAIRES
    # ──────────────────────────────────────────

    def _extract_text(self, response) -> str:
        """Extrait le texte de la réponse Claude."""
        texts = []

        for block in response.content:
            text = getattr(block, "text", None)
            if text:
                texts.append(text)

        return "\n".join(texts).strip()

    def reset_conversation(self):
        """Réinitialise l'historique de conversation."""
        self.conversation_history = []

        self.metrics["total_turns"] = 0
        self.metrics["total_tool_calls"] = 0
        self.metrics["total_input_tokens"] = 0
        self.metrics["total_output_tokens"] = 0
        self.metrics["llm_latencies"] = []
        self.metrics["tool_history"] = []
        self.metrics["errors"] = []
        self.metrics["turn_history"] = []
        self.metrics["session_start"] = time.time()

        if self.verbose:
            print(f"[STELLA] Conversation réinitialisée pour {self.user['prenom']}")

    def get_conversation_summary(self) -> str:
        """
        Génère un résumé simple de la conversation pour l'escalade humaine.
        """
        if not self.conversation_history:
            return "Aucun échange enregistré."

        messages_texte = []

        for msg in self.conversation_history:
            content = msg.get("content")

            if isinstance(content, str):
                role = "Utilisatrice" if msg.get("role") == "user" else "Stella"
                messages_texte.append(f"{role}: {content[:220]}")

        return " | ".join(messages_texte[-6:])

    def _save_session_log(self):
        """
        Sauvegarde l'état de session dans logs/session_<session_id>.json.
        Utile pour évaluation, debugging, audit et démonstration technique.
        """
        os.makedirs(LOGS_DIR, exist_ok=True)

        filepath = os.path.join(LOGS_DIR, f"session_{self.session_id}.json")

        data = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "model": MODEL,
            "user": {
                "user_id": self.user_id,
                "prenom": self.user.get("prenom"),
                "persona_type": self.user.get("persona_type"),
            },
            "vehicle": {
                "marque": self.vehicle.get("marque"),
                "modele": self.vehicle.get("modele"),
                "motorisation": self.vehicle.get("motorisation"),
            },
            "metrics": self.get_metrics(),
            "conversation_history": _safe_serialize(self.conversation_history),
            "turn_history": _safe_serialize(self.metrics["turn_history"]),
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────
# CLI TEST
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("   STELLA — Agent Mobilité Stellantis")
    print("   Test en ligne de commande")
    print("=" * 50)

    print("\nChoisir un profil de test :")
    print("  1. Camille (U001) — Citroën C3, voyant actif")
    print("  2. Sofia   (U002) — Peugeot e-208, batterie faible")
    print("  3. Inès    (U003) — Jeep Avenger, anniversaire véhicule")

    choix = input("\nProfil [1/2/3] : ").strip()
    user_ids = {"1": "U001", "2": "U002", "3": "U003"}
    user_id = user_ids.get(choix, "U001")

    agent = StellaAgent(user_id=user_id)

    print("\n[Stella est prête. Tape 'quit' pour quitter, 'metrics' pour voir les coûts]\n")

    while True:
        user_input = input("Toi : ").strip()

        if user_input.lower() == "quit":
            print("\n[Métriques finales de session]")
            metrics = agent.get_metrics()
            for k, v in metrics.items():
                if k not in ["tool_history", "errors"]:
                    print(f"  {k}: {v}")
            break

        if user_input.lower() == "metrics":
            metrics = agent.get_metrics()
            for k, v in metrics.items():
                if k not in ["tool_history", "errors"]:
                    print(f"  {k}: {v}")
            continue

        if not user_input:
            continue

        response = agent.chat(user_input)
        print(f"\nStella : {response}\n")