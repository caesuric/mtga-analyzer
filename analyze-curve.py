import argparse
import random

num_games = 1000000

def main(mana, turn, start, fetch_lands, mishras_baubles, once_upon_a_times):
    random.seed()
    for lands in range(start,61):
        print (f'Trying {lands} lands...')
        successes = 0.0
        for games in range(num_games):
            sim = Sim(lands, turn, fetch_lands, mishras_baubles, once_upon_a_times)
            successes += float(sim.run_game(mana))
        if successes >= float(num_games) * 0.9:
            print (f'{lands} lands needed')
            return

class Sim:
    def __init__(self, num_lands, num_turns, fetch_lands, mishras_baubles, once_upon_a_times):
        self.deck = []
        self.hand = []
        self.num_turns = num_turns
        for _ in range(fetch_lands):
            self.deck.append('fetch-land')
        for _ in range(mishras_baubles):
            self.deck.append('mishras-bauble')
        for _ in range(once_upon_a_times):
            self.deck.append('once-upon-a-time')
        for _ in range(num_lands):
            self.deck.append('land')
        while len(self.deck)<60:
            self.deck.append(None)

    def run_game(self, mana):
        random.shuffle(self.deck)
        self.draw_starting_hand()
        going_second = random.randint(0,1)
        for turn in range(self.num_turns - 1 + going_second):
            self.draw_cards(1)
            self.take_turn(turn)
        return self.check_success(mana)
    
    def take_turn(self, turn_number):
        if turn_number == 0:
            if 'once-upon-a-time' in self.hand:
                self.hand.remove('once-upon-a-time')
                looking_at = self.deck[0:5]
                for item in looking_at:
                    self.deck.remove(item)
                    self.deck.append(item)
                for item in looking_at:
                    if item == 'land' or item == 'fetch-land':
                        self.hand.append(item)
                        self.deck.remove(item)
                        break
        cast_mishras_bauble_count = 0
        while 'mishras-bauble' in self.hand:
            self.hand.remove('mishras-bauble')
            cast_mishras_bauble_count += 1
        if cast_mishras_bauble_count > 0 and 'fetch-land' in self.hand and 'land' in self.hand:
            if self.deck[0] == 'land' or self.deck[0] == 'fetch-land':
                self.hand.append(self.deck[0])
                self.deck.remove(self.deck[0])
            else:
                self.hand.remove('fetch-land')
                self.deck.remove('land')
                self.hand.append('land')
                random.shuffle(self.deck)
                self.hand.append(self.deck[0])
                self.deck.remove(self.deck[0])
            cast_mishras_bauble_count -= 1
        if cast_mishras_bauble_count > 0:
            self.draw_cards(cast_mishras_bauble_count)
        while 'fetch-land' in self.hand:
            self.hand.remove('fetch-land')
            self.deck.remove('land')
            self.hand.append('land')
            random.shuffle(self.deck)


    def draw_starting_hand(self):
        number = 7
        self.draw_cards(number)
        while self.should_take_mulligan():
            number -= 1
            for item in self.hand:
                self.deck.append(item)
            self.hand = []
            self.draw_cards(number)
    
    def draw_cards(self, number):
        for i in range(number):
            card = self.deck[0]
            self.hand.append(card)
            self.deck.remove(card)
    
    def should_take_mulligan(self):
        if len(self.hand)==4:
            return False
        count = 0
        for item in self.hand:
            if item is not None:
                count += 1
        if count <= 1 or count >= 6:
            return True
        return False
    
    def check_success(self, mana):
        count = 0
        for item in self.hand:
            if item == 'land':
                count += 1
        if count >= mana:
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
    args = parser.parse_args()
    main(args.mana, args.turn, args.start, args.fetch_lands, args.mishras_baubles, args.once_upon_a_times)
