from classes import dbhandler
from typing import Any
from pprint import pprint
import trueskill
import logging
import numpy as np


class MatchAnalyzer:

    TO_EXTRACT = {
        'player_info': [
            'puuid',
            'summonerName',
            'championName',
            ],
        'statistics': [
            'damageDealtToObjectives',
            'visionScore',
            'timeCCingOthers',
            ],
        'challenges': [
            'saveAllyFromDeath',
            'killParticipation',
            'effectiveHealAndShielding',
            'immobilizeAndKillWithAlly',
            ],
        }
     
    def __init__(self, match_data) -> None:
        self.log = logging.getLogger('Analyzer')
        match_id = match_data['metadata']['matchId']
        self.log.info(f'Initializing analyzer for {match_id}')
        self.data = match_data
        self.gamemode = match_data['info']['gameMode']
        self.extracted = []

    def analyze(self):
        self.extract_participants()
        self.calculate_performance()
        self.download_ratings()
        self.rate()
        self.show_details()

    def extract_participants(self):
        self.log.info('Extracting Participants')
        for value in self.TO_EXTRACT['player_info']:
            row = [x[value] for x in self.data['info']['participants']]
            self.extracted.append(row)
        for value in self.TO_EXTRACT['statistics']:
            row = [x[value] for x in self.data['info']['participants']]
            self.extracted.append(row)
        for value in self.TO_EXTRACT['challenges']:
            try:
                row = [x['challenges'][value] for x in self.data['info']['participants']]
                self.extracted.append(row)
            except Exception as e:
                print('Missing statistic: ' + value)
                continue
        k = np.array([x['kills'] for x in self.data['info']['participants']])
        d = np.array([x['deaths'] for x in self.data['info']['participants']])
        a = np.array([x['assists'] for x in self.data['info']['participants']])
        kda = (k+a)/d
        self.extracted.append(kda) 
        self.log.debug(self.extracted)

    def calculate_performance(self):
        self.log.info('Calculating performance')
        data = np.array(self.extracted[4:])
        normalized = [(arr/np.linalg.norm(arr)) for arr in data if sum(arr)]
        sumed = sum(normalized)
        performance_score = sumed / np.linalg.norm(sumed)
        self.extracted.append(performance_score)
        self.log.debug(performance_score)

    def download_ratings(self):
        self.log.info('Downloading ratings')
        db = dbhandler.DBHandler()
        ratings = [db.get_rating(puuid, self.gamemode) for puuid in self.extracted[0]]
        del db
        ratings = list(zip(*ratings))
        for row in ratings:
            self.extracted.append(row)

    def rate(self):
        self.log.info('Rating participants')
        x = list(zip(*self.extracted)) 
        x.sort(key=lambda i: i[-3])
        rating_group = []
        for i in x:
            row = (trueskill.Rating(i[-2], i[-1]),)
            rating_group.append(row)
        rated = trueskill.rate(rating_group)
        m, s = [],[]
        for r in rated:
            m.append(round(r[0].mu,3 ))
            s.append(round(r[0].sigma,3))
        self.extracted = list(zip(*x))
        self.extracted.append(m)
        self.extracted.append(s)

    def update_ratings(self):
        self.log.info('Updating ratings...')
        db = dbhandler.DBHandler()
        for i in range(10):
            puuid: str = self.extracted[0][i]
            mu: float = self.extracted[-2][i]
            sigma: float = self.extracted[-1][i]
            gamemode: str = self.gamemode
            db.update_rating(puuid, mu, sigma, gamemode)
        db.set_match_as_analyzed(self.data['metadata']['matchId'])
        del db

    def show_details(self):
        for i in range(10):
            name = self.extracted[1][i]
            champion = self.extracted[2][i]
            old_mu = self.extracted[-4][i]
            old_sigma = self.extracted[-3][i]
            old_rating = round((old_mu - 3*old_sigma)*100)
            mu = self.extracted[-2][i]
            sigma = self.extracted[-1][i]
            rating = round((mu - 3*sigma)*100)
            msg = f'{i+1}.\t{old_rating}\t->\t{rating}\t{name}\t{champion}'
            print(msg)
