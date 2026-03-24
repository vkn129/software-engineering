"""
Day 30: Monotonic Stack — Reference Implementations

Why monotonic stacks matter:
They convert O(n^2) "find next greater/smaller" problems into O(n)
by ensuring each element is pushed and popped at most once.
"""


def next_greater_element(arr):
    """
    For each element, find the first element to its right that is strictly greater.
    Returns -1 if no such element exists.

    Strategy: traverse left-to-right with a stack of indices.
    The stack holds indices whose NGE we haven't found yet.
    We maintain a *decreasing* stack (bottom-to-top): when arr[i] is greater
    than the top, the top has found its NGE.

    Why indices? So we can record the answer at the correct position AND
    compute distances if needed.
    """
    n = len(arr)
    result = [-1] * n
    stack = []  # stores indices; arr[stack[-1]] is decreasing from bottom to top

    for i in range(n):
        # Pop everything that arr[i] is greater than — arr[i] is their NGE
        while stack and arr[i] > arr[stack[-1]]:
            idx = stack.pop()
            result[idx] = arr[i]
        stack.append(i)

    # Anything left in the stack has no NGE — already -1 by default
    return result


def next_smaller_element(arr):
    """
    For each element, find the first element to its right that is strictly smaller.
    Returns -1 if no such element exists.

    Mirror of NGE: maintain an *increasing* stack (bottom-to-top).
    Pop when arr[i] < top, because the top has found its next smaller element.
    """
    n = len(arr)
    result = [-1] * n
    stack = []

    for i in range(n):
        while stack and arr[i] < arr[stack[-1]]:
            idx = stack.pop()
            result[idx] = arr[i]
        stack.append(i)

    return result


def largest_rectangle_histogram(heights):
    """
    Find the largest rectangular area in a histogram.

    Key insight: for each bar, the maximum rectangle using that bar as the
    shortest bar extends from its "previous smaller element" to its
    "next smaller element." The width is (right_boundary - left_boundary - 1).

    We use a single pass with an increasing stack. When we pop a bar because
    we found something shorter, we can compute that bar's rectangle:
    - The popped bar is the height
    - The current index is the right boundary (exclusive)
    - The new stack top is the left boundary (exclusive)

    Why append -1 sentinel? It forces all remaining bars to be popped at the end,
    and acts as a left boundary for bars that extend to index 0.
    """
    stack = []  # increasing stack of indices
    max_area = 0
    # Append 0-height sentinel to flush everything at the end
    heights = list(heights) + [0]

    for i, h in enumerate(heights):
        # Pop bars taller than current — they can't extend further right
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            # Width: from current position back to previous stack top
            # If stack is empty, the bar extended all the way to index 0
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)

    return max_area


def daily_temperatures(temps):
    """
    Given daily temperatures, return how many days you must wait for a warmer day.
    Returns 0 if no warmer day exists.

    This is literally "next greater element" but we return the *distance* instead
    of the value. That's why we store indices in the stack.
    """
    n = len(temps)
    result = [0] * n
    stack = []  # decreasing stack of indices (by temperature)

    for i in range(n):
        while stack and temps[i] > temps[stack[-1]]:
            idx = stack.pop()
            result[idx] = i - idx  # distance in days
        stack.append(i)

    return result


def stock_span(prices):
    """
    For each day, return the number of consecutive days (including today)
    where the price was <= today's price.

    This is "distance to previous greater element." If no previous greater
    element exists, the span extends to day 0.

    We traverse left-to-right with a decreasing stack.
    When prices[i] >= prices[stack[-1]], we pop (those days are "covered" by today).
    The span is i - stack[-1] if stack is non-empty, else i + 1 (extends to start).

    Why >=? Because the span includes days with equal price.
    """
    n = len(prices)
    result = [0] * n
    stack = []  # strictly decreasing stack of indices (by price)

    for i in range(n):
        # Pop days with price <= today's price
        while stack and prices[i] >= prices[stack[-1]]:
            stack.pop()
        # Span = distance to previous day with strictly greater price
        result[i] = i - stack[-1] if stack else i + 1
        stack.append(i)

    return result


if __name__ == "__main__":
    print("=== Monotonic Stack Demos ===\n")

    # Next Greater Element
    arr = [4, 5, 2, 10, 8]
    print(f"Array:               {arr}")
    print(f"Next Greater Element: {next_greater_element(arr)}")
    # Expected: [5, 10, 10, -1, -1]

    # Next Smaller Element
    print(f"Next Smaller Element: {next_smaller_element(arr)}")
    # Expected: [2, 2, -1, 8, -1]

    print()

    # Largest Rectangle in Histogram
    heights = [2, 1, 5, 6, 2, 3]
    print(f"Histogram heights:    {heights}")
    print(f"Largest rectangle:    {largest_rectangle_histogram(heights)}")
    # Expected: 10 (bars at index 2,3 with height 5, width 2)

    print()

    # Daily Temperatures
    temps = [73, 74, 75, 71, 69, 72, 76, 73]
    print(f"Temperatures:         {temps}")
    print(f"Days until warmer:    {daily_temperatures(temps)}")
    # Expected: [1, 1, 4, 2, 1, 1, 0, 0]

    print()

    # Stock Span
    prices = [100, 80, 60, 70, 60, 75, 85]
    print(f"Stock prices:         {prices}")
    print(f"Stock span:           {stock_span(prices)}")
    # Expected: [1, 1, 1, 2, 1, 4, 6]
