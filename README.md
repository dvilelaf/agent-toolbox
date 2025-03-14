# Eolas x Algo: Agent Skills Hackathon

A collection of agent tools.

## Requirements
* Python >= 3.10
* [UV](https://github.com/astral-sh/uv)

## Token discovery tool

A tool to discover newly created tokens.

```bash
uv run python test_token_discovery.py
```

```bash
uv run python test_token_discovery.py

Found 7 new pools in the last 200 blocks
Pool [WETH/CAT] has enough liquidity (10581.579828148 >= 100)
Pool [WETH/ewon] has enough liquidity (480.26120016 >= 100)
Pool [WETH/GOONERS] has enough liquidity (8443.358461399119 >= 100)
Pool [WETH/APEX] has enough liquidity (476.318920224 >= 100)
Pool [TEST/WETH] has enough liquidity (367346000000.0 >= 100)
Token TEST was deployed more than 168 hours ago. Ignoring.
Ignoring pool with low liquidity [YZY/WETH]: $0
Ignoring pool with low liquidity [WETH/ACCORDS]: $0
Found 4 new tokens with enough liquidity
Checking popularity on Twitter
Logged into Twitter
Is CAT popular? True
Is ewon popular? False
Is GOONERS popular? False
Is APEX popular? True
[
    {
        "address": "0x919010e4b0083A039842bB369dEF7888EeF15E40",
        "symbol": "CAT",
        "decimals": 15,
        "liquidity": 10581.579828148,
        "is_popular": true
    },
    {
        "address": "0x90ED158Ef26397f8d00f6Cd359Ef0FD1C2F9dc08",
        "symbol": "ewon",
        "decimals": 18,
        "liquidity": 480.26120016,
        "is_popular": false
    },
    {
        "address": "0x805eeECB42034d1a864C88520ceB1b7B8176899B",
        "symbol": "GOONERS",
        "decimals": 15,
        "liquidity": 8443.358461399119,
        "is_popular": false
    },
    {
        "address": "0x7D8741EbCBD987d7851a473d5b17F639C9156A36",
        "symbol": "APEX",
        "decimals": 18,
        "liquidity": 476.318920224,
        "is_popular": true
    }
]

```

## Dynamic tool

```bash
uv run python test_dynamic_tool.py
```

```bash
uv run python test_dynamic_tool.py

--------------------------------------------
Evaluating the following function:
def dynamic_function(address, symbol, decimals, liquidity, is_popular, available_balance_usd):
    """
    Decides whether to invest in an ERC-20 token and returns the amount to invest.

    Args:
        address (str): The ERC-20 token address.
        symbol (str): The ERC-20 token symbol.
        decimals (int): The number of decimals the token uses.
        liquidity (float): The liquidity of the token in USD.
        is_popular (bool): A flag indicating if the token is popular.
        available_balance_usd (float): The available balance in USD for investment.

    Returns:
        float: The amount to invest in USD, or 0.0 if no investment is recommended.
    """

    if liquidity < 1000:
        return 0.0  # Not enough liquidity to consider investing

    if not is_popular and liquidity < 5000:
        return 0.0 # not popular and low liquidity, skip investment

    if available_balance_usd < 10:
        return 0.0 # Don't invest if low balance

    if is_popular:
        investment_percentage = 0.05  # Invest 5% if popular
    else:
        investment_percentage = 0.02  # Invest 2% if not so popular

    investment_amount = available_balance_usd * investment_percentage

    #Limit the investment amount to 10% of the liquidity
    investment_amount = min(investment_amount, liquidity * 0.1)


    return investment_amount

kwargs = {'address': '0xdummy_address', 'symbol': 'TEST', 'decimals': 18, 'liquidity': 1000, 'is_popular': True, 'available_balance_usd': 100}
Result = 5.0
--------------------------------------------
5.0
```

## Orchestrator tool

```bash
uv run python test_orchestrator_tool.py
```

```bash
uv run python test_orchestrator_tool.py

Calling discover_tokens_tool({'deployment_threshold': 168.0, 'liquidity_threshold': 100.0, 'block_range': 200.0})
Found 7 new pools in the last 200 blocks
Pool [WETH/CAT] has enough liquidity (10580.9777935038 >= 100)
Pool [WETH/ewon] has enough liquidity (480.233875896 >= 100)
Pool [WETH/GOONERS] has enough liquidity (8442.87807998257 >= 100)
Pool [WETH/APEX] has enough liquidity (476.2918202544 >= 100)
Pool [TEST/WETH] has enough liquidity (367325100000.0 >= 100)
Token TEST was deployed more than 168 hours ago. Ignoring.
Ignoring pool with low liquidity [YZY/WETH]: $0
Ignoring pool with low liquidity [WETH/ACCORDS]: $0
Found 4 new tokens with enough liquidity
Result: [{'address': '0x919010e4b0083A039842bB369dEF7888EeF15E40', 'symbol': 'CAT', 'decimals': 15, 'liquidity': 10580.9777935038}, {'address': '0x90ED158Ef26397f8d00f6Cd359Ef0FD1C2F9dc08', 'symbol': 'ewon', 'decimals': 18, 'liquidity': 480.233875896}, {'address': '0x805eeECB42034d1a864C88520ceB1b7B8176899B', 'symbol': 'GOONERS', 'decimals': 15, 'liquidity': 8442.87807998257}, {'address': '0x7D8741EbCBD987d7851a473d5b17F639C9156A36', 'symbol': 'APEX', 'decimals': 18, 'liquidity': 476.2918202544}]

Calling dynamic_tool({'gemini_api_key': 'YOUR_API_KEY', 'user_prompt': 'Given the following token addresses, symbol, decimals and liquidity, write a python function that evaluates the tokens and returns a dictionary where the keys are the token addresses and the values are the amount to invest in each token. The function should consider the liquidity, symbol and address to decide whether to invest and how much. The function should not have any arguments.\ntokens = [{"address": "0x919010e4b0083A039842bB369dEF7888EeF15E40", "decimals": 15, "liquidity": 10580.9777935038, "symbol": "CAT"}, {"address": "0x90ED158Ef26397f8d00f6Cd359Ef0FD1C2F9dc08", "decimals": 18, "liquidity": 480.233875896, "symbol": "ewon"}, {"address": "0x805eeECB42034d1a864C88520ceB1b7B8176899B", "decimals": 15, "liquidity": 8442.87807998257, "symbol": "GOONERS"}, {"address": "0x7D8741EbCBD987d7851a473d5b17F639C9156A36", "decimals": 18, "liquidity": 476.2918202544, "symbol": "APEX"}]\n'})
--------------------------------------------
Evaluating the following function:
def dynamic_function():
    tokens = [{"address": "0x919010e4b0083A039842bB369dEF7888EeF15E40", "decimals": 15, "liquidity": 10580.9777935038, "symbol": "CAT"},
              {"address": "0x90ED158Ef26397f8d00f6Cd359Ef0FD1C2F9dc08", "decimals": 18, "liquidity": 480.233875896, "symbol": "ewon"},
              {"address": "0x805eeECB42034d1a864C88520ceB1b7B8176899B", "decimals": 15, "liquidity": 8442.87807998257, "symbol": "GOONERS"},
              {"address": "0x7D8741EbCBD987d7851a473d5b17F639C9156A36", "decimals": 18, "liquidity": 476.2918202544, "symbol": "APEX"}]

    investment_amounts = {}
    total_investment = 100  # Example total investment amount

    for token in tokens:
        address = token["address"]
        symbol = token["symbol"]
        liquidity = token["liquidity"]

        if liquidity < 500:
            print(f"Skipping {symbol} due to low liquidity: {liquidity}")
            continue

        if "GOONERS" in symbol:
            investment_amount = total_investment * 0.4 #Example investing 40% of total in GOONERS.
        elif liquidity > 5000 and "CAT" in symbol:
             investment_amount = total_investment * 0.3  # Example investing 30% of total in CAT if liquidity good
        else:
            investment_amount = total_investment * 0.1 # Example investing 10% otherwise.

        investment_amounts[address] = investment_amount

    return investment_amounts

kwargs = {}
Skipping ewon due to low liquidity: 480.233875896
Skipping APEX due to low liquidity: 476.2918202544
Result = {'0x919010e4b0083A039842bB369dEF7888EeF15E40': 30.0, '0x805eeECB42034d1a864C88520ceB1b7B8176899B': 40.0}
--------------------------------------------
Result: {'0x919010e4b0083A039842bB369dEF7888EeF15E40': 30.0, '0x805eeECB42034d1a864C88520ceB1b7B8176899B': 40.0}

Execution has finalized. Result = {'0x919010e4b0083A039842bB369dEF7888EeF15E40': 30.0, '0x805eeECB42034d1a864C88520ceB1b7B8176899B': 40.0}
{'0x919010e4b0083A039842bB369dEF7888EeF15E40': 30.0, '0x805eeECB42034d1a864C88520ceB1b7B8176899B': 40.0}
```