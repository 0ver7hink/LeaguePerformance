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
        query = f'select name,puuid,tracked FROM summoner_v2 WHERE name="{player_name}";'
        cursor = self.db.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        if not row:
            self.log.info('Player not found in local DB')
            self.insert_player(player_name, tracking=1)
            print('Player not found')
            return
        if row[2]:
            self.log.info('Player already tracked')
            print('Player already tracked')
            return
        query = f'UPDATE summoner_v2 SET tracked=1 WHERE name="{player_name}";'
        cursor.execute(query)
        self.db.commit()
        self.log.info(f'Player {player_name} is now tracked')
        print('Player is now tracked')

    def insert_player(self, player_name, puuid='', tracking=0) -> None:
        if not puuid:
            self.log.info('Checking if player exist in Riot Database')
            requesting = riotrequester.RiotRequester()
            player = requesting.get_summoner_by_name(player_name)
            if not player:
                self.log.warning('Cannot track unexisting player')
                return
            self.log.info('Player found')
            puuid = player['puuid']
        query: str = f'''INSERT INTO summoner_v2 (
            puuid, 
            name, 
            tracked, 
            mmr_mu, mmr_sigma,
            performance_mu, performance_sigma,
            match_count,
            join_date
        ) VALUES (
            "{puuid}", 
            "{player_name}", 
            {tracking}, 
            25.000, 8.333,
            25.000, 8.333,
            {0},
            NOW())
        ;'''
        cursor = self.db.cursor()
        cursor.execute(query)
        self.db.commit()
        self.log.info(f'Player {player_name} added to local database and its now tracked')

    def get_tracked_puuids(self):
        self.log.info('Requesting for tracked puuids')
        if self.warning:
            self.log.warning(self.warning)
            return
        query: str = 'SELECT puuid FROM summoner_v2 WHERE tracked=1;'
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
            values = f'("{match}", 0),'
            query += values
        query = query[:-1] + ';'
        cursor = self.db.cursor()
        cursor.execute(query)
        self.db.commit()
        self.log.info('Matchlist exported')

    def get_matchlist(self, limit=0, reverse=False, not_analyzed_only=True):
        self.log.info('Geting matchlist from local DB')
        query = 'SELECT `id` FROM `match` WHERE id like "EUN%" '
        if not_analyzed_only:
            query += 'AND `analyzed`=0 '
        query += 'ORDER BY `id` '
        if reverse:
            query += 'DESC '
        if limit != 0:
            query += f'LIMIT {limit}'
        query += ';'
        cursor = self.db.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        return data

    def get_rating(self, name, puuid):
        query = f'''
        SELECT 
            mmr_mu, mmr_sigma, 
            performance_mu, performance_sigma 
        FROM 
            summoner_v2
        WHERE 
            puuid="{puuid}";
        '''
        cursor = self.db.cursor()
        cursor.execute(query)
        if (row := cursor.fetchone()):
            return row
        cursor.reset()
        self.insert_player(name, puuid)
        return [25.000, 8.333, 25.000, 8.333]

    def update_rating(self, name, puuid, m1, s1, m2, s2):
        self.log.info(f'Updating ratings in local DB for {puuid[:8]}...')
        cursor = self.db.cursor()
        query = f'''
        UPDATE 
            summoner_v2 
        SET 
            name = "{name}",
            mmr_mu={m1}, 
            mmr_sigma={s1}, 
            performance_mu={m2},
            performance_sigma={s2},
            match_count = match_count+1 
        WHERE 
            puuid="{puuid}";
        '''
        cursor.execute(query)
        self.db.commit()

    def set_match_as_analyzed(self, match_id):
        self.log.info(f'setting match {match_id} as analyzed')
        cursor = self.db.cursor()
        query = f'UPDATE `match` SET analyzed=1 WHERE id="{match_id}";'
        cursor.execute(query)
        self.db.commit()
