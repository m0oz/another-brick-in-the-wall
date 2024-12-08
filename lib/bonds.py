from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from random import random


class BrickWidth(IntEnum):
    QUARTER = 1
    HALF = 2
    FULL = 4


class Bond(Enum):
    STRETCHER = auto()
    FLEMISH = auto()
    ENGLISH = auto()
    WILD = auto()


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
        # Start odd rows with half brick
        bricks = [] if is_even else [Brick(width=BrickWidth.HALF)]
        remaining_width = (
            width_in_half_bricks if is_even else width_in_half_bricks - BrickWidth.HALF
        )

        # Add as many full bricks as possible
        while remaining_width > 0:
            remaining_width = _add_largest_possible_brick(bricks, remaining_width)

        return bricks

    grid: list[list[Brick]] = []
    for row in range(height_in_rows):
        grid.append(_create_row(row % 2 == 0))
    return grid


def initialize_flemish_bond(
    width_in_half_bricks: int, height_in_rows: int
) -> list[list[Brick]]:
    """Initialize the wall with a flemish bond pattern."""

    def _create_row(is_even: bool) -> list[Brick]:
        # Start odd rows with quarter brick
        bricks = [] if is_even else [Brick(width=BrickWidth.QUARTER)]
        remaining = width_in_half_bricks - (0 if is_even else BrickWidth.QUARTER)

        # Main pattern: alternate between full+half or half+full bricks
        while remaining >= BrickWidth.FULL + BrickWidth.HALF:
            if is_even:
                remaining = _add_brick(bricks, remaining, Brick())
                remaining = _add_brick(bricks, remaining, Brick(width=BrickWidth.HALF))
            else:
                remaining = _add_brick(bricks, remaining, Brick(width=BrickWidth.HALF))
                remaining = _add_brick(bricks, remaining, Brick())

        # Fill remaining space with largest possible bricks
        while remaining > 0:
            remaining = _add_largest_possible_brick(bricks, remaining)

        return bricks

    grid: list[list[Brick]] = []
    for row in range(height_in_rows):
        grid.append(_create_row(row % 2 == 0))
    return grid


def initialize_english_bond(
    width_in_half_bricks: int, height_in_rows: int
) -> list[list[Brick]]:
    """Initialize the wall with an English bond pattern."""

    def _create_even_row() -> list[Brick]:
        bricks: list[Brick] = []
        remaining = width_in_half_bricks
        while remaining > 0:
            remaining = _add_largest_possible_brick(bricks, remaining)
        return bricks

    def _create_odd_row() -> list[Brick]:
        # Start odd rows with quarter brick
        bricks = [Brick(width=BrickWidth.QUARTER)]
        remaining = width_in_half_bricks - BrickWidth.QUARTER

        # Add as many half bricks as possible
        while remaining >= BrickWidth.HALF:
            remaining = _add_brick(bricks, remaining, Brick(width=BrickWidth.HALF))
        while remaining > 0:
            remaining = _add_largest_possible_brick(bricks, remaining)
        return bricks

    grid = []
    for row in range(height_in_rows):
        grid.append(_create_even_row() if row % 2 == 0 else _create_odd_row())
    return grid


def initialize_wild_bond(
    width_in_half_bricks: int, height_in_rows: int
) -> list[list[Brick]]:
    """Initialize the wall with Wildverband pattern.
    https://www.joostdevree.nl/shtmls/wildverband.shtml
    """

    def _create_row(is_even: bool, previous_row: list[Brick] | None) -> list[Brick]:
        # Initialize row with appropriate starter brick
        bricks = [Brick(width=BrickWidth.FULL if is_even else BrickWidth.QUARTER)]
        remaining_width = width_in_half_bricks - bricks[0].width

        consecutive_full = consecutive_half = 0

        while remaining_width >= BrickWidth.FULL:
            # Determine next brick based on pattern rules
            if consecutive_full == 5:
                brick = Brick(width=BrickWidth.HALF)
                consecutive_full, consecutive_half = 0, 1
            elif consecutive_half == 3:
                brick = Brick()  # Full brick
                consecutive_full, consecutive_half = 1, 0
            else:
                # Random brick with pattern checking
                brick = Brick(
                    width=BrickWidth.HALF if random() < 0.3 else BrickWidth.FULL
                )

                # Avoid head joints with previous row
                if previous_row and _bricks_have_head_joint_at_position(
                    previous_row, sum(b.width for b in bricks) + brick.width
                ):
                    brick = Brick(
                        width=BrickWidth.FULL
                        if brick.width == BrickWidth.HALF
                        else BrickWidth.FULL
                    )

            # Update counters and add brick
            if brick.width == BrickWidth.HALF:
                consecutive_half += 1
                consecutive_full = 0
            else:
                consecutive_full += 1
                consecutive_half = 0

            remaining_width = _add_brick(bricks, remaining_width, brick)

        # Fill remaining space with largest possible bricks
        while remaining_width > 0:
            remaining_width = _add_largest_possible_brick(bricks, remaining_width)

        return bricks

    grid: list[list[Brick]] = [_create_row(True, None)]
    for row in range(1, height_in_rows):
        while True:
            candidate_bricks = _create_row(row % 2 == 0, grid[-1])
            if _bricks_are_wild(grid, candidate_bricks):
                break
        grid.append(candidate_bricks)
    return grid


def _add_brick(bricks: list[Brick], remaining_width: int, brick: Brick) -> int:
    """Add a brick to the list and return the remaining width"""
    bricks.append(brick)
    remaining_width -= brick.width
    return remaining_width


def _add_largest_possible_brick(bricks: list[Brick], remaining_width: int) -> int:
    """Helper to add the largest possible brick and return remaining width"""
    if remaining_width >= BrickWidth.FULL:
        return _add_brick(bricks, remaining_width, Brick())
    if remaining_width >= BrickWidth.HALF:
        return _add_brick(bricks, remaining_width, Brick(width=BrickWidth.HALF))
    if remaining_width >= BrickWidth.QUARTER:
        return _add_brick(bricks, remaining_width, Brick(width=BrickWidth.QUARTER))
    return remaining_width


def _bricks_have_head_joint_at_position(bricks: list[Brick], position: int) -> bool:
    """Check if there is a head joint at the given position"""
    width_bricks = 0
    for brick in bricks:
        width_bricks += brick.width
        if width_bricks == position:
            return True
    return False


def _bricks_are_wild(
    grid: list[list[Brick]], bricks: list[Brick], max_steps: int = 4
) -> bool:
    """Check if the given row forms a valid wildverband pattern with the previous rows.
    A wild bond pattern is valid if it does not contain both an inclining and a declining step.
    """
    if len(grid) < max_steps:
        return True

    position = 0
    for brick in bricks:
        position += brick.width
        # check inclining steps
        has_inclining_steps = True
        for i, previous_row in enumerate(grid[-max_steps:]):
            if not _bricks_have_head_joint_at_position(
                previous_row, position + i * BrickWidth.QUARTER
            ):
                has_inclining_steps = False
                break
        # check declining steps
        has_declining_steps = True
        for i, previous_row in enumerate(grid[-max_steps:]):
            if not _bricks_have_head_joint_at_position(
                previous_row, position - i * BrickWidth.QUARTER
            ):
                has_declining_steps = False
                break
        print(f"Row {position}: {has_inclining_steps} {has_declining_steps}")
        if has_inclining_steps and has_declining_steps:
            return False
    return True
