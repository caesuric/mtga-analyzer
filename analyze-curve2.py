import argparse
import random

# num_games = 1000000
num_games = 10000

def main(mana, turn, start, fetch_lands, mishras_baubles, once_upon_a_times, one_mana_dorks, utopia_sprawls, paradise_druids):
    random.seed()
    for lands in range(start,61):
        print (f'===== Trying {lands} lands... =====')
        successes = 0.0
        for _games in range(num_games):
            sim = Sim(lands, turn, fetch_lands, mishras_baubles, once_upon_a_times, one_mana_dorks, utopia_sprawls, paradise_druids)
            successes += float(sim.run_game(mana))
        if successes >= float(num_games) * 0.9:
            print (f'===== {lands} lands needed =====')
            return

class Sim:
    def __init__(self, num_lands, num_turns, fetch_lands, mishras_baubles, once_upon_a_times, one_mana_dorks, utopia_sprawls, paradise_druids):
        print(f'===== starting sim with {num_lands} total lands in deck, {num_turns} to achieve goal. =====')
        self.deck = []
        self.hand = []
        self.lands_played = 0
        self.mana_accelerators = 0
        self.mana_accelerators_played_this_turn = 0
        self.num_turns = num_turns
        for _ in range(fetch_lands):
            self.deck.append('fetch-land')
        for _ in range(mishras_baubles):
            self.deck.append('mishras-bauble')
        for _ in range(once_upon_a_times):
            self.deck.append('once-upon-a-time')
        for _ in range(one_mana_dorks):
            self.deck.append('one-mana-dork')
        for _ in range(utopia_sprawls):
            self.deck.append('utopia-sprawl')
        for _ in range(paradise_druids):
            self.deck.append('paradise-druid')
        for _ in range(num_lands - fetch_lands):
            self.deck.append('land')
        while len(self.deck) < 60:
            self.deck.append(None)

    def run_game(self, mana):
        print(f'goal is {mana} mana')
        random.shuffle(self.deck)
        self.draw_starting_hand()
        going_second = random.randint(0,1) # 1 is second, 0 is first
        if going_second == 1:
            print('going second, drawing card to start')
            self.draw_cards(1)
        self.play_once_upon_a_time_if_available()
        for turn in range(self.num_turns):
            print(f'now on turn {turn+1}')
            self.take_turn()
            print('drawing a card')
            self.draw_cards(1)
        return self.check_success(mana)
    
    def take_turn(self):
        self.mana_accelerators_played_this_turn = 0
        print(f'taking turn, hand is {self.hand}')
        mishras_bauble_manipulation_opportunity = False
        if 'fetch-land' in self.hand and 'land' in self.hand and 'mishras-bauble' in self.hand:
            mishras_bauble_manipulation_opportunity = True
        baubles = self.hand.count('mishras-bauble')
        if baubles > 0:
            print (f'playing {baubles} Mishra\'s Bauble(s)')
        while 'mishras-bauble' in self.hand:
            self.hand.remove('mishras-bauble')
        if mishras_bauble_manipulation_opportunity and (self.deck[0] is None or self.deck[0] == 'mishras-bauble'):
            print('playing fetch land to manipulate topdeck')
            self.play_fetch_land()
        elif mishras_bauble_manipulation_opportunity and (self.deck[0] is not None and self.deck[0] != 'mishras-bauble'):
            print('playing land to manipulate topdeck')
            self.play_land()
        elif 'fetch-land' in self.hand:
            self.play_fetch_land()
        elif 'land' in self.hand:
            self.play_land()        
        print(f'now have {self.lands_played} lands in play')
        advantageous_utopia_sprawl_played = False
        if self.lands_played > 1 and 'utopia-sprawl' in self.hand:
            print('playing Utopia Sprawl on different land from one used to cast it')
            self.hand.remove('utopia-sprawl')
            self.mana_accelerators += 1
            advantageous_utopia_sprawl_played = True
        mana_available = self.lands_played + self.mana_accelerators
        if advantageous_utopia_sprawl_played:
            mana_available -= 1
        while mana_available > 0 and 'utopia-sprawl' in self.hand:
            mana_available -= 1
            self.hand.remove('utopia-sprawl')
            self.mana_accelerators += 1
            self.mana_accelerators_played_this_turn += 1
            print('playing Utopia Sprawl')
        while mana_available > 1 and 'paradise-druid' in self.hand:
            mana_available -= 2
            self.hand.remove('paradise-druid')
            self.mana_accelerators_played_this_turn += 1
            self.mana_accelerators += 1
            print('playing Paradise Druid')
        while mana_available > 0 and 'one-mana-dork' in self.hand:
            mana_available -= 1
            self.hand.remove('one-mana-dork')
            print('playing one-mana dork')
            survival_roll = random.randint(0, 1)
            if survival_roll == 1:
                self.mana_accelerators += 1
                self.mana_accelerators_played_this_turn += 1
                print('one-mana dork survived')
            else:
                print('one-mana dork died')
        print(f'now have total of {self.lands_played + self.mana_accelerators} mana available for next turn')
        if baubles > 0:
            print(f'drawing {baubles} cards from Mishra\'s Baubles')
        self.draw_cards(baubles)
    
    def play_fetch_land(self):
        print('playing a fetch land')
        self.hand.remove('fetch-land')
        if 'land' in self.deck:
            self.deck.remove('land')
            random.shuffle(self.deck)
            self.lands_played += 1
    
    def play_land(self):
        print('playing a land')
        self.hand.remove('land')
        self.lands_played += 1

    def play_once_upon_a_time_if_available(self):
        if 'once-upon-a-time' in self.hand:
            print('playing Once Upon a Time')
            self.hand.remove('once-upon-a-time')
            looking_at = self.deck[0:5]
            if 'fetch-land' in looking_at:
                print('grabbing a fetch land with Once Upon a Time')
                self.hand.append('fetch-land')
                looking_at.remove('fetch-land')
            elif 'land' in looking_at:
                print('grabbing a land with Once Upon a Time')
                self.hand.append('land')
                looking_at.remove('land')
            else:
                print('grabbing a random card with Once Upon a Time')
                self.hand.append(looking_at[0])
            self.deck = self.deck[5:]
            for item in looking_at:
                self.deck.append(item)

    def draw_starting_hand(self):
        number_to_return = 0
        print('drawing 7 cards')
        self.draw_cards(7)
        print(f'hand is {self.hand}')
        while self.should_take_mulligan():
            print('need to mulligan')
            number_to_return += 1
            print(f'now need to return {number_to_return} cards to deck')
            print('putting hand back in deck')
            for item in self.hand:
                self.deck.append(item)
            random.shuffle(self.deck)
            self.hand = []
            print('drawing 7 cards')
            self.draw_cards(7)
            print(f'hand is {self.hand}')
            print(f'returning {number_to_return} cards to deck')
            for _ in range(number_to_return):
                if None in self.hand:
                    print('returning non-tracked card to deck')
                    self.hand.remove(None)
                    self.deck.append(None)
                elif 'mishras-bauble' in self.hand:
                    print('returning Mishra\'s Bauble to deck')
                    self.hand.remove('mishras-bauble')
                    self.deck.append('mishras-bauble')
                else:
                    print('returning random card to deck')
                    self.deck.append(self.hand[0])
                    self.hand.remove(self.hand[0])
    
    def draw_cards(self, number):
        for _ in range(number):
            card = self.deck[0]
            self.hand.append(card)
            self.deck.remove(card)
    
    def should_take_mulligan(self):
        print('deciding whether to mulligan')
        if len(self.hand)==4:
            print('hand too small, not doing mulligan')
            return False
        count = 0.0
        once_upon_a_time_counted = False
        for item in self.hand:
            if item == 'land' or item == 'fetch-land':
                count += 1.0
            elif item == 'once-upon-a-time' and not once_upon_a_time_counted:
                count += 1.0
                once_upon_a_time_counted = True
            elif item == 'mishras-bauble':
                count += 0.5
        print(f'count of lands and equivalents is {count}')
        if count <= 1 or count >= 6:
            print(f'count of lands and equivalents is {count}, too high or low, doing mulligan')
            return True
        return False
    
    def check_success(self, mana):
        if self.lands_played + self.mana_accelerators - self.mana_accelerators_played_this_turn >= mana:
            return True
        return False

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Give lands needed for a 90%% ability to cast a spell with a certain number of colored mana on a given turn.')
    parser.add_argument('--mana', type=int, help='Mana required (either of color or overall).', default=1)
    parser.add_argument('--turn', type=int, help='Turn of game', default=1)
    parser.add_argument('--start', type=int, help='Lands to start trying from', default=1)
    parser.add_argument('--fetch-lands', type=int, help='Number of fetch lands to include', default=0)
    parser.add_argument('--mishras-baubles', type=int, help='Number of Mishra\'s Baubles to include', default=0)
    parser.add_argument('--once-upon-a-times', type=int, help='Number of Once Upon a Times to include', default=0)
    parser.add_argument('--one-mana-dorks', type=int, help='Number of one-mana dorks to include', default=0)
    parser.add_argument('--utopia-sprawls', type=int, help='Number of Utopia Sprawls to include', default=0)
    parser.add_argument('--paradise-druids', type=int, help='Number of Paradise Druids to include', default=0)
    args = parser.parse_args()
    main(args.mana, args.turn, args.start, args.fetch_lands, args.mishras_baubles, args.once_upon_a_times, args.one_mana_dorks, args.utopia_sprawls, args.paradise_druids)
