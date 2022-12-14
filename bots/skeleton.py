#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 20 21:13:56 2022

@author: stanley
"""

"""
bot0: first attempt at reactive markets

"""

import random

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
    """

    if len(state) == 0 or state["round_num"] < 3:
        state["buy_price"] = 740
        state["sell_price"] = 1260
        state["round_num"] = 1
    else:

        buyTot = 0
        buyNum = 0

        sellTot = 0
        sellNum = 0

        for i in period_history:
            if i["id_against"] == "team":
                continue

            if i["dir"] == "buy":
                buyTot += i["price"]
                buyNum += 1
            else:
                sellTot += i["price"]
                sellNum += 1

        buyAvg = buyTot/buyNum
        sellAvg = sellTot/sellNum

        theo = (buyAvg + sellAvg)/2

        state["buy_price"] = theo - 125
        state["sell_price"] = theo + 125
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

    

    '''  
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
        c = 2 + 15 * pow(0.8, state["round_num"])
        diff = total_sold - total_bought
        state["buy_price"] += int(c * diff)
        state["sell_price"] += int(c * diff)
        
        # adjust width of market
        # don't adjust if the spread is too small
        width_adj = (16 - total_bought - total_sold) * 5 * pow(0.95, state["round_num"])
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
    

'''
def submit_market(state, my_history, period_history):
    """
    Given user defined state and history of the trades you executed 
    last round, come up with a new market for this round.
    
    state is initially an empty dictionary
    
    Each trade in my_history is a dict of the format
    {
         "size": volume traded,
         "price": price traded at,
         "dir": either "buy" or "sell",
         "id_against": the type of party traded against, either "team"
                         or "customer"
    }
    """
    
    #diff 


    """
    Each trade in period_history is a dict of the format
    {
        "size": volume traded (will always be 1),
        "price": price traded at,
        "dir": either "buy" or "sell" depending on the team's action (not the customer's),
        "id_against": "customer",
    }
    """

    """
    One example of state you might want to keep track of are the last buy and sell prices
    you submitted to the market
    """

    if len(my_history) == 0:
        state["buy_price"] = 800
        state["sell_price"] = 1200
    else:
        net_position = 0


    for my_trade in my_history:
        if my_trade["dir"] == "buy":
            net_position += size
        else:
            net_position -= size

    last_order_retreat = 1 if my_history[-1]["dir"] == "buy" else -1

    """
    May want to keep track of round number
    """
    if "round" not in state:
        state["round"] = 0
    state["round"] += 1
    

    """
    One quantity you may wish to look at are the number of buys and sells you
    executed last round
    """
    num_buys = 0
    num_sells = 0
    for trade in my_history:
        if trade["dir"] == "buy":
            num_buys += 1
        elif trade["dir"] == "sell":
            num_sells += 1
    
    
    return {
            "buy": {
                    "price": state["buy_price"] + random.randint(-50, 50),
                    "size": 1
                    },
            "sell": {
                    "price": state["sell_price"] + random.randint(-50, 50),
                    "size": 1
                    },
            }
'''