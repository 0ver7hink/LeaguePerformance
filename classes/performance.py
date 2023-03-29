from classes import riotrequester
from classes.dbhandler import DBHandler
from typing import Any
from trueskill import rate, Rating
import keras
import logging
import numpy as np


def get_last_match_data_by_summoner_name(name) -> dict[str, Any]:
    ritopls = riotrequester.RiotRequester()
    summoner = ritopls.get_summoner_by_name(name)
    match_ids = ritopls.get_matchlist_by_puuid(summoner['puuid'])
    match_id = match_ids[0]
    match = ritopls.get_match_by_match_id(match_id)
    return match

class Match:
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
            'knockEnemyIntoTeamAndKill',],}

    def __init__(self, match_data: dict[str, Any]) -> None:
        self.log = logging.getLogger('Match')
        self.log.info('Class initiated...')
        self.data: dict[str, Any] = match_data
        self.data_extracted: list[Any] = self._extract()
        self.summoners: list[Summoner] = [
                Summoner(row) for row in self.data_extracted]
        self.model = keras.models.load_model('model_7828')
        self._calculate_win_probability()
        self._download_ratings()
        self._rate_mmr()
        self._rate_mvp()
    
    def _extract(self) -> list[Any]:
        self.log.info('extracting summoners from given data')
        x: list = []
        for value in self.TO_EXTRACT['player_info']:
            x.append([i[value] for i in self.data['info']['participants']])
        for value in self.TO_EXTRACT['statistics']:
            x.append(self._get_normalized_values(value))
        for value in self.TO_EXTRACT['challenges']:
            x.append(self._get_normalized_values(value, True))
        return list(zip(*x))

    def _get_normalized_values(self, value, challenge=False):
        self.log.info('Normalizing...')
        data = self.data['info']['participants']
        try:
            if challenge:
                arr = [row['challenges'][value] for row in data]
            else:
                arr = [row[value] for row in data]
            y = np.array(arr)
            x = y / np.linalg.norm(y)
            if np.isnan(x[0]):
                raise Exception
            self.log.info(f'Returning normalized data: {x}')
            return x 
        except Exception as e:
            self.log.info('Returning empty array due to unexpected error')
            return np.array([0.0 for _ in range(10)])

    def _download_ratings(self) -> None:
        self.log.info('Download ranking...')
        db: DBHandler = DBHandler()
        [summoner.download_rating(db) for summoner in self.summoners]
        del db

    def _rate_mmr(self) -> None:
        self.summoners.sort(key=lambda x: x.win, reverse=True)
        ratings: list[Rating] = [
            Rating(s.old_mmr_mu, s.old_mmr_si) for s in self.summoners]
        winners = ratings[:5]
        losers = ratings[5:]
        new_ratings = rate([winners, losers])
        new_ratings = new_ratings[0]+new_ratings[1]
        for idx, rating in enumerate(new_ratings):
            self.summoners[idx].new_mmr_mu = rating.mu
            self.summoners[idx].new_mmr_si = rating.sigma

    def _rate_mvp(self) -> None:
        self.summoners.sort(key=lambda x: x.win_prob, reverse=True)
        rating_group: list[list[Rating]] = [
            [Rating(s.old_mvp_mu, s.old_mvp_si)] for s in self.summoners]
        new_ratings = rate(rating_group)
        for idx, rating in enumerate(new_ratings):
            self.summoners[idx].new_mvp_mu = rating[0].mu
            self.summoners[idx].new_mvp_si = rating[0].sigma
            
    def _calculate_win_probability(self) -> None:
        self.log.info('Calculating win probability')
        for summoner in self.summoners:
            summoner.win_prob = self.model.predict([summoner.stats])[0,0]

    def show_participants(self) -> None:
        self.summoners.sort(key=lambda x: x.win_prob, reverse=True)
        [print(p) for p in self.summoners]

    def commit(self) -> None:
        db = DBHandler()
        for summoner in self.summoners:
            db.update_rating(
                summoner.name, 
                summoner.puuid, 
                summoner.new_mmr_mu, 
                summoner.new_mmr_si,
                summoner.new_mvp_mu,
                summoner.new_mvp_si,)
        db.set_match_as_analyzed(self.data['metadata']['matchId'])
        del db


class Summoner:
    new_mmr_mu = None
    new_mmr_si = None
    new_mvp_mu = None
    new_mvp_si = None
    old_mmr_mu = None
    old_mmr_si = None
    old_mvp_mu = None
    old_mvp_si = None
    win_prob = None
    
    def __init__(self, data) -> None:
        self.puuid = data[0]
        self.name = data[1]
        self.champion_name = data[2]
        self.win = data[3]
        self.stats = data[4:]

    def __str__(self) -> str:
        prob = ''
        if self.win_prob:
            prob = round(self.win_prob*100,2)
        win = 0
        if self.win:
            win = 1
        msg = f'{win} | {prob}%\t{self.name} - {self.champion_name}'
        # new_mmr = round(100*(self.new_mmr_mu - 3*self.new_mmr_si))
        # new_mvp = round(100*(self.new_mvp_mu - 3*self.new_mvp_si))
        # old_mmr = round(100*(self.old_mmr_mu - 3*self.old_mmr_si))
        # old_mvp = round(100*(self.old_mvp_mu - 3*self.old_mvp_si))
        # msg += f'\n\t\t\tMMR: {old_mmr} -> {new_mmr}\n'
        # msg += f'\t\t\tMVP: {old_mvp} -> {new_mvp}'
        return msg

    def download_rating(self, db) -> None:
        rating: list[float] = db.get_rating(self.name, self.puuid)
        self.old_mmr_mu = rating[0]
        self.old_mmr_si = rating[1]
        self.old_mvp_mu = rating[2]
        self.old_mvp_si = rating[3]

def main() -> None:
    logging.basicConfig(level=logging.INFO)
    match_data = get_last_match_data_by_summoner_name('Norcia')
    target: Match = Match(match_data)
    target.show_participants()

if __name__ == '__main__':
    main()
