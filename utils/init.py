#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 19 14:56:58 2022

@author: stanley
"""

import config
import subprocess


root = "../"

subprocess.run(['mkdir', '-p', f'{root}rounds'])

for i in range(1, config.NUM_ROUNDS + 1):
    subprocess.run(['mkdir', '-p', f'{root}rounds/round{i}'])
    
    for j in range(1, config.NUM_TEAMS + 1):
        subprocess.run(['mkdir', '-p', f'{root}rounds/round{i}/team{j}'])
        subprocess.run(['cp', f'{root}bots/skeleton.py', f'{root}rounds/round{i}/team{j}/bot{j}.py'])
        
    subprocess.run(['mkdir', '-p', f'{root}rounds/round{i}/public'])


def clean():
    subprocess.run('rm', '-r', f'{root}rounds')
