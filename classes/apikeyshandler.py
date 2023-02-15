from requests import get
from time import sleep
import logging


class APIKeyHandler:

    log = logging.getLogger('APIKeysHandler')
    def __init__(self) -> None:
        self.keys: list[str] = self.import_keys()
        self.speed_limit: float = self.get_absolute_requests_speed()
        self.check_keys()

    def import_keys(self) -> list[str]:
        pass

    def export_keys_0(self) -> None:
        pass

    def check_keys(self) -> None:
        pass

    def get_absolute_requests_speed(self) -> float:
        pass


if __name__ == '__main__':
    pass
