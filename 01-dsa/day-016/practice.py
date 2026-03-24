"""
Day 16 Practice: Dynamic Arrays
================================
Implement these exercises to solidify your understanding of dynamic arrays.
Run this file to test your solutions.
"""


# =============================================================================
# Exercise 1: Implement a Dynamic Array from scratch
# =============================================================================
# Build a dynamic array that doubles capacity when full and halves when 1/4 full.
# Track the number of element copies that happen during resizes.

class DynamicArray:
    """
    A resizable array that manages its own memory.

    Growth strategy: double when full
    Shrink strategy: halve when 1/4 full (avoids thrashing at 1/2)

    TODO: Implement all methods below
    """

    def __init__(self, initial_capacity=4):
        self._data = [None] * initial_capacity
        self._size = 0
        self._capacity = initial_capacity
        self.total_copies = 0  # Track element copies during resizes

    def append(self, value):
        """Add element to end. Resize if needed."""
        # TODO: Implement
        # Hint: if size == capacity, call _resize(2 * capacity)
        pass

    def pop(self):
        """Remove and return last element. Shrink if needed."""
        # TODO: Implement
        # Hint: if size <= capacity // 4 and capacity > 4, call _resize(capacity // 2)
        pass

    def insert(self, index, value):
        """Insert value at index, shifting elements right."""
        # TODO: Implement — this is O(n), why?
        pass

    def delete(self, index):
        """Delete element at index, shifting elements left."""
        # TODO: Implement
        pass

    def _resize(self, new_capacity):
        """Create new backing array and copy elements."""
        # TODO: Implement
        # Don't forget to update self.total_copies
        pass

    def __getitem__(self, index):
        if index < 0 or index >= self._size:
            raise IndexError(f"Index {index} out of range [0, {self._size})")
        return self._data[index]

    def __len__(self):
        return self._size

    def __repr__(self):
        elements = [str(self._data[i]) for i in range(self._size)]
        return f"DynamicArray([{', '.join(elements)}], size={self._size}, cap={self._capacity})"


# =============================================================================
# Exercise 2: Amortized Cost Tracker
# =============================================================================
# Append N elements and track the cost (number of copies) at each step.
# Verify that total copies ≤ 3N (amortized O(1) per append).

def verify_amortized_cost(n):
    """
    Append n elements, return (total_copies, theoretical_bound).

    TODO: Implement
    - Create a DynamicArray
    - Append n elements
    - Return (arr.total_copies, 3 * n)
    - The total copies should always be less than 3n
    """
    pass


# =============================================================================
# Exercise 3: Growth Strategy Comparison
# =============================================================================
# Compare doubling (2x) vs 1.5x vs additive (+10) growth strategies.
# Count total copies for N=1000 appends with each strategy.

def compare_growth_strategies(n=1000):
    """
    Compare total element copies for three growth strategies.

    TODO: Implement three simulations
    Returns dict: {'doubling': copies, 'factor_1_5': copies, 'additive_10': copies}

    For each strategy:
    - Start with capacity 4
    - Append n elements
    - When full, resize to: capacity * 2, int(capacity * 1.5), capacity + 10
    - Count total element copies across all resizes
    """
    pass


# =============================================================================
# Exercise 4: Ring Buffer (Circular Dynamic Array)
# =============================================================================
# A ring buffer allows O(1) push/pop from BOTH ends by using modular indexing.
# This is how Python's collections.deque works internally.

class RingBuffer:
    """
    Circular buffer with O(1) amortized push/pop at both ends.

    TODO: Implement using a fixed-size array with head/tail pointers.
    Resize (double) when full.
    """

    def __init__(self, capacity=4):
        self._data = [None] * capacity
        self._head = 0  # Index of first element
        self._size = 0
        self._capacity = capacity

    def push_back(self, value):
        """Add to end — O(1) amortized."""
        # TODO: Implement
        # Hint: tail index = (head + size) % capacity
        pass

    def push_front(self, value):
        """Add to front — O(1) amortized."""
        # TODO: Implement
        # Hint: new head = (head - 1) % capacity
        pass

    def pop_back(self):
        """Remove from end — O(1)."""
        # TODO: Implement
        pass

    def pop_front(self):
        """Remove from front — O(1)."""
        # TODO: Implement
        pass

    def __getitem__(self, index):
        if index < 0 or index >= self._size:
            raise IndexError
        return self._data[(self._head + index) % self._capacity]

    def __len__(self):
        return self._size


# =============================================================================
# SOLUTIONS (scroll down only after attempting)
# =============================================================================


def _solution_dynamic_array():
    """Reference solution for Exercise 1."""

    class SolvedDynamicArray:
        def __init__(self, initial_capacity=4):
            self._data = [None] * initial_capacity
            self._size = 0
            self._capacity = initial_capacity
            self.total_copies = 0

        def append(self, value):
            if self._size == self._capacity:
                self._resize(2 * self._capacity)
            self._data[self._size] = value
            self._size += 1

        def pop(self):
            if self._size == 0:
                raise IndexError("Pop from empty array")
            self._size -= 1
            val = self._data[self._size]
            self._data[self._size] = None
            if self._size <= self._capacity // 4 and self._capacity > 4:
                self._resize(self._capacity // 2)
            return val

        def insert(self, index, value):
            if index < 0 or index > self._size:
                raise IndexError
            if self._size == self._capacity:
                self._resize(2 * self._capacity)
            # Shift right — this is why insert is O(n)
            for i in range(self._size, index, -1):
                self._data[i] = self._data[i - 1]
            self._data[index] = value
            self._size += 1

        def delete(self, index):
            if index < 0 or index >= self._size:
                raise IndexError
            for i in range(index, self._size - 1):
                self._data[i] = self._data[i + 1]
            self._size -= 1
            self._data[self._size] = None
            if self._size <= self._capacity // 4 and self._capacity > 4:
                self._resize(self._capacity // 2)

        def _resize(self, new_capacity):
            new_data = [None] * new_capacity
            for i in range(self._size):
                new_data[i] = self._data[i]
            self.total_copies += self._size
            self._data = new_data
            self._capacity = new_capacity

        def __getitem__(self, index):
            if index < 0 or index >= self._size:
                raise IndexError
            return self._data[index]

        def __len__(self):
            return self._size

    return SolvedDynamicArray


# =============================================================================
# Tests
# =============================================================================

def run_tests():
    print("=" * 60)
    print("Day 16 Practice Tests: Dynamic Arrays")
    print("=" * 60)

    # Use solution if student hasn't implemented yet
    Sol = _solution_dynamic_array()

    # Test 1: Basic append and access
    arr = Sol()
    for i in range(10):
        arr.append(i)
    assert len(arr) == 10
    assert arr[0] == 0 and arr[9] == 9
    print("✓ Test 1: Append and access work correctly")

    # Test 2: Pop and shrink
    arr = Sol()
    for i in range(20):
        arr.append(i)
    for _ in range(18):
        arr.pop()
    assert len(arr) == 2
    print("✓ Test 2: Pop with shrinking works")

    # Test 3: Insert shifts elements
    arr = Sol()
    for i in range(5):
        arr.append(i)
    arr.insert(2, 99)
    assert arr[2] == 99 and arr[3] == 2 and len(arr) == 6
    print("✓ Test 3: Insert shifts elements correctly")

    # Test 4: Delete shifts elements
    arr = Sol()
    for i in range(5):
        arr.append(i)
    arr.delete(2)
    assert arr[2] == 3 and len(arr) == 4
    print("✓ Test 4: Delete shifts elements correctly")

    # Test 5: Amortized cost
    arr = Sol()
    for i in range(1000):
        arr.append(i)
    assert arr.total_copies < 3 * 1000, f"Copies {arr.total_copies} exceed 3N={3000}"
    print(f"✓ Test 5: Amortized cost verified — {arr.total_copies} copies for 1000 appends (< 3000)")

    print("\nAll tests passed!")


if __name__ == "__main__":
    run_tests()
