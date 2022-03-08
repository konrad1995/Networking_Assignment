import selectors
import queue
import SnakePy.SMTPEncryption
from threading import Thread

class Game(Thread):
    def __init__(self, user, type):
        Thread.__init__(self)
        self._user = user
        self._type = type

    def run(self):
        pass


