import argparse
import random
from tabulate import tabulate

subtiers_per_tier = {
    'bronze': 6,
    'silver': 6,
    'gold': 6,
    'platinum': 6,
    'diamond': 6
}

def main(winrate, rank, tier, subtier, num_games, time):
    show_rank(winrate, tier, rank, subtier, time)
    random.seed()
    all_total_time = 0.0
    all_total_games = 0
    table = []
    while rank != 'mythic':
        total_games = 0
        for i in range(num_games):
            sim = Sim(winrate, rank, tier, subtier)
            total_games += sim.run()
        all_total_games += total_games / float(num_games)
        total_time = float(total_games / float(num_games)) * time / 60.0
        all_total_time += total_time
        sub_table = [get_next_rank(rank), all_total_games, all_total_time]
        table.append(sub_table)
        rank = get_next_rank(rank)
        tier = 4
        subtier = 0
    print()
    print(tabulate(table, headers=['To get to this rank', 'Games', 'Hours']))

def show_rank(winrate, rank, tier, subtier, time):
    print('{0} tier {1}, with {2} bars'.format(rank, tier, subtier))
    print('Assuming {0}% winrate'.format(winrate*100.0))
    print(f'Assuming {time} minute games')

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
        self.subtier = self.determine_progress(rank, tier, subtier)
        self.rank = rank
        self.protected_games = 0
    
    def determine_progress(self, rank, tier, subtier):
        total_subtiers = 4 * subtiers_per_tier[rank]
        return total_subtiers - (tier*subtiers_per_tier[rank]) + subtier
    
    def determine_tier(self, rank, subtier):
        return int(subtier / subtiers_per_tier[rank])
    
    def run(self):
        games = 0
        while self.subtier<24:
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
        if self.protected_games>0:
            self.protected_games -= 1
    
    def process_win(self):
        if self.win_raises_tier():
            self.protected_games = 3
        else:
            self.protected_games = 0
        if self.rank in ['bronze', 'silver']:
            self.subtier += 2
        else:
            self.subtier += 1
    
    def process_loss(self):
        if self.loss_drops_tier() and self.protected_games > 0:
            return
        if self.rank!='bronze':
            self.subtier -= 1
    
    def win_raises_tier(self):
        return (self.determine_tier(self.rank, self.subtier+1) > self.determine_tier(self.rank, self.subtier))

    def loss_drops_tier(self):
        return (self.determine_tier(self.rank, self.subtier-1) < self.determine_tier(self.rank, self.subtier))

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Analyze games to rank up to the next rank in MTGA based on winrate.')
    parser.add_argument('--winrate', type=float, help='Your winrate at the current rank.', default=0.5)
    parser.add_argument('--rank', type=str, help='Current rank', default='gold', choices=['bronze', 'silver', 'gold', 'platinum', 'diamond'])
    parser.add_argument('--tier', type=int, help='Your tier at the current rank.', default=4)
    parser.add_argument('--subtier', type=int, help='Your "blocks" on the meter at the current tier.', default=0)
    parser.add_argument('--runs', type=int, help='Sim runs to execute. Increases execution time and accuracy.', default=10000)
    parser.add_argument('--total-playtime', type=float, help='Total playtime, in minutes.', default=0.0)
    parser.add_argument('--total-games', type=int, help='Total games played so far.', default=1)
    args = parser.parse_args()
    main(args.winrate, args.rank, args.tier, args.subtier, args.runs, args.total_playtime/float(args.total_games))
