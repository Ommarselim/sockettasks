import socket
from datetime import datetime , date

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(("127.0.0.1",12345))
socket.listen(1)
x = str(datetime.now())

while True:
    client , addr = socket.accept()
    print(f"connection from {addr}")
    client.send(x.encode('utf8'))



