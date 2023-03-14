from dbconfig import db_config
from classes import riotrequester
import mysql.connector
import logging


class DBHandler:

    warning: str = ''

    def __init__(self) -> None:
        self.log = logging.getLogger('DBHandler')
        self.log.info('Class initialized')
        self.config: dict[str, str] = db_config
        self.db = self.connect()

    def __del__(self) -> None:
        if self.db:
            self.log.info('Closing database connection')
            self.db.close()

    def connect(self): 
        self.log.info('connecting with database...')
        try:
            db = mysql.connector.connect(
                user = self.config['user'],
                password = self.config['pass'],
                host = self.config['host'],
                database = self.config['database'],
                )
        except Exception as e:
            self.warning = str(e)
            self.log.warning(e)
            return None
        return db

    def track_player(self, player_name: str) -> None:
        if self.warning:
            self.log.warning(self.warning)
            return
        self.log.info(f'Requested tracking of player: {player_name}')
        query = f'select name,puuid,tracking FROM summoner WHERE name="{player_name}";'
        cursor = self.db.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        if not row:
            self.log.info('Player not found in local DB')
            self.insert_player(player_name, tracking=1)
            return
        if row[2]:
            self.log.info('Player already tracked')
            return
        query = f'UPDATE summoner SET tracking=1 WHERE name="{player_name}";'
        cursor.execute(query)
        self.db.commit()
        self.log.info(f'Player {player_name} is now tracked')
        print('Player is now tracked')

    def insert_player(self, player_name, tracking=0) -> None:
        if self.warning:
            self.log.warning(self.warning)
            return
        self.log.info('Checking if player exist in Riot Database')
        requesting = riotrequester.RiotRequester()
        player = requesting.get_summoner_by_name(player_name)
        if not player:
            self.log.warning('Cannot track unexisting player')
            return
        self.log.info('Player found')
        name = player['name']
        puuid = player['puuid']
        query: str = 'INSERT INTO summoner (name, puuid, tracking, join_date) VALUES '
        query += f'("{name}", "{puuid}", {tracking}, NOW());'
        cursor = self.db.cursor()
        cursor.execute(query)
        self.db.commit()
        self.log.info(f'Player {player_name} added to local database and its now tracked')

    def get_tracked_puuids(self):
        self.log.info('Requesting for tracked puuids')
        if self.warning:
            self.log.warning(self.warning)
            return
        query: str = 'SELECT puuid FROM summoner WHERE tracking=1;'
        cursor = self.db.cursor()
        cursor.execute(query)
        puuids = cursor.fetchall() 
        x: list[str] = []
        for i in puuids:
            x.append(i[0])
        return x

    def export_matchlist_to_local_db(self, matchlist):
        if self.warning:
            self.log.warning(self.warning)
            return
        query = 'INSERT IGNORE INTO `match` VALUES '
        for match in matchlist:
            queue = int(match[0])
            match_id = match[1]
            values = f'("{match_id}", {queue}, 0),'
            query += values
        query = query[:-1] + ';'
        cursor = self.db.cursor()
        cursor.execute(query)
        self.db.commit()
        self.log.info('Matchlist exported')

    def get_matchlist(self, queue_id: str = '', limit: int = 0):
        self.log.info('Geting matchlist from local DB')
        query = f'SELECT `id` FROM `match` WHERE `analysed`=0 '
        if queue_id:
            query +=  f'AND queue_id={queue_id} '
        if limit:
            query += f'LIMIT {limit} '
        query += 'ORDER BY id;'
        cursor = self.db.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        return data

    def get_rating(self, puuid, gamemode):
        self.log.info(f'Geting ratings from local DB for {puuid[:8]}...')
        query = f'SELECT mu,sigma FROM rating WHERE puuid="{puuid}" AND gamemode="{gamemode}";'
        cursor = self.db.cursor()
        cursor.execute(query)
        if (row := cursor.fetchone()):
            return [row[0], row[1]]
        cursor.reset()
        query = 'INSERT INTO rating (puuid, gamemode, mu, sigma, match_count) '
        query += f'VALUES ("{puuid}","{gamemode}",25.000, 8.333, 0);'
        cursor = self.db.cursor()
        cursor.execute(query)
        self.db.commit()
        return [25.000, 8.333]

    def update_rating(self, puuid, mu, sigma, gamemode):
        self.log.info(f'Updating ratings in local DB for {puuid[:8]}...')
        cursor = self.db.cursor()
        query = f'UPDATE rating SET mu={mu}, sigma={sigma}, match_count = match_count+1 WHERE puuid="{puuid}" AND gamemode="{gamemode}";'
        cursor.execute(query)
        self.db.commit()

    def set_match_as_analyzed(self, match_id):
        self.log.info(f'setting match {match_id} as analyzed')
        cursor = self.db.cursor()
        query = f'UPDATE `match` SET analysed=1 WHERE id="{match_id}";'
        cursor.execute(query)
        self.db.commit()
