import random
import selectors
import queue
import SnakePy.SMTPEncryption

from threading import Thread


class Card:
    def __init__(self, index):
        self.picture_index = index
        if index >= 10:
            self.value = 10
        elif index < 10:
            self.value = index
        self.used = False


class Module(Thread):
    def __init__(self, sock, addr):
        Thread.__init__(self)

        self._selector = selectors.DefaultSelector()
        self._sock = sock
        self._addr = addr
        self.user = None

        self._incoming_buffer = queue.Queue()
        self._outgoing_buffer = queue.Queue()

        self.encryption = SnakePy.SMTPEncryption.nws_encryption()
        self.running = True

        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self._selector.register(self._sock, events, data=None)
        # MULTIPLAYER
        self.balance = 1000
        self.bet = 0
        self.used_cards = []
        self.drawn_cards = []
        self.deck = []
        self.player_cards = []
        self.dealer_cards = []
        self.player_score = 0
        self.dealer_score = 0
        self.max_bet = 500

    def run(self):
        try:
            while self.running:
                events = self._selector.select(timeout=None)
                for key, mask in events:
                    try:
                        if mask & selectors.EVENT_READ:
                            self._read()
                        if mask & selectors.EVENT_WRITE and not self._outgoing_buffer.empty():
                            self._write()
                    except Exception:
                        self.close()
                if not self._selector.get_map():
                    break
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self._selector.close()

    def _read(self):
        try:
            data = self._sock.recv(4096)
        except BlockingIOError:
            print("blocked")
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._incoming_buffer.put(self.encryption.decrypt(data.decode()))
            else:
                raise RuntimeError("Peer closed.")

        self._process_response()

    def _write(self):
        try:
            message = self._outgoing_buffer.get_nowait()
        except:
            message = None

        if message:
            print("sending", repr(message), "to", self._addr)
            try:
                self._sock.send(message)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass

    def _create_message(self, content):
        encoded = self.encryption.encrypt(content.encode())
        self._outgoing_buffer.put(encoded)

    def _process_response(self):
        message = self._incoming_buffer.get()
        split_message = message.split(":")
        self._module_processor(split_message[0], split_message[1])

    def _module_processor(self, command, message):
        print("Received a command: " + command)
        print("Received a message: " + message)
        if command == "connect":
            login_details = open('../login_details.txt')
            with login_details as ld:
                for line in ld:
                    if message == line:
                        ud = message.split("@")
                        self.user = ud[0]
                        self._create_message("connect:accepted")
        elif command == "start":
            if message == "single":
                self.balance = 1000
                self.max_bet = 500
                self._create_message("game:single")
        elif command == "request":
            if message == "create_deck":
                self.create_deck()
                self._create_message("request:deck_created")
            elif message == "player_score":
                self.player_score = self.calculate_score(self.player_cards)
                self._create_message("player_score:"+str(self.player_score))
            elif message == "dealer_score":
                self.dealer_score = self.calculate_score(self.dealer_cards)
                self._create_message("dealer_score:" + str(self.dealer_score))
            elif message == "balance":
                self._create_message("balance:" + str(self.balance))
            elif message == "bet":
                self._create_message("bet:" + str(self.bet))
            elif message == "username":
                self._create_message("username:" + self.user)
            elif message == "card_for_player":
                self.request_card_for_player()
            elif message == "card_for_dealer":
                self.request_card_for_dealer()
            elif message == "clear_bet":
                self.bet = 0
            elif message == "prize":
                self.balance += (self.bet * 2)
                self.bet = 0
            elif message == "push":
                self.balance += self.bet
                self.bet = 0
            elif message == "restart":
                self.player_cards.clear()
                self.dealer_cards.clear()


        elif command == "request_add_to_bet":
            result = self.check_can_player_bet(int(message))
            if result:
                self.transfer_from_balance_to_bet(int(message))
                self._create_message("request_add_to_bet:accepted")
            else:
                self._create_message("request_add_to_bet:declined")
        elif command == "request_remove_from_bet":
            result = self.check_can_player_remove_bet(int(message))
            if result:
                self.transfer_from_bet_to_balance(int(message))
                self._create_message("request_remove_from_bet:accepted")
            else:
                self._create_message("request_remove_from_bet:declined")
        else:
            self._create_message("500 Unknown command:" + command)
            print("Received an unknown command")

    def close(self):
        print("closing connection to", self._addr)
        self.running = False
        try:
            self._selector.unregister(self._sock)
            self._sock.close()
        except OSError as e:
            print(
                f"error: socket.close() exception for",
                f"{self._addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self._sock = None

    def request_card_for_player(self):
        drawn_card = random.randint(0, self.deck.__len__() - 1)
        card = self.deck[drawn_card]
        self.used_cards.append(card)
        del self.deck[drawn_card]
        self.player_cards.append(card)
        self._create_message("player_card:"+str(drawn_card))

    def request_card_for_dealer(self):
        drawn_card = random.randint(0, self.deck.__len__() - 1)
        card = self.deck[drawn_card]
        self.used_cards.append(card)
        del self.deck[drawn_card]
        self.dealer_cards.append(card)
        self._create_message("dealer_card:" + str(drawn_card))

    def create_deck(self):
        for x in range(1, 14):
            card = Card(x)
            self.deck.append(card)
            self.deck.append(card)
            self.deck.append(card)
            self.deck.append(card)
            self.deck.append(card)
            self.deck.append(card)
            self.deck.append(card)
            self.deck.append(card)

    def transfer_from_balance_to_bet(self, coin_value):
        self.bet += coin_value
        self.balance -= coin_value

    def transfer_from_bet_to_balance(self, coin_value):
        self.bet -= coin_value
        self.balance += coin_value

    @staticmethod
    def calculate_score(cards):
        score = 0
        aces = 0
        for x in cards:
            score += x.value
            if x.value == 1:
                aces += 1
                score += 10
        while aces > 0:
            if score > 21 and aces > 0:
                score -= 10
                aces -= 1
            elif score <= 21:
                return score
        return score



    def add_to_player_balance(self, amount):
        self.balance += amount

    def remove_from_player_balance(self, amount):
        self.balance -= amount

    def add_to_player_bet(self, amount):
        self.bet += amount

    def remove_from_player_bet(self, amount):
        self.bet -= amount

    def check_can_player_bet(self, amount):
        if self.balance >= amount:
            if self.bet + amount <= self.max_bet:
                return True
            else:
                return False
        else:
            return False

    def check_can_player_remove_bet(self, amount):
        if self.bet >= amount:
            if self.balance + amount >= 0:
                return True
            else:
                return False
        else:
            return False

    def transfer_from_balance_to_bet(self, coin_value):
        self.bet += coin_value
        self.balance -= coin_value

    def transfer_from_bet_to_balance(self, coin_value):
        self.bet -= coin_value
        self.balance += coin_value

