import pytest

from ..bonds import Bond, BrickWidth
from ..wall_state import Stride, WallState, find_best_stride

# pylint: disable=protected-access


def test_initialize_stretcher():
    wall = WallState()
    wall.initialize_wall(8 * BrickWidth.HALF, 3, Bond.STRETCHER)

    # Check grid dimensions
    assert len(wall.bricks) == 3
    assert all(
        sum([brick.width for brick in row]) == 4 * BrickWidth.FULL
        for row in wall.bricks
    )

    # Check row 0 (even row) - all full bricks
    assert all(brick.width == BrickWidth.FULL for brick in wall.bricks[0])
    assert all(not brick.placed for brick in wall.bricks[0])
    assert all(brick.stride is None for brick in wall.bricks[0])

    # Check row 1 (odd row) - half bricks at edges, full bricks in middle
    assert wall.bricks[1][0].width == BrickWidth.HALF
    assert wall.bricks[1][-1].width == BrickWidth.HALF
    assert all(brick.width == BrickWidth.FULL for brick in wall.bricks[1][1:-1])

    # Check row 2 (even row) - all full bricks
    assert all(brick.width == BrickWidth.FULL for brick in wall.bricks[2])


def test_initialize_grid_minimal():
    wall = WallState()
    wall.initialize_wall(2 * BrickWidth.HALF, 1, Bond.STRETCHER)

    assert len(wall.bricks) == 1
    assert len(wall.bricks[0]) == 1
    assert wall.bricks[0][0].width == BrickWidth.FULL


def test_initialize_grid_invalid_dimensions():
    wall = WallState()

    # Test invalid dimensions
    with pytest.raises(AssertionError):
        wall.initialize_wall(0, 1, Bond.STRETCHER)

    with pytest.raises(AssertionError):
        wall.initialize_wall(1, 0, Bond.STRETCHER)


def test_get_brick_edges():
    wall = WallState()
    wall.initialize_wall(4 * BrickWidth.HALF, 2, Bond.STRETCHER)

    # Test even row (all full bricks)
    assert wall._get_brick_edges(0, 0) == (0, BrickWidth.FULL)  # First brick
    assert wall._get_brick_edges(0, 1) == (BrickWidth.FULL, 2 * BrickWidth.FULL)

    # Test odd row (half bricks at edges)
    assert wall._get_brick_edges(1, 0) == (0, BrickWidth.HALF)
    assert wall._get_brick_edges(1, 1) == (
        BrickWidth.HALF,
        BrickWidth.HALF + BrickWidth.FULL,
    )
    assert wall._get_brick_edges(1, 2) == (
        BrickWidth.HALF + BrickWidth.FULL,
        2 * BrickWidth.FULL,
    )


def test_has_placed_brick_at_position():
    wall = WallState()
    wall.initialize_wall(6 * BrickWidth.HALF, 2, Bond.STRETCHER)

    # Place some bricks
    wall.bricks[0][0].placed = True  # First brick in first row
    wall.bricks[0][2].placed = True  # Last brick in first row
    wall.bricks[1][0].placed = True  # First brick in second row (half)

    # First brick
    assert wall._has_placed_brick_at_position(0, 0) is True
    assert wall._has_placed_brick_at_position(0, BrickWidth.HALF) is True
    assert wall._has_placed_brick_at_position(0, BrickWidth.FULL) is True

    # Middle of first row (no brick)
    assert (
        wall._has_placed_brick_at_position(0, BrickWidth.FULL + BrickWidth.HALF)
        is False
    )

    # Third brick
    assert wall._has_placed_brick_at_position(0, 3 * BrickWidth.FULL) is True

    # Test second row (half bricks at edges)
    assert wall._has_placed_brick_at_position(1, 0) is True
    assert wall._has_placed_brick_at_position(1, BrickWidth.HALF) is True
    assert wall._has_placed_brick_at_position(1, BrickWidth.FULL) is False

    # Test out of bounds
    assert wall._has_placed_brick_at_position(0, 4 * BrickWidth.FULL) is False


def test_can_place_brick():
    wall = WallState()
    wall.initialize_wall(6 * BrickWidth.HALF, 3, Bond.STRETCHER)

    # Test placing a brick in the bottom row (always supported)
    assert wall._can_place_brick(0, 0) is True

    # Place some bricks in the first row to support the second row
    wall.bricks[0][0].placed = True
    wall.bricks[0][2].placed = True

    # Test placing a brick that is already placed
    assert wall._can_place_brick(0, 0) is False

    # Test placing a brick in the second row
    assert wall._can_place_brick(1, 0) is True
    assert wall._can_place_brick(1, 1) is False
    assert wall._can_place_brick(1, 2) is False
    assert wall._can_place_brick(1, 3) is True

    # Test placing a brick in the third row (not supported)
    assert wall._can_place_brick(2, 0) is False
    assert wall._can_place_brick(2, 1) is False
    assert wall._can_place_brick(2, 2) is False

    # Place bricks remaining brick in the first
    wall.bricks[0][1].placed = True

    # Test placing a brick in the second row, all are now supported
    assert wall._can_place_brick(1, 0) is True
    assert wall._can_place_brick(1, 1) is True
    assert wall._can_place_brick(1, 2) is True
    assert wall._can_place_brick(1, 3) is True


def test_is_brick_in_stride_window():
    # pylint: disable=protected-access
    wall = WallState()
    wall.initialize_wall(6 * BrickWidth.HALF, 3, Bond.STRETCHER)

    # Test case first row, first full brick is not fully inside stride window
    stride = Stride(0, 0, 2 * BrickWidth.FULL, 2)
    assert wall._is_brick_in_stride_window(0, 0, stride) is True
    assert wall._is_brick_in_stride_window(0, 1, stride) is True
    assert wall._is_brick_in_stride_window(0, 2, stride) is False

    # Test case second row, first half brick and full brick are not fully inside
    # stride window
    assert wall._is_brick_in_stride_window(1, 0, stride) is True
    assert wall._is_brick_in_stride_window(1, 1, stride) is True
    assert wall._is_brick_in_stride_window(1, 2, stride) is False
    assert wall._is_brick_in_stride_window(1, 3, stride) is False


def test_place_bricks_for_stride():
    wall = WallState()
    wall.initialize_wall(6 * BrickWidth.HALF, 3, Bond.STRETCHER)

    # Place bricks in the bottom row
    wall.bricks[0][0].placed = True
    wall.bricks[0][1].placed = True
    wall.bricks[0][2].placed = True

    # Create a stride window that covers the middle section
    placed_bricks = list(
        wall.place_bricks_for_stride(Stride(BrickWidth.FULL, 1, 2 * BrickWidth.FULL, 2))
    )

    # Should yield bricks that can be placed in the stride window
    assert len(placed_bricks) == 3
    for brick in placed_bricks:
        assert brick.placed is True

    # Right half of second row was placed
    assert wall.bricks[1][0].placed is False
    assert wall.bricks[1][1].placed is False
    assert wall.bricks[1][2].placed is True
    assert wall.bricks[1][3].placed is True

    # Right-most brick in third row was placed
    assert wall.bricks[2][0].placed is False
    assert wall.bricks[2][1].placed is False
    assert wall.bricks[2][2].placed is True


def test_find_best_stride():
    wall = WallState()
    wall.initialize_wall(6 * BrickWidth.HALF, 3, Bond.STRETCHER)

    # Place bricks in the bottom row and half bricks at the edges of the second row
    # ██        ██
    # ████    ████
    wall.bricks[0][0].placed = True
    wall.bricks[0][0].placed = True
    wall.bricks[0][2].placed = True
    wall.bricks[1][0].placed = True
    wall.bricks[1][3].placed = True

    # Find best stride position
    optimal_stride = find_best_stride(
        wall, stride_width=2 * BrickWidth.FULL, stride_height=2
    )

    # Should start at row 0
    assert optimal_stride.origin_y == 0

    # Should start at x=BrickWidth.HALF to maximize placeable bricks
    # This allows placing 1 brick on row 0 and 2 bricks on row 1
    assert optimal_stride.origin_x == BrickWidth.HALF

    # Verify by placing bricks at the optimal position
    placed_bricks = list(wall.place_bricks_for_stride(optimal_stride))
    assert len(placed_bricks) == 3  # Should be able to place 3 bricks
