import argparse
import logging
from mazes.square_maze import SquareMaze


def main():

    logging.getLogger().setLevel('INFO')
    parser = argparse.ArgumentParser(description='Generate and save a maze')
    parser.add_argument('-x', metavar='x', type=int, nargs=1,
                        help='maze width', default=[100])

    parser.add_argument('-y', metavar='y', type=int, nargs=1,
                        help='maze height', default=[100])

    parser.add_argument('-r', metavar='r', type=float, nargs=1,
                        help='growth rate (0-1)', default=[1])

    parser.add_argument('-s', metavar='s', type=str, nargs=1,
                        help='branching strategy (random, partial, full)', default=["random"])

    parser.add_argument('-p', metavar='p', type=str, nargs=1,
                        help='path to save maze to', default=["maze.png"])

    parser.add_argument('-b', metavar='b', type=int, nargs=1,
                        help='block size (pixels)', default=[3])

    args = parser.parse_args()

    strategy = {
        "random": SquareMaze.BranchingStrategy.RANDOM,
        "partial": SquareMaze.BranchingStrategy.PARTIAL,
        "full": SquareMaze.BranchingStrategy.FULL
    }

    x = args.x[0]
    y = args.y[0]
    r = args.r[0]
    s = args.s[0]
    p = args.p[0]
    b = args.b[0]

    maze = SquareMaze(width=min(20, x), height=min(20, y), rate=min(0.1, max(1, r)),
               strategy=strategy.get(s, SquareMaze.BranchingStrategy.RANDOM))
    maze.build()
    maze.save_state_to_image(path=p, scale_factor=max(1, b))


if __name__ == "__main__":
    main()
