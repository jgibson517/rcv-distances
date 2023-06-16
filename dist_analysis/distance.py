import pandas as pd
import numpy as np
import itertools
import matplotlib.pyplot as plt


class DistanceSim:
    def __init__(self, data, dist_func):
        self.data = data
        self.irv_map = dict([(cand, int(rank)) for cand, rank in zip(data['candidate'], data['IRV order'])])
        self.dist_func = dist_func
        self.results_df = None

    def borda(self, a, b, c):
        self.data['score'] = (self.data['first'].astype(int)*a) + (self.data['second'].astype(int)*b) + (self.data['third'].astype(int)*c)
        sorted = self.data.sort_values(by='score', ascending=False)

        return sorted.set_index('candidate').to_dict()['score']

    def calc_distances(self, m): 
        dist_df = pd.DataFrame({'a' : [], 'b' : [], 'c' :  [], 'dist': []})
        a = m
        bc_pairs = []

        for i in range(0, m+1):
            bc_pairs += list(itertools.product(list(range(i, m+1)), [i]))

        for b, c in bc_pairs:

            # calculate borda scores
            cand_score = self.borda(a, b, c) 
   

            # sort candidates by borda score
            borda_rank = dict(sorted(cand_score.items(), key=lambda i: i[1], reverse=True))
           
             #abc_rank = list(map(lambda k: cand_id[k], list(sorted_cand.keys())))

            # maps list of candidates sorted by borda rank onto IRV rank
            borda_irv_rank = list(map(lambda k: self.irv_map[k], list(borda_rank.keys())))

            dist = self.dist_func(borda_irv_rank)

            dist_df = pd.concat([pd.DataFrame({'a': a, 'b': b, 'c': c, 'dist': dist}, index=[0]), dist_df.loc[:]]).reset_index(drop=True)
            
        self.results_df = dist_df
        return dist_df

    def find_min_sets(self, dist_df):
        '''
        add doc string
        '''
        return dist_df[dist_df['dist']==dist_df['dist'].min()]

    def gen_3d_plot(self):
    
        fig = plt.figure(figsize = (10, 7))
        ax = plt.axes(projection ="3d")
        ax.scatter3D(self.results_df['b'], self.results_df['c'], self.results_df['dist'])
        ax.set_xlabel('b value')
        ax.set_ylabel('c value')
        fig.show()
        return ax     


# Distance functions

def kendall_tau(blist):
    '''
    Add doc strings
    '''
    swapcount = 0 
    for j in range(len(blist)):
        for i in range(1, len(blist)-j):
            if blist[i-1] > blist[i]:
                swapcount += 1
                blist[i-1], blist[i] = blist[i], blist[i-1]
    
    return swapcount


def rank_diff(blist):

    sum_dist = 0
    for index, value in enumerate(blist):
        sum_dist += abs(value - (index + 1))

    return sum_dist

