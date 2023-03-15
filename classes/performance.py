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
            'win',
            ],
        'statistics': [
            'damageDealtToObjectives',
            'totalDamageDealtToChampions',
            'timeCCingOthers',
            ],
        'challenges': [
            'killParticipation',
            'kda',
            'effectiveHealAndShielding',
            'saveAllyFromDeath',
            'immobilizeAndKillWithAlly',
            'killAfterHiddenWithAlly',
            'knockEnemyIntoTeamAndKill',
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
        self.rate_mmr()
        self.rate_performance()
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
        self.log.debug(self.extracted)

    def calculate_performance(self):
        self.log.info('Calculating performance')
        data = np.array(self.extracted[5:])
        normalized = [(arr/np.linalg.norm(arr)) for arr in data if sum(arr)]
        sumed = sum(normalized)
        performance_score = sumed / np.linalg.norm(sumed)
        self.extracted.append(performance_score)
        self.log.debug(performance_score)

    def download_ratings(self):
        self.log.info('Downloading ratings')
        db = dbhandler.DBHandler()
        ratings = [db.get_rating(p) for p in self.data['info']['participants']]
        del db
        ratings = list(zip(*ratings))
        for row in ratings:
            self.extracted.append(row)

    def rate_mmr(self):
        x = list(zip(*self.extracted))
        a, b = [],[]
        for i in range(10):
            m = x[i][-4]
            s = x[i][-3]
            if i<5:
                a.append(trueskill.Rating(m, s))
            else:
                b.append(trueskill.Rating(m, s))
        if x[0][3]:
            w = [0,1]
        else:
            w = [1,0]

        rated = trueskill.rate([a,b],ranks=w)
        m, s = [],[]
        rated = rated[0] + rated[1]
        for r in rated:
            m.append(round(r.mu,3 ))
            s.append(round(r.sigma,3))
        self.extracted.append(m)
        self.extracted.append(s)

    def rate_performance(self):
        self.log.info('Rating participants')
        x = list(zip(*self.extracted)) 
        x.sort(key=lambda i: i[-7], reverse=True)
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
            name: str = self.extracted[1][i]
            puuid: str = self.extracted[0][i]
            p_mu: float = self.extracted[-2][i]
            p_sigma: float = self.extracted[-1][i]
            m_mu: float = self.extracted[-4][i]
            m_sigma: float = self.extracted[-3][i]
            db.update_rating(name, puuid, m_mu, m_sigma, p_mu, p_sigma)
        db.set_match_as_analyzed(self.data['metadata']['matchId'])
        del db

    def show_details(self):
        for i in range(10):
            name = self.extracted[1][i]
            champion = self.extracted[2][i]
            old_mu = self.extracted[-6][i]
            old_sigma = self.extracted[-5][i]
            mu = self.extracted[-2][i]
            sigma = self.extracted[-1][i]
            old_rating = round((old_mu - 3*old_sigma)*100)
            rating = round((mu - 3*sigma)*100)
            msg = f'{i+1}.\t{old_rating}\t->\t{rating}\t{name}\t{champion}'
            print(msg)
        x = list(zip(*self.extracted))
        x = sorted(x, key=lambda y: y[3], reverse=True)
        self.extracted = list(zip(*x))
        print()
        for i in range(10):
            name = self.extracted[1][i]
            champion = self.extracted[2][i]
            old_mu = self.extracted[-8][i]
            old_sigma = self.extracted[-7][i]
            old_rating = round((old_mu - 3*old_sigma)*100)
            mu = self.extracted[-4][i]
            sigma = self.extracted[-3][i]
            rating = round((mu - 3*sigma)*100)
            msg = f'{i+1}.\t{old_rating}\t->\t{rating}\t{name}\t{champion}'
            print(msg)
