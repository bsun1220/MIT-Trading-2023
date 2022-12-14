#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  1 13:57:03 2022

@author: stanley
"""

import matplotlib.pyplot as plt
import datetime
import pytz


def extract_team_num(s):
    """
    Small helper method to plot PnLs
    """
    
    ret = 0
    
    if s[:3] != "bot":
        print(f"found team name {s} when extracting team num")
        return -1
        
    try:
        ret = int(s[3:])
    except ValueError:
        print("couldn't convert string to number when extracting team num")
        return -1
        
    
    return ret



def make_plots(team_info):
    
    teams_sorted_by_id = list(team_info.keys())
    teams_sorted_by_id = list(filter(lambda name : extract_team_num(name) >= 0, teams_sorted_by_id))
    teams_sorted_by_id.sort(key = lambda x : extract_team_num(x))
    
    # print(teams_sorted_by_id)
    
    # divide num teams by 10, rounding up
    for i in range((len(teams_sorted_by_id) - 1) // 10 + 1):
    
        plt.title(f"""Teams {10*i+1}-{10*i+10} PnL over trading periods\n
                  Report generated at: {datetime.datetime.now(pytz.timezone('America/New_York'))}""")
        
        for team in teams_sorted_by_id[10*i: 10*(i+1)]:
            plt.plot(team_info[team]["PnL"], label=team)
            
        plt.legend()
        
        plt.savefig(f"graph{i+1}.png")
        plt.clf()