"""Contains the job definitions"""

import asyncio
import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from twikit import Client
from web3 import Web3

from packages.dvilela.customs.token_discovery.constants import (
    ERC20_ABI,
    UNISWAP_FACTORY_ABI,
    UNISWAP_POOL_ABI,
    UNISWAP_V2_FACTORY,
)

BLOCK_RANGE = 1000
LIQUIDITY_THRESHOLD = 1000

BASE_TOKEN_ADDRESES_BASE = {
    "WETH": "0x4200000000000000000000000000000000000006",
    "USDC": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
    "USDT": "0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2",
}

twikit_client = Client(language="en-US")


def tweet_to_json(tweet: Any, user_id: Optional[str] = None) -> Dict:
    """Tweet to json"""
    return {
        "id": tweet.id,
        "user_name": tweet.user.name,
        "user_id": user_id or tweet.user.id,
        "text": tweet.text,
        "created_at": tweet.created_at,
        "view_count": tweet.view_count,
        "favorite_count": tweet.favorite_count,
        "retweet_count": tweet.retweet_count,
        "quote_count": tweet.quote_count,
        "view_count_state": tweet.view_count_state,
    }


def get_eth_price():
    """Get the current price of Ethereum"""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    response = requests.get(url)
    return response.json()["ethereum"]["usd"]


def find_token_age(web3, contract_address) -> Optional[int]:
    """Find the time when a contract was created"""

    creation_block = None

    # Search in the latest 5k blocks
    end_block = web3.eth.block_number
    start_block = end_block - BLOCK_RANGE

    while start_block <= end_block:
        mid = (start_block + end_block) // 2
        code = web3.eth.get_code(contract_address, block_identifier=mid)

        # The contract was not created yet
        if code == b"" or code.hex() == "0x":
            start_block = mid + 1
        else:
            # The contract was created here or before
            creation_block = mid
            end_block = mid - 1

    if not creation_block:
        return None

    creation_timestamp = web3.eth.get_block(creation_block)["timestamp"]
    token_age_hours = (datetime.now().timestamp() - creation_timestamp) / 3600
    return token_age_hours


def get_token_info(web3, token_address) -> Optional[Dict[str, Any]]:
    """Get token information"""
    try:
        contract = web3.eth.contract(address=token_address, abi=ERC20_ABI)
        return {
            "address": token_address,
            "symbol": contract.functions.symbol().call(),
            "decimals": contract.functions.decimals().call(),
        }
    except Exception:
        return None


def analyze_liquidity(
    web3, pool_address, token_0_info, token_1_info
) -> Optional[float]:
    """Analyze liquidity of a pool"""
    pool_contract = web3.eth.contract(address=pool_address, abi=UNISWAP_POOL_ABI)

    base_token_address = (
        token_0_info["address"]
        if token_0_info["address"] in BASE_TOKEN_ADDRESES_BASE.values()
        else token_1_info["address"]
    )
    base_is_weth = base_token_address == BASE_TOKEN_ADDRESES_BASE["WETH"]

    try:
        reserves = pool_contract.functions.getReserves().call()
        reserve0 = reserves[0] / (10 ** token_0_info["decimals"])

        if base_is_weth:
            eth_price = get_eth_price()
            liquidity = (reserve0 * eth_price) * 2  # Total liquidity in USD
        else:
            liquidity = reserve0 * 2  # Asumes the stablecoin is worth 1 USD

        return liquidity

    except Exception:
        return 0


def find_new_tokens(web3) -> List[Dict[str, Any]]:
    """Analyze newly deployed pools and find new tokens"""
    factory = web3.eth.contract(address=UNISWAP_V2_FACTORY, abi=UNISWAP_FACTORY_ABI)
    latest_block = web3.eth.block_number
    pool_created_logs = factory.events.PairCreated.get_logs(
        from_block=web3.eth.block_number - BLOCK_RANGE, to_block=latest_block
    )
    print(f"Found {len(pool_created_logs)} new pools in the last {BLOCK_RANGE} blocks")

    if not pool_created_logs:
        return None

    BASE_ADDRESSES = list(BASE_TOKEN_ADDRESES_BASE.values())

    new_tokens = []

    for log in pool_created_logs:
        token0_address = log.args.token0
        token1_address = log.args.token1
        pool_address = log.args.pair

        token_0_info = get_token_info(web3, token0_address)
        token_1_info = get_token_info(web3, token1_address)

        # Ignore tokens with missing information
        if not token_0_info or not token_1_info:
            print(f"Token info not found for {token0_address} or {token1_address}")
            continue

        liquidity = analyze_liquidity(web3, pool_address, token_0_info, token_1_info)

        # Ignore tokens with low liquidity
        if liquidity < LIQUIDITY_THRESHOLD:
            print(
                f"Ignoring pool with low liquidity [{token_0_info['symbol']}/{token_1_info['symbol']}]: ${liquidity}"
            )
            continue

        # Check if the token is paired with a base token and is less than 24 hours old
        if token_0_info["address"] in BASE_ADDRESSES:
            if find_token_age(web3, token_1_info["address"]) < 24:
                new_tokens.append(token_1_info | {"liquidity": liquidity})

        if token_1_info["address"] in BASE_ADDRESSES:
            if find_token_age(web3, token_0_info["address"]) < 24:
                new_tokens.append(token_0_info | {"liquidity": liquidity})

    print(f"Found {len(new_tokens)} new tokens with enough liquidity")
    return new_tokens


async def get_tweets(token_name) -> Optional[List]:
    """Get recent tweets about a token"""
    token_name = token_name if token_name.startswith("$") else f"${token_name}"
    try:
        tweets = await twikit_client.search_tweet(
            f"{token_name} -is:retweet", product="Top", count=100
        )
        return [tweet_to_json(t) for t in tweets]
    except Exception:
        return None


async def is_popular(token) -> Optional[bool]:
    """
    Check if a token is popular based on the number of likes, retweets and quotes
    """
    tweets = await get_tweets(token["symbol"])

    if tweets is None:
        return None

    total_tweets = len(tweets)
    total_likes = sum(tweet["favorite_count"] for tweet in tweets)
    total_retweets = sum(tweet["retweet_count"] for tweet in tweets)
    total_quotes = sum(tweet["quote_count"] for tweet in tweets)

    return (
        total_tweets > 100
        or total_likes > 1000
        or total_retweets > 1000
        or total_quotes > 100
    )


async def twikit_login(twitter_credentials):
    """Login into Twitter"""

    with tempfile.TemporaryDirectory() as temp_dir:
        cookies = json.loads(twitter_credentials["twitter_cookies"])
        cookies_path = Path(temp_dir) / "twikit_cookies.json"
        with open(cookies_path, "w", encoding="utf-8") as f:
            json.dump(cookies, f)

        await twikit_client.login(
            auth_info_1=twitter_credentials["twitter_email"],
            auth_info_2=twitter_credentials["twitter_user"],
            password=twitter_credentials["twitter_password"],
            cookies_file=str(cookies_path),
        )


def error_response(msg: str) -> Tuple[str, None, None, None]:
    """Return an error mech response."""
    return msg, None, None, None


def run(**kwargs) -> Tuple[Optional[str], Optional[Dict[str, Any]], Any, Any]:
    """Run the task"""

    # RPC
    RPC = kwargs.get("api_keys", {}).get("RPCS", {}).get("base", None)
    if not RPC:
        return error_response("RPC was not provided")

    # Twitter credentials
    twitter_credentials = kwargs.get("api_keys", {}).get("twitter", None)

    # Get tokens
    web3 = Web3(Web3.HTTPProvider(RPC))
    new_tokens = find_new_tokens(web3)

    # Check popularity on Twitter
    if new_tokens and twitter_credentials:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(twikit_login(twitter_credentials))

        for token in new_tokens:
            token["is_popular"] = loop.run_until_complete(is_popular(token))

    return new_tokens, None, None, None
