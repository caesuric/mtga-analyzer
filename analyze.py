import argparse
import random

def main(winrate, tier, rank, subrank, num_games):
    show_tier(winrate, tier, rank, subrank)
    random.seed()
    total = 0.0
    for i in range(num_games):
        sim = Sim(winrate, tier, rank, subrank)
        total += sim.run()
    total /= float(num_games)
    print('Need to play {0} games on average to rank up to {1}'.format(total, get_next_tier(tier)))

def show_tier(winrate, tier, rank, subrank):
    print('{0} tier {1}, with {2} bars'.format(tier, rank, subrank))
    print('Assuming {0}% winrate'.format(winrate*100.0))

def get_next_tier(tier):
    results = {
        'bronze': 'silver',
        'silver': 'gold',
        'gold': 'platinum',
        'platinum': 'diamond',
        'diamond': 'mythic'
    }
    return results[tier]

class Sim():
    def __init__(self, winrate, tier, rank, subrank):
        self.winrate = winrate
        self.rank = self.determine_rank(tier, rank, subrank)
        self.tier = tier
    
    def determine_rank(self, tier, rank, subrank):
        subranks_per_tier = {
            'bronze': 4,
            'silver': 5,
            'gold': 6,
            'platinum': 7,
            'diamond': 7
        }
        total_subranks = 4 * subranks_per_tier[tier]
        return total_subranks - 1 - (rank*subranks_per_tier[tier]) + subrank
    
    def run(self):
        games = 0
        while self.rank<23:
            self.run_game()
            games += 1
        return games
    
    def run_game(self):
        roll = random.random()
        if roll<=self.winrate:
            self.process_win()
        else:
            self.process_loss()
        if self.rank<0:
            self.rank = 0
    
    def process_win(self):
        if self.tier in ['bronze', 'silver']:
            self.rank += 2
        else:
            self.rank += 1
    
    def process_loss(self):
        if self.tier!='bronze':
            self.rank -= 1

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Analyze games to rank up to the next tier in MTGA based on winrate.')
    parser.add_argument('--winrate', type=float, help='Your winrate at the current tier.', default=0.5)
    parser.add_argument('--tier', type=str, help='Current tier', default='gold', choices=['bronze', 'silver', 'gold', 'platinum', 'diamond'])
    parser.add_argument('--rank', type=int, help='Your rank at the current tier.', default=4)
    parser.add_argument('--subrank', type=int, help='Your "blocks" on the meter at the current rank.', default=0)
    parser.add_argument('--runs', type=int, help='Sim runs to execute. Increases execution time and accuracy.', default=10000)
    args = parser.parse_args()
    main(args.winrate, args.tier, args.rank, args.subrank, args.runs)