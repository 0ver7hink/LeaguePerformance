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
    QUEUE = {
            'draft':  '400',
            'ranked': '420',
            'blind':  '430',
            'flex':   '440',
            'aram':   '450',
            }
    def __init__(self) -> None:
        self.log = logging.getLogger('RiotRequester')
        self.log.info('Initializing RiotRequester')
        self.keys = apikeyshandler.APIKeysHandler()
        if not self.keys:
            self.log.warning('API keys are missing')
            raise Exception('Error: No valid keys found')
        self.last_status_code = False

    def get_matchlist_by_puuid(self, puuid: str, queue: str = QUEUE['aram']) -> list[str]:
        self.log.info(f'Requesting match list by puuid: {puuid}')
        key: str = self.keys.get_one()
        query: str = ''
        query += self.URL['matchids']
        query += puuid + '/ids?'
        query += 'queue=' + queue
        query += '&start=0&count=100&'
        query += 'api_key=' + key
        response = get(query)
        self.request_check(response)
        matchlist: list[str] = response.json()
        return matchlist

    def get_match_by_match_id(self, match_id) -> dict[str, Any]:
        self.log.info(f'Requesting match data by match id: {match_id}')
        url: str = self.URL['matchdata']
        key: str = self.keys.get_one()
        query: str = url + match_id + '?api_key=' + key
        response = get(query)
        self.request_check(response)
        match: dict[str, Any] = response.json()
        return match

    def get_summoner_by_name(self, name: str) -> dict[str, Any]:
        self.log.info(f'Requesting summoner data for name: {name}')
        key: str = self.keys.get_one()
        url: str = self.URL['summoner']
        query: str = url + name + '?api_key=' + key
        self.log.debug(f'query: {query}')
        response = get(query)
        self.request_check(response)
        summoner: dict[str, Any] = response.json()
        return summoner

    def request_check(self, response) -> None:
        code: int = response.status_code
        url: str = response.url
        self.last_status_code: int = code
        if code == 200:
            msg: str = f'[OK] geting response for: {url}'
            self.log.info(msg)
        if code != 200:
            msg: str = f'Unhandled request response. Status code: {code}'
            self.log.warning(msg)
