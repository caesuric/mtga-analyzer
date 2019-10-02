import random
import csv
import json

num_games = 1000

def main():
    random.seed()
    total = 0.0
    for i in range(num_games):
        sim = Sim()
        total += sim.run()
    total /= float(num_games)
    print ('Chances to achieve goal are {0}%'.format(total*100.0))

class Sim():
    def __init__(self):
        self.cards = []
        with open('draw-analyzer-deck.csv') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                self.cards.append(row)
        with open('draw-analyzer-requirement.json') as json_file:
            self.requirements = json.loads(json_file.read())
        self.form_deck()

    def form_deck(self):
        self.deck = []
        for card in self.cards:
            for i in range(int(card['count'])):
                self.deck.append(Card(card['mana'], card['makes_mana'], card['cantrip']=="TRUE", int(card['wincon']), card['special']))
        for mana_basis in self.requirements['manaBase']:
            for i in range(mana_basis['copies']):
                self.deck.append(Card('L', mana_basis['mana'], False, -1, -1))
        count = 0
        for outcome in self.requirements['successfulOutcomes']:
            if outcome['autoAdd']:
                for i in range(outcome['copiesOfNeededCard']):
                    self.deck.append(Card('X', '', False, count, -1))
            count += 1
        while len(self.deck)<60:
            self.deck.append(Card('X', '', False, -1, -1))
        random.shuffle(self.deck)
    
    def run(self):
        turn = 1
        self.hand = []
        self.played = []
        self.mana_available = ''
        self.total_mana_available = 0
        for i in range(7):
            self.hand.append(self.draw())
        while turn <= self.requirements['turn']:
            if turn>1:
                self.hand.append(self.draw())
            self.play_land()
            if turn == self.requirements['turn']:
                return self.check_conditions()
            self.select_and_play_card()
            turn += 1
    
    def draw(self):
        return self.deck.pop()
    
    def play_land(self):
        for card in self.hand:
            if card.mana == 'L' and self.helps_mana_requirements(card):
                self.play_card(card)
                return
        for card in self.hand:
            if card.mana == 'L':
                self.play_card(card)
                return
    
    def helps_mana_requirements(self, card):
        if card.makes_mana == '*':
            return True
        for outcome in self.requirements['successfulOutcomes']:
            if card.makes_mana!='' and card.makes_mana in outcome['mana']:
                return True
        return False
    
    def play_card(self, card):
        self.played.append(card)
        self.hand.remove(card)
        self.mana_available += card.makes_mana
        if card.makes_mana!='':
            self.total_mana_available += 1
    
    def check_conditions(self):
        count = 0
        for condition in self.requirements['successfulOutcomes']:
            if self.condition_met(condition, count):
                return True
            count += 1
        return False
    
    def condition_met(self, condition, wincon_number):
        return self.mana_requirements_met(condition) and self.wincon_met(condition, wincon_number)
    
    def mana_requirements_met(self, condition):
        condition_total_mana_count = self.get_cmc(condition['mana'])
        condition_colored_mana_only = self.get_colored_mana(condition['mana'])
        available_colored_mana_only = self.get_colored_mana(self.mana_available)
        if self.total_mana_available < condition_total_mana_count:
            return False
        for x in condition_colored_mana_only:
            condition_count = condition_colored_mana_only.count(x)
            available_count = available_colored_mana_only.count(x)
            available_count += available_colored_mana_only.count('*')
            if available_count < condition_count:
                return False
        return True
    
    def get_cmc(self, mana_cost):
        count = 0
        for x in mana_cost:
            if x in '123456789':
                num = int(x)
                count += num
            else:
                count += 1
        return count
    
    def get_colored_mana(self, mana_cost):
        output = ''
        for x in mana_cost:
            if x not in '123456789':
                output += x
        return output
    
    def wincon_met(self, condition, wincon_number):
        for card in self.hand:
            if card.wincon==wincon_number:
                return True
        for card in self.played:
            if card.wincon==wincon_number:
                return True
        return False
    
    def select_and_play_card(self):
        for card in self.hand:
            if self.playable(card) and self.helps_mana_requirements(card):
                self.play_card(card)
                return
        for card in self.hand:
            if self.playable(card) and card.cantrip:
                self.play_card(card)
                self.hand.append(self.draw())
                if card.special==0:
                    self.play_land()
                return
    
    def playable(self, card):
        card_total_mana_count = self.get_cmc(card.mana)
        card_colored_mana_only = self.get_colored_mana(card.mana)
        available_colored_mana_only = self.get_colored_mana(
            self.mana_available)
        if self.total_mana_available < card_total_mana_count:
            return False
        for x in card_colored_mana_only:
            condition_count = card_colored_mana_only.count(x)
            available_count = available_colored_mana_only.count(x)
            available_count += available_colored_mana_only.count('*')
            if available_count < condition_count:
                return False
        return True


class Card():
    def __init__(self, mana, makes_mana, cantrip, wincon, special):
        self.mana = mana
        self.makes_mana = makes_mana
        self.cantrip = cantrip
        self.wincon = wincon
        self.special = special

if __name__=='__main__':
    main()
