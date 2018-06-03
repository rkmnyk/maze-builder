import imageio
import logging
import numpy as np

from abc import ABC, abstractmethod


class Maze(ABC):

    @property
    @abstractmethod
    def maze(self) -> np.ndarray:
        """
        :return: the maze
        """

    @property
    @abstractmethod
    def entry(self):
        """
        :return: the entry point
        """

    @property
    @abstractmethod
    def exit(self):
        """
        :return: the exit point
        """

    @abstractmethod
    def build(self):
        """
        build the maze
        """

    @abstractmethod
    def expand(self) -> bool:
        """
        expand the maze by one iteration
        :return: true when the maze is finished
        """

    @abstractmethod
    def build_and_animate(self, path: str, scale_factor: int):
        """
        :param path:            file path to save animation to
        :param scale_factor:    scale factor of the maze to animation (# elements -> # pixels)
        build the maze and capture animation
        """

    def save_state_to_image(self, path: str, scale_factor: int):
        """
        save the current maze state as an image
        :param path:            file path
        :param scale_factor:    scale factor (elements -> pixels)
        """
        logging.info("Saving maze to {}".format(path))
        imageio.imsave(path, self.image_snapshot(scale_factor))

    def image_snapshot(self, sf: int=1) -> np.ndarray:
        """
        :param sf: scale factor (array elements -> pixels)
        :return: np array of the maze image
        """
        image = np.zeros((self.maze.shape[0] * sf, self.maze.shape[1] * sf, 3), np.uint8)
        for x in range(self.maze.shape[0]):
            for y in range(self.maze.shape[1]):
                image[x * sf:x * sf + sf, y * sf:y * sf + sf, :] = self.maze[x, y] * 255

        if self.entry:
            image[self.entry[0] * sf:self.entry[0] * sf + sf, self.entry[1] * sf:self.entry[1] * sf + sf, [0, 2]] = 0
        if self.exit:
            image[self.exit[0] * sf:self.exit[0] * sf + sf, self.exit[1] * sf:self.exit[1] * sf + sf, [0, 2]] = 0

        return image
