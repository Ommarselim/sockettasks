import socket
import threading

class TicTacToeServer:
    def __init__(self, host, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (host, port)
        self.clients = []
        self.board = [' '] * 9
        self.current_player = 'X'
        self.game_over = False
        self.lock = threading.Lock()

    def start(self):
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(2)
        print('Server started and listening for connections...')

        while True:
            client_socket, client_address = self.server_socket.accept()
            print('Client connected:', client_address)
            self.clients.append(client_socket)

            if len(self.clients) == 2:
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
                threading.Thread(target=self.handle_client, args=(self.clients[0],)).start()
                break

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024).decode().strip()
                if data == 'quit':
                    client_socket.close()
                    self.clients.remove(client_socket)
                    print('Client disconnected:', client_socket.getpeername())
                    break
                else:
                    move = int(data)
                    self.lock.acquire()
                    if self.valid_move(move):
                        self.board[move] = self.current_player
                        self.game_over = self.check_win() or self.check_draw()
                        self.current_player = 'O' if self.current_player == 'X' else 'X'
                    self.lock.release()
                    self.update_clients()
            except Exception as e:
                print('Error occurred:', e)
                break

    def valid_move(self, move):
        return self.board[move] == ' ' and not self.game_over

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

    def update_clients(self):
        for client_socket in self.clients:
            client_socket.sendall(self.board_str().encode())

    def board_str(self):
        return ','.join(self.board)

    def stop(self):
        self.server_socket.close()

# Create the TicTacToeServer instance
server = TicTacToeServer('localhost', 8888)
server.start()
