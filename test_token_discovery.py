import json
import os

from dotenv import load_dotenv

from packages.dvilela.customs.token_discovery_tool.token_discovery_tool import run

load_dotenv(override=True)

new_tokens, _, _, _ = run(
    api_keys={
        "RPCS": {"base": os.getenv("RPC_BASE")},
        "twitter": json.loads(os.getenv("TWITTER_CREDENTIALS")),
    },
    block_range=200,
    liquidity_threshold=100,
    deployment_threshold=24 * 7,
)

print(json.dumps(new_tokens, indent=4))
