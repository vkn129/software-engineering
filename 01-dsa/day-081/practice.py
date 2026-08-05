"""
Day 81 Practice: Topological Sort Problems

Five exercises covering dependency resolution, ordering constraints,
and cycle detection in directed graphs.
"""

from collections import defaultdict, deque
import heapq


# ---------------------------------------------------------------------------
# Exercise 1: Course Schedule II (LeetCode 210)
# ---------------------------------------------------------------------------
# Given numCourses and prerequisites list of [course, prereq] pairs,
# return a valid order to take all courses. Return [] if impossible.

def find_course_order(num_courses, prerequisites):
    """
    Find a valid order to complete all courses given prerequisites.

    Args:
        num_courses: number of courses labeled 0 to num_courses-1
        prerequisites: list of [course, prerequisite] pairs

    Returns:
        List of courses in valid order, or [] if impossible (cycle exists).

    Example:
        find_course_order(4, [[1,0],[2,0],[3,1],[3,2]]) -> [0,1,2,3] or [0,2,1,3]
    """
    # Build adjacency list and in-degree array
    graph = defaultdict(list)
    in_degree = [0] * num_courses

    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    # Kahn's algorithm
    queue = deque()
    for i in range(num_courses):
        if in_degree[i] == 0:
            queue.append(i)

    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) == num_courses:
        return order
    return []


# ---------------------------------------------------------------------------
# Exercise 2: Alien Dictionary (LeetCode 269)
# ---------------------------------------------------------------------------
# Given a sorted list of words in an alien language, derive the character
# ordering. Return "" if no valid ordering exists.

def alien_order(words):
    """
    Determine the character ordering of an alien language from sorted words.

    By comparing adjacent words, we can infer ordering between characters.
    The first differing character between adjacent words gives us an edge.

    Args:
        words: list of words sorted in alien dictionary order

    Returns:
        String of characters in alien alphabetical order, or "" if invalid.

    Example:
        alien_order(["wrt","wrf","er","ett","rftt"]) -> "wertf"
    """
    # Collect all unique characters
    chars = set()
    for word in words:
        for c in word:
            chars.add(c)

    graph = defaultdict(set)
    in_degree = {c: 0 for c in chars}

    # Compare adjacent words to derive ordering
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i + 1]
        # Edge case: if w1 is longer than w2 and w2 is a prefix of w1, invalid
        if len(w1) > len(w2) and w1[:len(w2)] == w2:
            return ""
        for c1, c2 in zip(w1, w2):
            if c1 != c2:
                if c2 not in graph[c1]:
                    graph[c1].add(c2)
                    in_degree[c2] += 1
                break  # Only first difference matters

    # Kahn's algorithm
    queue = deque()
    for c in chars:
        if in_degree[c] == 0:
            queue.append(c)

    result = []
    while queue:
        c = queue.popleft()
        result.append(c)
        for neighbor in graph[c]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) == len(chars):
        return "".join(result)
    return ""  # Cycle detected


# ---------------------------------------------------------------------------
# Exercise 3: Parallel Job Scheduling
# ---------------------------------------------------------------------------
# Given jobs with dependencies and durations, find the minimum time to
# complete all jobs (critical path).

def min_completion_time(num_jobs, dependencies, durations):
    """
    Find minimum time to complete all jobs with unlimited parallelism.

    This is the critical path problem: the longest path in the DAG
    determines the minimum completion time.

    Args:
        num_jobs: number of jobs (0-indexed)
        dependencies: list of [job, prerequisite] pairs
        durations: list of duration for each job

    Returns:
        Minimum time to complete all jobs.

    Example:
        min_completion_time(4, [[1,0],[2,0],[3,1],[3,2]], [3,2,4,1])
        -> 8  (path 0->2->3: 3+4+1=8)
    """
    graph = defaultdict(list)
    in_degree = [0] * num_jobs

    for job, prereq in dependencies:
        graph[prereq].append(job)
        in_degree[job] += 1

    # earliest_start[i] = earliest time job i can start
    earliest_start = [0] * num_jobs

    queue = deque()
    for i in range(num_jobs):
        if in_degree[i] == 0:
            queue.append(i)

    while queue:
        job = queue.popleft()
        finish_time = earliest_start[job] + durations[job]
        for next_job in graph[job]:
            earliest_start[next_job] = max(earliest_start[next_job], finish_time)
            in_degree[next_job] -= 1
            if in_degree[next_job] == 0:
                queue.append(next_job)

    # The answer is the maximum finish time across all jobs
    return max(earliest_start[i] + durations[i] for i in range(num_jobs))


# ---------------------------------------------------------------------------
# Exercise 4: Longest Path in DAG
# ---------------------------------------------------------------------------
# Find the longest path (by number of edges) in a DAG.

def longest_path_in_dag(num_nodes, edges):
    """
    Find the length of the longest path (by edge count) in a DAG.

    Uses topological sort + dynamic programming.
    dist[v] = max distance (edges) from any source to v.

    Args:
        num_nodes: number of nodes (0-indexed)
        edges: list of [u, v] directed edges

    Returns:
        Length of the longest path (number of edges).

    Example:
        longest_path_in_dag(6, [[0,1],[0,2],[1,3],[2,3],[3,4],[2,5]])
        -> 3  (path 0->2->3->4 or 0->1->3->4)
    """
    graph = defaultdict(list)
    in_degree = [0] * num_nodes

    for u, v in edges:
        graph[u].append(v)
        in_degree[v] += 1

    # Topological sort via Kahn's
    queue = deque()
    for i in range(num_nodes):
        if in_degree[i] == 0:
            queue.append(i)

    topo_order = []
    while queue:
        node = queue.popleft()
        topo_order.append(node)
        for v in graph[node]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    # DP: longest path ending at each node
    dist = [0] * num_nodes
    for u in topo_order:
        for v in graph[u]:
            dist[v] = max(dist[v], dist[u] + 1)

    return max(dist) if dist else 0


# ---------------------------------------------------------------------------
# Exercise 5: Task Scheduling with Deadlines
# ---------------------------------------------------------------------------
# Given tasks with durations, dependencies, and deadlines, determine which
# tasks (if any) will miss their deadline.

def find_late_tasks(num_tasks, dependencies, durations, deadlines):
    """
    Find tasks that will miss their deadline given dependencies.

    Assumes tasks start as early as possible (once all prereqs are done)
    and unlimited parallelism.

    Args:
        num_tasks: number of tasks (0-indexed)
        dependencies: list of [task, prerequisite] pairs
        durations: list of duration for each task
        deadlines: list of deadline for each task

    Returns:
        List of (task_id, finish_time, deadline) for tasks that miss deadline.

    Example:
        find_late_tasks(3, [[1,0],[2,1]], [5,3,2], [5,9,8])
        -> [(2, 10, 8)]  # task 2 finishes at 10, deadline is 8
    """
    graph = defaultdict(list)
    in_degree = [0] * num_tasks

    for task, prereq in dependencies:
        graph[prereq].append(task)
        in_degree[task] += 1

    earliest_start = [0] * num_tasks

    queue = deque()
    for i in range(num_tasks):
        if in_degree[i] == 0:
            queue.append(i)

    while queue:
        task = queue.popleft()
        finish = earliest_start[task] + durations[task]
        for next_task in graph[task]:
            earliest_start[next_task] = max(earliest_start[next_task], finish)
            in_degree[next_task] -= 1
            if in_degree[next_task] == 0:
                queue.append(next_task)

    late = []
    for i in range(num_tasks):
        finish_time = earliest_start[i] + durations[i]
        if finish_time > deadlines[i]:
            late.append((i, finish_time, deadlines[i]))

    return late


# ===========================================================================
# Tests
# ===========================================================================

def test_course_schedule():
    # Basic case
    result = find_course_order(4, [[1, 0], [2, 0], [3, 1], [3, 2]])
    assert len(result) == 4
    assert result.index(0) < result.index(1)
    assert result.index(0) < result.index(2)
    assert result.index(1) < result.index(3)
    assert result.index(2) < result.index(3)

    # Impossible (cycle)
    assert find_course_order(2, [[0, 1], [1, 0]]) == []

    # No prerequisites
    result = find_course_order(3, [])
    assert len(result) == 3
    assert set(result) == {0, 1, 2}

    # Single course
    assert find_course_order(1, []) == [0]

    # Linear chain
    result = find_course_order(4, [[1, 0], [2, 1], [3, 2]])
    assert result == [0, 1, 2, 3]

    print("  [PASS] Course Schedule II")


def test_alien_dictionary():
    assert alien_order(["wrt", "wrf", "er", "ett", "rftt"]) == "wertf"

    # Two words, single difference
    result = alien_order(["ab", "ba"])
    assert result.index("a") < result.index("b")

    # Invalid: longer word before its prefix
    assert alien_order(["abc", "ab"]) == ""

    # Single word
    result = alien_order(["z"])
    assert result == "z"

    print("  [PASS] Alien Dictionary")


def test_parallel_scheduling():
    # Linear chain: 3->2->4->1 = 10
    assert min_completion_time(4, [[1, 0], [2, 1], [3, 2]], [3, 2, 4, 1]) == 10

    # Diamond: two parallel paths
    # Path 0->1->3: 3+2+1=6, Path 0->2->3: 3+4+1=8. Answer: 8
    assert min_completion_time(4, [[1, 0], [2, 0], [3, 1], [3, 2]], [3, 2, 4, 1]) == 8

    # No dependencies: max single duration
    assert min_completion_time(3, [], [5, 3, 7]) == 7

    # Single job
    assert min_completion_time(1, [], [42]) == 42

    print("  [PASS] Parallel Job Scheduling")


def test_longest_path():
    assert longest_path_in_dag(6, [[0, 1], [0, 2], [1, 3], [2, 3], [3, 4], [2, 5]]) == 3

    # Linear chain of 5 nodes
    assert longest_path_in_dag(5, [[0, 1], [1, 2], [2, 3], [3, 4]]) == 4

    # No edges
    assert longest_path_in_dag(3, []) == 0

    # Single edge
    assert longest_path_in_dag(2, [[0, 1]]) == 1

    # Wide graph (all edges from 0)
    assert longest_path_in_dag(4, [[0, 1], [0, 2], [0, 3]]) == 1

    print("  [PASS] Longest Path in DAG")


def test_task_deadlines():
    # Task 2 finishes at time 10 but deadline is 8
    late = find_late_tasks(3, [[1, 0], [2, 1]], [5, 3, 2], [5, 9, 8])
    assert len(late) == 1
    assert late[0] == (2, 10, 8)

    # All on time
    late = find_late_tasks(3, [[1, 0], [2, 1]], [5, 3, 2], [5, 10, 20])
    assert len(late) == 0

    # No dependencies, some late
    late = find_late_tasks(3, [], [5, 3, 7], [4, 3, 10])
    assert len(late) == 1
    assert late[0][0] == 0  # Task 0 finishes at 5, deadline 4

    # Multiple late tasks
    late = find_late_tasks(3, [[1, 0], [2, 0]], [10, 5, 5], [10, 10, 10])
    assert len(late) == 2  # Both task 1 and 2 finish at 15, deadline 10

    print("  [PASS] Task Scheduling with Deadlines")


if __name__ == "__main__":
    print("Running Day 81 practice tests...\n")
    test_course_schedule()
    test_alien_dictionary()
    test_parallel_scheduling()
    test_longest_path()
    test_task_deadlines()
    print("\nAll tests passed!")
