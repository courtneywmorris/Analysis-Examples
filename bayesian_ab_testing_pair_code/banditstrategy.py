import scipy.stats as stats
import numpy as np
import random
import math


class BanditStrategy(object):
    '''
    Implements a online, learning strategy to solve
    the Multi-Armed Bandit problem.

    parameters:
        bandits: a Bandit class with .pull method
		choice_function: accepts a self argument (which gives access to all the variables), and
						returns and int between 0 and n-1
    methods:
        sample_bandits(n): sample and train on n pulls.

    attributes:
        N: the cumulative number of samples
        choices: the historical choices as a (N,) array
        bb_score: the historical score as a (N,) array
    '''

    def __init__(self, bandits, choice_function):
        '''
        INPUT: Bandits, function

        Initializes the BanditStrategy given an instance of the Bandits class
        and a choice function.
        '''
        self.bandits = bandits
        n_bandits = len(self.bandits)
        self.wins = np.zeros(n_bandits)
        self.losses = np.zeros(n_bandits)
        self.trials = np.zeros(n_bandits)
        self.N = 0
        self.choices = []
        self.score = []
        self.choice_function = choice_function

    def sample_bandits(self, n=1):
        '''
        INPUT: int
        OUTPUT: None

        Simulate n rounds of running the bandit machine.
        '''
        score = np.zeros(n)
        choices = np.zeros(n)

        # seed the random number generators so you get the same results every
        # time.
        np.random.seed(101)
        random.seed(101)

        for k in range(n):
            #sample from the bandits's priors, and select the largest sample
            choice = self.choice_function(self)

            #sample the chosen bandit
            result = self.bandits.pull(choice)

            #update priors and score
            self.wins[choice] += result
            self.losses[choice] += result == False
            self.trials[choice] += 1
            score[k] = result
            self.N += 1
            choices[k] = choice

        self.score = np.r_[self.score, score]
        self.choices = np.r_[self.choices, choices]


    def max_mean(self):
        '''
        Pick the bandit with the current best observed proportion of winning.
        Return the index of the winning bandit.
        '''
        # make sure to play each bandit at least once
        if len(self.trials.nonzero()[0]) < len(self.bandits):
            return np.random.randint(0, len(self.bandits))
        return np.argmax(self.wins / (self.trials + 1))

    def random_choice(self):
        '''
        Pick a bandit uniformly at random.
        Return the index of the winning bandit.
        '''
        return np.random.randint(0, len(self.wins))

    def epsilon_greedy(self, epsilon=0.1):
        '''
        Pick a bandit uniformly at random epsilon percent of the time.
        Otherwise pick the bandit with the best observed proportion of winning.
        Return the index of the winning bandit.
        '''
        if random.random() < .1:
            return self.random_choice()
        else:
            return self.max_mean()

    def softmax(self, tau=0.001):
        '''
        Pick an bandit according to the Boltzman Distribution.
        Return the index of the winning bandit.
        '''
        totals = [item1 + item2 for item1, item2 in zip(self.wins, self.losses)]
        denominator = sum([math.exp((float(w)/t)/tau) for w, t in zip(self.wins, totals)])
        boltz = [math.exp((float(w)/t)/tau)/denominator for w, t in zip(self.wins, totals)]
        return boltz.index(max(boltz))


    def ucb1(self):
        '''
        Pick the bandit according to the UCB1 strategy.
        Return the index of the winning bandit.
        '''
        totals = [item1 + item2 for item1, item2 in zip(self.wins, self.losses)]
        if min(totals) == 0:
            return np.random.randint(0, len(self.wins))
        else:
            p_vals = [float(item1) / item2 for item1, item2 in zip(self.wins, totals)]
            ucb = map((lambda p: p + math.sqrt(2*math.log(self.N)/(self.wins[p] + self.losses[p]))), p_vals)
            return ucb.index(max(ucb))

    def bayesian_bandit(self):
        '''
        Randomly sample from a beta distribution for each bandit and pick the one
        with the largest value.
        Return the index of the winning bandit.
        '''
        betas = self.losses + 1
        alphas = self.wins + 1

        distr = [stats.beta.rvs(a=alpha, b=beta) for alpha, beta in zip(alphas, betas)]

        return distr.index(max(distr))
