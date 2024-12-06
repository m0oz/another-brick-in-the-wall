from copy import deepcopy
from dataclasses import dataclass, field
from typing import Generator

from .bonds import (
    Bond,
    Brick,
    initialize_english_bond,
    initialize_flemish_bond,
    initialize_stretcher_bond,
)


@dataclass
class Stride:
    origin_x: int
    origin_y: int
    width: int
    height: int


@dataclass
class WallState:
    """Keeps track of the state of the wall and provides methods to manipulate it."""

    bricks: list[list[Brick]] = field(default_factory=list)
    current_stride: int = 0

    def to_dict(self) -> dict:
        return {
            "bricks": [
                [
                    {
                        "placed": brick.placed,
                        "width": brick.width.value,
                        "stride": brick.stride,
                    }
                    for brick in row
                ]
                for row in self.bricks
            ],
            "is_complete": self.is_complete,
        }

    @property
    def width(self) -> int:
        return sum(brick.width for brick in self.bricks[0])

    @property
    def height(self) -> int:
        return len(self.bricks)

    @property
    def is_complete(self) -> bool:
        return all(brick.placed for brick in self.bricks[-1])

    def initialize_wall(
        self, width_in_half_bricks: int, height_in_rows: int, bond: Bond
    ) -> None:
        """Common initialization for all bond patterns."""
        assert (
            width_in_half_bricks > 0 and height_in_rows > 0
        ), "Number of rows and columns must be positive"

        self.bricks = []
        self.current_stride = 0

        if bond == Bond.STRETCHER:
            self.bricks = initialize_stretcher_bond(
                width_in_half_bricks, height_in_rows
            )
        elif bond == Bond.FLEMISH:
            self.bricks = initialize_flemish_bond(width_in_half_bricks, height_in_rows)
        elif bond == Bond.ENGLISH:
            self.bricks = initialize_english_bond(width_in_half_bricks, height_in_rows)


    def reset(self) -> None:
        """Reset the wall to its initial state."""
        for row in self.bricks:
            for brick in row:
                brick.placed = False
                brick.stride = None
        self.current_stride = 1

    def _get_brick_edges(self, row: int, col: int) -> tuple[int, int]:
        """Get distances to left and right edge of a brick in a row"""
        try:
            row_blocks = self.bricks[row]
        except IndexError as e:
            raise ValueError(f"Row out of bounds: {row}") from e

        # Get left edge by summing widths of all bricks before this one
        left_edge = sum(row_blocks[i].width for i in range(col))
        right_edge = left_edge + row_blocks[col].width

        return (left_edge, right_edge)

    def _has_placed_brick_at_position(self, row: int, position: int) -> bool:
        """Check if there is a placed brick at a given position in a row."""
        try:
            row_blocks = self.bricks[row]
        except IndexError as e:
            raise ValueError(f"Row out of bounds: {row}") from e

        # Find which brick contains this position by tracking cumulative width
        current_edge = 0
        for i, brick in enumerate(row_blocks):
            next_edge = current_edge + brick.width

            # Check if position is at this brick
            if current_edge <= position <= next_edge:
                # If exactly at right edge, check current and next brick
                if position == next_edge and i + 1 < len(row_blocks):
                    return brick.placed or row_blocks[i + 1].placed
                # Otherwise just check current brick
                return brick.placed

            current_edge = next_edge

        return False  # Position is beyond row bounds

    def _can_place_brick(self, row: int, col: int) -> bool:
        """Check if a given brick is supported and can be placed."""
        try:
            brick = self.bricks[row][col]
        except IndexError as e:
            raise ValueError(f" Brick out of bounds: row {row}, col {col}") from e

        if brick.placed:
            return False

        if row == 0:
            return True  # Bottom row is always supported

        (left_edge, right_edge) = self._get_brick_edges(row, col)

        # Check if left middle and right are supported
        left_supported = self._has_placed_brick_at_position(row - 1, left_edge)
        right_supported = self._has_placed_brick_at_position(row - 1, right_edge)

        return left_supported and right_supported

    def _is_brick_in_stride_window(self, row: int, col: int, stride: Stride) -> bool:
        (left_edge, right_edge) = self._get_brick_edges(row, col)
        return (
            left_edge >= stride.origin_x
            and right_edge <= stride.origin_x + stride.width
        )

    def place_bricks_left_to_right(self) -> Generator[Brick, None, None]:
        """Place bricks left to right, bottom to top."""
        for row in self.bricks:
            for brick in row:
                if not brick.placed:
                    brick.placed = True
                    yield brick

    def place_bricks_for_stride(
        self,
        stride: Stride,
    ) -> Generator[Brick, None, None]:
        """Place all placable bricks in a given stride and yield the bricks."""
        self.current_stride += 1
        for row in range(stride.origin_y, stride.origin_y + stride.height):
            if row >= self.height:
                continue
            for col, brick in enumerate(self.bricks[row]):
                if not self._is_brick_in_stride_window(row, col, stride):
                    continue  # brick is outside stride window
                if self._can_place_brick(row, col):
                    brick.placed = True
                    brick.stride = self.current_stride
                    yield brick


def find_best_stride(wall: WallState, stride_width: int, stride_height: int) -> Stride:
    """Find the next best stride for the wall."""
    optimal_stride_origin_x = 0
    optimal_stride_origin_y = 0

    # find first row with at least one brick not placed
    for y, row in enumerate(wall.bricks):
        if any(not brick.placed for brick in row):
            optimal_stride_origin_y = y
            break

    # for the given row, find the optimal starting x position to
    # maximize number of bricks placed
    max_num_placed_bricks = 0
    for x in range(wall.width):
        # copy wall to avoid modifying original
        wall_temp = deepcopy(wall)
        num_placed_bricks = len(
            list(
                wall_temp.place_bricks_for_stride(
                    Stride(x, optimal_stride_origin_y, stride_width, stride_height)
                )
            )
        )
        if num_placed_bricks > max_num_placed_bricks:
            max_num_placed_bricks = num_placed_bricks
            optimal_stride_origin_x = x

    return Stride(
        optimal_stride_origin_x, optimal_stride_origin_y, stride_width, stride_height
    )
