import random
import os
import json

PRICES_DICT = {}


def get_price(ticker: str) -> float:
    dice = random.randint(1,10)
    if dice < 5:
        raise RuntimeError("rate limited")
    if ticker not in PRICES_DICT:
        PRICES_DICT[ticker] = random.randint(25, 300)
    return PRICES_DICT[ticker] 


def size_position(cash: float, price: float) -> int:
    return int(cash // price)

def get_portfolio() -> dict:
    return {"cash":2318.65,"shares":{"AAPL":10,"MSFT":20,"GOOGL":30}}


def place_order(ticker: str, qty: int, side: str) -> dict:
    if os.path.exists(".portfolio.json"):
        with open(".portfolio.json", "r") as f:
            orders = json.load(f)
    else:
        orders = []

    new_order = {"ticker": ticker, "qty": qty, "side": side}
    orders.append(new_order)

    with open(".portfolio.json", "w") as f:
        json.dump(orders, f, indent=2)

    return new_order


TOOL_SPECS = [
    {
        "type": "function",
        "function": {
            "name": "get_price",
            "description": "Get the current fake price for a stock ticker.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol, e.g. AAPL.",
                    },
                },
                "required": ["ticker"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "size_position",
            "description": (
                "Calculate the number of whole shares a cash amount buys "
                "at a given price. Call this after get_price."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "cash": {
                        "type": "number",
                        "description": "Cash available to spend, in dollars.",
                    },
                    "price": {
                        "type": "number",
                        "description": "Price per share, in dollars.",
                    },
                },
                "required": ["cash", "price"],
            },
        },
    },
    {
        "type": "function",
        "function":{
            "name":"get_portfolio",
            "description":(
                "Returns the current portfolio held by user at the starting of trading period"
            ),
            "parameters":{
                "type":"object",
                "properties":{},
                "required":[],
            },
        }
    },
    {
        "type": "function",
        "function":{
            "name":"place_order",
            "description":(
                "Read the saved portfolio, append new order to it and save it back to .portfolio.json"
            ),
            "parameters":{
                "type":"object",
                "properties":{
                    "ticker":{
                        "type":"string",
                        "description":"Stock ticker symbol, e.g. AAPL.",
                    },
                    "qty":{
                        "type":"number",
                        "description":"Number of shares to buy or sell, in whole shares.",
                    },
                    "side":{
                        "type":"string",
                        "description":"'buy' or 'sell'.",
                    },
                },
                "required":["ticker","qty","side"],
            },
        }
    }
]

TOOLS = {
    "get_price": get_price,
    "size_position": size_position,
    "get_portfolio":get_portfolio,
    "place_order":place_order,
}
