import json
import random
import os
import sys
import time
import threading
import hashlib
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from tabulate import tabulate
from pathlib import Path

num_sim_games = 10000
subtiers_per_tier = {
    'Bronze': 6,
    'Silver': 6,
    'Gold': 6,
    'Platinum': 6,
    'Diamond': 6
}
log_path = os.path.join('data', 'show-progress-log.json')

def main():
    appdata_path = Path(os.getenv('APPDATA')).parent
    appdata_path = appdata_path.joinpath('LocalLow').joinpath('Wizards of The Coast').joinpath('MTGA')
    log_path = appdata_path.joinpath('Player-prev.log')
    log_path2 = appdata_path.joinpath('Player.log')
    log_data = LogData()
    parse_logs(log_data, log_path, log_path2)
    time1 = get_time(str(log_path))
    time2 = get_time(str(log_path2))
    app = create_main_window(log_data)
    launch_main_loop(app, time1, time2, log_path, log_path2, log_data)
    app.mainloop()

def create_main_window(log_data):
    root = tk.Tk()
    root.overrideredirect(1)
    root.attributes('-topmost', 'true')
    app = Application(log_data, master=root)
    return app

def launch_main_loop(app, time1, time2, log_path, log_path2, log_data):
    t = threading.Thread(target=main_loop, args=(app,time1,time2,log_path,log_path2,log_data))
    t.start()

def main_loop(app, time1, time2, log_path, log_path2, log_data):
    while app.running:
        time1, time2 = main_loop_iteration(app, time1, time2, log_path, log_path2, log_data)
    sys.exit()

def main_loop_iteration(app, time1, time2, filename1, filename2, log_data):
    new_time1 = get_time(str(filename1))
    new_time2 = get_time(str(filename2))
    if new_time1 != time1 or new_time2 != time2:
        parse_logs(log_data, filename1, filename2)
        update_window_labels(log_data, app)
    time.sleep(1)
    return new_time1, new_time2

def update_window_labels(log_data, app):
    match_stats = get_match_stats(log_data)
    game_time = match_stats['time'] / 60.0 / 60.0 / 10000000.0 / (match_stats['wins'] + match_stats['losses'])
    table = run_sims(log_data.rank_detail, match_stats['win_percent'], game_time)
    app.rank_text.config(text=f'At rank {log_data.rank_detail["rank"]}, tier {log_data.rank_detail["tier"]}, subtier {log_data.rank_detail["subtier"]}')
    app.using_deck_text.config(text=f'Using deck {log_data.decks[match_stats["most_recent_deck"]]}')
    app.win_percent_text.config(text=f'Win percent {match_stats["win_percent"] * 100:.2f}%')
    app.played_time_text.config(text=f'Played this deck for {match_stats["time"] / 60 / 10000000:.2f} minutes')
    app.table_text.config(text=tabulate(table, headers=['To get to this rank', 'Games', 'Hours']))

class Application(tk.Frame):
    def __init__(self, log_data, master=None):
        super().__init__(master)
        self.master = master
        self.running = True
        self.pack()
        self.create_widgets(log_data)
    
    def create_widgets(self, log_data):
        match_stats = get_match_stats(log_data)
        game_time = match_stats['time'] / 60.0 / 60.0 / 10000000.0 / (match_stats['wins'] + match_stats['losses'])
        table = run_sims(log_data.rank_detail, match_stats['win_percent'], game_time)
        self.font = tkfont.Font(family='Courier', size=10)
        self.rank_text = tk.Label(text=f'At rank {log_data.rank_detail["rank"]}, tier {log_data.rank_detail["tier"]}, subtier {log_data.rank_detail["subtier"]}', font=self.font)
        self.rank_text.pack(side='top')
        self.using_deck_text = tk.Label(text=f'Using deck {log_data.decks[match_stats["most_recent_deck"]]}', font=self.font)
        self.using_deck_text.pack(side='top')
        self.win_percent_text = tk.Label(text=f'Win percent {match_stats["win_percent"] * 100:.2f}%', font=self.font)
        self.win_percent_text.pack(side='top')
        self.played_time_text = tk.Label(text=f'Played this deck for {match_stats["time"] / 60 / 10000000:.2f} minutes', font=self.font)
        self.played_time_text.pack(side='top')
        self.separator = ttk.Separator(orient='horizontal')
        self.separator.pack(side='top', fill='x')
        self.table_text = tk.Label(text=tabulate(table, headers=['To get to this rank', 'Games', 'Hours']), font=self.font)
        self.table_text.pack(side='top')
        self.exit_button = tk.Button(text='Exit', command=self.exit)
        self.exit_button.pack(side='top')
    
    def exit(self):
        self.running = False
        self.master.destroy()

def get_time(filename):
    return os.stat(filename).st_mtime

def parse_logs(log_data, log_path, log_path2):
    load_log_data(log_data)
    log_data.parse_log(log_path)
    log_data.parse_log(log_path2)
    save_log_data(log_data)

def load_log_data(log_data):
    if os.path.exists(log_path):
        with open(log_path) as log_file:
            data = log_file.read()
            obj = json.loads(data)
            log_data.from_json(obj)

def save_log_data(log_data):
    with open(log_path, 'w') as log_file:
        obj = log_data.to_json()
        data = json.dumps(obj)
        log_file.write(data)

def show_results(log_data):
    match_stats = get_match_stats(log_data)
    print(f'At rank {log_data.rank_detail["rank"]}, tier {log_data.rank_detail["tier"]}, subtier {log_data.rank_detail["subtier"]}')
    print(f'Using deck {log_data.decks[match_stats["most_recent_deck"]]}')
    print(f'Win percent {match_stats["win_percent"] * 100}%')
    print(match_stats['time'] / 60 / 10000000, 'minutes')

def get_match_stats(log_data):
    output = {'wins': 0, 'losses': 0, 'time': 0, 'most_recent_deck': log_data.matches[-1]['deck']}
    for match in log_data.matches:
        if match['deck'] == output['most_recent_deck'] and match['won']:
            output['wins'] += 1
            output['time'] += int(match['end']) - int(match['start'])
        elif match['deck'] == output['most_recent_deck']:
            output['losses'] += 1
            output['time'] += int(match['end']) - int(match['start'])
    output['win_percent'] = output['wins'] / (output['wins'] + output['losses'])
    return output

def run_sims(rank_detail, winrate, game_time):
    random.seed()
    total_time = 0.0
    game_count = 0
    table = []
    while rank_detail['rank'] != 'Mythic':
        total_time, game_count, table = run_sim_set(rank_detail['rank'], rank_detail['tier'], rank_detail['subtier'], winrate, game_time, total_time, game_count, table)
        rank_detail = {'rank': get_next_rank(rank_detail['rank']), 'tier': 4, 'subtier': 0}
    return table

def run_sim_set(rank, tier, subtier, winrate, game_time, total_time, game_count, table):
    game_count_subtotal = 0
    for i in range(num_sim_games):
        sim = Sim(winrate, rank, tier, subtier)
        game_count_subtotal += sim.run()
    game_count += game_count_subtotal / float(num_sim_games)
    time_subtotal = float(game_count_subtotal / float(num_sim_games)) * game_time
    total_time += time_subtotal
    sub_table = [get_next_rank(rank), game_count, total_time]
    table.append(sub_table)
    return total_time, game_count, table

class LogData():
    def __init__(self):
        self.decks = []
        self.matches = []
        self.rank_detail = {}
        self.deck_ids = {}
        self.current_match = {}
        self.player_name = ''
        self.deck_list_string = ''
        self.rank_detail_string = ''
        self.selected_deck = ''
        self.team_id = 0
        self.parsing_match = False
        self.handler_table = {
            '[Accounts - Client] Successfully logged in to account: ': self.handle_login,
            'Deck.GetDeckListsV3': self.handle_get_deck_list,
            'Event.GetCombinedRankInfo': self.handle_get_rank_info,
            '<== Deck.CreateDeckV3': self.handle_create_deck,
            '<== Deck.UpdateDeckV3': self.handle_update_deck,
            '[UnityCrossThreadLogger]<== Event.DeckSubmitV3 ': self.handle_deck_submit,
            'Event.MatchCreated': self.handle_match_created,
            'MatchGameRoomStateChangedEvent': self.handle_state_changed_event
        }
    
    def to_json(self):
        return {
            'decks': self.decks,
            'matches': self.matches,
            'rank_detail': self.rank_detail,
            'deck_ids': self.deck_ids,
            'current_match': self.current_match,
            'player_name': self.player_name,
            'deck_list_string': self.deck_list_string,
            'rank_detail_string': self.rank_detail_string,
            'selected_deck': self.selected_deck,
            'team_id': self.team_id,
            'parsing_match': self.parsing_match
        }
    
    def from_json(self, data):
        self.decks = data['decks']
        self.matches = data['matches']
        self.rank_detail = data['rank_detail']
        self.deck_ids = data['deck_ids']
        self.current_match = data['current_match']
        self.player_name = data['player_name']
        self.deck_list_string = data['deck_list_string']
        self.rank_detail_string = data['rank_detail_string']
        self.selected_deck = data['selected_deck']
        self.team_id = data['team_id']
        self.parsing_match = data['parsing_match']
    
    def handle_login(self, logfile, line):
        self.player_name = line.replace('[Accounts - Client] Successfully logged in to account: ', '').strip()
    
    def handle_get_deck_list(self, logfile, line):
        self.deck_list_string = line

    def handle_get_rank_info(self, logfile, line):
        self.rank_detail_string = line

    def handle_create_deck(self, logfile, line):
        create_deck_obj = json.loads(line.replace('[UnityCrossThreadLogger]<== Deck.CreateDeckV3 ', '').strip())['payload']
        self.deck_ids[create_deck_obj['id']] = create_deck_obj['name']

    def handle_update_deck(self, logfile, line):
        update_deck_obj = json.loads(line.replace('[UnityCrossThreadLogger]<== Deck.UpdateDeckV3 ', '').strip())['payload']
        self.deck_ids[update_deck_obj['id']] = update_deck_obj['name']

    def handle_deck_submit(self, logfile, line):
        deck_selected_obj = json.loads(line.replace('[UnityCrossThreadLogger]<== Event.DeckSubmitV3 ', '').strip())
        event = deck_selected_obj['payload']
        if event['InternalEventName'] == 'Ladder' and event['ModuleInstanceData']['DeckSelected']:
            self.selected_deck = event['CourseDeck']['id']

    def handle_match_created(self, logfile, line):
        self.current_match = {'won': None, 'deck': self.selected_deck}
        self.parsing_match = True

    def handle_state_changed_event(self, logfile, line):
        line = logfile.readline()
        match_game_obj = json.loads(line.strip())
        if self.parsing_match:
            self.current_match['id'] = match_game_obj['matchGameRoomStateChangedEvent']['gameRoomInfo']['gameRoomConfig']['matchId']
            if 'reservedPlayers' in match_game_obj['matchGameRoomStateChangedEvent']['gameRoomInfo']['gameRoomConfig']:
                self.get_team_id(match_game_obj['matchGameRoomStateChangedEvent']['gameRoomInfo']['gameRoomConfig']['reservedPlayers'])
        if 'finalMatchResult' in match_game_obj['matchGameRoomStateChangedEvent']['gameRoomInfo']:
            self.get_win_status(match_game_obj['matchGameRoomStateChangedEvent']['gameRoomInfo']['finalMatchResult']['resultList'])
    
    def get_team_id(self, reserved_players):
        for player in reserved_players:
            if player['playerName'] == self.player_name:
                self.team_id = player['teamId']
    
    def get_win_status(self, result_list):
        for result in result_list:
            if result['scope'] == 'MatchScope_Game' and result['result'] == 'ResultType_WinLoss':
                self.current_match['won'] = self.team_id == result['winningTeamId']

    def handle_gre_to_client_event(self, logfile, line):
        line = logfile.readline()
        if '[Message summarized because one or more GameStateMessages exceeded the 50 GameObject or 50 Annotation limit.]' in line:
            return
        client_event = json.loads(line)
        if 'start' not in self.current_match:
            self.current_match['start'] = client_event['timestamp']
        for entry in client_event['greToClientEvent']['greToClientMessages']:
            if 'start' in self.current_match and entry['type'] == 'GREMessageType_GameStateMessage' and 'gameInfo' in entry['gameStateMessage'] and 'stage' in entry['gameStateMessage']['gameInfo'] and entry['gameStateMessage']['gameInfo']['stage'] == 'GameStage_GameOver' and not self.match_already_parsed():
                self.end_parsing_match(client_event)

    def end_parsing_match(self, client_event):
        self.current_match['end'] = client_event['timestamp']
        self.matches.append(self.current_match)
        self.parsing_match = False
    
    def match_already_parsed(self):
        for match in self.matches:
            if match['id'] == self.current_match['id'] and match['won'] is not None:
                return True
            elif match['id'] == self.current_match['id'] and match['won'] is None:
                self.matches.remove(match)
                return False
        return False
        
    def parse_log(self, log_path):
        self.read_log_file(log_path)
        self.set_parse_variables()
    
    def read_log_file(self, log_path):
        with log_path.open() as logfile:
            line = logfile.readline()
            while line:
                for key in self.handler_table:
                    if key in line:
                        self.handler_table[key](logfile, line)
                        break
                if self.parsing_match and 'GreToClientEvent' in line:
                    self.handle_gre_to_client_event(logfile, line)
                line = logfile.readline()
    
    def set_parse_variables(self):
        self.decks = get_decks(self.deck_list_string, self.deck_ids)
        self.rank_detail = get_rank_detail(self.rank_detail_string)

def get_decks(deck_list_string, decks):
    deck_list_string = deck_list_string.replace('[UnityCrossThreadLogger]<== Deck.GetDeckListsV3 ', '').strip()
    deck_list_obj = json.loads(deck_list_string)
    for entry in deck_list_obj['payload']:
        decks[entry['id']] = entry['name']
    return(decks)

def get_rank_detail(rank_detail_string):
    rank_detail_string = rank_detail_string.replace('[UnityCrossThreadLogger]<== Event.GetCombinedRankInfo ', '').strip()
    rank_detail_obj = json.loads(rank_detail_string)['payload']
    return {
        'rank': rank_detail_obj['constructedClass'],
        'tier': rank_detail_obj['constructedLevel'],
        'subtier': rank_detail_obj['constructedStep']
    }

def show_rank(winrate, rank, tier, subtier, time):
    print('{0} tier {1}, with {2} bars'.format(rank, tier, subtier))
    print('Assuming {0}% winrate'.format(winrate*100.0))
    print(f'Assuming {time} minute games')

def get_next_rank(rank):
    results = {
        'Bronze': 'Silver',
        'Silver': 'Gold',
        'Gold': 'Platinum',
        'Platinum': 'Diamond',
        'Diamond': 'Mythic'
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
        if self.rank in ['Bronze', 'Silver']:
            self.subtier += 2
        else:
            self.subtier += 1
    
    def process_loss(self):
        if self.loss_drops_tier() and self.protected_games > 0:
            return
        if self.rank!='Bronze':
            self.subtier -= 1
    
    def win_raises_tier(self):
        return (self.determine_tier(self.rank, self.subtier+1) > self.determine_tier(self.rank, self.subtier))

    def loss_drops_tier(self):
        return (self.determine_tier(self.rank, self.subtier-1) < self.determine_tier(self.rank, self.subtier))

if __name__=='__main__':
    main()
