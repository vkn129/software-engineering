"""
Day 79 Practice: Breadth-First Search (BFS)

Exercises: word ladder, rotten oranges, bipartite verification,
multi-source BFS, knight's minimum moves.
"""

from collections import deque, defaultdict
from typing import List, Optional, Set, Dict, Tuple


# ============================================================
# Exercise 1: Word Ladder
# ============================================================
# Given a start word, end word, and dictionary, find the shortest
# transformation sequence where each step changes exactly one letter.
#
# Example: "hit" -> "hot" -> "dot" -> "dog" -> "cog"
#
# WHY BFS: Each transformation is one "edge". BFS finds the shortest
# sequence of transformations.

def word_ladder(begin_word: str, end_word: str, word_list: List[str]) -> int:
    """
    Return the length of shortest transformation sequence (number of words
    including begin_word and end_word), or 0 if no sequence exists.

    Time: O(M^2 * N) where M = word length, N = number of words
    Space: O(M^2 * N) for the pattern map
    """
    word_set = set(word_list)
    if end_word not in word_set:
        return 0

    # Build adjacency via wildcard patterns: "hot" -> ["*ot", "h*t", "ho*"]
    pattern_map = defaultdict(list)
    for word in word_set:
        for i in range(len(word)):
            pattern = word[:i] + "*" + word[i + 1:]
            pattern_map[pattern].append(word)

    visited = {begin_word}
    queue = deque([(begin_word, 1)])

    while queue:
        word, length = queue.popleft()
        for i in range(len(word)):
            pattern = word[:i] + "*" + word[i + 1:]
            for neighbor in pattern_map[pattern]:
                if neighbor == end_word:
                    return length + 1
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, length + 1))

    return 0


# ============================================================
# Exercise 2: Rotten Oranges
# ============================================================
# In a grid, 0 = empty, 1 = fresh orange, 2 = rotten orange.
# Each minute, rotten oranges rot adjacent fresh oranges (4-directional).
# Return minimum minutes until no fresh oranges remain, or -1 if impossible.
#
# WHY multi-source BFS: All rotten oranges spread simultaneously.
# The answer is the maximum BFS distance from any rotten source.

def rotten_oranges(grid: List[List[int]]) -> int:
    """
    Return minimum minutes to rot all oranges, or -1 if impossible.

    Time: O(rows * cols)
    Space: O(rows * cols)
    """
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh_count = 0

    # Find all initial rotten oranges and count fresh ones
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c, 0))
            elif grid[r][c] == 1:
                fresh_count += 1

    if fresh_count == 0:
        return 0

    max_time = 0
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while queue:
        r, c, time = queue.popleft()
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                grid[nr][nc] = 2
                fresh_count -= 1
                max_time = time + 1
                queue.append((nr, nc, time + 1))

    return max_time if fresh_count == 0 else -1


# ============================================================
# Exercise 3: Bipartite Verification
# ============================================================
# Determine if a graph can be 2-colored such that no adjacent
# vertices share a color. Return the two partitions if bipartite.
#
# WHY BFS: BFS assigns levels; bipartite iff even-level and
# odd-level vertices form valid 2-coloring.

def bipartite_partition(
    graph: Dict[int, List[int]], vertices: Set[int]
) -> Optional[Tuple[Set[int], Set[int]]]:
    """
    If bipartite, return (set_a, set_b) the two partitions.
    If not bipartite, return None.

    Time: O(V + E)
    Space: O(V)
    """
    color = {}
    set_a, set_b = set(), set()

    for start in vertices:
        if start in color:
            continue

        color[start] = 0
        set_a.add(start)
        queue = deque([start])

        while queue:
            v = queue.popleft()
            for neighbor in graph.get(v, []):
                if neighbor not in color:
                    color[neighbor] = 1 - color[v]
                    if color[neighbor] == 0:
                        set_a.add(neighbor)
                    else:
                        set_b.add(neighbor)
                    queue.append(neighbor)
                elif color[neighbor] == color[v]:
                    return None

    return (set_a, set_b)


# ============================================================
# Exercise 4: Multi-Source BFS - Nearest Exit in Maze
# ============================================================
# Given a maze grid and an entrance, find the shortest path to any
# exit (a cell on the border that is not a wall). The entrance
# does not count as an exit.

def nearest_exit(
    maze: List[List[str]], entrance: Tuple[int, int]
) -> int:
    """
    Return minimum steps to reach any exit, or -1 if impossible.

    maze[r][c] = '.' for open, '+' for wall.
    An exit is any '.' on the grid border other than the entrance.

    Time: O(rows * cols)
    Space: O(rows * cols)
    """
    rows, cols = len(maze), len(maze[0])
    er, ec = entrance

    visited = set()
    visited.add((er, ec))
    queue = deque([(er, ec, 0)])
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while queue:
        r, c, steps = queue.popleft()

        # Check if this is an exit (on border and not the entrance)
        if (r, c) != (er, ec) and (r == 0 or r == rows - 1 or c == 0 or c == cols - 1):
            return steps

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and (nr, nc) not in visited and maze[nr][nc] == '.'):
                visited.add((nr, nc))
                queue.append((nr, nc, steps + 1))

    return -1


# ============================================================
# Exercise 5: Knight's Minimum Moves
# ============================================================
# On an infinite chess board, find the minimum number of moves
# for a knight to reach position (target_x, target_y) from (0, 0).
#
# Knight moves: 8 possible L-shaped moves.
# WHY BFS: each move is one step; BFS finds minimum moves.

def knight_minimum_moves(target_x: int, target_y: int) -> int:
    """
    Return minimum knight moves from (0,0) to (target_x, target_y).

    Uses BFS with symmetry optimization: only search in the first quadrant
    since the problem is symmetric.

    Time: O(max(|x|, |y|)^2) in practice
    Space: O(max(|x|, |y|)^2)
    """
    # Exploit symmetry: target in any quadrant has same distance
    tx, ty = abs(target_x), abs(target_y)

    if tx == 0 and ty == 0:
        return 0

    visited = set()
    visited.add((0, 0))
    queue = deque([(0, 0, 0)])

    moves = [
        (2, 1), (2, -1), (-2, 1), (-2, -1),
        (1, 2), (1, -2), (-1, 2), (-1, -2),
    ]

    while queue:
        x, y, steps = queue.popleft()

        for dx, dy in moves:
            nx, ny = x + dx, y + dy

            if nx == tx and ny == ty:
                return steps + 1

            # Prune: don't wander too far from target
            # Allow some slack beyond target for the knight to maneuver
            if (nx, ny) not in visited and -2 <= nx <= tx + 4 and -2 <= ny <= ty + 4:
                visited.add((nx, ny))
                queue.append((nx, ny, steps + 1))

    return -1  # Should not reach here for valid inputs


# ============================================================
# Tests
# ============================================================

def test_word_ladder():
    words = ["hot", "dot", "dog", "lot", "log", "cog"]
    assert word_ladder("hit", "cog", words) == 5  # hit->hot->dot->dog->cog

    assert word_ladder("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0  # no cog

    assert word_ladder("a", "c", ["a", "b", "c"]) == 2  # a->c
    print("  [PASS] Word ladder")


def test_rotten_oranges():
    grid1 = [[2, 1, 1], [1, 1, 0], [0, 1, 1]]
    assert rotten_oranges(grid1) == 4

    grid2 = [[2, 1, 1], [0, 1, 1], [1, 0, 1]]
    assert rotten_oranges(grid2) == -1  # bottom-left is unreachable

    grid3 = [[0, 2]]
    assert rotten_oranges(grid3) == 0  # no fresh oranges

    print("  [PASS] Rotten oranges")


def test_bipartite_partition():
    # Square graph is bipartite
    square = {0: [1, 3], 1: [0, 2], 2: [1, 3], 3: [0, 2]}
    result = bipartite_partition(square, {0, 1, 2, 3})
    assert result is not None
    a, b = result
    # Check no edge within same partition
    for v in a:
        for neighbor in square[v]:
            assert neighbor in b
    for v in b:
        for neighbor in square[v]:
            assert neighbor in a

    # Triangle is NOT bipartite
    triangle = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
    assert bipartite_partition(triangle, {0, 1, 2}) is None

    print("  [PASS] Bipartite partition")


def test_nearest_exit():
    maze1 = [
        ["+", "+", ".", "+"],
        [".", ".", ".", "+"],
        ["+", "+", "+", "."],
    ]
    assert nearest_exit(maze1, (1, 0)) == 2  # (1,0) -> (0,2) in 2 steps or similar

    maze2 = [
        ["+", "+", "+"],
        [".", ".", "."],
        ["+", "+", "+"],
    ]
    assert nearest_exit(maze2, (1, 1)) == 1  # left or right edge

    print("  [PASS] Nearest exit")


def test_knight_moves():
    assert knight_minimum_moves(0, 0) == 0
    assert knight_minimum_moves(1, 1) == 2  # (0,0)->(2,1)->(1,1) won't work directly
    # Actually (0,0) -> (2,-1) -> (1,1) = 2 moves
    assert knight_minimum_moves(2, 1) == 1
    assert knight_minimum_moves(5, 5) == 4

    print("  [PASS] Knight's minimum moves")


if __name__ == "__main__":
    print("Day 79 Practice Tests")
    print("-" * 40)
    test_word_ladder()
    test_rotten_oranges()
    test_bipartite_partition()
    test_nearest_exit()
    test_knight_moves()
    print("-" * 40)
    print("All tests passed!")
