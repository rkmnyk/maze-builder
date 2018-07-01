import imageio
import logging
import numpy as np
import random

from enum import Enum
from typing import List, Tuple

from mazes.base_maze import Maze


class BranchingStrategy(Enum):
    RANDOM = "Random"
    PARTIAL = "Partial"
    FULL = "Full"


class SquareMaze(Maze):

    def __init__(self, width: int, height: int, n_trees: int = 1, rate: float = 1,
                 strategy: BranchingStrategy = BranchingStrategy.RANDOM):
        """

        :param width:       width of the maze (blocks)
        :param height:      height of the maze (blocks)
        :param n_trees:     number of maze trees
        :param rate:        rate of maze growth
        :param strategy:    branching strategy - how many of the possible new branches are activated
        """

        self.__exit = None
        self.__entry = None
        self.__height = height
        self.__width = width
        self.__strategy = strategy
        self.__rate = max(0.1, rate)
        self.__trees = {}
        self.__block_assignments = {}
        self.__maze = np.zeros((width, height), dtype=int)
        self.__mappings = {i + 1: i + 1 for i in range(n_trees)}
        # seed the trees. ensure there is no overlap by randomly sampling from the grid.
        scale = 5
        for i, v in enumerate(zip(random.sample([i for i in range((self.__width - 4) // scale)], n_trees),
                                  random.sample([i for i in range((self.__height - 4) // scale)], n_trees))):
            pos = [(2 + i + v[0] * scale, 2 + v[1] * scale) for i in (-1, 0, 1)]
            pos += [(2 + v[0] * scale, 2 + i + v[1] * scale) for i in (-1, 1)]

            for p in pos:
                self.__maze[p[0], p[1]] = i + 1

            self.__trees[i + 1] = pos

        logging.info("Initialized square tree maze of size ({}x{}) with {} seeds"
                     .format(self.__width, self.__height, n_trees))

    @property
    def maze(self) -> np.ndarray:
        return self.__maze

    @property
    def entry(self):
        return self.__entry

    @property
    def exit(self):
        return self.__exit

    def __new_branches(self, moves: List) -> List[Tuple[int, int]]:
        """
        subsamples a list of available moves based on the branching strategy
        :param moves: a list of available moves
        :return: subsampled list of moves
        """
        if self.__strategy == BranchingStrategy.RANDOM:
            return random.sample(moves, np.random.randint(1, len(moves))) if len(moves) > 1 else moves
        elif self.__strategy == BranchingStrategy.PARTIAL:
            return random.sample(moves, min(len(moves), 2))
        else:
            return moves

    def __activate(self, x: int, y: int, tree: int) -> None:
        """
        activate maze block at given location
        :param x: x position
        :param y: y position
        """
        self.__maze[x, y] = tree

    def __erase(self, x: int, y: int) -> None:
        """
        remove maze block at given location
        :param x: x position
        :param y: y position
        """
        self.__maze[x, y] = 0

    def __check_row(self, x: int, y: int) -> bool:
        """
        checks whether or not a row of 3 is occupied or in any branches
        :param x: x position
        :param y: y position
        :return: true if the row is free
        """
        return not any([self.__maze[x, y + i] for i in (-1, 0, 1)])

    def __check_col(self, x: int, y: int) -> bool:
        """
        checks whether a given column of 3 is occupied or in any branches
        :param x: x position
        :param y: y position
        :return: true if the column is free
        """
        return not any([self.__maze[x + i, y] for i in (-1, 0, 1)])

    def __remap(self, tree1: int, tree2: int) -> None:
        """
        for joining trees, this function remaps tree 1 to tree 2
        :param tree1: tree index to map from
        :param tree2: tree index to map to
        """
        # if the branch was deleted in the same iteration skip
        if self.__trees.get(tree1) is None:
            return

        # re map all mazes to tree2
        self.__mappings[tree1] = tree2
        for key, value in self.__mappings.items():
            if value == tree1:
                self.__mappings[key] = tree2
        self.__trees[tree2] += self.__trees[tree1]
        del self.__trees[tree1]

    def __check_and_join_row(self, x: int, y: int, tree: int, increment: int) -> bool:
        """
        checks a row and force join mazes if possible
        :param x:           x pos
        :param y:           y pos
        :param tree:        tree index
        :param increment:   direction to search (+/-1)
        :return: true if the row can be occupied else false
        """
        for m in [self.__maze[x + (2 * increment), y + i] for i in (-1, 0, 1)]:
            # if any square maps to a different maze connect it and redo the mappings
            if m == 0:
                continue
            main_tree = self.__mappings.get(m, tree)
            if main_tree != tree:
                self.__activate(x + increment, y, tree)
                self.__activate(x + (2 * increment), y, tree)
                self.__remap(tree, main_tree)
            return False
        return True

    def __check_and_join_col(self, x: int, y: int, tree: int, increment: int) -> bool:
        """
        checks a column and force join mazes if possible
        :param x:           x pos
        :param y:           y pos
        :param tree:        tree index
        :param increment:   direction to search (+/-1)
        :return: true if the row can be occupied else false
        """
        for m in [self.__maze[x + i, y + (2 * increment)] for i in (-1, 0, 1)]:
            # if any square maps to a different maze connect it and redo the mappings
            if m == 0:
                continue

            main_tree = self.__mappings.get(m, tree)
            if main_tree != tree:
                self.__activate(x, y + increment, tree)
                self.__activate(x, y + (2 * increment), tree)
                self.__remap(tree, main_tree)
            return False
        return True

    def __free_spots(self, pos: Tuple[int, int], tree: int) -> List:
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
                self.__activate(x + 1, y, tree)
                self.__exit = (x + 1, y)
            return []

        elif self.__check_row(x + 1, y):
            # iterate through this row and compare maze assignments
            if self.__check_and_join_row(x, y, tree, 1):
                possible_slots.append((x + 1, y))

        if x > 1:
            if self.__check_row(x - 1, y):
                if self.__check_and_join_row(x, y, tree, -1):
                    possible_slots.append((x - 1, y))

        elif self.__entry is None:
            # if we are on the left edge and there's no entry, connect
            self.__activate(0, y, tree)
            self.__entry = (0, y)
            return []

        # check left and right.
        if y + 2 < self.__height and self.__check_col(x, y + 1):
            if self.__check_and_join_col(x, y, tree, 1):
                possible_slots.append((x, y + 1))

        if y > 1 and self.__check_col(x, y - 1):
            if self.__check_and_join_col(x, y, tree, -1):
                possible_slots.append((x, y - 1))

        return possible_slots

    def __branch_out(self, pos, tree) -> List[Tuple[int, int]]:
        """
        extend and activate all new moves around a branch
        :param pos:
        :return:
        """
        moves = self.__new_branches(self.__free_spots(pos, tree))
        for x, y in moves:
            self.__activate(x, y, tree)
        return moves

    def __build_iteration(self) -> None:
        """ perform one iteration of the build process """
        trees = [t for t in self.__trees.keys()]
        for tree in trees:
            heads = []
            branches = self.__trees[tree]
            for i in range(len(branches) - 1, -1, -1):
                if self.__trees.get(tree) and np.random.rand(1)[0] < self.__rate:
                    heads += self.__branch_out(branches.pop(i), tree)
            self.__trees[self.__mappings[tree]] += heads

            # NB: this can cause errors when seeds spawn near the edge
            if len(self.__trees[self.__mappings[tree]]) == 0:
                logging.info("deleting tree with id {}".format(tree))
                del self.__trees[self.__mappings[tree]]

    def expand(self) -> bool:
        """
        expand maze by one and return true if construction is complete
        :return:
        """
        self.__build_iteration()
        return len(self.__trees.keys()) == 0

    def build(self) -> None:
        """
        build the maze
        """
        logging.info("Building square maze...")
        while len(self.__trees.keys()) > 0:
            self.__build_iteration()

    def build_and_animate(self, path: str, scale_factor: int) -> None:
        """
        build the maze and capture the growth animation
        :param path:            file path
        :param scale_factor:    scale factor (elements -> pixels)
        """

        logging.info("Building and animating square maze...")
        images = []

        while len(self.__trees.keys()) > 0:
            self.__build_iteration()
            images.append(self.image_snapshot(scale_factor))

        logging.info("Build complete.")
        logging.info("Animating construction...")

        imageio.mimsave(path, images)
        logging.info("Animation complete.")
        
    def image_snapshot(self, sf: int=1) -> np.ndarray:
        """
        overrides snapshot to show joints and seeds
        :param sf: scale factor (array elements -> pixels)
        :return: np array of the maze image
        """
        return super(SquareMaze, self).image_snapshot(sf)
        # for x in self.joins:
        #     image[x[0] * sf:x[0] * sf + sf, x[1] * sf:x[1] * sf + sf, [0, 2]] = 0
        # for x in self.seeds:
        #     image[x[0] * sf:x[0] * sf + sf, x[1] * sf:x[1] * sf + sf, [1, 2]] = 0
        # return image
