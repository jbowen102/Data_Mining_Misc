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
                if frozenset(item) in self.transaction_db_vert:
                    self.transaction_db_vert[frozenset(item)].add(transaction_id)
                else:
                    self.transaction_db_vert[frozenset(item)] = set((transaction_id))


    def _prune_infrequent(self):
        """Imposes min_support on all 1-itemsets found in transformed db.
        """
        self._transform_db()

        single_items = list(self.transaction_db_vert.keys())
        for item in single_items:
            if len(self.transaction_db_vert[item]) < self.min_sup_count:
                # Remove any 1-itemset from vertical db if its support is too low
                _ = self.transaction_db_vert.pop(item)


    def find_L_all(self, min_sup_abs):
        """
        Mine transformed "vertical" data structure using Eclat algorithm.
        Find set of all frequent itemsets (of any length) in the database.
        """
        self.min_sup_count = min_sup_abs
        self._transform_db()
        self._prune_infrequent()

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
            for itemset1 in L_km1:
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

                    # If any k-1 subpattern of the candidate k-subset is not present in
                    # L_k-1, the k-itemset can't be frequent. Prune
                    for km1_combo_subset in set(itertools.combinations(k_itemset_cand, k-1)):
                        if frozenset(km1_combo_subset) not in L_km1:
                            # print("Subset ", end="") # DEBUG
                            # print(km1_combo_subset, end="") # DEBUG
                            # print("didn't pass min_sup") # DEBUG
                            L_k.pop(k_itemset_cand)
                            break
                            # don't continue looking for k-1-subsets in L_k-1 if one
                            # already was missing. And don't try to remove candidate k-itemset from L_k again.

            L = {**L, **L_k} # https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression-in-python
            k += 1

        print()
        for item in L:
            print("%s:\t\t\t" % item + Fore.YELLOW + Style.BRIGHT + "%d" % len(L[item]) + Style.RESET_ALL)
        print(Style.RESET_ALL)