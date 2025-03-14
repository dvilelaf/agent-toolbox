# Eolas x Algo: Agent Skills Hackathon

A collection of tools for your agent's toolbox.

<p align="center">
  <img width="30%" src="img/logo.png">
</p>


# What is it

This repository implements three different agent tools. All of them are compatible with [Olas Mechs](https://olas.network/services/ai-mechs).

* **Token discovery tool**: a tool to discover newly deployed tokens, based on age, liquidity and popularity on Twitter.

* **Dynamic tool**: a meta-tool that *writes itself*. Given a prompt with a function description and some arguments, the tool will **create** that function and then evaluate it passing the arguments to it.

* **Orchestrator tool**: one tool to rule them all. This tool looks for other locally available tools, loads them into an agent and uses other tools as required to reach its goal.

# Requirements
* Python >= 3.10
* [UV](https://github.com/astral-sh/uv)

# Tools

## Token discovery tool

A tool for discovering newly created tokens. It scans recently deployed pools, verifies if their tokens have sufficient liquidity, and filters out older tokens. Additionally, it checks for token popularity on Twitter.

Its goal is to identify emerging tokens that remain under the radar but are gaining traction on Twitter.

### How to test

```bash
uv run python test_token_discovery.py
```

### How it works

1. Pools deployed during the last *n* blocks are scanned (configurable)
2. We only keep pools where one of the tokens is WETH or a stablecoin
3. Pools with low liquidity are filtered out (configurable)
4. Tokens in those pools that were deployed longer that *h* hours ago are filtered out (configurable)
5. Twitter popularity is calculated and added to the token info

### What it looks like

When the test is run, the tool searches for tokens in the last 200 blocks, where:
* The liquidity pool has at least $100 in liquidity
* The token was deployed during the last week


```bash
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

A self-generating meta-tool. Simply describe your function to the LLM, and it will be created and evaluated on the fly.

### How to test

```bash
uv run python test_dynamic_tool.py
```
### How it works

1. A prompt describing a function plus some arguments are prepared
2. We use Gemini to dynamically write the requested function
3. The function is evaluated passing the arguments to it

### What it looks like

When the test is run, the tool asks for *A function that decides whether to invest in a ERC-20 token or not and returns the amount to be invested* and evaluates the function with the following arguments:

```python
address="0xdummy_address"
symbol="TEST"
decimals=18
liquidity=1000
is_popular=True
available_balance_usd=100
```

The investment strategy is implemented by the LLM and evaluated with those arguments, returning the amount that should be invested in that token:

```bash
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

A master tool for orchestrating others. Given a set of tools, it coordinates them to work together and accomplish a specific goal.

### How to test

```bash
uv run python test_orchestrator_tool.py
```

### How it works

1. The tool searches for other available tools
2. Available tools are loaded into Gemini
3. A prompt with a goal is passed to the LLM
4. An agent will dynamically use the tool to achieve its goal


### What it looks like

A goal prompt is provided so that the tool uses the other two tools described above to find new investment opportunities and evaluate them. It finally decides how much to invest in the tokens it finds interesting.

```bash
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