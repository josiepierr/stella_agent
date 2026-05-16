"""
stella.py
Moteur principal de l'agent Stella.

Gère :
- la boucle conversationnelle Claude → tool use → exécution → réponse finale ;
- les métriques tokens/coûts ;
- la latence LLM ;
- le tracing des tools ;
- les logs de session pour évaluation et observabilité ;
- le changement de conducteur actif depuis Streamlit.
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

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
MAX_TOKENS = int(os.getenv("STELLA_MAX_TOKENS", "1024"))
MAX_TOOL_ITERATIONS = int(os.getenv("STELLA_MAX_TOOL_ITERATIONS", "5"))

USD_TO_EUR = float(os.getenv("USD_TO_EUR", "0.92"))

# Estimation indicative des coûts.
PRICE_INPUT_PER_MILLION = float(os.getenv("PRICE_INPUT_PER_MILLION", "3.0"))
PRICE_OUTPUT_PER_MILLION = float(os.getenv("PRICE_OUTPUT_PER_MILLION", "15.0"))


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
    """Charge le profil utilisatrice et son véhicule."""
    users = _load_json("users.json")
    vehicles = _load_json("vehicles.json")

    user = next((u for u in users.get("users", []) if u.get("user_id") == user_id), None)
    vehicle = next((v for v in vehicles.get("vehicles", []) if v.get("user_id") == user_id), None)

    if not user:
        raise ValueError(f"Utilisateur introuvable pour user_id={user_id}")

    if not vehicle:
        raise ValueError(f"Véhicule introuvable pour user_id={user_id}")

    return user, vehicle


# ──────────────────────────────────────────────
# SÉRIALISATION POUR LOGS
# ──────────────────────────────────────────────

def _safe_serialize(obj: Any) -> Any:
    """Rend les objets Anthropic sérialisables en JSON."""
    if obj is None:
        return None

    if isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, list):
        return [_safe_serialize(x) for x in obj]

    if isinstance(obj, dict):
        return {str(k): _safe_serialize(v) for k, v in obj.items()}

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

    def __init__(
        self,
        user_id: str,
        enable_logging: bool = True,
        verbose: bool = True,
        conducteur_actif: dict | None = None,
    ):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY manquante. Vérifie ton fichier .env.")

        self.client = anthropic.Anthropic(api_key=api_key)

        self.user_id = user_id
        self.user, self.vehicle = load_user_profile(user_id)
        self.conducteur_actif = conducteur_actif
        self.voice_mode = False
        self.system_prompt = self._build_prompt()

        self.conversation_history: list[dict] = []
        self.enable_logging = enable_logging
        self.verbose = verbose

        self.session_id = f"{self.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self._init_metrics()

        if self.verbose:
            print(f"[STELLA] Agent initialisé pour {self.user.get('prenom', self.user_id)} ({user_id})")

    # ──────────────────────────────────────────
    # INITIALISATION MÉTRIQUES
    # ──────────────────────────────────────────

    def _init_metrics(self) -> None:
        self.metrics = {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_tool_calls": 0,
            "total_turns": 0,
            "session_start": time.time(),
            "llm_latencies": [],
            "tool_history": [],
            "errors": [],
            "turn_history": [],
        }

    def _build_prompt(self) -> str:
        """
        Reconstruit le system prompt avec compatibilité descendante :
        - ancienne signature : build_system_prompt(user, vehicle, conducteur_actif)
        - nouvelle signature : build_system_prompt(..., voice_mode=...)
        """
        try:
            return build_system_prompt(
                self.user,
                self.vehicle,
                conducteur_actif=self.conducteur_actif,
                voice_mode=self.voice_mode,
            )
        except TypeError:
            return build_system_prompt(self.user, self.vehicle, self.conducteur_actif)

    def set_voice_mode(self, enabled: bool) -> None:
        """Informe l'agent que l'interface est en mode vocal ou texte."""
        self.voice_mode = bool(enabled)
        self.system_prompt = self._build_prompt()

    # ──────────────────────────────────────────
    # MÉTHODE PRINCIPALE
    # ──────────────────────────────────────────

    def chat(self, user_message: str) -> str:
        """Traite un message utilisatrice et retourne la réponse finale de Stella."""
        if not user_message or not user_message.strip():
            return "Je n'ai pas reçu de message. Peux-tu reformuler ?"

        turn_start = time.time()
        clean_user_message = user_message.strip()

        self.conversation_history.append({
            "role": "user",
            "content": clean_user_message,
        })

        self.metrics["total_turns"] += 1

        turn_trace = {
            "turn": self.metrics["total_turns"],
            "timestamp": datetime.now().isoformat(),
            "user_message": clean_user_message,
            "tools_called": [],
            "llm_calls": [],
            "final_response": None,
            "success": False,
            "latency_sec": None,
        }

        try:
            for iteration in range(1, MAX_TOOL_ITERATIONS + 1):
                response = self._call_llm(iteration, turn_trace)

                if response.stop_reason == "end_turn":
                    final_response = self._extract_text(response)
                    return self._finalize_turn(response, final_response, turn_trace, turn_start, success=True)

                if response.stop_reason == "tool_use":
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": response.content,
                    })

                    tool_results = self._execute_requested_tools(response, iteration, turn_trace)

                    self.conversation_history.append({
                        "role": "user",
                        "content": tool_results,
                    })
                    continue

                error_msg = f"Stop reason inattendu : {response.stop_reason}"
                self._record_error("unexpected_stop_reason", error_msg)
                fallback = "Je rencontre une difficulté technique. Un conseiller Stellantis peut t'aider directement."
                return self._finalize_turn(None, fallback, turn_trace, turn_start, success=False)

            self._record_error("max_tool_iterations", f"MAX_TOOL_ITERATIONS={MAX_TOOL_ITERATIONS} atteint")
            fallback = "Je préfère te connecter à un conseiller Stellantis pour éviter de te donner une réponse incomplète."
            return self._finalize_turn(None, fallback, turn_trace, turn_start, success=False)

        except Exception as e:
            self._record_error("chat_error", str(e))

            if self.verbose:
                print(f"[ERROR] {e}")

            fallback = "Je rencontre une difficulté technique. Je peux transférer la demande à un conseiller Stellantis."
            turn_trace["error"] = str(e)
            return self._finalize_turn(None, fallback, turn_trace, turn_start, success=False)

    def _call_llm(self, iteration: int, turn_trace: dict):
        llm_start = time.time()

        response = self.client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=self.system_prompt,
            tools=TOOLS_DEFINITION,
            messages=self.conversation_history,
        )

        llm_latency = round(time.time() - llm_start, 3)
        self.metrics["llm_latencies"].append(llm_latency)

        input_tokens = getattr(response.usage, "input_tokens", 0)
        output_tokens = getattr(response.usage, "output_tokens", 0)

        self.metrics["total_input_tokens"] += input_tokens
        self.metrics["total_output_tokens"] += output_tokens

        turn_trace["llm_calls"].append({
            "iteration": iteration,
            "stop_reason": response.stop_reason,
            "latency_sec": llm_latency,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        })

        return response

    def _execute_requested_tools(self, response, iteration: int, turn_trace: dict) -> list[dict]:
        tool_results = []

        for block in response.content:
            if getattr(block, "type", None) != "tool_use":
                continue

            self.metrics["total_tool_calls"] += 1

            tool_name = block.name
            tool_input = dict(block.input or {})

            if self.verbose:
                print(f"[TOOL] {tool_name}({tool_input})")

            tool_start = time.time()
            tool_trace = {
                "turn": self.metrics["total_turns"],
                "iteration": iteration,
                "tool": tool_name,
                "input": tool_input,
                "success": False,
                "latency_sec": None,
                "error": None,
            }

            try:
                result = execute_tool(tool_name, tool_input)
                tool_trace["success"] = not (isinstance(result, dict) and result.get("error"))
                if not tool_trace["success"]:
                    tool_trace["error"] = result.get("error")
                    self._record_error("tool_error", result.get("error", "Erreur tool"), tool=tool_name)

            except Exception as e:
                result = {"error": str(e)}
                tool_trace["success"] = False
                tool_trace["error"] = str(e)
                self._record_error("tool_exception", str(e), tool=tool_name)

            tool_trace["latency_sec"] = round(time.time() - tool_start, 3)
            self.metrics["tool_history"].append(tool_trace)
            turn_trace["tools_called"].append(tool_trace)

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result, ensure_ascii=False, indent=2),
            })

        return tool_results

    def _finalize_turn(self, response, final_response: str, turn_trace: dict, turn_start: float, success: bool) -> str:
        if response is not None:
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content,
            })
        else:
            self.conversation_history.append({
                "role": "assistant",
                "content": final_response,
            })

        turn_trace["final_response"] = final_response
        turn_trace["success"] = success
        turn_trace["latency_sec"] = round(time.time() - turn_start, 3)
        self.metrics["turn_history"].append(turn_trace)

        if self.enable_logging:
            self._save_session_log()

        return final_response

    # ──────────────────────────────────────────
    # CONDUCTEUR ACTIF
    # ──────────────────────────────────────────

    def set_conducteur(self, conducteur: dict | None, reset_conversation: bool = True) -> None:
        """
        Change le conducteur actif depuis Streamlit.

        Important :
        - reconstruit le system prompt ;
        - réinitialise l'historique si demandé, pour éviter de mélanger deux conducteurs ;
        - ne réinitialise pas les métriques globales sauf nouvelle conversation explicite.
        """
        current_id = self.conducteur_actif.get("conducteur_id") if self.conducteur_actif else None
        new_id = conducteur.get("conducteur_id") if conducteur else None

        if current_id == new_id:
            return

        self.conducteur_actif = conducteur
        self.system_prompt = self._build_prompt()

        if reset_conversation:
            self.conversation_history = []

        if self.verbose:
            nom = conducteur.get("prenom") if conducteur else self.user.get("prenom", "propriétaire")
            print(f"[STELLA] Conducteur actif changé → {nom}")

    # ──────────────────────────────────────────
    # MÉTRIQUES
    # ──────────────────────────────────────────

    def get_metrics(self) -> dict:
        """Retourne les métriques de session."""
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

        avg_llm_latency = sum(llm_latencies) / len(llm_latencies) if llm_latencies else 0

        tool_latencies = [
            t.get("latency_sec")
            for t in tool_history
            if isinstance(t.get("latency_sec"), (int, float))
        ]
        avg_tool_latency = sum(tool_latencies) / len(tool_latencies) if tool_latencies else 0

        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "prenom": self.user.get("prenom"),
            "conducteur_actif": self.conducteur_actif,

            "duree_session_sec": round(duration, 1),
            "nb_tours_conversation": self.metrics["total_turns"],

            "nb_appels_tools": self.metrics["total_tool_calls"],
            "nb_tools_success": len(successful_tools),
            "nb_tools_failed": len(failed_tools),
            "tool_success_rate": round(len(successful_tools) / len(tool_history), 3) if tool_history else 1.0,

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

    def _record_error(self, error_type: str, error: str, tool: str | None = None) -> None:
        payload = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "error": error,
        }
        if tool:
            payload["tool"] = tool
        self.metrics["errors"].append(payload)

    def _extract_text(self, response) -> str:
        """Extrait le texte de la réponse Claude."""
        texts = []

        for block in response.content:
            text = getattr(block, "text", None)
            if text:
                texts.append(text)

        return "\n".join(texts).strip()

    def reset_conversation(self, reset_metrics: bool = True) -> None:
        """Réinitialise l'historique de conversation et, par défaut, les métriques."""
        self.conversation_history = []

        if reset_metrics:
            self._init_metrics()

        if self.verbose:
            print(f"[STELLA] Conversation réinitialisée pour {self.user.get('prenom', self.user_id)}")

    def get_conversation_summary(self) -> str:
        """Génère un résumé simple de la conversation pour l'escalade humaine."""
        if not self.conversation_history:
            return "Aucun échange enregistré."

        messages_texte = []

        for msg in self.conversation_history:
            content = msg.get("content")

            if isinstance(content, str):
                role = "Utilisatrice" if msg.get("role") == "user" else "Stella"
                messages_texte.append(f"{role}: {content[:220]}")

        return " | ".join(messages_texte[-6:])

    def _save_session_log(self) -> None:
        """Sauvegarde l'état de session dans logs/session_<session_id>.json."""
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
            "conducteur_actif": _safe_serialize(self.conducteur_actif),
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
