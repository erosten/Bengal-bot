from typing import Any, Optional
from engine_wrapper import MinimalEngine, OPTIONS_TYPE, COMMANDS_TYPE
from config import Configuration
from chess.engine import PlayResult, Limit
import chess
from chess import Move
import time
import math

from Bengal import Searcher, Board, evaluate
from Bengal import Board

BOOK_PATH = './books/bin/M11_2.bin'

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
        self.n_oobook = 0
        self.depths = []
        assert self.searcher.book_op

    def search(self, board: chess.Board, time_limit: Limit, ponder: bool, draw_offered: bool,
               root_moves) -> PlayResult:
        self.N_MOVES -= 1
        b = Board(board.fen())
        t_tot = time_limit.white_clock if board.turn else time_limit.black_clock
        inc = time_limit.white_inc if board.turn else time_limit.black_inc
        if not t_tot:
            print('defaulting to beginning time')
            search_t_per_move = 10

        m = max(self.N_MOVES, 40)
        if t_tot:
            search_t_per_move = t_tot / m

        strict = False
        if inc:
            search_t_per_move += inc
            strict = search_t_per_move < 30
        print(f'time remaining {t_tot}, time for move {search_t_per_move}')

        
        # t = time.time()
        move = Move.null()
        t1 = time.time()
        t_search = 0
        best_move = None
        best_move_repeats = 0
        best_scores = []
        d_avg = math.ceil(sum(self.depths[-3:]) / 3)
        d=0
        for score, pv in self.searcher._search_at_depth(b, 100, can_null=True):
            d+=1
            move = pv[0]
            if move == best_move:
                best_move_repeats += 1
            else:
                best_move_repeats = 0
            best_move = move
            best_scores.append(score)
            # Time Management
            t2 = time.time()
            t_search += t2 - t1
            # if d > d_avg and best_move_repeats >= 4:
            #     break
            if strict and t_search + (t2-t1) > search_t_per_move:
                break
            if t_search > search_t_per_move: # if time to search longer than allowed time, break
                break

        if move is None:
            move = next(b.generate_legal_moves()).uci()
        self.depths.append(d)
        return PlayResult(Move.from_uci(move), None)