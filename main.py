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
    queue = '450'
    ritopls = riotrequester.RiotRequester()
    summoner = ritopls.get_summoner_by_name(name)
    last_match_ids = ritopls.get_matchlist_by_puuid(summoner['puuid'])
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
    queue_ids: list[str] = ritopls.get_queue_ids()
    db = dbhandler.DBHandler()
    puuids: list[str] | None = db.get_tracked_puuids() 
    match_ids: list[list[str, str]] = [] 
    for puuid, queue_id in itertools.product(puuids, queue_ids):
        matchlist = ritopls.get_matchlist_by_puuid(puuid, queue_id)
        if not matchlist:
            continue
        for match in matchlist:
            match_ids.append([queue_id, match]) 
    db.export_matchlist_to_local_db(match_ids)
    del db

def analyze_last_10_matches():
    db = dbhandler.DBHandler()
    match_ids = db.get_matchlist(queue_id="450", limit=0)
    del db
    ritopls = riotrequester.RiotRequester()
    current = 1
    total = len(match_ids)
    for match_id in match_ids:
        match_data = ritopls.get_match_by_match_id(match_id[0])
        # clear()
        msg = f'({current}/{total}) {match_id[0]}'
        print(msg)
        current += 1
        target = performance.MatchAnalyzer(match_data)     
        target.analyze()
        target.update_ratings()
        del target

def main_menu() -> None:
    print('''
    1. Track player
    2. harvest match ids
    3. Last match result
    4. Analyze last 10 Matches
    0. Exit
    ''')
    choice: int = int(input(':> '))
    clear()
    if choice == 0:
        exit()
    elif choice == 1:
        add_player_to_tracklist()
    elif choice == 2:
        harvest_match_ids()
    elif choice == 3:
        last_match_result()
    elif choice == 4:
        analyze_last_10_matches()
    elif choice == 5:
        pass
    else:
        print('Invalid Option')
    main_menu()
    

if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO)
    clear()
    main_menu()
