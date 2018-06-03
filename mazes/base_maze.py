import imageio
import numpy as np
from abc import ABC, abstractmethod

class Maze(ABC):

    @property
    @abstractmethod
    def maze(self) -> np.ndarray:
        """
        :return: the maze
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
        imageio.imsave(path, self.image_snapshot(scale_factor))

    def image_snapshot(self, sf: int=1) -> np.ndarray:
        """
        :param sf: scale factor (array elements -> pixels)
        :return: np array of the maze image
        """
        image = np.zeros((self.maze.shape[0] * sf, self.maze.shape[1] * sf, 3), np.uint8)
        for x in range(self.maze.shape[0]):
            for y in range(self.maze.shape[1]):
                for s in range(sf):
                    image[x * sf:x * sf + s, y * sf:y * sf + s, :] = self.maze[x, y] * 255
        return image
