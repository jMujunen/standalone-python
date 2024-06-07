#!/usr/bin/env python3

# sort.py - Extenting the `sort` command for special use cases

import argparse
import subprocess
import sys
import os                                                                                                      
from datetime import datetime, timedelta                                                                         
                                                                                                                     
def get_untracked_files(repo_path):                                                                              
    """                                                                                                          
    Returns a list of untracked files in a Git repository.                                                       
                                                                                                                 
    Args:                                                                                                        
        repo_path (str): The path to the Git repository.                                                         
                                                                                                                 
    Returns:                                                                                                     
        A list of untracked files.                                                                               
    """                                                                                                          
    # Open the Git repository                                                                                    
    repo = git.Repo(repo_path)                                                                                   
                                                                                                                 
    # Get the status of each file in the repository                                                              
    statuses = repo.status()                                                                                     
                                                                                                                 
    # Iterate through the statuses and print out any untracked files                                             
    for status in statuses:                                                                                      
        if status.untracked:                                                                                     
            print(status.path)    
