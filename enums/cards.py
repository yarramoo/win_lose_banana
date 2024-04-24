from enum import Enum
from random import shuffle
import json

class Card(Enum):
    WIN = 'win'
    LOSE = 'lose'
    BANANA = 'banana'

    @classmethod
    def mapping(cls):
        return {value.value: value for value in cls}

    @classmethod
    def random_card_list(cls):
        cards = [card for card in cls]
        shuffle(cards)
        return cards

class CardEnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)