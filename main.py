from classes import riotrequester
from classes import dbhandler
from classes import performance
import os
import keras
model = keras.models.load_model('model_7828')


def clear() -> None:
    os.system('clear')


def last_match_result() -> None:
    name = 'Norcia'
    ritopls = riotrequester.RiotRequester()
    summoner = ritopls.get_summoner_by_name(name)
    last_match_ids = ritopls.get_matchlist_by_puuid(summoner['puuid'], 1)
    match_id = last_match_ids[0]
    match_data = ritopls.get_match_by_match_id(match_id)
    target = performance.Match(match_data, model=model)
    target.show_participants()


def add_player_to_tracklist() -> None:
    print('(To exit, isnert 0)')
    name: str = input('Player name: ')
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


def analyze_matches() -> None:
    db = dbhandler.DBHandler()
    match_ids = db.get_matchlist()
    del db
    ritopls = riotrequester.RiotRequester()
    for idx, match_id in enumerate(match_ids):
        print(f'({idx}/{len(match_ids)}) {match_id[0]}')
        try:
            analyze_match(match_id[0], ritopls, model)
        except TypeError as e:
            print(f'An error has occured: {e}')
        except Exception as e:
            print(f'Ło panie co to się staneło: {e}')


def analyze_match(match_id, ritopls, model) -> None:
    match_data = ritopls.get_match_by_match_id(match_id)
    clear()
    target = performance.Match(match_data, model)
    target.show_participants()
    target.commit()
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
    if command == '0':
        exit()
    if command == '1':
        add_player_to_tracklist()
    if command == '2':
        harvest_match_ids()
    if command == '3':
        last_match_result()
    if command == '4':
        analyze_matches()


def main() -> None:
    clear()
    while True:
        menu_index()
        command: str = input(':> ')
        run_command(command)


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    main()
