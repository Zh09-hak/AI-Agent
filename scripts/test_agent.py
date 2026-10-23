import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.agent.orchestrator import run_agent


def show(title: str, task: str) -> None:
    print("\n" + "█" * 70)
    print(f"TASK: {title}")
    print(f"INPUT: {task}")
    print("█" * 70)

    result = run_agent(task, max_steps=4)

    print("\n" + "─" * 70)
    print(f"TOOL CALLS: {result['steps']} | TRUNCATED: {result['truncated']}")
    print("─" * 70)
    for t in result["trace"]:
        status = "ERROR" if t["error"] else "ok"
        print(f"  step {t['step']}: {t['tool']}({t['arguments']}) → {status}")

    print("\n" + "─" * 70)
    print("FINAL ANSWER:")
    print("─" * 70)
    print(result["answer"] or "(empty)")


if __name__ == "__main__":
    show("Document listing", "What documents do we have in the knowledge base?")

    show("Factual question", "What is pruning in decision trees?")

    show(
        "Compare documents",
        "Compare the Top 100 Machine Learning Interview Questions and ML_book documents. "
        "Focus on how they explain regularization.",
    )