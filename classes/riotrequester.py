from typing import Any
from requests import get
from classes import apikeyshandler
import logging


class RiotRequester:

    URL = {
            'summoner': 'https://eun1.api.riotgames.com/lol/summoner/v4/summoners/by-name/',
            'matchids': 'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/',
            'matchdata': 'https://europe.api.riotgames.com/lol/match/v5/matches/',
            }

    def __init__(self) -> None:
        self.log = logging.getLogger('RiotRequester')
        self.log.info('Initializing RiotRequester')
        self.keys = apikeyshandler.APIKeysHandler()
        if not self.keys:
            self.log.warning('API keys are missing')
            raise Exception('Error: No valid keys found')
        self.last_status_code = False

    def get_matchlist_by_puuid(self, puuid: str, quantity: int = 100):
        log_msg = f'Requesting match list by puuid: {puuid}'
        self.log.info(log_msg)
        key: str = self.keys.get_one()
        query: str = ''
        query += self.URL['matchids']
        query += puuid + '/ids?'
        query += 'queue=450'
        query += f'&start=0&count={quantity}&'
        query += 'api_key=' + key
        try:
            response = get(query)
        except Exception as e:
            self.log.warning(e)
            return
        matchlist: list[str] = self.request_check(response, log_msg)
        if matchlist:
            self.log.info(f'Recieved {len(matchlist)} match identities')
            print(f'Got {len(matchlist)} matches from {puuid[:8]}')
            return matchlist
        return None

    def get_match_by_match_id(self, match_id) -> dict[str, Any]:
        log_msg = f'Requesting match data by match id: {match_id}' 
        self.log.info(log_msg)
        url: str = self.URL['matchdata']
        key: str = self.keys.get_one()
        query: str = url + match_id + '?api_key=' + key
        response = get(query)
        match: dict[str, Any] = self.request_check(response, log_msg)
        return match

    def get_summoner_by_name(self, name: str) -> dict[str, Any]:
        log_msg: str  = f'Requesting summoner data for name: {name}'
        self.log.info(log_msg)
        key: str = self.keys.get_one()
        url: str = self.URL['summoner']
        query: str = url + name + '?api_key=' + key
        self.log.debug(f'query: {query}')
        response = get(query)
        summoner: dict[str, Any] = self.request_check(response, log_msg)
        return summoner

    def request_check(self, response, topic: str):
        if not response.ok:
            reason: str = response.reason
            code: int = response.status_code
            msg: str = f'[{code}][{reason}] {topic}'
            self.log.warning(msg)
            return 
        return response.json()
