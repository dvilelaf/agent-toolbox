import os

from dotenv import load_dotenv

from packages.dvilela.customs.dynamic_tool.dynamic_tool import run

load_dotenv(override=True)

response, _, _, _ = run(
    api_keys={
        "gemini": os.getenv("GEMINI_API_KEY"),
    },
    prompt="A function that decides to invest in a ERC-20 token or not and returns the amount to be invested",
    address="0xdummy_address",
    symbol="TEST",
    decimals=18,
    liquidity=1000,
    is_popular=True,
    available_balance_usd=100,
)

print(response)
