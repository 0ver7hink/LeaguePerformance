from requests import get
from time import sleep
import logging


class APIKeysHandler:

    log = logging.getLogger('APIKeysHandler')
    KEYS_LOCATION = 'apikeys.md'
    KEY_MAX_REQUESTS_PER_MINUTE = 60
    URL_FOR_KEY_CHECK = 'https://eun1.api.riotgames.com/lol/status/v4/platform-data?api_key='

    def __init__(self) -> None:
        self.log.info('APIKeysHandler initialized')
        self.keys: list[str] = self.import_keys()
        self.speed_limit: float = 0
        if not self.keys:
            self.log.warning('No keys loaded. Key file seems empty')
            raise Exception('Missing API Key') 
        if self.check_keys():
            self.speed_limit: float = self.get_absolute_requests_speed()

    def __str__(self) -> str:
        msg = 'Here are all the keys:\n'
        for key in self.keys:
            msg += key + '\n'
        return msg

    def import_keys(self) -> list[str]:
        self.log.info('Importing keys')
        file_name = self.KEYS_LOCATION
        keys: list[str] = []
        with open(file_name, 'r') as file:
            [keys.append(line[:-1]) for line in file]
        return keys

    def check_keys(self) -> bool:
        self.log.info('Checking keys')
        current_keys: list[str] = self.keys
        working_keys: list[str] = []
        for key in current_keys:
            if self.validate_key(key):
                working_keys.append(key)
        if working_keys != current_keys:
            self.log.info('Detected some invalid keys...')
            self.keys = working_keys
            self.update_keys_file()
        if not working_keys:
            self.log.warning('There is no single valid key')
            
        return True
        
    def validate_key(self, apikey) -> bool:
        url: str = self.URL_FOR_KEY_CHECK
        query: str = url + apikey 
        self.log.debug(f'Executing query: {query}')
        response = get(query)
        if response.status_code == 403:
            self.log.info(f'[False][403] Validation of {apikey}')
            return False
        if response.status_code == 401:
            self.log.info(f'[False][401] Validation of {apikey}')
            return False
        if response.status_code == 200:
            self.log.info(f'[OK][200] Validation of {apikey}')
            return True
        self.log.info('Unexpected status code. Hence validation pass')
        return True

    def update_keys_file(self) -> None:
        self.log.info(f'Updating key file with new key set: {self.keys}')
        file_name: str = self.KEYS_LOCATION
        with open(file_name, 'w') as file:
            [file.write(key + '\n') for key in self.keys]

    def get_absolute_requests_speed(self) -> float:
        keys_quantity: int = len(self.keys)
        key_limit = self.KEY_MAX_REQUESTS_PER_MINUTE
        absolute_speed: float = (key_limit / keys_quantity) / 60
        self.log.info(f'Seting cap to 1 request per {absolute_speed} seconds')
        return absolute_speed

    def get_one(self) -> str:
        if not self.keys:
            self.log.warning('There is no key to return')
            return ''
        sleep(self.speed_limit)
        if len(self.keys) > 1:
            self.move_keys_queue_by_one()
        self.log.info(f'Returning key: {self.keys[0]}')
        return self.keys[0]

    def move_keys_queue_by_one(self) -> None:
        first_key: str = self.keys.pop(0)
        self.keys.append(first_key)
        self.log.info(f'Moving keys by one')


if __name__ == '__main__':
    keys = APIKeysHandler()
    print(keys)
    
