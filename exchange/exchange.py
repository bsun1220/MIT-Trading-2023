#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 20 20:14:10 2022

@author: stanley
"""

import pprint
import customerorder as CO
import plotpnl
import copy
import random
import datetime
import pytz
import sys
import pandas as pd



class Exchange:


    def __init__(self, bots, verbose=0):

        self.info = {}              # keep track of positions and PnL
        self.bots = bots            # BE CAREFUL HERE! We have two references to one dict
        self.orderbook = {
                            "buy": [],
                            "sell": [],
                            }
        self.period_history = []    # keep track of customer trades in each period

        self.result_f = None               # result file object to use later
        self.customer_f = None             # customer order result file object to use later
        self.verbose = verbose

        self.customer = None        # initialize the customer orders later
        
        self.MAX_ORDER_SIZE = 10
        self.MAX_ORDER_PRICE = 9999
        
        self.SUBMISSION_ERROR_LIMIT = 2     # competitors can only have 2 faulty submissions
        self.submission_errors = {}         # before they get shut off



        # init teams
        for b in self.bots:
            cur_team_info = {}
            cur_team_info["cash"] = 0
            cur_team_info["pos"] = 0
            cur_team_info["trades"] = []
            cur_team_info["state"] = {}
            cur_team_info["PnL"] = []

            self.info[b] = cur_team_info
            
            self.submission_errors[b] = 0

        cur_team_info = {}
        cur_team_info["cash"] = 0
        cur_team_info["pos"] = 0
        cur_team_info["trades"] = []
        cur_team_info["state"] = {}
        cur_team_info["PnL"] = []

        self.info["marketmakerbot"] = cur_team_info


    def reset(self):
        """
        Clear all participant cash, positions, history etc.
        in preparation for the next round

        """

        self.info = {}              # keep track of positions and PnL
        self.orderbook = {
                            "buy": [],
                            "sell": [],
                            }
        self.period_history = []    # keep track of customer trades in each period


        # init teams
        for b in self.bots:
            cur_team_info = {}
            cur_team_info["cash"] = 0
            cur_team_info["pos"] = 0
            cur_team_info["trades"] = []
            cur_team_info["state"] = {}
            cur_team_info["PnL"] = []

            self.info[b] = cur_team_info
            
            self.submission_errors[b] = 0

        cur_team_info = {}
        cur_team_info["cash"] = 0
        cur_team_info["pos"] = 0
        cur_team_info["trades"] = []
        cur_team_info["state"] = {}
        cur_team_info["PnL"] = []

        self.info["marketmakerbot"] = cur_team_info


    def clear_orderbook(self):
        self.orderbook["buy"] = []
        self.orderbook["sell"] = []


    def clear_team_trades(self):
        for b in self.bots:
            self.info[b]["trades"] = []



    def read_orderbook(self):
        """
        query the bots for their markets for the current trading period
        """

        for b in self.bots:
            
            if self.submission_errors[b] <= self.SUBMISSION_ERROR_LIMIT:
            
                cur_team = self.info[b]
                
                try:
                    # send competitors a copy of period_history so they can't modify it
                    cur_market = self.bots[b].submit_market(cur_team["state"], cur_team["trades"], \
                                            copy.deepcopy(self.period_history))
    
    
                    buy_order = {}
                    buy_order["price"] = min(max(int(cur_market["buy"]["price"]), 0), self.MAX_ORDER_PRICE)
                    buy_order["size"] = min(max(int(cur_market["buy"]["size"]), 0), self.MAX_ORDER_SIZE)
                    buy_order["id"] = b
    
                    sell_order = {}
                    sell_order["price"] = min(max(int(cur_market["sell"]["price"]), 0), self.MAX_ORDER_PRICE)
                    sell_order["size"] = min(max(int(cur_market["sell"]["size"]), 0), self.MAX_ORDER_SIZE)
                    sell_order["id"] = b
    
                    # the orderbook should never store orders of size 0
                    if buy_order["size"] > 0:
                        self.orderbook["buy"].append(buy_order)
                    if sell_order["size"] > 0:
                        self.orderbook["sell"].append(sell_order)
    
    
                    team_num = plotpnl.extract_team_num(b)
    
                    if self.verbose >= 2:
    
                        with open(f"results{team_num}.txt", 'a') as temp_f:
                            print(f"{b} market:", file=temp_f)
                            print(f"buy {buy_order}", file=temp_f)
                            print(f"sell {sell_order}", file=temp_f)
                            print(file=temp_f)
    
                except KeyboardInterrupt:
                    sys.exit(0)
    
                except Exception as e:
                    self.submission_errors[b] += 1
                    print(f"{e} error in {b}")
                    
                    if self.verbose >= 2:
                        
                        team_num = plotpnl.extract_team_num(b)

                        with open(f"results{team_num}.txt", 'a') as temp_f:
                            print(f"{e} error", file=temp_f)
                            print(file=temp_f)
                    
            else:
                
                if self.verbose >= 2:
                    
                    team_num = plotpnl.extract_team_num(b)
    
                    with open(f"results{team_num}.txt", 'a') as temp_f:
                        print(f"SUBMISSION ERROR LIMIT EXCEEDED FOR TEAM {b}", file=temp_f)
                        print(file=temp_f)

        # add in market maker bot orders for some regularity in markets
        buy_order = {}
        buy_order["price"] = self.customer.fair - self.customer.spread \
                                - random.randint(100, 200)
        buy_order["size"] = 99999
        buy_order["id"] = "marketmakerbot"

        sell_order = {}
        sell_order["price"] = self.customer.fair + self.customer.spread \
                                + random.randint(100, 200)
        sell_order["size"] = 99999
        sell_order["id"] = "marketmakerbot"

        self.orderbook["buy"].append(buy_order)
        self.orderbook["sell"].append(sell_order)

        random.shuffle(self.orderbook["buy"])
        random.shuffle(self.orderbook["sell"])
        self.orderbook["buy"].sort(key = lambda x : x["price"])
        self.orderbook["sell"].sort(key = lambda x : x["price"], reverse=True)



    def update_team_info(self, team_id, cash, pos, trade):
        """
        Update team info after a trade has occurred.
        Update cash, positions, and trade history
        """
        self.info[team_id]["cash"] += cash
        self.info[team_id]["pos"] += pos
        self.info[team_id]["trades"].append(trade)



    def auction(self):
        """
        Uncross the orderbook at a single auction price.
        
        We remove one each of bid and ask orders until the book uncrosses. The
        midmarket of the final pair of uncrossed orders is the auction price.
        """
        
        
        buy_book = copy.deepcopy(self.orderbook["buy"])
        sell_book = copy.deepcopy(self.orderbook["sell"])
        
        auction_price = None
        
        while len(buy_book) > 0 and len(sell_book) > 0 and \
            buy_book[-1]["price"] >= sell_book[-1]["price"]:
                
            auction_price = (buy_book[-1]["price"] + sell_book[-1]["price"]) / 2
                
            shares_to_remove = min(buy_book[-1]["size"], sell_book[-1]["size"])
            
            #print(f"bid {buy_book[-1]['price']} ask {sell_book[-1]['price']}, size {shares_to_remove}")
            
            buy_book[-1]["size"] -= shares_to_remove
            if buy_book[-1]["size"] == 0:
                buy_book.pop()
                
            sell_book[-1]["size"] -= shares_to_remove
            if sell_book[-1]["size"] == 0:
                sell_book.pop()
                
                
        if auction_price == None:
            #print("no auction!")
            return "no trades"
        
        
        #print(f"Auction price: {auction_price}")
        
        while len(self.orderbook["buy"]) > 0 and len(self.orderbook["sell"]) > 0 and \
            self.orderbook["buy"][-1]["price"] >= self.orderbook["sell"][-1]["price"]:
        
            best_buy = self.orderbook["buy"][-1]
            best_sell = self.orderbook["sell"][-1]
                
            vol_traded = min(best_buy["size"], best_sell["size"])
            price_traded = auction_price
            
            self.update_team_info(best_buy["id"],
                             -1 * vol_traded * price_traded,
                             vol_traded,
                             {
                                "size": vol_traded,
                                "price": price_traded,
                                "dir": "buy",
                                "id_against": "team",
                                })

            self.update_team_info(best_sell["id"],
                             vol_traded * price_traded,
                             -1 * vol_traded,
                             {
                                "size": vol_traded,
                                "price": price_traded,
                                "dir": "sell",
                                "id_against": "team",
                                })

            if vol_traded == best_buy["size"]:
                self.orderbook["buy"].pop()
            else:
                self.orderbook["buy"][-1]["size"] -= vol_traded

            if vol_traded == best_sell["size"]:
                self.orderbook["sell"].pop()
            else:
                self.orderbook["sell"][-1]["size"] -= vol_traded

            trade_hist = {
                    "size": vol_traded,
                    "price": price_traded,
                    "buyer": best_buy["id"],
                    "seller": best_sell["id"],
                    }

            if self.verbose >= 3:
                pprint.pprint(trade_hist)
                
        """
        if len(self.orderbook["buy"]) == 0:
            print("no bids")
        else:
            print(f"best buy: {self.orderbook['buy'][-1]}")
            
        if len(self.orderbook["sell"]) == 0:
            print("no asks")
        else:
            print(f"best sell: {self.orderbook['sell'][-1]}")
        """

        return "auction done"
        






    def make_customer_trade(self, customer_order):
        """
        Tries to match best buy or best sell in the orderbook with customer order

        Returns a trade message if a trade occurred, else return
        'no trades'.
        """
        if customer_order["dir"] == "sell" and len(self.orderbook["buy"]) > 0 and \
            (self.orderbook["buy"][-1]["price"] >= customer_order["price"]):

            best_buy = self.orderbook["buy"][-1]

            self.update_team_info(best_buy["id"],
                             -1 * best_buy["price"],
                             1,
                             {
                                "size": 1,
                                "price": best_buy["price"],
                                "dir": "buy",
                                "id_against": "customer",
                                     })

            self.period_history.append({
                                "size": 1,
                                "price": best_buy["price"],
                                "dir": "buy",
                                #"id_of": best_buy["id"],
                                "id_against": "customer",
                                     })

            if self.verbose >= 3:
                print("bought by ", best_buy["id"])

            self.orderbook["buy"][-1]["size"] -= 1
            if self.orderbook["buy"][-1]["size"] == 0:
                self.orderbook["buy"].pop()


        elif customer_order["dir"] == "buy" and len(self.orderbook["sell"]) > 0 and \
            (self.orderbook["sell"][-1]["price"] <= customer_order["price"]):

            best_sell = self.orderbook["sell"][-1]

            self.update_team_info(best_sell["id"],
                             best_sell["price"],
                             -1,
                             {
                                "size": 1,
                                "price": best_sell["price"],
                                "dir": "sell",
                                "id_against": "customer",
                                     })

            self.period_history.append({
                                "size": 1,
                                "price": best_sell["price"],
                                "dir": "sell",
                                #"id_of": best_sell["id"],
                                "id_against": "customer",
                                     })

            if self.verbose >= 3:
                print("sold by ", best_sell["id"])

            self.orderbook["sell"][-1]["size"] -= 1
            if self.orderbook["sell"][-1]["size"] == 0:
                self.orderbook["sell"].pop()




    def run_period(self, period_num):

        """
        run a trading period of the game

        clears the trading period history after the teams submit markets
        and then updates trading period history with data from the new period


        """


        # remove this for production code
        print("-----------------------------------------", file=self.result_f)


        if self.verbose >= 2:

            sorted_team_nums = list(self.bots.keys())
            sorted_team_nums.sort(key = lambda x : plotpnl.extract_team_num(x))

            for team in sorted_team_nums:

                team_num = plotpnl.extract_team_num(team)

                with open(f"results{team_num}.txt", 'a') as temp_f:

                    num_trades = 0
                    for trade in self.info[team]['trades']:
                        num_trades += trade["size"]

                    print("-----------------------------------------", file=temp_f)
                    print(f"INFO FOR PERIOD {period_num}", file=temp_f)
                    print("-----------------------------------------", file=temp_f)



        self.clear_orderbook()
        self.read_orderbook()

        # make sure to clear team trades after receive team markets from the period
        self.clear_team_trades()
        self.period_history.clear()

        if self.verbose >= 3:
            print("PRE MARKET OPEN", file=self.result_f)
            print("sell:", file=self.result_f)
            pprint.pprint(self.orderbook["sell"], stream=self.result_f)
            print("buy:", file=self.result_f)
            pprint.pprint(self.orderbook["buy"][::-1], stream=self.result_f)
            print("-----------------------------------------", file=self.result_f)

            print("OPENING TRADES", file=self.result_f)

        self.auction()

        if self.verbose >= 3:
            pprint.pprint(self.info, stream=self.result_f)
            print("-----------------------------------------", file=self.result_f)

            print("PRE CUSTOMER ORDERS", file=self.result_f)
            print("sell:", file=self.result_f)
            pprint.pprint(self.orderbook["sell"], stream=self.result_f)
            print("buy:", file=self.result_f)
            pprint.pprint(self.orderbook["buy"][::-1], stream=self.result_f)
            print("-----------------------------------------", file=self.result_f)


        period_volume = self.customer.generate_period_volume()


        if self.verbose >= 3:
            print("FAIR: ", self.customer.fair, file=self.result_f)
            print("SPREAD: ", self.customer.spread, file=self.result_f)
            print("PERIOD VOLUME: ", period_volume, file=self.result_f)


        num_buy = 0
        num_sell = 0

        # keep track of customer orders to log them later
        customer_orders = []

        for i in range(period_volume):
            cur_order = self.customer.generate_single_customer_order()

            customer_orders.append(cur_order)

            if cur_order["dir"] == "buy":
                num_buy += 1
            else:
                num_sell += 1

            """
            it's kind of weird to execute customer order logic like this, but the
            generalizable alternative requires inserting the customer orders into
            the orderbook, which is slow
            """

            if self.verbose >= 3:
                print(cur_order, file=self.result_f)

            self.make_customer_trade(cur_order)

        if self.verbose >= 2:
            # write customer order to log file
            customer_orders.sort(key = lambda x : (x["dir"], x["price"]))

            #for cur_order in customer_orders:
            #    print(f"{period_num}, {cur_order['dir']}, {cur_order['price']}", file=self.customer_f)
            
            customer_buys = pd.DataFrame(filter(lambda x: x["dir"] == "buy", customer_orders))
            customer_sells = pd.DataFrame(filter(lambda x: x["dir"] == "sell", customer_orders))
            
            print(f"Period {period_num} customer buys summary:", file=self.customer_f)
            print(f"{customer_buys.describe()}", file=self.customer_f)
            
            print(f"Period {period_num} customer sells summary:", file=self.customer_f)
            print(f"{customer_sells.describe()}", file=self.customer_f)
            
            print("==========================================================", file=self.customer_f)

            

        print("#buy customer orders:", num_buy, file=self.result_f)
        print("#sell customer orders:", num_sell, file=self.result_f)
        print("period_volume:", period_volume, file=self.result_f)
        print("fair value:", self.customer.fair, file=self.result_f)


        for team in self.info:
            self.info[team]["PnL"].append(self.info[team]["cash"] \
                     + self.info[team]["pos"] * self.customer.fair)


        if self.verbose >= 2:

            for team in sorted_team_nums:

                team_num = plotpnl.extract_team_num(team)

                with open(f"results{team_num}.txt", 'a') as temp_f:

                    num_trades = 0
                    for trade in self.info[team]['trades']:
                        num_trades += trade["size"]

                    print(f"{team} info post trading:", file=temp_f)
                    print(f"pos: {self.info[team]['pos']}", file=temp_f)
                    print(f"cash: {self.info[team]['cash']}", file=temp_f)
                    print(f"PnL: {self.info[team]['cash'] + self.info[team]['pos'] * self.customer.fair}", file=temp_f)
                    print(f"#Trades: {num_trades}", file=temp_f)
                    print(file=temp_f)



        if self.verbose >= 3:
            print("-----------------------------------------", file=self.result_f)


            print("AFTER CUSTOMER ORDERS", file=self.result_f)
            print("sell:", file=self.result_f)
            pprint.pprint(self.orderbook["sell"], stream=self.result_f)
            print("buy:", file=self.result_f)
            pprint.pprint(self.orderbook["buy"][::-1], stream=self.result_f)
            print("Team Info", file=self.result_f)

            for team in self.info:
                print(team, self.info[team]["cash"], self.info[team]["pos"], file=self.result_f)
                for trade in self.info[team]["trades"]:
                    print(trade, file=self.result_f)
            print("-----------------------------------------", file=self.result_f)



        self.customer.update_params()





    def run_scenario(self, scenario, num_periods, result_filename, customer_filename):
        """
        Run the case under a given scenario (fixed, momentum, news)
        with a given dictionary of bots. Dictionary bots is of the form

            bots["teami"] = object pointing to bot

        for 0 <= i < num_teams.
        """

        self.result_f = open(result_filename, 'w')

        if self.verbose >= 2:
            self.customer_f = open(customer_filename, 'w')

            print("Customer Order Info:", file=self.customer_f)
            print("==========================================================", file=self.customer_f)
                  
        print(f"Report generated at: {datetime.datetime.now(pytz.timezone('America/New_York'))}", file=self.result_f)

        print("Initializing bots!")
        self.reset()
        print("Initializing customer orders!")
        # init customer order
        self.customer = CO.CustomerOrder(scenario)

        self.period_history = []

        if self.verbose >= 2:
            for team in self.bots:
                team_num = plotpnl.extract_team_num(team)
                with open(f"results{team_num}.txt", 'w') as temp_f:
                    # we write to the file, potentially overwriting previous contents
                    print(f"Detailed results for team {team_num}:", file=temp_f)
                    print(f"Report generated at: {datetime.datetime.now(pytz.timezone('America/New_York'))}", file=temp_f)

        for i in range(num_periods):
            print("-----------------------------------------", file=self.result_f)
            print("STARTING PERIOD", i+1, file=self.result_f)
            self.run_period(i+1)
            print(file=self.result_f)
            print(file=self.result_f)

        print("-----------------------------------------", file=self.result_f)
        print("LIQUIDATING POSITIONS...", file=self.result_f)
        for team in self.info:
            self.info[team]["cash"] += self.customer.fair * self.info[team]["pos"]
            self.info[team]["pos"] = 0
        print("-----------------------------------------", file=self.result_f)


        teams_sorted = list(self.bots.keys())
        teams_sorted.sort(key=lambda x : self.info[x]["cash"], reverse=True)


        print("PnLs", file=self.result_f)
        for team in teams_sorted:
            print(team, self.info[team]["cash"], file=self.result_f)

            if self.verbose >= 2:

                team_num = plotpnl.extract_team_num(team)
                with open(f"results{team_num}.txt", 'a') as temp_f:
                    print("-----------------------------------------", file=temp_f)
                    print(f"FINAL PNL: {self.info[team]['cash']}", file=temp_f)

        print("-----------------------------------------", file=self.result_f)




        print("SCENARIO:", scenario, file=self.result_f)

        print("CUSTOMER ORDER PARAMS", file=self.result_f)
        print("fair:", self.customer.fair, file=self.result_f)
        print("spread:", self.customer.spread, file=self.result_f)
        print("vol_p:", self.customer.vol_p, file=self.result_f)
        print("price_path:", file=self.result_f)

        for i, p in enumerate(self.customer.price_path):
            print(f"    {i+1}: {p}", file=self.result_f)


        # plot PnL visualization
        plotpnl.make_plots(self.info)

        self.result_f.close()
        self.result_f = None

        if self.verbose >= 2:
            self.customer_f.close()
            self.customer_f = None

        return teams_sorted




if __name__ == '__main__':
    print("Try out the run_scenario function!")
