import random
import socket
import time
import tkinter as tk
import tkinter.font
from SMTPClient import SMTPClientLib
from tkinter import *
from tkinter import messagebox
from tkinter import HORIZONTAL

from PIL import ImageTk, Image


class Card:
    def __init__(self, index):
        self.picture_index = index
        if index >= 10:
            self.value = 10
        elif index < 10:
            self.value = index
        self.used = False


class Snake21:
    def __init__(self, host="127.0.0.1", port=50000):
        if __debug__:
            print("NWSThreadedClient.__init__", host, port)
        self._module = None
        self.login_win = tk.Tk()
        self.login_win.configure()
        self.states = [0, 1, 2, 3, 4, 5, 6]
        self.current_state = self.states[0]
        self.username_label = tk.Label(self.login_win,
                                       text="Username").grid(row=0)
        self.password_label = tk.Label(self.login_win,
                                       text="Password").grid(row=1)

        self.host_label = tk.Label(self.login_win, text="Host").grid(row=2)
        self.port_label = tk.Label(self.login_win, text="Port").grid(row=3)

        self.username = tk.Entry(self.login_win)
        self.password = tk.Entry(self.login_win)
        self.host_input = tk.Entry(self.login_win)
        self.port_input = tk.Entry(self.login_win)
        self.menu_win = None
        self.game_win = None
        self.window_game = None
        self.balance = None
        self.bet = 0
        self.used_cards = []
        self.drawn_cards = []
        self.deck = []
        self.coins = []
        self.cards = []
        self.player_cards = []
        self.dealer_cards = []
        self.hit_button = None
        self.split_button = None
        self.stand_button = None
        self.double_button = None
        self.bet_button = None
        self.coin_button_10 = None
        self.coin_button_20 = None
        self.coin_button_50 = None
        self.coin_button_100 = None
        self.coin_button_500 = None
        self.var_bet = None
        self.var_dealer_score = None
        self.var_player_score = None
        self.var_balance = StringVar()
        self.bet_label = None
        self.game_info_label = None
        self.player_score_label = None
        self.dealer_score_label = None
        self.player_score = 0
        self.dealer_score = 0
        self.player_canvas = None
        self.dealer_canvas = None
        self.max_bet = 500
        self.score_font = None
        self.info_font = None
        self.game_info_var = None
        self.username.grid(row=0, column=1)
        self.password.grid(row=1, column=1)
        self.balance_label = None
        self.waiting = None
        self.players = []
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        self.host_input.grid(row=2, column=1)
        self.port_input.grid(row=3, column=1)

        self.login_win.resizable(False, False)
        tk.Button(self.login_win, text='Login', command=self.login).grid(row=4,
                                                                         column=1,
                                                                         sticky=tk.W,
                                                                         pady=4)
        tk.Button(self.login_win, text='Exit', command=self.exit_login).grid(row=4,
                                                                             column=0,
                                                                             sticky=tk.W,
                                                                             pady=4)
        self.login_win.mainloop()

    def exit_login(self):
        self.login_win.destroy()

    def start_connection(self, host, port):
        addr = (host, port)
        print("starting connection to", addr)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(addr)
        self._module = SMTPClientLib.Module(sock, addr)
        self._module.start()

    @staticmethod
    def cards_sum(rand_cards):
        value = 0
        for x in rand_cards:
            value += x
        value += rand_cards.__len__()
        return value

    def prepare_game(self):
        self.switch_decision_buttons()
        # player_cards.append(Card(1))
        # player_cards.append(Card(1))
        self.waiting = True

        self.request_card_for_player()
        self.request_card_for_player()
        self.request_card_for_dealer()
        self.request_card_for_dealer()
        self.request_player_score()

        if self.dealer_cards[0].value == 1:
            self.dealer_score = 11
        else:
            self.dealer_score = self.dealer_cards[0].value

            # self._module._create_message(ask:)
        self.update_player_score()
        self.update_dealer_score()

        self.add_card_to_player_canvas(self.player_cards)

        self.dealer_canvas.create_image(10, 20, anchor=tk.NW, image=self.cards[self.dealer_cards[0].picture_index])
        self.dealer_canvas.create_image(25, 20, anchor=tk.NW, image=self.cards[0])

        if self.player_score == 21:
            self.update_info_panel("Nice! You have BlackJack!!!")

            self.dealer_turn()
        else:
            self.update_info_panel("What would you like to do?")

        self.window_game.mainloop()

    def create_coins(self):

        self.coins = []
        img0 = Image.open("Graphics/10coin.png")
        img1 = Image.open("Graphics/20coin.png")
        img2 = Image.open("Graphics/50coin.png")
        img3 = Image.open("Graphics/100coin.png")
        img4 = Image.open("Graphics/500coin.png")

        resized_image0 = img0.resize((100, 100), Image.ANTIALIAS)
        resized_image1 = img1.resize((100, 100), Image.ANTIALIAS)
        resized_image2 = img2.resize((100, 100), Image.ANTIALIAS)
        resized_image3 = img3.resize((100, 100), Image.ANTIALIAS)
        resized_image4 = img4.resize((100, 100), Image.ANTIALIAS)

        new_image0 = ImageTk.PhotoImage(resized_image0)
        new_image1 = ImageTk.PhotoImage(resized_image1)
        new_image2 = ImageTk.PhotoImage(resized_image2)
        new_image3 = ImageTk.PhotoImage(resized_image3)
        new_image4 = ImageTk.PhotoImage(resized_image4)

        self.coins.append(new_image0)
        self.coins.append(new_image1)
        self.coins.append(new_image2)
        self.coins.append(new_image3)
        self.coins.append(new_image4)

    def create_cards(self):
        img0 = Image.open("Graphics/back.jpg")
        img1 = Image.open("Graphics/As.jpg")
        img2 = Image.open("Graphics/2.jpg")
        img3 = Image.open("Graphics/3.jpg")
        img4 = Image.open("Graphics/4.jpg")
        img5 = Image.open("Graphics/5.jpg")
        img6 = Image.open("Graphics/6.jpg")
        img7 = Image.open("Graphics/7.jpg")
        img8 = Image.open("Graphics/8.jpg")
        img9 = Image.open("Graphics/9.jpg")
        img10 = Image.open("Graphics/10.jpg")
        img11 = Image.open("Graphics/J.jpg")
        img12 = Image.open("Graphics/Q.jpg")
        img13 = Image.open("Graphics/K.jpg")

        resized_image0 = img0.resize((50, 100), Image.ANTIALIAS)
        resized_image1 = img1.resize((50, 100), Image.ANTIALIAS)
        resized_image2 = img2.resize((50, 100), Image.ANTIALIAS)
        resized_image3 = img3.resize((50, 100), Image.ANTIALIAS)
        resized_image4 = img4.resize((50, 100), Image.ANTIALIAS)
        resized_image5 = img5.resize((50, 100), Image.ANTIALIAS)
        resized_image6 = img6.resize((50, 100), Image.ANTIALIAS)
        resized_image7 = img7.resize((50, 100), Image.ANTIALIAS)
        resized_image8 = img8.resize((50, 100), Image.ANTIALIAS)
        resized_image9 = img9.resize((50, 100), Image.ANTIALIAS)
        resized_image10 = img10.resize((50, 100), Image.ANTIALIAS)
        resized_image11 = img11.resize((50, 100), Image.ANTIALIAS)
        resized_image12 = img12.resize((50, 100), Image.ANTIALIAS)
        resized_image13 = img13.resize((50, 100), Image.ANTIALIAS)

        new_image0 = ImageTk.PhotoImage(resized_image0)
        new_image1 = ImageTk.PhotoImage(resized_image1)
        new_image2 = ImageTk.PhotoImage(resized_image2)
        new_image3 = ImageTk.PhotoImage(resized_image3)
        new_image4 = ImageTk.PhotoImage(resized_image4)
        new_image5 = ImageTk.PhotoImage(resized_image5)
        new_image6 = ImageTk.PhotoImage(resized_image6)
        new_image7 = ImageTk.PhotoImage(resized_image7)
        new_image8 = ImageTk.PhotoImage(resized_image8)
        new_image9 = ImageTk.PhotoImage(resized_image9)
        new_image10 = ImageTk.PhotoImage(resized_image10)
        new_image11 = ImageTk.PhotoImage(resized_image11)
        new_image12 = ImageTk.PhotoImage(resized_image12)
        new_image13 = ImageTk.PhotoImage(resized_image13)

        self.cards.append(new_image0)
        self.cards.append(new_image1)
        self.cards.append(new_image2)
        self.cards.append(new_image3)
        self.cards.append(new_image4)
        self.cards.append(new_image5)
        self.cards.append(new_image6)
        self.cards.append(new_image7)
        self.cards.append(new_image8)
        self.cards.append(new_image9)
        self.cards.append(new_image10)
        self.cards.append(new_image11)
        self.cards.append(new_image12)
        self.cards.append(new_image13)

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

    def request_player_score(self):
        self._module.create_message("request:player_score")
        while True:
            if self._module.state == "player_score":
                self.player_score = int(self._module.msg)
                self.update_player_score()
                break

    def request_card(self):
        self._module.create_message("request:card")
    def request_dealer_score(self):
        self._module.create_message("request:dealer_score")
        while True:
            if self._module.state == "dealer_score":
                self.dealer_score = int(self._module.msg)
                self.update_dealer_score()
                break

    def request_balance_score(self):
        self._module.create_message("request:balance")
        while True:
            if self._module.state == "balance":
                if self._module.msg != "accepted" or self._module.msg != "declined":
                    time.sleep(0.5)
                    self.balance = int(self._module.msg)
                    self.update_player_balance()
                    break

    def request_bet_score(self):
        self._module.create_message("request:bet")
        while True:
            if self._module.state == "bet":
                if self._module.msg != "accepted" or self._module.msg != "declined":
                    time.sleep(0.5)
                    self.bet = int(self._module.msg)
                    self.update_player_bet()
                    break

    def request_username(self):
        self._module.create_message("request:username")
        while True:
            if self._module.state == "username":
                self.players = ["Dealer", ""]
                self.players[1] = self._module.msg
                break

    def new_game(self):
        self.window_game = tk.Tk()
        self.window_game.configure()
        self.window_game.resizable(0, 0)
        self.window_game.geometry("800x800")
        self.create_cards()
        self._module.create_message("request:create_deck")
        self.create_deck()
        self.create_coins()
        self.score_font = tkinter.font.Font(weight="bold")
        self.info_font = tkinter.font.Font(weight="bold", size=25)

        game_info = "What do you wish to do?"

        window_panel = tk.PanedWindow(self.window_game, orient=VERTICAL)
        window_panel.pack()

        info_panel = tk.PanedWindow(window_panel, orient=HORIZONTAL, width=800, height=100, bg="green")
        window_panel.add(info_panel)
        info_panel.pack()

        gap_panel = tk.PanedWindow(window_panel, orient=HORIZONTAL, height=25)
        window_panel.add(gap_panel)
        gap_panel.pack()

        buttons_panel_row_1 = tk.PanedWindow(window_panel, orient=HORIZONTAL)
        window_panel.add(buttons_panel_row_1)
        buttons_panel_row_1.pack()

        self.game_info_var = StringVar()
        self.game_info_var.set(game_info)
        self.game_info_label = Label(info_panel, anchor=CENTER, textvariable=self.game_info_var, font=self.info_font)
        info_panel.add(self.game_info_label)

        buttons_panel_row_2 = tk.PanedWindow(window_panel, orient=HORIZONTAL)
        window_panel.add(buttons_panel_row_2)
        buttons_panel_row_2.pack()

        gap_panel = tk.PanedWindow(window_panel, orient=HORIZONTAL, height=25)
        window_panel.add(gap_panel)
        gap_panel.pack()

        player_coin_panel = tk.PanedWindow(window_panel,
                                           orient=VERTICAL,
                                           showhandle=False,
                                           sashwidth=0,
                                           sashpad=0,
                                           handlesize=0, handlepad=0)
        window_panel.add(player_coin_panel)
        player_coin_panel.pack()

        coin_panel = tk.PanedWindow(player_coin_panel,
                                    orient=HORIZONTAL,
                                    showhandle=False,
                                    sashwidth=0,
                                    sashpad=0,
                                    handlesize=0,
                                    handlepad=0)
        player_coin_panel.add(coin_panel)
        coin_panel.pack()

        player_info_panel = tk.PanedWindow(coin_panel, orient=VERTICAL, showhandle=False,
                                           sashwidth=0,
                                           sashpad=0,
                                           handlesize=0,
                                           handlepad=0,
                                           width=100)
        coin_panel.add(player_info_panel)

        self.coin_button_10 = tk.Button(coin_panel, image=self.coins[0])
        self.coin_button_10.bind("<Button-1>", self.add_10_to_bet)
        self.coin_button_10.bind("<Button-3>", self.remove_10_from_bet)
        self.coin_button_10.pack()
        self.coin_button_20 = tk.Button(coin_panel, image=self.coins[1])
        self.coin_button_20.bind("<Button-1>", self.add_20_to_bet)
        self.coin_button_20.bind("<Button-3>", self.remove_20_from_bet)
        self.coin_button_20.pack()
        self.coin_button_50 = tk.Button(coin_panel, image=self.coins[2])
        self.coin_button_50.bind("<Button-1>", self.add_50_to_bet)
        self.coin_button_50.bind("<Button-3>", self.remove_50_from_bet)
        self.coin_button_50.pack()
        self.coin_button_100 = tk.Button(coin_panel, image=self.coins[3])
        self.coin_button_100.bind("<Button-1>", self.add_100_to_bet)
        self.coin_button_100.bind("<Button-3>", self.remove_100_from_bet)
        self.coin_button_100.pack()
        self.coin_button_500 = tk.Button(coin_panel, image=self.coins[4])
        self.coin_button_500.bind("<Button-1>", self.add_500_to_bet)
        self.coin_button_500.bind("<Button-3>", self.remove_500_from_bet)
        self.coin_button_500.pack()

        coin_panel.add(self.coin_button_10)
        coin_panel.add(self.coin_button_20)
        coin_panel.add(self.coin_button_50)
        coin_panel.add(self.coin_button_100)
        coin_panel.add(self.coin_button_500)

        player_balance_panel = tk.PanedWindow(coin_panel,
                                              orient=VERTICAL,
                                              showhandle=False,
                                              sashwidth=0,
                                              sashpad=0,
                                              handlesize=0,
                                              handlepad=0)
        coin_panel.add(player_balance_panel)

        balance_label_text = Label(player_balance_panel, anchor=W, text="Balance", font=self.score_font)
        player_balance_panel.add(balance_label_text)
        balance_label_text.pack()

        self.var_balance = StringVar()
        self.var_balance.set(str(self.balance))
        self.balance_label = Label(player_balance_panel, anchor=W, textvariable=self.var_balance, font=self.score_font)
        player_balance_panel.add(self.balance_label)
        self.balance_label.pack()

        bet_label_text = Label(player_balance_panel, anchor=W, text="Bet", font=self.score_font)
        player_balance_panel.add(bet_label_text)
        bet_label_text.pack()

        self.var_bet = StringVar()
        self.var_bet.set(str(self.bet))
        self.bet_label = Label(player_balance_panel, anchor=W, textvariable=self.var_bet, font=self.score_font)
        player_balance_panel.add(self.bet_label)
        self.bet_label.pack()

        self.request_username()
        var_player_name = StringVar()
        var_player_name.set(self.players[1])
        player_name_label = Label(player_info_panel, anchor=W, textvariable=var_player_name, font=self.score_font)
        player_info_panel.add(player_name_label)

        self.var_player_score = StringVar()
        self.var_player_score.set(str("Score: " + str(self.player_score)))
        self.player_score_label = Label(player_info_panel, anchor=W, textvariable=self.var_player_score,
                                        font=self.score_font)
        player_info_panel.add(self.player_score_label)

        self.player_canvas = tk.Canvas(window_panel)
        self.player_canvas.configure(bg='red', width=800, height=200)
        self.player_canvas.pack(expand=YES, fill=BOTH)

        dealer_info_panel = tk.PanedWindow(window_panel, orient=HORIZONTAL)
        window_panel.add(dealer_info_panel)
        dealer_info_panel.pack()

        str_score_dealer = Label(dealer_info_panel, text="Score: ", font=self.score_font)
        dealer_info_panel.add(str_score_dealer)

        self.dealer_canvas = tk.Canvas(window_panel)
        self.dealer_canvas.configure(bg='blue', width=800, height=200)
        self.dealer_canvas.pack(expand=YES, fill=BOTH)

        self.var_dealer_score = StringVar()
        self.var_dealer_score.set(self.dealer_score)
        self.dealer_score_label = Label(dealer_info_panel, textvariable=self.var_dealer_score, font=self.score_font)
        dealer_info_panel.add(self.dealer_score_label)

        self.hit_button = tk.Button(buttons_panel_row_1,
                                    text='Hit',
                                    command=self.hit,
                                    width=50)
        self.hit_button.pack(side=LEFT)

        self.stand_button = tk.Button(buttons_panel_row_1,
                                      text='Stand',
                                      command=self.stand,
                                      width=50)
        self.stand_button.pack(side=RIGHT)

        self.split_button = tk.Button(buttons_panel_row_2,
                                      text='Split',
                                      command=self.split,
                                      width=33)
        self.split_button.pack(side=LEFT)

        self.double_button = tk.Button(buttons_panel_row_2,
                                       text='Double',
                                       command=self.double,
                                       width=33)
        self.double_button.pack(side=RIGHT)

        self.bet_button = tk.Button(buttons_panel_row_2,
                                    text='Bet',
                                    command=self.bet_placed,
                                    width=33)
        self.bet_button.pack(side=RIGHT)
        self.request_player_score()
        self.request_dealer_score()


        self.request_balance_score()
        self.request_bet_score()

        self.update_info_panel("Welcome to the table.")
        self.switch_decision_buttons()
        self.window_game.mainloop()

    def login(self):
        usr_and_pass = str(self.username.get()) + "@" + str(self.password.get())
        if usr_and_pass == "@":
            usr_and_pass = "user@user"
        if __name__ == "__main__":
            self.run(usr_and_pass)

    def request_card_for_player(self):
        self._module.create_message("request:card_for_player")
        while True:
            if self._module.state == "player_card":
                time.sleep(0.5)
                drawn_card = int(self._module.msg)
                card = self.deck[drawn_card]
                self.used_cards.append(card)
                del self.deck[drawn_card]
                self.player_cards.append(card)
                break

    def request_card_for_dealer(self):
        self._module.create_message("request:card_for_dealer")
        while True:
            if self._module.state == "dealer_card":
                time.sleep(0.5)
                drawn_card = int(self._module.msg)
                card = self.deck[drawn_card]
                self.used_cards.append(card)
                del self.deck[drawn_card]
                self.dealer_cards.append(card)
                break

    def menu(self):
        self.menu_win = tk.Tk()
        self.menu_win.configure()
        self.menu_win.resizable(False, False)
        canvas = tk.Canvas(self.menu_win,
                           width=800,
                           height=600)
        canvas.configure(bg='red')
        canvas.pack()

        img_single = Image.open("Graphics/singleGame.jpg")

        img_exit = Image.open("Graphics/exit.jpg")

        resized_image_single = img_single.resize((200, 400),
                                                 Image.ANTIALIAS)

        resized_image_exit = img_exit.resize((200, 400),
                                             Image.ANTIALIAS)

        new_image_single = ImageTk.PhotoImage(resized_image_single)
        new_image_exit = ImageTk.PhotoImage(resized_image_exit)

        single_button = tk.Button(self.menu_win,
                                  text='NewGame!',
                                  image=new_image_single,
                                  command=self.connect_single)
        single_button.place(x=200, y=50)
        exit_button = tk.Button(self.menu_win,
                                text='NewGame!',
                                image=new_image_exit,
                                command=self.exit_game)
        exit_button.place(x=400, y=50)

        self.menu_win.mainloop()

    def start_menu(self):
        self.login_win.destroy()
        self.menu()

    def start_game(self):
        self.menu_win.destroy()
        self.new_game()

    @staticmethod
    def exit_game():
        res = messagebox.askquestion("Exit?", "You want to exit game?")
        if res == 'yes':
            sys.exit()

    def connect_single(self):
        msg = "single"
        self.run(msg)

    def connect_multi(self):
        msg = "multi"
        self.run(msg)

    def run(self, message):
        not_leave_loop = True
        while not_leave_loop:
            if self.current_state == self.states[0]:
                int(self.port_input.get())
                self.start_connection(self.host_input.get(), int(self.port_input.get()))
                self.current_state = self.states[1]
            elif self.current_state == self.states[1]:  # Connected
                command = "connect:" + message
                self._module.create_message(command)
                self.current_state = self.states[2]
            elif self.current_state == self.states[2]:  # LoginIn
                if self._module.state == "accepted":
                    self.current_state = self.states[3]
                    print("Accepted")
                    not_leave_loop = False
                    self.start_menu()
                elif self._module.state == "not_accepted":
                    print("Wrong username or password.")
                    not_leave_loop = False
                    self.current_state = self.states[2]
            elif self.current_state == self.states[3]:  # LoggedIn
                command = "start:" + message
                self._module.create_message(command)
                self.current_state = self.states[4]
            elif self.current_state == self.states[4]:
                self.current_state = self.states[5]
                command = "connect:" + message
                self._module.create_message(command)
            elif self.current_state == self.states[5]:
                if self._module.state == "single":
                    self.start_game()
                elif self._module.state == "multi":
                    self.start_game()
                    self.current_state = self.states[6]
            elif self.current_state == self.states[6]:
                break

    def restart_game(self):
        self._module.create_message("request:restart")
        self.player_canvas.delete("all")
        self.dealer_canvas.delete("all")
        self.player_cards.clear()
        self.dealer_cards.clear()
        self.switch_bet_buttons()

    def bet_placed(self):
        if not self.bet == 0:
            self.switch_all_buttons()
            self.update_info_panel("Thank you for the bet :D")

            self.switch_decision_buttons()
            self.prepare_game()
        else:
            self.update_info_panel("I am sorry. You did not bet any coins.")

    def dealer_turn(self):
        end_of_turn = False
        self.add_card_to_dealer_canvas(self.dealer_cards)
        self.request_dealer_score()
        self.request_player_score()
        if self.dealer_score < 21:
            self.update_info_panel("Dealer have " + str(self.dealer_score))
        elif self.dealer_score == 21:
            self.update_info_panel("Dealer have BlackJack!")
            if self.player_cards.__len__() == 2 and self.player_score == 21:
                self.update_info_panel("That's a push!")

        while not end_of_turn:
            if self.dealer_score < 17 and self.dealer_score < self.player_score <= 21:
                self.update_info_panel("One more card for a dealer :D")
                self.request_card_for_dealer()
                self.add_card_to_dealer_canvas(self.dealer_cards)
                self.request_dealer_score()
                self.update_info_panel("Dealer have " + str(self.dealer_score))
            else:
                end_of_turn = True
        if self.player_score > 21:
            self.clear_bet()
        elif self.player_score <= 21 and self.dealer_score > 21:
            self.update_info_panel("Dealer Bust! Congratulations for the win!")
            self.distribute_win_prize_()
        elif self.player_score == self.dealer_score:
            self.update_info_panel("That's a push :D")
            self.push()
        elif self.player_score <= 21 and self.dealer_score <= 21:
            if self.player_score < self.dealer_score:
                self.update_info_panel("It is player "
                                       + str(self.player_score)
                                       + " to dealer "
                                       + str(self.dealer_score))
                self.update_info_panel("Dealer Won this time :(")

                self.clear_bet()
            elif self.player_score > self.dealer_score:
                self.update_info_panel(
                    "It is player " + str(self.player_score) + " to dealer " + str(self.dealer_score))
                self.update_info_panel("Congratulations for the winner :D")
                self.distribute_win_prize_()
        self.update_info_panel("Thank you for the game!")
        self.restart_game()

    def split(self):
        self.update_info_panel("That function required DLC!")

    def stand(self):
        self.switch_decision_buttons()
        self.update_info_panel("So you decided to stand.")
        self.update_info_panel("Lets see what dealer have :D.")
        if self._module.state == "single":
            self.dealer_turn()
        elif self._module.state == "multi":
            self.multi_dealer_turn()

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

    @staticmethod
    def switch_button_state(button):
        if button['state'] == tk.NORMAL:
            button['state'] = tk.DISABLED
        else:
            button['state'] = tk.NORMAL

    def double(self):
        self.update_info_panel("That function required DLC!")

    def switch_all_buttons(self):
        self.switch_button_state(self.hit_button)
        self.switch_button_state(self.split_button)
        self.switch_button_state(self.stand_button)
        self.switch_button_state(self.double_button)
        self.switch_button_state(self.bet_button)
        self.switch_button_state(self.coin_button_10)
        self.switch_button_state(self.coin_button_20)
        self.switch_button_state(self.coin_button_50)
        self.switch_button_state(self.coin_button_100)
        self.switch_button_state(self.coin_button_500)

    def switch_bet_buttons(self):
        self.switch_button_state(self.bet_button)
        self.switch_button_state(self.coin_button_10)
        self.switch_button_state(self.coin_button_20)
        self.switch_button_state(self.coin_button_50)
        self.switch_button_state(self.coin_button_100)
        self.switch_button_state(self.coin_button_500)

    def switch_decision_buttons(self):
        self.switch_button_state(self.hit_button)
        self.switch_button_state(self.split_button)
        self.switch_button_state(self.stand_button)
        self.switch_button_state(self.double_button)

    def hit(self):
        self.request_card_for_player()
        self.add_card_to_player_canvas(self.player_cards)
        self.request_player_score()
        if self.player_score > 21:
            self.switch_decision_buttons()
            self.update_info_panel("You Bust!")
            self.dealer_turn()
        elif self.player_score == 21:
            self.switch_decision_buttons()
            self.update_info_panel("Congratulations! You have 21 :D")
            self.dealer_turn()
        elif 21 > self.player_score > 17:
            self.update_info_panel("Very nice score :D!")
            self.update_info_panel("What is your next decision?")
        else:
            self.update_info_panel("That's " + str(self.player_score))
            self.update_info_panel("What is your next decision?")

    def add_card_to_dealer_canvas(self, cards_arr):
        x_pos = 10
        self.dealer_canvas.delete(all)
        for x in cards_arr:
            self.dealer_canvas.create_image(x_pos, 20, anchor=tk.NW, image=self.cards[x.picture_index])
            x_pos += 15

    def update_dealer_score(self):
        self.var_dealer_score.set(self.dealer_score)
        self.dealer_score_label.update()

    def update_info_panel(self, new_text):
        self.game_info_var.set(new_text)
        self.game_info_label.update()
        time.sleep(1)

    def add_card_to_player_canvas(self, cards_arr):
        x_pos = 10
        self.player_canvas.delete(all)
        for x in cards_arr:
            self.player_canvas.create_image(x_pos, 20, anchor=tk.NW, image=self.cards[x.picture_index])
            x_pos += 15

    def update_player_score(self):
        self.var_player_score.set(str("Score: " + str(self.player_score)))
        self.player_score_label.update()

    def update_player_balance(self):
        self.var_balance.set(str(self.balance))
        self.balance_label.update()

    def update_player_bet(self):
        self.var_bet.set(str(self.bet))
        self.bet_label.update()

    def clear_bet(self):
        self._module.create_message("request:clear_bet")
        self.bet = 0
        self.update_player_bet()

    def distribute_win_prize_(self):
        self._module.create_message("request:prize")
        self.balance += (self.bet * 2)
        self.update_info_panel("You won " + str((self.bet * 2)))
        self.bet = 0
        self.update_player_bet()
        self.update_player_balance()

    def push(self):
        self._module.create_message("request:push")
        self.balance += self.bet
        self.bet = 0
        self.update_player_bet()
        self.update_player_balance()

    def add_10_to_bet(self, event):
        state = str(self.coin_button_10["state"])
        if state == "normal":
            coin_value = 10
            respond = self.request_add_to_bet(coin_value)
            if respond == "accepted":
                time.sleep(0.5)
                self.request_bet_score()
                self.request_balance_score()

    def add_20_to_bet(self, event):
        state = str(self.coin_button_10["state"])
        if state == "normal":
            coin_value = 20
            respond = self.request_add_to_bet(coin_value)
            if respond == "accepted":
                time.sleep(0.5)
                self.request_bet_score()
                self.request_balance_score()

    def add_50_to_bet(self, event):
        state = str(self.coin_button_10["state"])
        if state == "normal":
            coin_value = 50
            respond = self.request_add_to_bet(coin_value)
            if respond == "accepted":
                time.sleep(0.5)
                self.request_bet_score()
                self.request_balance_score()

    def add_100_to_bet(self, event):
        state = str(self.coin_button_10["state"])
        if state == "normal":
            coin_value = 100
            respond = self.request_add_to_bet(coin_value)
            if respond == "accepted":
                time.sleep(0.5)
                self.request_bet_score()
                self.request_balance_score()

    def add_500_to_bet(self, event):
        state = str(self.coin_button_10["state"])
        if state == "normal":
            coin_value = 500
            respond = self.request_add_to_bet(coin_value)
            if respond == "accepted":
                time.sleep(0.5)
                self.request_bet_score()
                self.request_balance_score()

    def remove_10_from_bet(self, event):
        state = str(self.coin_button_10["state"])
        if state == "normal":
            coin_value = 10
            respond = self.request_remove_from_bet(coin_value)
            if respond == "accepted":
                time.sleep(0.5)
                self.request_bet_score()
                self.request_balance_score()

    def remove_20_from_bet(self, event):
        state = str(self.coin_button_10["state"])
        if state == "normal":
            coin_value = 20
            respond = self.request_remove_from_bet(coin_value)
            if respond == "accepted":
                time.sleep(0.5)
                self.request_bet_score()
                self.request_balance_score()

    def remove_50_from_bet(self, event):
        state = str(self.coin_button_10["state"])
        if state == "normal":
            coin_value = 50
            respond = self.request_remove_from_bet(coin_value)
            if respond == "accepted":
                time.sleep(0.5)
                self.request_bet_score()
                self.request_balance_score()

    def remove_100_from_bet(self, event):
        state = str(self.coin_button_10["state"])
        if state == "normal":
            coin_value = 100
            respond = self.request_remove_from_bet(coin_value)
            if respond == "accepted":
                time.sleep(0.5)
                self.request_bet_score()
                self.request_balance_score()

    def remove_500_from_bet(self, event):
        state = str(self.coin_button_10["state"])
        if state == "normal":
            coin_value = 500
            respond = self.request_remove_from_bet(coin_value)
            if respond == "accepted":
                time.sleep(0.5)
                self.request_bet_score()
                self.request_balance_score()

    def request_add_to_bet(self, value):
        self._module.create_message("request_add_to_bet:" + str(value))
        while True:
            if self._module.msg == "accepted":
                return self._module.msg
            elif self._module.msg == "declined":
                return self._module.msg

    def request_remove_from_bet(self, value):
        self._module.create_message("request_remove_from_bet:" + str(value))
        while True:
            if self._module.msg == "accepted":
                return self._module.msg
            elif self._module.msg == "declined":
                return self._module.msg


if __name__ == "__main__":
    game = Snake21()
    game.run("")
