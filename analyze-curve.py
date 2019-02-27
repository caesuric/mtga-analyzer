import argparse
import random

num_games = 1000000

def main(mana, turn, start):
    random.seed()
    for lands in range(start,61):
        print ('Trying {0} lands...'.format(lands))
        successes = 0.0
        for games in range(num_games):
            sim = Sim(lands, turn)
            successes += float(sim.run_game(mana))
        if successes >= float(num_games) * 0.9:
            print ('{0} lands needed'.format(lands))
            return

class Sim:
    def __init__(self, num_lands, num_turns):
        self.deck = []
        self.hand = []
        self.num_turns = num_turns
        for x in range(num_lands):
            self.deck.append(True)
        while len(self.deck)<60:
            self.deck.append(False)

    def run_game(self, mana):
        self.draw_starting_hand()
        going_second = random.randint(0,1)
        for turn in range(self.num_turns - 1 + going_second):
            self.draw_cards(1)
        return self.check_success(mana)
    
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
            card = random.choice(self.deck)
            self.hand.append(card)
            self.deck.remove(card)
    
    def should_take_mulligan(self):
        if len(self.hand)==4:
            return False
        count = 0
        for item in self.hand:
            if item:
                count += 1
        if count <= 1 or count >= 6:
            return True
        return False
    
    def check_success(self, mana):
        count = 0
        for item in self.hand:
            if item:
                count += 1
        if count >= mana:
            return True
        return False

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Give lands needed for a 90%% ability to cast a spell with a certain number of colored mana on a given turn.')
    parser.add_argument('--mana', type=int, help='Colored mana required.', default=1)
    parser.add_argument('--turn', type=int, help='Turn of game', default=1)
    parser.add_argument('--start', type=int, help='Lands to start trying from', default=1)
    args = parser.parse_args()
    main(args.mana, args.turn, args.start)
