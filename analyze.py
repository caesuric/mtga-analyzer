import argparse
import random

def main(winrate, rank, tier, subtier, num_games):
    show_rank(winrate, tier, rank, subtier)
    random.seed()
    total = 0.0
    for i in range(num_games):
        sim = Sim(winrate, rank, tier, subtier)
        total += sim.run()
    total /= float(num_games)
    print('Need to play {0} games on average to rank up to {1}'.format(total, get_next_rank(rank)))

def show_rank(winrate, rank, tier, subtier):
    print('{0} tier {1}, with {2} bars'.format(rank, tier, subtier))
    print('Assuming {0}% winrate'.format(winrate*100.0))

def get_next_rank(rank):
    results = {
        'bronze': 'silver',
        'silver': 'gold',
        'gold': 'platinum',
        'platinum': 'diamond',
        'diamond': 'mythic'
    }
    return results[rank]

class Sim():
    def __init__(self, winrate, rank, tier, subtier):
        self.winrate = winrate
        self.subtier = self.determine_tier(rank, tier, subtier)
        self.rank = rank
    
    def determine_tier(self, rank, tier, subtier):
        subtiers_per_tier = {
            'bronze': 4,
            'silver': 5,
            'gold': 6,
            'platinum': 7,
            'diamond': 7
        }
        total_subtiers = 4 * subtiers_per_tier[rank]
        return total_subtiers - 1 - (tier*subtiers_per_tier[rank]) + subtier
    
    def run(self):
        games = 0
        while self.subtier<23:
            self.run_game()
            games += 1
        return games
    
    def run_game(self):
        roll = random.random()
        if roll<=self.winrate:
            self.process_win()
        else:
            self.process_loss()
        if self.subtier<0:
            self.subtier = 0
    
    def process_win(self):
        if self.rank in ['bronze', 'silver']:
            self.subtier += 2
        else:
            self.subtier += 1
    
    def process_loss(self):
        if self.rank!='bronze':
            self.subtier -= 1

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Analyze games to rank up to the next rank in MTGA based on winrate.')
    parser.add_argument('--winrate', type=float, help='Your winrate at the current rank.', default=0.5)
    parser.add_argument('--rank', type=str, help='Current rank', default='gold', choices=['bronze', 'silver', 'gold', 'platinum', 'diamond'])
    parser.add_argument('--tier', type=int, help='Your tier at the current rank.', default=4)
    parser.add_argument('--subtier', type=int, help='Your "blocks" on the meter at the current tier.', default=0)
    parser.add_argument('--runs', type=int, help='Sim runs to execute. Increases execution time and accuracy.', default=10000)
    args = parser.parse_args()
    main(args.winrate, args.rank, args.tier, args.subtier, args.runs)