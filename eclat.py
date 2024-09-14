import os
import itertools

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
                if frozenset({item}) in self.transaction_db_vert:
                    self.transaction_db_vert[frozenset({item})].add(transaction_id)
                else:
                    self.transaction_db_vert[frozenset({item})] = set({transaction_id})


    def _prune_infrequent(self):
        """Imposes min_support on all 1-itemsets found in transformed db.
        """
        assert self.transaction_db_vert is not None, \
                "Attempted to prune infrequent items before vertical db created."
        # Make temp list so not looping over dict itself, when its size may change
        single_items = list(self.transaction_db_vert.keys())
        for item in single_items:
            if len(self.transaction_db_vert[item]) < self.min_sup_count:
                # Remove any 1-itemset from vertical db if its support is too low
                self.transaction_db_vert.pop(item)


    def _prune_universal(self):
        """Removes single itemsets that have "universal" support - items found
        in every transaction of database so they're excluded from pattern
        discovery (if it is known that those rules will be uninteresting).
        """
        assert self.transaction_db_vert is not None, \
                "Attempted to prune universal items before vertical db created."
        # Make temp list so not looping over dict itself, when its size may change
        single_items = list(self.transaction_db_vert.keys())
        for item in single_items:
            if len(self.transaction_db_vert[item]) >= len(self.transaction_db_horiz):
                self.transaction_db_vert.pop(item)


    def find_L_all(self, min_sup_abs, include_univ=True):
        """
        Mine transformed "vertical" data structure using Eclat algorithm.
        Find set of all frequent itemsets (of any length) in the database.
        """
        self.min_sup_count = min_sup_abs
        self._transform_db()
        self._prune_infrequent()

        if not include_univ:
            self._prune_universal()

        print(Fore.CYAN + Style.BRIGHT, end="")
        print("Found %d frequent 1-itemsets" % len(self.transaction_db_vert))
        print(Style.RESET_ALL, end="")

        # for transaction in self.transaction_db_vert:
        #     print("%s: " % transaction, end="") # DEBUG
        #     print(sorted(self.transaction_db_vert[transaction])) # DEBUG
        L = self.transaction_db_vert
        L_k = self.transaction_db_vert
        k = 2
        while len(L_k) > 0:
            L_km1 = L_k
            L_k = dict()
            seen = set() # Maintain list of already-seen itemset candidates to eliminate duplicate effort.
            print()
            for itemset1 in tqdm(L_km1, desc="Finding %s-itemsets" % k, colour="#4ab19d"):
                for itemset2 in L_km1:
                    k_itemset_cand = itemset1.union(itemset2)
                    if k_itemset_cand in seen:
                        continue # Already seen and evaluated
                    else:
                        seen.add(k_itemset_cand)

                    if len(itemset1.symmetric_difference(itemset2)) != 2:
                        # Only look at pairings w/ one element different
                        continue

                    shared_transactions = L_km1[itemset1].intersection(L_km1[itemset2])
                    # print("\n%s: " % itemset1, end="") # DEBUG
                    # print(sorted(L_km1[itemset1])) # DEBUG
                    # print("%s: " % itemset2, end="") # DEBUG
                    # print(sorted(L_km1[itemset2])) # DEBUG
                    # print("Shared\t: ", end="") # DEBUG
                    # print(sorted(shared_transactions)) # DEBUG
                    if len(shared_transactions) >= self.min_sup_count:
                        # print("passed min_sup") # DEBUG
                        # print("Union: ", end="") # DEBUG
                        # print(k_itemset_cand) # DEBUG
                        L_k[k_itemset_cand] = shared_transactions
                    else:
                        continue

            print(Fore.CYAN + Style.BRIGHT, end="")
            print("Found %d frequent %d-itemsets" % (len(L_k), k) + Style.RESET_ALL)
            L = {**L, **L_k} # https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression-in-python
            k += 1

        print()
        for item in L:
            print("%s:\t\t\t" % item + Fore.YELLOW + Style.BRIGHT + "%d" % len(L[item]) + Style.RESET_ALL)
        print(Style.RESET_ALL)

        return L