import socket
import threading
import json
import sys

from enums.game_message import MessageType, Message
from enums.cards import Card

HOST = '127.0.0.1'
PORT = 12345
BUFFER_LENGTH = 1024

def handle_message(msg):
    '''
    Message handler. The client would only expect to get SERVER_MESSAGE in this game.
    Anything else is unexpected
    '''
    msg = Message.json_load(msg)
    match msg.type:
        case MessageType.SERVER_MESSAGE:
            print(f"{msg.contents['sender']}: {msg.contents['message']}")
        case _:
            raise Exception(f"handle_message: Unexpected message {msg}")

def receive(client_socket):
    '''
    Receive function to run in receiver thread
    '''
    while True:
        try:
            msg = client_socket.recv(BUFFER_LENGTH).decode()
            if msg:
                handle_message(msg)
        except Exception as e:
            raise Exception(e)


def init_client():
    '''
    Socket code
    '''
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    return client_socket

# What should happen?
# - Start the client program and it should ask for their name
# - Connect to the server and wait until three players join
# - Once three players join, the game starts. Each player is given a card.
# - The player with the winner card is revealed. The remaining two players must convince the winner they are the loser. 
def run_client(client_socket):
    '''
    Game logic for client
    '''
    # Get name and send to server
    name = input("Enter your name: ")
    msg = Message.new_player_name(name) 
    client_socket.send(msg.json_dump().encode())
    # Wait for card
    msg = client_socket.recv(BUFFER_LENGTH)
    msg = Message.json_load(msg)
    player_card = msg.contents['card']
    print("SERVER: Your card is ", msg.contents['card'])
    # Begin receiver thread
    receiver_thread = threading.Thread(
        target=receive,
        args=(
            client_socket,
        )
    )
    receiver_thread.start()
    # Accept player input
    while True:
        msg = input()
        if player_card == Card.WIN and msg.startswith(">select"):
            msg = Message.new_player_loser_decision(msg.split(' ')[1])
        else:
            msg = Message.new_player_message(msg)
        client_socket.send(msg.json_dump().encode())


def main():
    client_socket = init_client()
    run_client(client_socket)

if __name__ == '__main__':
    main()





