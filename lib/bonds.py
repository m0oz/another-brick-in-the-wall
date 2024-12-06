from dataclasses import dataclass
from enum import Enum, IntEnum, auto


class BrickWidth(IntEnum):
    QUARTER = 1
    HALF = 2
    FULL = 4


class Bond(Enum):
    STRETCHER = auto()
    FLEMISH = auto()
    ENGLISH = auto()


@dataclass
class Brick:
    placed: bool = False
    width: BrickWidth = BrickWidth.FULL
    stride: int | None = None


def initialize_stretcher_bond(
    width_in_half_bricks: int, height_in_rows: int
) -> list[list[Brick]]:
    """Initialize the grid with a stretcher bond pattern."""

    def _create_row(is_even: bool) -> list[Brick]:
        row = [] if is_even else [Brick(width=BrickWidth.HALF)]
        remaining = (
            width_in_half_bricks if is_even else width_in_half_bricks - BrickWidth.HALF
        )

        # Add full bricks while possible
        while remaining >= BrickWidth.FULL:
            row.append(Brick())
            remaining -= BrickWidth.FULL

        # Add final half brick if needed
        if remaining >= BrickWidth.HALF:
            row.append(Brick(width=BrickWidth.HALF))

        return row

    grid: list[list[Brick]] = []
    for row in range(height_in_rows):
        grid.append(_create_row(row % 2 == 0))
    return grid


def initialize_flemish_bond(
    width_in_half_bricks: int, height_in_rows: int
) -> list[list[Brick]]:
    """Initialize the wall with a flemish bond pattern."""

    def _create_row(is_even: bool) -> list[Brick]:
        # Start with quarter brick for odd rows
        row = [] if is_even else [Brick(width=BrickWidth.QUARTER)]
        remaining = width_in_half_bricks - (0 if is_even else BrickWidth.QUARTER)

        # Main pattern: alternate between full+half or half+full bricks
        while remaining >= BrickWidth.FULL + BrickWidth.HALF:
            if is_even:
                row.extend([Brick(), Brick(width=BrickWidth.HALF)])  # full + half
            else:
                row.extend([Brick(width=BrickWidth.HALF), Brick()])  # half + full
            remaining -= BrickWidth.FULL + BrickWidth.HALF

        # Fill remaining space with largest possible bricks
        while remaining > 0:
            remaining = _add_largest_possible_brick(row, remaining)

        return row

    grid: list[list[Brick]] = []
    for row in range(height_in_rows):
        grid.append(_create_row(row % 2 == 0))
    return grid


def initialize_english_bond(
    width_in_half_bricks: int, height_in_rows: int
) -> list[list[Brick]]:
    """Initialize the wall with an English bond pattern."""

    def _create_even_row() -> list[Brick]:
        row: list[Brick] = []
        remaining = width_in_half_bricks
        while remaining > 0:
            remaining = _add_largest_possible_brick(row, remaining)
        return row

    def _create_odd_row() -> list[Brick]:
        row = [Brick(width=BrickWidth.QUARTER)]
        remaining = width_in_half_bricks - BrickWidth.QUARTER

        while remaining > BrickWidth.QUARTER:
            row.append(Brick(width=BrickWidth.HALF))
            remaining -= BrickWidth.HALF

        if remaining > 0:
            row.append(Brick(width=BrickWidth.QUARTER))
        return row

    grid = []
    for row in range(height_in_rows):
        grid.append(_create_even_row() if row % 2 == 0 else _create_odd_row())
    return grid


def _add_largest_possible_brick(row: list[Brick], remaining: int) -> int:
    """Helper to add the largest possible brick and return remaining width"""
    if remaining >= BrickWidth.FULL:
        row.append(Brick())
        return remaining - BrickWidth.FULL
    elif remaining >= BrickWidth.HALF:
        row.append(Brick(width=BrickWidth.HALF))
        return remaining - BrickWidth.HALF
    elif remaining > 0:
        row.append(Brick(width=BrickWidth.QUARTER))
        return remaining - BrickWidth.QUARTER
    return remaining
