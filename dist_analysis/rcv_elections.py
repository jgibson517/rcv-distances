# RCV sim 
import matplotlib.pyplot as plt
import pandas as pd
import random
import itertools
from numpy.random import choice
import random

class rcvElections:

    def __init__(self, ballot_list, cand_list, num_seats):
        self.ballot_list = ballot_list
        self.cand_list = cand_list
        self.num_seats = num_seats
        self.results_df = None

    # Helper functions for rcv_sim
    def remove_cand(self, cand, ballot_list):
        for n, ballot in enumerate(ballot_list):
            new_ballot = []
            for c in ballot:
                if c!= cand:
                    new_ballot.append(c)
            ballot_list[n]= new_ballot

    def recompute_count(self, candidates, ballot_list):
        cand_totals = {}
        for cand in candidates:
            cand_totals[cand] = len([ballot for ballot in ballot_list if ballot[0] == cand])
        return cand_totals

# Transfer method functions
    def cincinnati_transfer(self, cand, ballot_list, win_lose, cutoff):
        remove_cand = self.remove_cand
        if win_lose == 'lose':
            remove_cand(cand, ballot_list)
        else:
            cand_ballots_index = []
            single_cand_ballots_index = []
            for n, ballot in enumerate(ballot_list):
                if ballot[0] == cand and len(ballot) == 1:
                    single_cand_ballots_index.append(n)
                elif ballot[0] == cand and len(ballot) >1:
                    cand_ballots_index.append(n)

            rand_winners1 = random.sample(single_cand_ballots_index, min(int(cutoff), len(single_cand_ballots_index)))
            rand_winners2 = random.sample(cand_ballots_index, int(cutoff)- len(rand_winners1))
            rand_winners = rand_winners1 + rand_winners2

            #remove winning ballots from simulation
            for index in sorted(rand_winners, reverse = True):
                del ballot_list[index]

            #remove candidate from rest of ballots
            remove_cand(cand, ballot_list)

 

    def rcv_run(self, transfer_method=cincinnati_transfer, verbose_bool=False):
        winners = []
        losers = []
        num_seats = self.num_seats
        ballot_list = self.ballot_list
        cutoff = int(len(ballot_list)/(num_seats+1) + 1)
        candidates = self.cand_list.copy()
        ballot_list = [x for x in ballot_list if x != []]
        recompute_count = self.recompute_count
        cand_totals = recompute_count(candidates, ballot_list)

        while len(winners) < num_seats:
            remaining_cands = candidates
            if len(remaining_cands) == num_seats - len(winners):
                winners = winners + remaining_cands
                # remove remaining candidates from list of candidates
                candidates = []
                break

            cand_totals = recompute_count(candidates, ballot_list)

            for cand in list(candidates):
                if len(winners) == num_seats:
                        break
                if cand_totals[cand] >= cutoff:
                    winners.append(cand)
                    transfer_method(self, cand, ballot_list, "win", cutoff)
                    candidates.remove(cand)
                    ballot_list = [x for x in ballot_list if x != []]
                    cand_totals = recompute_count(candidates, ballot_list)
                    if verbose_bool:
                        print("candidate", cand, "elected")

            if len(winners) == num_seats:
                break

            min_count = min(cand_totals.values())
            min_cand_list = [k for k,v in cand_totals.items() if v == min_count]
            min_cand = random.choice(min_cand_list)
            losers.append(min_cand)
        #   min_cand = min(cand_totals, key=cand_totals.get)
            transfer_method(self, min_cand, ballot_list, "lose", cutoff)
            candidates.remove(min_cand)
            ballot_list = [x for x in ballot_list if x != []]
            cand_totals= recompute_count(candidates, ballot_list)
            if verbose_bool:
                print("candidate", min_cand, "eliminated")

        # sort remaining candidates by vote totals
        candidates = sorted(candidates, key = lambda x: cand_totals[x])

        # edge case where last remaining candidate is actually the winner
        if winners == candidates:
            candidates = []
        # print("winners, losers, leftovers:")
        # print(winners, losers, candidates)

        candidate_ranking = winners + candidates + list(reversed(losers))
        return candidate_ranking