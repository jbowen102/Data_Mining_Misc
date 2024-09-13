import os

import pandas as pd
from tqdm import tqdm
from colorama import Style, Fore, Back


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))



class Eclat(object):
    def __init__(self, transaction_dict):
        """Takes in an itemset dict where each value (representing transaction)
        is a set of strings.
        """
        self.transaction_db_horiz = transaction_dict

        self.transaction_db_vert = None  # Will hold transformed db
        self.min_sup_count = None

        self.L = None

    def _transform_db(self):
        """Transforms input "horizontal" database dict into a vertical format.
        """
        self.transaction_db_vert = dict()
        for transaction_id in self.transaction_db_horiz:
            for item in self.transaction_db_horiz[transaction_id]:
                if frozenset(item) in self.transaction_db_vert:
                    self.transaction_db_vert[frozenset(item)].add(transaction_id)
                else:
                    self.transaction_db_vert[frozenset(item)] = set((transaction_id))


    def _prune_infrequent(self):
        """Imposes min_support on all 1-itemsets found in transformed db.
        """
        self._transform_db()

        # print(Fore.GREEN + Style.BRIGHT + "Pruning C1." + Style.RESET_ALL, end="")
        single_items = list(self.transaction_db_vert.keys())
        for item in single_items:
            if len(self.transaction_db_vert[item]) < self.min_sup_count:
                # Remove any 1-itemset from vertical db if its support is too low
                _ = self.transaction_db_vert.pop(item)
        # print(Fore.GREEN + Style.BRIGHT + "..done\n" + Style.RESET_ALL)


    def find_L_all(self, min_sup_abs):
        """
        Mine transformed "vertical" data structure using Eclat algorithm.
        Find set of all frequent itemsets (of any length) in the database.
        """
        self.min_sup_count = min_sup_abs
        self._transform_db()
        self._prune_infrequent()

        C_k_dict = dict()
        for itemset1 in self.transaction_db_vert:
            for itemset2 in self.transaction_db_vert:
                if itemset1 == itemset2:
                    continue
                intersect = self.transaction_db_vert[itemset1].intersection(self.transaction_db_vert[itemset2])
                if len(intersect) >= self.min_sup_count:
                    C_k_dict[itemset1.union(itemset2)] = intersect

        print(C_k_dict)
