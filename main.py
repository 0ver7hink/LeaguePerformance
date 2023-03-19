from classes import riotrequester
from classes import dbhandler
from classes import performance
from typing import Any
from pprint import pprint
import itertools
import logging
import os


def clear() -> None:
    os.system('clear')

def last_match_result() -> None:
    name = 'Norcia'
    ritopls = riotrequester.RiotRequester()
    summoner = ritopls.get_summoner_by_name(name)
    last_match_ids = ritopls.get_matchlist_by_puuid(summoner['puuid'], 1)
    match_id = last_match_ids[0]
    match = ritopls.get_match_by_match_id(match_id)
    target = performance.MatchAnalyzer(match)
    target.analyze()

def add_player_to_tracklist() -> None:
    msg: str = 'Player name: ' 
    print('(To exit, isnert 0)')
    name: str = input(msg)
    clear()
    if name == '0':
        return
    db = dbhandler.DBHandler()
    db.track_player(name)
    del db

def harvest_match_ids() -> None:
    ritopls = riotrequester.RiotRequester()
    db = dbhandler.DBHandler()
    puuids: list[str] = db.get_tracked_puuids() 
    total: int = len(puuids)
    current: int = 0
    match_ids: list[str] = [] 
    for puuid in puuids:
        current += 1
        matchlist = ritopls.get_matchlist_by_puuid(puuid)
        if not matchlist:
            continue
        for match in matchlist:
            match_ids.append(match) 
        msg = f'({current}/{total}) -> {len(match_ids)}'
        clear()
        print(msg)
    db.export_matchlist_to_local_db(match_ids)
    del db

def analyze_matches():
    db = dbhandler.DBHandler()
    match_ids = db.get_matchlist()
    del db
    total = len(match_ids)
    for idx, match_id in enumerate(match_ids):
        msg = f'({idx}/{total}) {match_id[0]}'
        try:
            analyze_match(match_id)
            print(msg)
        except TypeError as e:
            print(f'An error has occured: {e}')

def analyze_match(match_id) -> None:
    ritopls = riotrequester.RiotRequester()
    match_data = ritopls.get_match_by_match_id(match_id[0])
    clear()
    target = performance.MatchAnalyzer(match_data)     
    target.analyze()
    target.update_ratings()
    del target

def menu_index() -> None:
    print('''
    1. Track player
    2. harvest match ids
    3. Last match result
    4. Analyze Matches
    0. Exit
    ''')

def run_command(command: str) -> None:
    match command:
        case '0':
            exit()
        case '1':
            add_player_to_tracklist()
        case '2':
            harvest_match_ids()
        case '3':
            last_match_result()
        case '4':
            analyze_matches()
        case other:
            clear()
            print('Invalid command')

def main() -> None:
    clear()
    while True:
        menu_index()
        command: str = input(':> ')
        run_command(command)

if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    main()
