"""
evaluate_agent.py
Évaluation automatique de Stella.

Usage :
    python evaluation/evaluate_agent.py
"""

import json
import os
import sys
import time
from datetime import datetime
from statistics import mean

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL_DIR = os.path.join(BASE_DIR, "evaluation")
RESULTS_DIR = os.path.join(EVAL_DIR, "results")

os.makedirs(RESULTS_DIR, exist_ok=True)

sys.path.insert(0, os.path.join(BASE_DIR, "agent"))

from stella import StellaAgent


SCENARIOS_PATH = os.path.join(EVAL_DIR, "scenarios.json")


def load_scenarios():
    if not os.path.exists(SCENARIOS_PATH):
        raise FileNotFoundError(f"Fichier introuvable : {SCENARIOS_PATH}")

    with open(SCENARIOS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def keyword_score(response: str, expected_keywords: list[str]) -> dict:
    response_lower = response.lower()

    matched = [
        kw for kw in expected_keywords
        if kw.lower() in response_lower
    ]

    score = len(matched) / len(expected_keywords) if expected_keywords else 1.0

    return {
        "matched_keywords": matched,
        "keyword_score": round(score, 3)
    }


def tool_score(metrics: dict, expected_tools: list[str]) -> dict:
    tool_history = metrics.get("tool_history", [])
    used_tools = [t.get("tool") for t in tool_history]

    matched = [
        tool for tool in expected_tools
        if tool in used_tools
    ]

    if not expected_tools:
        score = 1.0
    else:
        score = len(matched) / len(expected_tools)

    return {
        "used_tools": used_tools,
        "matched_tools": matched,
        "tool_score": round(score, 3)
    }


def evaluate_scenario(scenario: dict) -> dict:
    scenario_id = scenario["scenario_id"]
    user_id = scenario["user_id"]
    message = scenario["message"]

    expected_keywords = scenario.get("expected_keywords", [])
    expected_tools = scenario.get("expected_tools", [])

    print(f"\n▶️  Scenario : {scenario_id}")
    print(f"    User     : {user_id}")
    print(f"    Message  : {message}")

    agent = StellaAgent(
        user_id=user_id,
        enable_logging=True,
        verbose=False
    )

    start = time.time()

    try:
        response = agent.chat(message)
        latency = round(time.time() - start, 3)
        metrics = agent.get_metrics()

        kw_eval = keyword_score(response, expected_keywords)
        tool_eval = tool_score(metrics, expected_tools)

        global_score = round(
            0.55 * kw_eval["keyword_score"] +
            0.45 * tool_eval["tool_score"],
            3
        )

        success = (
            global_score >= 0.6
            and metrics.get("nb_erreurs", 0) == 0
        )

        result = {
            "scenario_id": scenario_id,
            "persona": scenario.get("persona"),
            "user_id": user_id,
            "message": message,
            "response": response,

            "expected_keywords": expected_keywords,
            "matched_keywords": kw_eval["matched_keywords"],
            "keyword_score": kw_eval["keyword_score"],

            "expected_tools": expected_tools,
            "used_tools": tool_eval["used_tools"],
            "matched_tools": tool_eval["matched_tools"],
            "tool_score": tool_eval["tool_score"],

            "global_score": global_score,
            "success": success,
            "latency_sec": latency,

            "metrics": {
                "tokens_total": metrics.get("tokens_total", 0),
                "tokens_input": metrics.get("tokens_input", 0),
                "tokens_output": metrics.get("tokens_output", 0),
                "cout_estime_eur": metrics.get("cout_estime_eur", 0),
                "nb_appels_tools": metrics.get("nb_appels_tools", 0),
                "tool_success_rate": metrics.get("tool_success_rate", 1.0),
                "avg_llm_latency_sec": metrics.get("avg_llm_latency_sec", 0),
                "avg_tool_latency_sec": metrics.get("avg_tool_latency_sec", 0),
                "nb_erreurs": metrics.get("nb_erreurs", 0)
            },

            "errors": metrics.get("errors", [])
        }

        print(f"    ✅ Score global : {global_score}")
        print(f"    🛠 Tools utilisés : {tool_eval['used_tools']}")
        print(f"    ⏱ Latence : {latency}s")
        print(f"    💶 Coût estimé : {metrics.get('cout_estime_eur', 0)} €")

        return result

    except Exception as e:
        print(f"    ❌ Erreur : {e}")

        return {
            "scenario_id": scenario_id,
            "persona": scenario.get("persona"),
            "user_id": user_id,
            "message": message,
            "response": None,
            "success": False,
            "global_score": 0,
            "latency_sec": None,
            "error": str(e)
        }


def summarize_results(results: list[dict]) -> dict:
    valid = [r for r in results if r.get("response") is not None]

    if not valid:
        return {
            "nb_scenarios": len(results),
            "success_rate": 0,
            "avg_score": 0,
            "avg_latency_sec": 0,
            "avg_cost_eur": 0,
            "avg_tokens": 0,
            "avg_tool_calls": 0,
            "total_errors": len(results)
        }

    return {
        "nb_scenarios": len(results),
        "nb_success": sum(1 for r in results if r.get("success")),
        "success_rate": round(
            sum(1 for r in results if r.get("success")) / len(results),
            3
        ),
        "avg_score": round(mean(r.get("global_score", 0) for r in valid), 3),
        "avg_latency_sec": round(mean(r.get("latency_sec", 0) for r in valid), 3),
        "avg_cost_eur": round(mean(r["metrics"]["cout_estime_eur"] for r in valid), 6),
        "avg_tokens": round(mean(r["metrics"]["tokens_total"] for r in valid), 1),
        "avg_tool_calls": round(mean(r["metrics"]["nb_appels_tools"] for r in valid), 2),
        "avg_tool_success_rate": round(mean(r["metrics"]["tool_success_rate"] for r in valid), 3),
        "total_errors": sum(r["metrics"].get("nb_erreurs", 0) for r in valid)
    }


def main():
    print("\n" + "=" * 60)
    print(" STELLA — ÉVALUATION AUTOMATIQUE")
    print("=" * 60)

    scenarios = load_scenarios()
    results = []

    for scenario in scenarios:
        result = evaluate_scenario(scenario)
        results.append(result)

    summary = summarize_results(results)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output = {
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "results": results
    }

    output_json = os.path.join(RESULTS_DIR, f"evaluation_results_{timestamp}.json")

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(" RÉSUMÉ FINAL")
    print("=" * 60)
    for k, v in summary.items():
        print(f"{k}: {v}")

    print("\nRésultats sauvegardés dans :")
    print(output_json)


if __name__ == "__main__":
    main()