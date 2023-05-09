from dataclasses import dataclass, field
from copy import deepcopy
import numpy as np

@dataclass
class Move():
    path: list[int] = field(default_factory=list, init=False)
    position: tuple = field(default_factory=tuple, init=False)
    next_moves: list[tuple()] = field(default_factory=list[tuple()], init=False)
    possible_moves: list[tuple()] = field(default_factory=list[tuple()])

    def __post_init__(self):
        self.next_moves = [item for move in self.possible_moves for item in move]

    def overwrite_next_moves(self, next_moves):
        self.next_moves = next_moves
        return self

    def move(self, position: tuple):
        new_move = deepcopy(self)
        assert (position[1] not in new_move.path)
        if len(new_move.path) == 0:
            new_move.path.append(position[0])
    
        tmp_possible_moves = []
        for index, move_set in enumerate(new_move.possible_moves):
            tmp_possible_moves.append([])
            for move in move_set:
                if move[0] not in new_move.path and move[1] not in new_move.path:
                    tmp_possible_moves[index].append(move)

        new_move.possible_moves = tmp_possible_moves
        new_move.path.append(position[1])

        new_move.next_moves = []
        for move_set in new_move.possible_moves:
            for move in move_set:
                if position[1] == move[0]:
                    new_move.next_moves.append(move)

        return new_move

def generalized_petersen_adj_matrix(n, k):
    adj_matrix = np.zeros((2 * n, 2 * n), dtype=int)

    for i in range(n):
        # Connect outer cycle nodes
        x_out = i
        y_out = (i + 1) % n
        adj_matrix[x_out, y_out] = 1
        adj_matrix[y_out, x_out] = 1

        # Connect inner cycle nodes
        x_in = n + i
        y_in = n + (i + k) % n
        adj_matrix[x_in, y_in] = 1
        adj_matrix[y_in, x_in] = 1

        # # Connect outer and inner cycle nodes
        # adj_matrix[x_out, y_in] = 1
        # adj_matrix[y_in, x_out] = 1

        adj_matrix[x_out, x_in] = 1
        adj_matrix[x_in, x_out] = 1

    return adj_matrix