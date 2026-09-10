"""Immutable ARC grids and the original project's symbolic transformations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator

Grid = tuple[tuple[int, ...], ...]
MAX_GRID_SIZE = 30


@dataclass(frozen=True)
class Action:
    """A named transformation and its numeric arguments."""

    name: str
    args: tuple[int | float, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "args", tuple(self.args))

    def __str__(self) -> str:
        if not self.args:
            return self.name
        return f"{self.name}({','.join(str(arg) for arg in self.args)})"


def make_grid(data: Iterable[Iterable[int]]) -> Grid:
    """Validate a rectangular, nonempty ARC grid and make it immutable.

    ARC grids contain integer colors 0 through 9 and have at most 30 rows
    and columns. Booleans are rejected rather than treated as integer colors.
    """
    try:
        grid = tuple(tuple(row) for row in data)
    except TypeError as exc:
        raise ValueError("A grid must contain rows of integer colors.") from exc
    if not 1 <= len(grid) <= MAX_GRID_SIZE:
        raise ValueError("A grid must have 1 to 30 rows.")
    width = len(grid[0])
    if not 1 <= width <= MAX_GRID_SIZE:
        raise ValueError("A grid must have 1 to 30 columns.")
    if any(len(row) != width for row in grid):
        raise ValueError("A grid must be rectangular.")
    if any(type(color) is not int or not 0 <= color <= 9
           for row in grid for color in row):
        raise ValueError("Grid colors must be integers from 0 through 9.")
    return grid


def _integer_args(action: Action, count: int) -> tuple[int, ...]:
    if len(action.args) != count or any(type(arg) is not int for arg in action.args):
        raise ValueError(f"{action.name} requires {count} integer arguments.")
    return action.args  # type: ignore[return-value]


def apply_action(grid: Grid, action: Action) -> Grid:
    """Apply one transformation, rejecting empty or oversized results.

    Crop coordinates are inclusive and clipped to the input bounds, matching
    the notebook. Scaling down samples every second cell; it is not averaging.
    """
    grid = make_grid(grid)
    name = action.name
    height, width = len(grid), len(grid[0])
    simple = {"tophalf", "hmirror", "vmirror", "lshift", "compress",
              "alternate_pattern", "pattern_repeat"}
    if name in simple and action.args:
        raise ValueError(f"{name} does not accept arguments.")

    if name == "tophalf":
        result = grid[:height // 2]
    elif name == "hmirror":
        result = grid[::-1]
    elif name == "vmirror":
        result = tuple(row[::-1] for row in grid)
    elif name == "lshift":
        result = tuple(tuple(color for color in row if color != 0)
                       + (0,) * row.count(0) for row in grid)
    elif name == "compress":
        rows = [i for i, row in enumerate(grid) if len(set(row)) != 1]
        columns = [j for j, column in enumerate(zip(*grid)) if len(set(column)) != 1]
        result = tuple(tuple(grid[i][j] for j in columns) for i in rows)
    elif name == "alternate_pattern":
        result = tuple(
            tuple(row[j + 1] if j % 2 == 0 and j + 1 < width
                  else row[j - 1] if j % 2 == 1 else row[j]
                  for j in range(width)) if (i // 2) % 2 else row
            for i, row in enumerate(grid)
        )
    elif name == "pattern_repeat":
        if height * 3 > MAX_GRID_SIZE or width * 3 > MAX_GRID_SIZE:
            raise ValueError("Repeated grid would exceed 30 rows or columns.")
        result = tuple(row * 3 for row in grid) * 3
    elif name == "mapcolor":
        source, target = _integer_args(action, 2)
        if not 0 <= source <= 9 or not 0 <= target <= 9:
            raise ValueError("Color arguments must be from 0 through 9.")
        result = tuple(tuple(target if color == source else color for color in row)
                       for row in grid)
    elif name == "flood_fill":
        x, y, target = _integer_args(action, 3)
        if not 0 <= target <= 9:
            raise ValueError("Fill color must be from 0 through 9.")
        if not 0 <= x < height or not 0 <= y < width or grid[x][y] == target:
            return grid
        source = grid[x][y]
        mutable = [list(row) for row in grid]
        mutable[x][y] = target
        stack = [(x, y)]
        while stack:
            row, column = stack.pop()
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = row + dx, column + dy
                if (0 <= nx < height and 0 <= ny < width
                        and mutable[nx][ny] == source):
                    mutable[nx][ny] = target
                    stack.append((nx, ny))
        result = tuple(tuple(row) for row in mutable)
    elif name == "crop":
        x1, y1, x2, y2 = _integer_args(action, 4)
        x1, x2 = max(0, x1), min(height - 1, x2)
        y1, y2 = max(0, y1), min(width - 1, y2)
        result = tuple(row[y1:y2 + 1] for row in grid[x1:x2 + 1])
    elif name == "scale":
        if (len(action.args) != 1 or type(action.args[0]) not in (int, float)
                or action.args[0] not in (0.5, 2)):
            raise ValueError("Scale requires one factor: 0.5 or 2.")
        if action.args[0] == 2:
            if height * 2 > MAX_GRID_SIZE or width * 2 > MAX_GRID_SIZE:
                raise ValueError("Scaled grid would exceed 30 rows or columns.")
            result = tuple(tuple(color for color in row for _ in range(2))
                           for row in grid for _ in range(2))
        else:
            result = tuple(tuple(grid[i * 2][j * 2] for j in range(width // 2))
                           for i in range(height // 2))
    elif name == "rotate":
        degrees, = _integer_args(action, 1)
        if degrees == 90:
            result = tuple(zip(*grid[::-1]))
        elif degrees == 180:
            result = tuple(row[::-1] for row in grid[::-1])
        elif degrees == 270:
            result = tuple(zip(*grid))[::-1]
        else:
            raise ValueError("Rotation must be 90, 180, or 270 degrees.")
    else:
        raise ValueError(f"Unknown action: {name}")
    return make_grid(result)


def legal_actions(grid: Grid) -> Iterator[Action]:
    """Yield deterministic candidates from the notebook's transformation set.

    Some content-dependent candidates (for example, compression of a uniform
    grid) can produce invalid grids and are rejected by ``apply_action``.
    Exhaustive fill and crop candidates retain the original 10-by-10 bound.
    """
    grid = make_grid(grid)
    height, width = len(grid), len(grid[0])
    if height >= 2:
        yield Action("tophalf")
    for name in ("hmirror", "vmirror", "lshift", "compress", "alternate_pattern"):
        yield Action(name)
    for source in sorted({color for row in grid for color in row}):
        for target in range(10):
            if source != target:
                yield Action("mapcolor", (source, target))
    if height <= 10 and width <= 10:
        yield Action("pattern_repeat")
        for x in range(height):
            for y in range(width):
                for target in range(10):
                    yield Action("flood_fill", (x, y, target))
        for x1 in range(height):
            for y1 in range(width):
                for x2 in range(x1, height):
                    for y2 in range(y1, width):
                        yield Action("crop", (x1, y1, x2, y2))
    if height >= 2 and width >= 2:
        yield Action("scale", (0.5,))
    if height <= 15 and width <= 15:
        yield Action("scale", (2,))
    for degrees in (90, 180, 270):
        yield Action("rotate", (degrees,))


def execute_actions(input_grid: Iterable[Iterable[int]], actions: Iterable[Action]) -> Grid:
    """Replay a learned transformation program without mutating the input."""
    grid = make_grid(input_grid)
    for action in actions:
        grid = apply_action(grid, action)
    return grid
