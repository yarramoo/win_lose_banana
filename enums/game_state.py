from enum import Enum

class GameState(Enum):
    THREE_PLAYERS_JOINED = "Three players joined"
    LOSER_SELECTED = "Loser selected"
    GAME_OVER = "Game over"