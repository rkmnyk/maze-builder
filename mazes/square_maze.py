import imageio
import logging
import numpy as np
import random

from enum import Enum
from typing import List, Tuple

from mazes.base_maze import Maze


class SquareMaze(Maze):

    class BranchingStrategy(Enum):

        RANDOM = "Random"
        PARTIAL = "Partial"
        FULL = "Full"

    def __init__(self, width: int, height: int, rate: float=1,
                 strategy: BranchingStrategy=BranchingStrategy.RANDOM):
        """

        :param width:       width of the maze (blocks)
        :param height:      height of the maze (blocks)
        :param rate:        rate of maze growth
        :param strategy:    branching strategy - how many of the possible new branches are activated
        """
        
        self.__exit = None
        self.__entry = None
        self.__height = height
        self.__width = width

        self.__strategy = strategy
        self.__rate = max(0.1, rate)

        sy = np.random.randint(2, height - 2)
        sx = np.random.randint(2, width - 2)

        self.__maze = np.zeros((width, height), dtype=int)
        self.__branches = {(sx, sy): (sx, sy)}
        self.__maze[sx, sy] = 1

        logging.info("Initialized square maze of size ({}x{}), seeded at ({}x{})"
                     .format(self.__width, self.__height, sx, sy))

    @property
    def maze(self) -> np.ndarray:
        return self.__maze

    @property
    def entry(self):
        return self.__entry

    @property
    def exit(self):
        return self.__exit

    def __new_branches(self, moves: List) -> List:
        """

        :param moves:
        :return:
        """

        if self.__strategy == self.BranchingStrategy.RANDOM:
            return random.sample(moves, np.random.randint(1, len(moves))) if len(moves) > 1 else moves
        elif self.__strategy == self.BranchingStrategy.PARTIAL:
            return random.sample(moves, min(len(moves), 2))
        else:
            return moves

    def __activate(self, x: int, y: int) -> None:
        """
        activate maze block at given location
        :param x: x position
        :param y: y position
        """
        self.__maze[x, y] = 1

    def __erase(self, x: int, y: int) -> None:
        """
        remove maze block at given location
        :param x: x position
        :param y: y position
        """
        self.__maze[x, y] = 0

    def __is_occupied(self, x: int, y: int) -> bool:
        """
        determine whether a given set of co-ordinates are active
        :param x: x position
        :param y: y position
        :return: true / false if active
        """
        return self.__maze[x, y]

    def __check_row(self, x: int, y: int) -> bool:
        """
        checks whether or not a row of 3 is occupied or in any branches
        :param x: x position
        :param y: y position
        :return: true if the row is free
        """
        return not any([self.__is_occupied(x, y + i) for i in (-1, 0, 1)] +
                       [self.__branches.get((x, y + i)) for i in (-1, 0, 1)])
        
    def __check_col(self, x: int, y: int) -> bool:
        """
        checks whether a given column of 3 is occupied or in any branches
        :param x: x position
        :param y: y position
        :return: true if the column is free
        """
        return not any([self.__is_occupied(x + i, y) for i in (-1, 0, 1)] +
                       [self.__branches.get((x + i, y)) for i in (-1, 0, 1)])

    def free_spots(self, pos: Tuple[int, int]) -> List:
        """
        this function checks free slots surrounding a piece. it automatically creates an entrance and an exit
        at the top and bottom of the maze, but never the left or right.
        :param pos: x, y position
        :return: list of available moves
        """
        x, y = pos
        possible_slots = []

        if x + 2 == self.__width:
            if self.__exit is None:
                # if we are next to the right edge and the exit is not set, connect and return
                self.__activate(x + 1, y)
                self.__exit = (x + 1, y)
            return []
        elif self.__check_row(x + 1, y) and self.__check_row(x + 2, y):
            # otherwise check the outer rows and add them
            possible_slots.append((x + 1, y))

        if x > 1:
            if self.__check_row(x - 1, y) and self.__check_row(x - 2, y):
                # if we are not on the left edge, then check the left rows and append
                possible_slots.append((x - 1, y))
        elif self.__entry is None:
            # if we are on the left edge and there's no entry, connect
            self.__activate(0, y)
            self.__entry = (0, y)
            return []

        # check left and right.
        if y + 2 < self.__height and self.__check_col(x, y + 1) and self.__check_col(x, y + 2):
            possible_slots.append((x, y + 1))

        if y > 1 and self.__check_col(x, y - 1) and self.__check_col(x, y - 2):
            possible_slots.append((x, y - 1))
                    
        return possible_slots

    def __extend_path(self, pos) -> None:
        """
        extend the maze by activating a position and adding the next move to branches
        :param pos: x, y position
        """

        self.__activate(pos[0], pos[1])

        try:
            del self.__branches[pos]
        except KeyError:
            logging.warning("Attempting to delete non-existent branch.")

        moves = self.free_spots(pos)

        if len(moves) == 0:
            return

        # take a subsample of the available moves and activate new branches with a random wait
        for branch in self.__new_branches(moves):
            self.__branches[branch] = branch

    def __build_iteration(self) -> None:
        """
        perform one iteration of the build process
        """
        for key in [key for key in self.__branches.keys() if np.random.rand(1)[0] < self.__rate]:
            self.__extend_path(key)

    def expand(self) -> bool:
        """
        expand maze by one and return true if construction is complete
        :return:
        """
        self.__build_iteration()
        return len(self.__branches.keys()) == 0

    def build(self) -> None:
        """
        build the maze
        """

        logging.info("Building square maze...")
        while len(self.__branches.keys()) > 0:
            self.__build_iteration()

    def build_and_animate(self, path: str, scale_factor: int) -> None:
        """
        build the maze and capture the growth animation
        :param path:            file path
        :param scale_factor:    scale factor (elements -> pixels)
        """

        logging.info("Building and animating square maze...")
        images = []

        while len(self.__branches) > 0:
            self.__build_iteration()
            images.append(self.image_snapshot(scale_factor))

        logging.info("Build complete.")
        logging.info("Animating construction...")

        imageio.mimsave(path, images)
        logging.info("Animation complete.")
