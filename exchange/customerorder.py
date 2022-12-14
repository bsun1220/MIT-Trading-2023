#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 29 15:59:22 2022

@author: stanley
"""

import random

class CustomerOrder:
    def __init__(self, scenario):
        
        self.scenario = scenario
        
        self.max_volume = 1000
        self.volume_mu = 500
        self.volume_sigma = 30
        self.fair = random.randint(500, 1500)
        self.spread = random.randint(50, 200)
        
        # probability we see a liquidity event for volatility scenario
        self.vol_p = random.uniform(0.05, 0.07)


        # integer indicating number of days until next big price change
        # it is -1 if no impending price change
        self.countdown = -1
        # integer indicating number of days until next big price change IS ALLOWED
        # it is -1 if big price change currently allowed
        if scenario == "volatility":
            self.cooldown = 0
        else:
            self.cooldown = 5

        self.price_path = []
        self.price_path.append(self.fair)
        
        

    def other_dir(s):
        if s == "buy":
            return "sell"
        else:
            return "buy"
        

    def update_params(self):
        """
        This function will update customer order parameters in a certain manner
        depending on which scenario we are currently running.

        Scenario 1: fixed
            fair value is fixed
            spread is fixed
            momentum_p is unused
            
        Scenario 2: volatility
            fair value can move
            spread can vary during vol period
            volume can vary during vol period
            

        """
        
        if self.scenario == "volatility":
            self.fair += int(random.gauss(0, 1) * 5)
            
            if len(self.price_path) > 5 and self.cooldown <= 0 and random.uniform(0, 1) < self.vol_p:
                self.cooldown = random.randint(8, 12)   # duration of liquidity event
                print(f"ROUND {len(self.price_path)} STARTING LIQUIDITY EVENT LASTING {self.cooldown} ROUND")
                
            self.cooldown -= 1
                
            self.price_path.append(self.fair)

            


    def generate_single_customer_order(self):
        """
        This distribution is uniform on [fair - spread, fair + spread]

        Requires: fair, spread are integers, spread >= 0

        Returns: dictionary of the form
                {
                    "price": price of order
                    "dir": direction of order (buy/sell)
                }
        """

        assert isinstance(self.fair, int), "fair is nonintegral"
        assert isinstance(self.spread, int), "spread is nonintegral"
        assert self.spread >= 0, "spread is negative"

        if self.scenario == "fixed":
            return {
                    "price": random.randint(self.fair - self.spread, self.fair + self.spread),
                    "dir": "buy" if random.randint(0, 1) == 1 else "sell"
                    }
            
        elif self.scenario == "volatility":
            
            order_dir = "buy" if random.randint(0, 1) == 1 else "sell"
            
            if self.cooldown > 0:
                # liquidity event
                # make the order sweeter for competitors
                if order_dir == "buy":
                    order_price = self.fair + self.spread + random.randint(200, 300)
                elif order_dir == "sell":
                    order_price = self.fair - self.spread - random.randint(200, 300)
                    
                return {
                        "price": order_price,
                        "dir": order_dir,
                        }
                
            else:
                return {
                        "price": random.randint(self.fair - self.spread, self.fair + self.spread),
                        "dir": order_dir,
                        }
                



    def generate_period_volume(self):
        """
        This distribution is normal with mean mu, std sigma
        """

        mu = self.volume_mu
        sigma = self.volume_sigma

        if (self.scenario == "volatility" and self.cooldown > 0):
            # should be a high volume day in anticipation of price change
            mu *= 2
            


        return min(max(int(random.gauss(mu, sigma)), 0), self.max_volume)



