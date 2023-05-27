from typing import Any, Optional
from engine_wrapper import MinimalEngine, OPTIONS_TYPE, COMMANDS_TYPE
from config import Configuration
from chess.engine import PlayResult, Limit
import chess
from chess import Move
import time

from Bengal import Searcher, Board, evaluate
from Bengal import Board

BOOK_PATH = './books/bin/Cerebellum_Light_Poly.bin'

class BengalEngine(MinimalEngine):
    def __init__(self, commands: COMMANDS_TYPE, options: OPTIONS_TYPE, stderr: Optional[int],
                 draw_or_resign: Configuration, name: Optional[str] = None, **popen_args: str) -> None:
        """
        Initialize the values of the engine that all homemade engines inherit.

        :param options: The options to send to the engine.
        :param draw_or_resign: Options on whether the bot should resign or offer draws.
        """
        super().__init__(commands, options, stderr, draw_or_resign, name, **popen_args)

        self.N_MOVES = 100
        self.searcher = Searcher(BOOK_PATH)
        
    def search(self, board: chess.Board, time_limit: Limit, ponder: bool, draw_offered: bool,
               root_moves) -> PlayResult:
        self.N_MOVES -= 1
        b = Board(board.fen())
        t_tot = time_limit.white_clock if board.turn else time_limit.black_clock
        if not t_tot:
            print('defaulting to beginning time')
            search_t_per_move = 10

        m = max(self.N_MOVES, 40)
        if t_tot:
            search_t_per_move = t_tot / m

        print(f'time remaining {t_tot}, time for move {search_t_per_move}')

        # t = time.time()
        move = Move.null()
        t1 = time.time()
        t_search = 0
        for d, pv in self.searcher._search_at_depth(b, 8, can_null=False):
            move = pv[0]
            t2 = time.time()
            t_search += t2 - t1
            if t_search > search_t_per_move: # if time to search longer than allowed time, break
                break

        if move == Move.null():
            move = next(b.generate_legal_moves()).uci()
        return PlayResult(Move.from_uci(move), None)