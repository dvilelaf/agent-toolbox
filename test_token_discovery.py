import json
import os

from dotenv import load_dotenv

from packages.dvilela.customs.token_discovery.token_discovery import run

load_dotenv(override=True)

new_tokens, _, _, _ = run(
    api_keys={
        "RPCS": {"base": os.getenv("RPC_BASE")},
        "twitter": {
            "twitter_email": os.getenv("TWITTER_EMAIL"),
            "twitter_user": os.getenv("TWITTER_USER"),
            "twitter_password": os.getenv("TWITTER_PASSWORD"),
            "twitter_cookies": os.getenv("TWITTER_COOKIES"),
        },
    }
)

print(json.dumps(new_tokens, indent=4))
