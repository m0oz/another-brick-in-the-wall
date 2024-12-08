from unittest import TestCase

from lib.bonds import (
    Brick,
    BrickWidth,
    _check_wildverband,
    initialize_english_bond,
    initialize_flemish_bond,
    initialize_stretcher_bond,
    initialize_wild_bond,
)


class TestWildBond(TestCase):
    def test_bricks_are_wild(self):
        # Test case 1: Less than max_steps rows should always return True
        grid = [
            [Brick(width=BrickWidth.HALF)],
            [Brick(width=BrickWidth.FULL)],
        ]
        bricks = [Brick(width=BrickWidth.FULL)]
        self.assertEqual(_check_wildverband(grid, bricks, max_steps=3), 0)

        # Test case 2: Step pattern should be invalid
        bricks = [Brick(width=BrickWidth.FULL)]
        grid = [
            [  # Row 0 -> no step
                Brick(width=BrickWidth.FULL),
                Brick(width=BrickWidth.QUARTER),
            ],
            [  # Row 1 -> has step
                Brick(width=BrickWidth.FULL),
                Brick(width=BrickWidth.HALF),
            ],
            [  # Row 2 -> has step
                Brick(width=BrickWidth.FULL),
                Brick(width=BrickWidth.QUARTER),
            ],
        ]
        self.assertEqual(_check_wildverband(grid, bricks, max_steps=2), 1)
        self.assertEqual(_check_wildverband(grid, bricks, max_steps=3), 0)

        # Test case 3: ZigZag pattern should be invalid
        bricks = [Brick(width=BrickWidth.FULL)]
        grid = [
            [  # Row 0
                Brick(width=BrickWidth.FULL),
                Brick(width=BrickWidth.HALF),
            ],
            [  # Row 1 -> has zigzag
                Brick(width=BrickWidth.FULL),
            ],
            [  # Row 2 -> has zigzag
                Brick(width=BrickWidth.FULL),
                Brick(width=BrickWidth.QUARTER),
            ],
        ]
        self.assertEqual(_check_wildverband(grid, bricks, max_steps=2), 1)
        self.assertEqual(_check_wildverband(grid, bricks, max_steps=3), 0)

        grid = [
            [Brick(width=BrickWidth.FULL), Brick(width=BrickWidth.FULL)],
            [
                Brick(width=BrickWidth.QUARTER),
                Brick(width=BrickWidth.FULL),
                Brick(width=BrickWidth.QUARTER),
                Brick(width=BrickWidth.HALF),
            ],
            [Brick(width=BrickWidth.FULL), Brick(width=BrickWidth.FULL)],
            [
                Brick(width=BrickWidth.HALF),
                Brick(width=BrickWidth.FULL),
                Brick(width=BrickWidth.HALF),
            ],
        ]
        bricks = [Brick(width=BrickWidth.FULL), Brick(width=BrickWidth.FULL)]
        self.assertEqual(_check_wildverband(grid, bricks, max_steps=4), 0)


class TestBondInitialization(TestCase):
    def test_initialize_stretcher_bond(self):
        # Test basic stretcher bond pattern
        width, height = 8, 3  # 8 half-bricks wide, 3 rows high
        grid = initialize_stretcher_bond(width, height)

        self.assertEqual(len(grid), height)
        self.assertEqual(len(grid[0]), 2)  # First row should have 2 full bricks
        self.assertEqual(len(grid[1]), 3)  # Second row should start with half brick

        # Check first row pattern (even)
        self.assertEqual(grid[0][0].width, BrickWidth.FULL)
        self.assertEqual(grid[0][1].width, BrickWidth.FULL)

        # Check second row pattern (odd)
        self.assertEqual(grid[1][0].width, BrickWidth.HALF)
        self.assertEqual(grid[1][1].width, BrickWidth.FULL)
        self.assertEqual(grid[1][2].width, BrickWidth.HALF)

    def test_initialize_flemish_bond(self):
        # Test basic flemish bond pattern
        width, height = 10, 3  # 10 half-bricks wide, 3 rows high
        grid = initialize_flemish_bond(width, height)

        self.assertEqual(len(grid), height)

        # Check first row pattern (even)
        first_row = grid[0]
        self.assertEqual(first_row[0].width, BrickWidth.FULL)
        self.assertEqual(first_row[1].width, BrickWidth.HALF)
        self.assertEqual(first_row[2].width, BrickWidth.FULL)

        # Check second row pattern (odd)
        second_row = grid[1]
        self.assertEqual(second_row[0].width, BrickWidth.QUARTER)
        self.assertEqual(second_row[1].width, BrickWidth.HALF)
        self.assertEqual(second_row[2].width, BrickWidth.FULL)

    def test_initialize_english_bond(self):
        # Test basic english bond pattern
        width, height = 8, 3  # 8 half-bricks wide, 3 rows high
        grid = initialize_english_bond(width, height)

        self.assertEqual(len(grid), height)

        # Check first row (even) - should be all full bricks
        first_row = grid[0]
        self.assertTrue(all(brick.width == BrickWidth.FULL for brick in first_row))

        # Check second row (odd) - should start with quarter and then half bricks
        second_row = grid[1]
        self.assertEqual(second_row[0].width, BrickWidth.QUARTER)
        self.assertEqual(second_row[1].width, BrickWidth.HALF)
        self.assertEqual(second_row[2].width, BrickWidth.HALF)

    def test_initialize_wild_bond(self):
        # Test basic wild bond pattern
        width, height = 12, 4  # 12 half-bricks wide, 4 rows high
        grid = initialize_wild_bond(width, height)

        self.assertEqual(len(grid), height)

        # Check first row starts with full brick
        self.assertEqual(grid[0][0].width, BrickWidth.FULL)

        # Check second row starts with quarter brick
        self.assertEqual(grid[1][0].width, BrickWidth.QUARTER)

        # Verify no invalid patterns exist
        for i in range(1, len(grid)):
            self.assertEqual(_check_wildverband(grid[:i], grid[i]), 0)

        # Test with small width
        narrow_grid = initialize_wild_bond(6, 3)
        self.assertEqual(len(narrow_grid), 3)
