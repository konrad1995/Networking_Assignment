import sys
import selectors
import queue
import json
import io
import struct
import traceback
import SMTPEncryption
from threading import Thread


class Module (Thread):
    def __init__(self, sock, addr):
        Thread.__init__(self)

        self._selector = selectors.DefaultSelector()
        self._sock = sock
        self._addr = addr
        self._incoming_buffer = queue.Queue()
        self._outgoing_buffer = queue.Queue()
        self.state = "connect"
        self.msg = ""

        self.running = True
        self.encryption = SMTPEncryption.nws_encryption()
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self._selector.register(self._sock, events, data=None)

    def run(self):
        try:
            while self.running:
                events = self._selector.select(timeout=1)
                for key, mask in events:
                    try:
                        if mask & selectors.EVENT_READ:
                            self._read()
                        if mask & selectors.EVENT_WRITE and not self._outgoing_buffer.empty():
                            self._write()
                    except Exception:
                        self.close()
                # Check for a socket being monitored to continue.
                if not self._selector.get_map():
                    break
        finally:
            self._selector.close()

    def _read(self):
        try:
            data = self._sock.recv(4096)
        except BlockingIOError:
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
                sent = self._sock.send(message)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass

    def _module_processor(self, command, message):
        if command == "connect":
            if message == "accepted":
                print("User details correct!")
                self.state = "accepted"
                #here I need open new window
            elif message == "not_accepted":
                print("Wrong user details.")
                self.state = "not_accepted"
        elif command == "game":
            print("Game")
            if message == "single":
                print("Game single stared.")
                self.state = "single"
            elif message == "multi":
                print("Game multi started.")
                self.state = "multi"
        elif command == "HELP":
            self.create_message(f"250 This is a help message: {message}")
            print("Received a HELP")
        elif command == "request":
            print("Received " + command + ":" + message)
        elif command == "player_score":
            self.msg = message
            self.state = command
            print("Received " + command + ":" + message)
        elif command == "dealer_score":
            self.msg = message
            self.state = command
            print("Received " + command + ":" + message)
        elif command == "balance":
            self.msg = message
            self.state = command
            print("Received " + command + ":" + message)
        elif command == "bet":
            self.msg = message
            self.state = command
            print("Received " + command + ":" + message)
        elif command == "username":
            self.msg = message
            self.state = command
            print("Received " + command + ":" + message)
        elif command == "request_add_to_bet":
            print("Received " + command + ":" + message)
            self.msg = message
        elif command == "request_remove_from_bet":
            print("Received " + command + ":" + message)
            self.msg = message
        elif command == "player_card":
            print("Received " + command + ":" + message)
            self.msg = message
            self.state = command
        elif command == "dealer_card":
            print("Received " + command + ":" + message)
            self.msg = message
            self.state = command
        else:
            self.create_message("500 Unknown command")
            print("Received an unknown command")

    def create_message(self, content):
        encoded = self.encryption.encrypt(content.encode())
        self._outgoing_buffer.put(encoded)

    def _process_response(self):
        message = self._incoming_buffer.get()
        split_message = message.split(':')
        self._module_processor(split_message[0], split_message[1])

    def close(self):
        print("closing connection to", self._addr)

        self.running = False
        try:

            self._selector.unregister(self._sock)
            self._sock.close()
        except OSError as e:
            pass
        finally:
            # Delete reference to socket object for garbage collection
            self._sock = None
