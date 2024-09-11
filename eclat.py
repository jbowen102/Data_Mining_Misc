import os

import pandas as pd
from tqdm import tqdm
from colorama import Style, Fore, Back


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))



class Eclat(object):
    def __init__(self, min_sup_abs, transaction_dict):
        """Takes in an itemset dict where each value (representing transaction)
        is a set of strings.
        """
        self.min_sup_count = min_sup_abs
        self.transaction_db = transaction_dict

        self.C1 = None
        self.L1 = None
        self.L = None

    def read_in_C1(self):
        """Creates self.C1 dict containing all 1-itemsets (no min_sup imposed)
        from database self.transaction_db.
        Key: 1-itemset (as frozenset) | Value: support
        """        
        transaction_itemsets = [set(val) for val in self.transaction_db.values()]

        self.C1 = dict()
        # Loop through db transactions and tally 1-itemset supports
        for itemset in transaction_itemsets:
            for item in itemset:
                if self.C1.get(frozenset([item])) is None:
                    # If item doesn't exist in C_1 dictionary yet, add it.
                    self.C1[frozenset([item])] = 1
                else:
                    self.C1[frozenset([item])] += 1

    def find_L1(self):
        """Imposes min_support on all 1-itemsets (self.C1) found in
        self.transaction_db to determine which of them are frequent.
        Transfers all frequent 1-itemsets to self.L1.
        """
        self.read_in_C1()
        
        self.L1 = dict()
        print(Fore.GREEN + Style.BRIGHT + "Pruning C1." + Style.RESET_ALL, end="")
        for itemset in self.C1:
            if self.C1[itemset] >= self.min_sup_count:
                self.L1[itemset] = self.C1[itemset]
        # print(len(L_1)) # DEBUG: should be 50
        print(Fore.GREEN + Style.BRIGHT + "..done\n" + Style.RESET_ALL)     
