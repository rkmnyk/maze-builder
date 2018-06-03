import logging
import numpy as np

from PIL import Image as PILImage
from PIL import ImageTk as PILIMageTk
from tkinter import *
from tkinter.ttk import Style

from mazes.square_maze import SquareMaze


class MazeCanvas(Canvas):

    def __init__(self, parent, **kwargs):

        Canvas.__init__(self, parent, **kwargs)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.place(x=-2, y=-2)


class MainWindow:

    def __init__(self):

        self.width = 600
        self.height = 600

        self._maze_size = 200
        self._scale_factor = 3

        self.master = Tk()
        self.master.title("MazeBuilder")

        Style().configure("TButton", padding=(0, 5, 0, 5))

        for i in range(8):
            self.master.columnconfigure(i, pad=5)
        for i in range(4):
            self.master.rowconfigure(i, pad=2)

        self.maze_canvas = MazeCanvas(self.master, width=self.width, height=self.height, highlightbackground='black')
        self.maze_canvas.grid(row=0, column=0, columnspan=8)

        # init with white box and black border
        self._image_data = PILImage.frombytes('L', (self.width, self.height),
                                              (np.ones((self.width, self.height))*255).astype('b').tostring())
        self._image = PILIMageTk.PhotoImage(image=self._image_data)
        self.maze_canvas.create_image(0, 0, image=self._image, anchor=NW)

        self.options_frame = Frame(self.master)
        self.options_frame.grid(row=1, column=0, columnspan=5, rowspan=2, sticky=W)

        self.rate_slider_label = Label(self.options_frame, text="Growth rate")
        self.rate_slider_label.grid(row=0, column=0, sticky=W)
        self.rate_slider = Scale(self.options_frame, from_=0.1, to=1, width=10, length=100,
                                 resolution=0.05, orient=HORIZONTAL)
        self.rate_slider.set(1)
        self.rate_slider.grid(row=0, column=1, columnspan=2, padx=2, pady=2)

        self.size_slider_label = Label(self.options_frame, text="Size (blocks)")
        self.size_slider_label.grid(row=1, column=0, sticky=W)
        self.size_slider = Scale(self.options_frame,  from_=50, to=300, width=10, length=100, orient=HORIZONTAL)
        self.size_slider.set(100)
        self.size_slider.grid(row=1, column=1, columnspan=2, padx=2, pady=2)

        self.square_strategy_label = Label(self.options_frame, text="Branching Strategy")
        self.square_strategy_label.grid(row=0, column=3, sticky=W)
        self.square_strategy = StringVar(self.master)
        self.square_strategy.set(SquareMaze.BranchingStrategy.RANDOM.value)
        self.square_option = OptionMenu(self.options_frame, self.square_strategy,
                                        SquareMaze.BranchingStrategy.RANDOM.value,
                                        SquareMaze.BranchingStrategy.PARTIAL.value,
                                        SquareMaze.BranchingStrategy.FULL.value)
        self.square_option.grid(row=0, column=4, columnspan=1, padx=2, pady=2)

        self.animate = IntVar()
        self.animate_checkbox = Checkbutton(self.options_frame, text="Animate",
                                            onvalue=1, offvalue=0, variable=self.animate)
        self.animate_checkbox.deselect()
        self.animate_checkbox.grid(row=1, column=3, sticky=W)

        self.build_button = Button(self.options_frame, text="Generate Maze", command=self.generate)
        self.build_button.grid(row=1, column=4, rowspan=1, columnspan=1)

        self.save_maze_location = Entry(self.master, width=15)
        self.save_maze_location.insert(0, "maze.png")
        self.save_maze_location.grid(row=2, column=5, columnspan=2, sticky=E)

        self.save_maze_button = Button(self.master, text="Save", command=self.save_maze)
        self.save_maze_button.grid(row=2, column=7, columnspan=1, sticky=W)

        self.maze = None
        self.set_square_maze()
        self.master.mainloop()

    def save_maze(self):
        """
        save the maze to f-ile
        """
        self.maze.save_state_to_image(self.save_maze_location.get(), self._scale_factor)

    def set_square_maze(self):
        """
        initialize the square maze based on config
        """
        self.set_square_maze_size()
        self.maze = SquareMaze(width=self._maze_size, height=self._maze_size, rate=self.rate_slider.get(),
                               strategy=SquareMaze.BranchingStrategy(self.square_strategy.get()))

    def set_square_maze_size(self):
        """
        set the size of the square maze such that it renders nicely
        """
        self._maze_size = self.size_slider.get()
        self._scale_factor = self.width // self._maze_size
        self._maze_size = int(self.width / self._scale_factor)

    def generate(self):
        """
        Generate the maze class and build
        """

        self.set_square_maze()

        if self.animate.get():
            self.build_and_animate()
        else:
            self.build()

    def build(self):
        """
        build the maze
        """

        self.maze.build()
        data = self.maze.image_snapshot(self._scale_factor)
        self._image_data = PILImage.frombytes('L', (data.shape[1], data.shape[0]), data[:, :, 0].astype('b').tostring())
        self._image = PILIMageTk.PhotoImage(image=self._image_data)

        self.maze_canvas.create_image(2, 2, image=self._image, anchor=NW)
        self.master.update()

    def build_and_animate(self):
        """
        build the maze and display each stage of the animation
        """

        while not self.maze.expand():
            data = self.maze.image_snapshot(self._scale_factor)
            self._image_data = PILImage.frombytes('L', (data.shape[1], data.shape[0]), data[:, :, 0].astype('b').tostring())
            self._image = PILIMageTk.PhotoImage(image=self._image_data)
            self.maze_canvas.create_image(2, 2, image=self._image, anchor=NW)
            self.master.update()


def main():
    logging.getLogger().setLevel('INFO')
    MainWindow()


if __name__ == "__main__":
    main()
