import socket
import threading
from tkinter import *

class TicTacToeClient:
    def __init__(self, host, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (host, port)
        self.board = [' '] * 9
        self.current_player = 'X'
        self.game_over = False
        self.lock = threading.Lock()

        self.window = Tk()
        self.window.title('Tic Tac Toe')

        self.buttons = []
        for i in range(9):
            button = Button(self.window, text='', width=10, height=5, command=lambda idx=i: self.make_move(idx))
            button.grid(row=i // 3, column=i % 3)
            self.buttons.append(button)

        self.status_label = Label(self.window, text='Waiting for opponent...')
        self.status_label.grid(row=3, columnspan=3)

    def start(self):
        self.client_socket.connect(self.server_address)
        print('Connected to the server:', self.server_address)

        threading.Thread(target=self.receive_updates).start()
        self.window.mainloop()

    def make_move(self, move):
        if not self.game_over and self.board[move] == ' ':
            self.lock.acquire()
            self.board[move] = self.current_player
            self.lock.release()
            self.update_ui()
            self.client_socket.sendall(str(move).encode())

    def receive_updates(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode().strip()
                if not data:
                    break
                self.lock.acquire()
                self.board = data.split(',')
                self.game_over = self.check_win() or self.check_draw()
                self.current_player = 'O' if self.current_player == 'X' else 'X'
                self.lock.release()
                self.update_ui()
            except Exception as e:
                print('Error occurred:', e)
                break

    def check_win(self):
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]  # diagonals
        ]

        for condition in win_conditions:
            if self.board[condition[0]] == self.board[condition[1]] == self.board[condition[2]] != ' ':
                return True

        return False

    def check_draw(self):
        return ' ' not in self.board

    def update_ui(self):
        for i in range(9):
            self.buttons[i].config(text=self.board[i])
            self.buttons[i].config(state=DISABLED if self.board[i] != ' ' or self.game_over else NORMAL)

        if self.game_over:
            if self.check_win():
                self.status_label.config(text=f'Player {self.current_player} wins!')
            else:
                self.status_label.config(text="It's a draw!")
        else:
            self.status_label.config(text=f'Player {self.current_player}\'s turn')

    def stop(self):
        self.client_socket.sendall('quit'.encode())
        self.client_socket.close()

# Create the TicTacToeClient instance
client = TicTacToeClient('localhost', 8888)
client.start()
