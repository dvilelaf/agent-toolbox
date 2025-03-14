import os

from dotenv import load_dotenv

from packages.dvilela.customs.orchestrator_tool.orchestrator_tool import (
    run,
)

load_dotenv(override=True)

GOAL = """
"Find interesting new tokens, evaluate them and decide whether to invest in them or not (and how much).
The goal is to have a python dict where the keys are token addresses (if any) and the values the amount to invest.
"""

response, _, _, _ = run(
    api_keys={
        "gemini": os.getenv("GEMINI_API_KEY"),
    },
    goal=GOAL,
)

print(response)
