#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 20 21:13:56 2022

@author: stanley
"""


"""
bot7: bot 3 with spread adjustments properly implemented

Does the best in the fixed scenario
"""


def submit_market(state, team_history, round_history):
    """
    Given user defined state and history of the trades you executed 
    last round, come up with a new market for this round.
    
    Each trade in trade_history is a dict of the format
    {
         "size": volume traded,
         "price": price traded at,
         "dir": either "buy" or "sell",
         "id_against": the type of party traded against, either "team"
                         or "customer"
    }

    Each trade in period_history is a dict of the format
    {
        "size": volume traded (will always be 1),
        "price": price traded at,
        "dir": either "buy" or "sell" depending on the team's action (not the customer's),
        "id_against": "customer",
    }
    """
    
    if len(state) == 0:
        state["buy_price"] = 740
        state["sell_price"] = 1260
        state["round_num"] = 1

        
    else:
        total_bought = 0
        total_sold = 0
        spread = state["sell_price"] - state["buy_price"]
        
        for trade in team_history:
            #if trade["id_against"] == "customer":
            if trade["dir"] == "buy":
                total_bought += trade["size"]
            else:
                total_sold += trade["size"]

        # adjust position of market
        c = 2 + 15 * pow(0.86, state["round_num"])
        diff = total_sold - total_bought

        state["buy_price"] += int(c * diff)
        state["sell_price"] += int(c * diff)
        
        # adjust width of market
        # don't adjust if the spread is too small
        width_adj = (20 - total_bought - total_sold) * 5 * pow(0.95, state["round_num"])
        if spread - 2 * width_adj <= 40:
            # don't adjust if the spread is too small
            pass
        else:
            state["buy_price"] += int(width_adj)
            state["sell_price"] -= int(width_adj)  
        if state["buy_price"] >= state["sell_price"]:
            state["buy_price"] = (state["buy_price"] + state["sell_price"]) // 2 - 2
            state["sell_price"] = (state["buy_price"] + state["sell_price"]) // 2 + 2
        
        
    state["round_num"] += 1
    
    return {
            "buy": {
                    "price": state["buy_price"],
                    "size": 10 #random.randint(1, 5)
                    },
            "sell": {
                    "price": state["sell_price"],
                    "size": 10 #random.randint(1, 5)
                    },
            }
