from enum import Enum
import json

from enums.cards import Card

class MessageType(Enum):
    '''
    Enum to differentiate different kinds of messages
    The intended usage is within the Message class. Each Message instance has a type and dictionary with relevant value
    The keys for the dictionary is commented above each enum variant

    TODO: It might be an idea to seperate the Client and Server messages into different classes. Fine for now
    '''
    # { name }
    PLAYER_NAME = 'player_name'
    # { message }
    PLAYER_MESSAGE = 'player_message'
    # { name }
    PLAYER_LOSER_DECISION = 'player_loser_decision'

    # { message, sender }
    SERVER_MESSAGE = 'server_message'
    # { card }
    SERVER_CARD = 'server_card'

    @classmethod
    def mapping(cls):
        return {value.value: value for value in cls}

class Message:
    '''
    Message class for sending messages between the server and clients. Each message has a type and relevant contents
    The keys in the contents dict can be found in the MessageType comments above
    '''
    def __init__(self, message_type: MessageType, contents: dict):
        self.type = message_type
        self.contents = contents

    def __str__(self):
        return f'{self.type.value}: {self.contents}'
    
    # ----- FACTORY METHODS -----
    # INTENDED CONSTRUCTION METHOD

    @classmethod
    def new_player_name(cls, name: str):
        return cls(
            MessageType.PLAYER_NAME,
            { 'name': name }
        )

    @classmethod
    def new_player_message(cls, message: str):
        return cls(
            MessageType.PLAYER_MESSAGE,
            { 'message': message }
        )

    @classmethod
    def new_player_loser_decision(cls, name: str):
        return cls(
            MessageType.PLAYER_LOSER_DECISION,
            { 'name': name }
        )

    @classmethod
    def new_server_message(cls, message: str, sender: str):
        return cls(
            MessageType.SERVER_MESSAGE, 
            contents={
                'message': message,
                'sender': sender
            }
        )

    @classmethod
    def new_server_card(cls, card: Card):
        return cls(
            MessageType.SERVER_CARD,
            { 'card': card.value }
        )

    
    # ----- JSON METHODS -----

    def json_dump(self):
        msg = {'type': self.type.value, 'contents': self.contents}
        return json.dumps(msg)
    
    @classmethod
    def json_load(cls, msg: bytes):
        '''
        Load Message class from json-encoded bytes. Restore erased enum types too
        '''
        msg = json.loads(msg)
        msg_type = MessageType.mapping()[msg['type']]
        msg_contents = msg['contents']
        match msg_type:
            case MessageType.SERVER_CARD:
                # Restore Card enum
                msg_contents['card'] = Card.mapping()[msg_contents['card']]

        return cls(msg_type, msg_contents)



