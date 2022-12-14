#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 21:49:08 2022

@author: stanley
"""

import argparse
import importlib
import sys
import subprocess
import numpy as np
import os
import datetime
import pytz
import pickle

# we're going to selectively import bots instead
sys.path.insert(1, "../exchange")
import exchange


ROOT = '../'

bots = {}
rankings = {}
overall_rankings = {}

result_filename = "results.txt"
customer_filename = "customer.txt"


def init_bots(args):
    # import competitor code
    if len(args.bots) == 1 and args.bots[0] == "all":
        # import all bots!
        base_path = f"../rounds/round{args.round}"
        for f in os.listdir(base_path):
            team_num = f.replace("team", "")
            # print(team_num)
            team_path = os.path.join(base_path, f)
            team_submission = os.path.join(team_path, f"bot{team_num}.py")
            if os.path.isdir(team_path) and os.path.isfile(team_submission):
                sys.path.insert(1, team_path)
                bots["bot"+team_num] = importlib.import_module(f"bot{team_num}")
                
    
    else:
        for b in args.bots:
            sys.path.insert(1, f"../rounds/round{args.round}/team{b}")
            bots["bot"+b] = importlib.import_module(f"bot{b}")
            
    
    # init rankings dictionary
    for b in bots:
        rankings[b] = []
        
    print(bots)



def preprocess_files(verbose=0):
    
    subprocess.run(['touch', result_filename])
    
    if verbose >= 2:
        subprocess.run(['touch', customer_filename])
        
        
        
def postprocess_files(verbose=0):
    
    print("Copying over result files and graph...")
    
    if verbose >= 2:
        # add results files to relevant competitor folders
        for b in bots:
            bot_num = int(b[3:])       # b of the form "boti" for int i
            cur_path = os.path.join(ROOT, 'rounds', f'round{args.round}', f'team{bot_num}')
            #print(cur_path)
            #print(type(cur_path))
            subprocess.run(['mv', f"results{bot_num}.txt", f'{cur_path}'])
            
            
    public_path = os.path.join(ROOT, 'rounds', 'round'+str(args.round), 'public', '')
            
    subprocess.run(['mv', result_filename, f'{public_path}'])
    
    if verbose >= 2:
        subprocess.run(['mv', customer_filename, f'{public_path}'])
    
    # move graphs to relevant folders
    for f in os.listdir('.'):
        if os.path.isfile(f) and f.startswith("graph"):
            subprocess.run(['mv', f, f'{public_path}'])
            



def run_case(scenario="fixed", periods_per_game=50, verbose=0):
    
    print(f"Starting case with scenario {scenario}, num of periods {periods_per_game}, verbose level {verbose}")
    
    exch = exchange.Exchange(bots, verbose)
    game_rankings = exch.run_scenario(scenario, periods_per_game, result_filename, customer_filename)
    
    for i in range(len(game_rankings)):
        cur_bot = game_rankings[i]
        rankings[cur_bot].append(i+1)
    
    
    print("Done running case!")
    



def compute_overall_rankings(rankings):
    
    print("Computing overall rankings...")
    
    """
    # take geometric mean for overall rankings
    for b in rankings:
        overall_rankings[b] = np.exp(np.mean(np.log(np.array(rankings[b]))))
    """
        
    # take arithmetic mean for overall rankings
    for b in rankings:
        overall_rankings[b] = np.mean(np.array(rankings[b]))
        
        
    subprocess.run(['touch', "rankings.txt"])
    
    with open("rankings.txt", 'w') as f:
                
        print("OVERALL RANKINGS", file=f)
        print(f"Report generated at: f{datetime.datetime.now(pytz.timezone('America/New_York'))}", file=f)
        
    
        for b in sorted(overall_rankings, key = lambda x : overall_rankings[x]):
            print(b, round(overall_rankings[b], 3), file=f)
            
        print("\n\n\n\nRANKINGS BY ROUND", file=f)    
        
        for b in sorted(overall_rankings, key = lambda x : overall_rankings[x]):
            print(b, rankings[b], file=f)
            
    public_path = os.path.join(ROOT, 'rounds', f'round{args.round}', 'public')
    subprocess.run(['mv', 'rankings.txt', public_path])

    with open("rankings.pkl", "wb") as f:
        pickle.dump(overall_rankings, f)
    subprocess.run(['mv', 'rankings.pkl', public_path])
    
    



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="read in scenario, round number, and bots, then run case")
    parser.add_argument("-round", default="1", help="round number")
    parser.add_argument("-games", type=int, default=1, help="number of games to run")
    parser.add_argument("-scenario", default="fixed", help="case scenario to run")
    parser.add_argument("-verbose", type=int, default=0, help="detailed case output verbosity level")
    parser.add_argument("bots", nargs='+', help="list of bots")

    args = parser.parse_args()
    print(args)

    print("Initializing bots!")
    init_bots(args)
    
    

    for i in range(args.games):
        if i == args.games - 1:
            # run last round at higher verbosity level
            preprocess_files(verbose=2)
            run_case(scenario=args.scenario, verbose=2)
            postprocess_files(verbose=2)
        else:
            preprocess_files(verbose=args.verbose)
            run_case(scenario=args.scenario, verbose=args.verbose)
            postprocess_files(verbose=args.verbose)
        
    compute_overall_rankings(rankings)
    
    print("Done!")
                
            
    
    
    
    




