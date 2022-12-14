#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 11:35:29 2022

@author: stanley
"""

import pickle
import argparse
import numpy as np
import sys

sys.path.insert(1, "../exchange")
from plotpnl import extract_team_num


def grade_case(rounds_to_grade, sort_by):
    
    round_rankings = {}
    final_case_rankings = {}

    for r in rounds_to_grade:
        
        try:
        
            with open(f"../rounds/round{r}/public/rankings.pkl", "rb") as f:
                cur_round_rankings = pickle.load(f)
                
            for team in cur_round_rankings:
                
                if team not in round_rankings:
                    round_rankings[team] = []
                
                round_rankings[team].append(cur_round_rankings[team])
                
        except:
            
            print(f"Couldn't grade round {r}!")
            
    
    for team in round_rankings:
        
        final_case_rankings[team] = np.exp(np.mean(np.log(np.array(round_rankings[team]))))
        
    print(f"SORT_BY: {sort_by}")
        
    if sort_by == "team_num":
        
        final_case_rankings = sorted(final_case_rankings.items(), key = lambda tup : extract_team_num(tup[0]))
        
    else:
        
        final_case_rankings = sorted(final_case_rankings.items(), key = lambda tup : tup[1])
            
            
    for tup in final_case_rankings:
        
        #print(team, ["{0:0.2f}".format(i) for i in final_case_rankings[team]])
        print(tup[0], round(tup[1], 3))
    
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="read in rounds to grade")
    parser.add_argument("sort_by", default="rank", help="rank to sort by case performance, team_num to sort by team number")
    parser.add_argument("rounds", nargs='+', help="rounds to grade")

    args = parser.parse_args()
    print(args)
    
    
    grade_case(args.rounds, args.sort_by)
    
    
