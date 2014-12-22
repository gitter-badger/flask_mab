import unittest
from tests.test_utils import makeBandit
import random
import sys
from collections import Counter

class MonteCarloTest(unittest.TestCase):

    def draw(self, arm_name):
        if random.random() > self.true_arm_probs[arm_name]:
            return 0.0
        return 1.0

    @classmethod
    def get_bandit(cls):
        return makeBandit(cls.bandit_name, **cls.bandit_args)

    def run_algo(self, num_sims, horizon):
        chosen_arms = [0.0 for i in range(num_sims * horizon)]
        rewards = [0.0 for i in range(num_sims * horizon)]
        cumulative_rewards = [0.0 for i in range(num_sims * horizon)]
        sim_nums = [0.0 for i in range(num_sims * horizon)]
        times = [0.0 for i in range(num_sims * horizon)]

        for sim in range(num_sims):
            sim = sim + 1
            bandit = self.get_bandit()


            for t in range(horizon):
                t = t + 1
                index = (sim - 1) * horizon + t - 1
                sim_nums[index] = sim
                times[index] = t

                chosen_arm = bandit.suggest_arm()
                chosen_arms[index] = chosen_arm['id']
                reward = self.draw(chosen_arm['id'])
                rewards[index] = reward

                if t == 1:
                    cumulative_rewards[index] = reward
                else:
                    cumulative_rewards[index] = cumulative_rewards[index - 1] + reward

                if reward:
                    bandit.reward_arm(chosen_arm['id'], reward)

        return [sim_nums, times, chosen_arms, rewards, cumulative_rewards]

    def save_results(self, results, output_stream):
        for sim in range(len(results[0])):
            output_stream.write("  ".join([str(results[j][sim]) for j in range(len(results))]) + "\n")
            sys.stdout.flush()


class EpsilonGreedyTest(MonteCarloTest):

    bandit_name = 'EpsilonGreedyBandit'
    bandit_args = {'epsilon':0.3}
    true_arm_probs = dict(green=0.9, blue=0.1, red=0.1)

    def test_bandit(self):
        results = self.run_algo(5000, 250)
        data = Counter(results[2])
        assert data.most_common(1)[0][0] is 'green'

