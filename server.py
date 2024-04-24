import socket
import threading
import json
import signal
import sys
import queue
from dataclasses import dataclass

from enums.game_message import MessageType, Message
from enums.game_state import GameState
from enums.errors import *
from enums.cards import Card

BUFFER_LENGTH = 1024
HOST = '127.0.0.1'
PORT = 12345

NUM_PLAYERS = 3

players = []
events = {
    GameState.THREE_PLAYERS_JOINED: threading.Event(),
    GameState.LOSER_SELECTED: threading.Event(),
    GameState.GAME_OVER: threading.Event(),
}

@dataclass
class Player:
    name: str
    socket: socket.socket
    card: Card

def player_names() -> list:
    return list(map(lambda player: player.name, players))

def loser_name() -> str:
    for player in players:
        if player.card == Card.LOSE:
            return player.name
    raise Exception("No loser player in game")

def server_broadcast(contents):
    msg = Message.new_server_message(contents, "SERVER")
    for player in players:
        player.socket.send(msg.json_dump().encode())

def handle_loser_decision(msg, player: Player):
    if player.card != Card.WIN:
        raise Exception("Non winner tried to choose a loser")
    selected_loser = msg.contents['name']
    if selected_loser not in player_names() or selected_loser == player.name:
        raise Exception("Invalid loser choice")
    events[GameState.LOSER_SELECTED].set()
    server_broadcast(
        f"The WINNER has chosen {selected_loser}]",
    )
    if selected_loser == loser_name():
        server_broadcast(
            "The WINNER and LOSER win!!!",
        )
    else:
        server_broadcast(
            "The BANANA wins!!!",
        )
    return

def handle_player_message(contents, sender_player):
    msg = Message.new_server_message(contents, sender_player.name)
    for player in players:
        if player != sender_player:
            player.socket.send(msg.json_dump().encode())

def handle_message(msg, player: Player):
    msg = Message.json_load(msg)
    match msg.type:
        case MessageType.PLAYER_MESSAGE:
            # Send message to other players
            handle_player_message(msg.contents['message'], player)
        case MessageType.PLAYER_LOSER_DECISION:
            handle_loser_decision(msg, player)
            events[GameState.GAME_OVER].set()
        case _:
            raise Exception(f"Unexpected message {msg}")

def handle_client(
    client_socket, 
    client_id, 
    events, 
    player
    ):
    '''
    Handle the client connection for the duration of the game
    '''

    # Wait for signal to begin game
    events[GameState.THREE_PLAYERS_JOINED].wait()
    # Begin game
    # Tell player their card
    card_msg = Message.new_server_card(player.card)
    client_socket.send(card_msg.json_dump().encode())
    # Allow dialogue until the loser is selected
    while not events[GameState.GAME_OVER].is_set():
        msg = client_socket.recv(BUFFER_LENGTH)
        if not msg:
            # TODO some better error handling here
            break
        handle_message(msg, player)


def init_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Doing this to allow quickly reconnecting to the same socket. Security implications so address before actually using.
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print("Server is waiting for connections")
    return server_socket



def run_server(server_socket):
    '''
    For each new connection
    1) Accept if new players can be added to game
    2) Accept their name
    3) Assign a card
    4) Pass off to handler
    '''

    def get_name(client_socket) -> str:
        '''
        Helper to get the client's name
        '''
        msg = client_socket.recv(BUFFER_LENGTH)
        msg = Message.json_load(msg)
        if msg.type != MessageType.PLAYER_NAME:
            raise UnexpectedMessageTypeError(msg.type)
        print(msg.contents)
        return msg.contents['name']

    cards = Card.random_card_list()

    while True:
        client_socket, addr = server_socket.accept()
        print("New connection from:", addr)
        if len(players) == NUM_PLAYERS:
            # Reject connection
            print("New connection closed. Server already full")
            client_socket.close()
        else:
            # Accept connection
            print("New player added to game")
            # Receive name
            name = get_name(client_socket)
            print(name, 'has given their name')
            # Choose card
            card = cards.pop()
            # Record player
            player = Player(name, client_socket, card)
            players.append(player)
            # Start thread to handle player
            client_thread = threading.Thread(
                target=handle_client, 
                args=(
                    client_socket, 
                    client_socket,
                    events, 
                    player
                )
            )
            client_thread.start()
            # Check if lobby full
            if len(players) == NUM_PLAYERS:
                print("Three players joined. Time to begin!")
                events[GameState.THREE_PLAYERS_JOINED].set()


def main():
    server_socket = init_server()
    try:
        run_server(server_socket)
    except KeyboardInterrupt:
        print("Received KeyboardInterrupt, closing server...")
        server_socket.close()
        sys.exit(0)

if __name__ == '__main__':
    main()
