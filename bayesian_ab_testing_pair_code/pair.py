from bandits import Bandits
from banditstrategy import BanditStrategy
import numpy as np


def regret(probabilities, choices):
    '''
    INPUT: array of floats (0 to 1), array of ints
    OUTPUT: array of floats

    Take an array of the true probabilities for each machine and an
    array of the indices of the machine played at each round.
    Return an array giving the total regret after each round.
    '''
    p_opt = np.max(probabilities)
    return np.cumsum(p_opt - probabilities[choices])


def run_bandits_run(bandits = Bandits([0.05, 0.03, 0.06]), choice = BanditStrategy.random_choice):
    strat = BanditStrategy(bandits, choice)
    strat.sample_bandits(1000)
    print regret(bandits, strat.wins)
    # print "Number of trials:", strat.trials
    # print "Number of wins:", strat.wins
    # print "Conversion rates:", strat.wins / strat.trials
    # print "A total of %d wins of %d trials." % \
    #     (strat.wins.sum(), strat.trials.sum())

l = [[0.1, 0.1, 0.1, 0.1, 0.9], [0.1, 0.1, 0.1, 0.1, 0.12], [0.1, 0.2, 0.3, 0.4, 0.5]]








# for item in l:
    # print '/n --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- /n'
    # run_bandits_run(choice = BanditStrategy.epsilon_greedy, bandits = Bandits(item))
    # run_bandits_run(choice = BanditStrategy.softmax, bandits = Bandits(item))
    # run_bandits_run(choice = BanditStrategy.ucb1, bandits = Bandits(item))
    # run_bandits_run(choice = BanditStrategy.bayesian_bandit, bandits = Bandits(item))
