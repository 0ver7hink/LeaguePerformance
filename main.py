from classes import apikeyshandler
from classes import riotrequester
import logging


logging.basicConfig(level=logging.DEBUG)

def main() -> None:
    keys = apikeyshandler.APIKeysHandler()
    key = keys.get_one()
    print(keys)

if __name__ == '__main__':
    main()
