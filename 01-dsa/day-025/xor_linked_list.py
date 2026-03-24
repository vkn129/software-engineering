"""
Day 25: XOR Linked List — Implementation

WHY: A standard doubly-linked list uses two pointers per node (prev, next).
An XOR linked list stores just one value: prev_addr XOR next_addr.
This halves pointer overhead while preserving bidirectional traversal.

HOW IT WORKS:
  Each node stores: npx = address(prev) ^ address(next)
  Given prev's address: next = npx ^ prev_addr  (prev cancels out)
  Given next's address: prev = npx ^ next_addr  (next cancels out)

  The key identity: A ^ B ^ A = B (XOR is its own inverse)

PYTHON LIMITATION:
  Python doesn't let you XOR raw object addresses and dereference the result.
  We simulate it: each node gets an integer ID, a dict maps IDs back to nodes.
  The XOR math is real — only the "address space" is simulated.
"""


class XORNode:
    """A node in an XOR linked list.

    npx stores prev_id XOR next_id instead of two separate pointers.
    This is the entire point — one field does the work of two.
    """

    _next_id = 1  # Class-level counter for assigning unique IDs

    def __init__(self, data):
        self.data = data
        self.npx = 0  # prev_id XOR next_id (both are 0 until linked)
        # Assign a unique integer ID to simulate a memory address.
        # Real XOR linked lists use actual pointer values here.
        self.node_id = XORNode._next_id
        XORNode._next_id += 1


class XORLinkedList:
    """Doubly-linked list using XOR pointer compression.

    Uses a registry dict to map integer IDs back to node objects.
    In C, you'd cast pointers to uintptr_t for XOR and back — no registry needed.
    """

    def __init__(self):
        self.head_id = 0  # 0 means NULL (no node)
        self.tail_id = 0
        self.registry = {}  # id -> XORNode (our simulated address space)
        self.size = 0

    def _get_node(self, node_id):
        """Look up a node by its ID. Returns None for ID 0 (NULL)."""
        if node_id == 0:
            return None
        return self.registry.get(node_id)

    def _register(self, node):
        """Add a node to the registry so we can find it by ID later."""
        self.registry[node.node_id] = node

    def _unregister(self, node):
        """Remove a node from the registry (frees it from our address space)."""
        del self.registry[node.node_id]

    def insert_front(self, data):
        """Insert a new node at the front of the list. O(1).

        WHY front insertion: Same as standard linked list — no traversal needed.
        We update the old head's npx to include the new node's address.
        """
        new_node = XORNode(data)
        self._register(new_node)

        if self.head_id == 0:
            # Empty list: new node is both head and tail
            # npx = 0 ^ 0 = 0 (no neighbors)
            new_node.npx = 0
            self.head_id = new_node.node_id
            self.tail_id = new_node.node_id
        else:
            # New node's npx: prev=0 (it's the new head), next=old_head
            new_node.npx = 0 ^ self.head_id

            # Old head's npx was: 0 ^ old_head_next
            # It needs to become: new_node ^ old_head_next
            # old_head_next = old_npx ^ 0 = old_npx
            # new_npx = new_node.node_id ^ old_head_next
            old_head = self._get_node(self.head_id)
            old_head_next_id = old_head.npx ^ 0  # prev of old head was 0 (NULL)
            old_head.npx = new_node.node_id ^ old_head_next_id

            self.head_id = new_node.node_id

        self.size += 1

    def insert_back(self, data):
        """Insert a new node at the back of the list. O(1).

        Mirror image of insert_front — update tail instead of head.
        """
        new_node = XORNode(data)
        self._register(new_node)

        if self.tail_id == 0:
            new_node.npx = 0
            self.head_id = new_node.node_id
            self.tail_id = new_node.node_id
        else:
            # New node's npx: prev=old_tail, next=0 (it's the new tail)
            new_node.npx = self.tail_id ^ 0

            # Old tail's npx was: old_tail_prev ^ 0
            # It needs to become: old_tail_prev ^ new_node
            old_tail = self._get_node(self.tail_id)
            old_tail_prev_id = old_tail.npx ^ 0  # next of old tail was 0 (NULL)
            old_tail.npx = old_tail_prev_id ^ new_node.node_id

            self.tail_id = new_node.node_id

        self.size += 1

    def traverse_forward(self):
        """Traverse head to tail, yielding each node's data.

        WHY this works: At each step we know the previous node's ID.
        next_id = current.npx ^ prev_id
        This is the core XOR trick — knowing one neighbor recovers the other.
        """
        results = []
        prev_id = 0
        curr_id = self.head_id

        while curr_id != 0:
            curr = self._get_node(curr_id)
            results.append(curr.data)
            # Recover next: npx = prev ^ next, so next = npx ^ prev
            next_id = curr.npx ^ prev_id
            prev_id = curr_id
            curr_id = next_id

        return results

    def traverse_backward(self):
        """Traverse tail to head, yielding each node's data.

        WHY this is symmetric: The XOR field doesn't encode direction.
        prev ^ next looks the same regardless of which direction you're going.
        Starting from tail with next_id=0 recovers prev just like starting
        from head with prev_id=0 recovers next.
        """
        results = []
        next_id = 0
        curr_id = self.tail_id

        while curr_id != 0:
            curr = self._get_node(curr_id)
            results.append(curr.data)
            # Recover prev: npx = prev ^ next, so prev = npx ^ next
            prev_id = curr.npx ^ next_id
            next_id = curr_id
            curr_id = prev_id

        return results

    def delete(self, data):
        """Delete the first node with the given data. O(n) search + O(1) removal.

        WHY O(n): We must traverse to find the node (same as standard linked list).
        WHY O(1) removal: Once found, we update neighbors' npx fields in constant time.

        The tricky part: to update a neighbor's npx, we need to know the node being
        removed so we can XOR it out and XOR in the other neighbor.
        """
        prev_id = 0
        curr_id = self.head_id

        while curr_id != 0:
            curr = self._get_node(curr_id)
            next_id = curr.npx ^ prev_id

            if curr.data == data:
                # Found the node to delete. Update neighbors.

                if prev_id != 0:
                    # Previous node's npx included curr_id.
                    # Replace curr_id with next_id in prev's npx.
                    prev_node = self._get_node(prev_id)
                    # prev's npx = prev_prev ^ curr_id
                    # We need: prev_prev ^ next_id
                    # prev_prev = prev.npx ^ curr_id
                    prev_prev_id = prev_node.npx ^ curr_id
                    prev_node.npx = prev_prev_id ^ next_id
                else:
                    # Deleting head: new head is next_id
                    self.head_id = next_id

                if next_id != 0:
                    # Next node's npx included curr_id.
                    # Replace curr_id with prev_id in next's npx.
                    next_node = self._get_node(next_id)
                    # next's npx = curr_id ^ next_next
                    # We need: prev_id ^ next_next
                    next_next_id = next_node.npx ^ curr_id
                    next_node.npx = prev_id ^ next_next_id
                else:
                    # Deleting tail: new tail is prev_id
                    self.tail_id = prev_id

                self._unregister(curr)
                self.size -= 1
                return True

            prev_id = curr_id
            curr_id = next_id

        return False  # Not found

    def __len__(self):
        return self.size

    def __repr__(self):
        return f"XORLinkedList({self.traverse_forward()})"


# --- Demo ---

def demo():
    """Show that XOR linked list supports bidirectional traversal
    with only one 'pointer' field per node."""

    print("=" * 60)
    print("XOR Linked List Demo")
    print("=" * 60)

    xll = XORLinkedList()

    # Build list: 10 <-> 20 <-> 30 <-> 40
    print("\nInserting 20, 30 at back, then 10 at front, then 40 at back:")
    xll.insert_back(20)
    xll.insert_back(30)
    xll.insert_front(10)
    xll.insert_back(40)

    print(f"  Forward:  {xll.traverse_forward()}")
    print(f"  Backward: {xll.traverse_backward()}")
    print(f"  Size: {len(xll)}")

    # Show the XOR values to make the trick visible
    print("\nNode internals (the XOR trick in action):")
    prev_id = 0
    curr_id = xll.head_id
    while curr_id != 0:
        curr = xll._get_node(curr_id)
        next_id = curr.npx ^ prev_id
        print(f"  data={curr.data:3d}  id={curr.node_id:2d}  "
              f"npx={curr.npx:3d}  (prev_id={prev_id}, next_id={next_id})")
        prev_id = curr_id
        curr_id = next_id

    # Delete from middle
    print("\nDeleting 20:")
    xll.delete(20)
    print(f"  Forward:  {xll.traverse_forward()}")
    print(f"  Backward: {xll.traverse_backward()}")

    # Delete head
    print("\nDeleting 10 (head):")
    xll.delete(10)
    print(f"  Forward:  {xll.traverse_forward()}")
    print(f"  Backward: {xll.traverse_backward()}")

    # Delete tail
    print("\nDeleting 40 (tail):")
    xll.delete(40)
    print(f"  Forward:  {xll.traverse_forward()}")
    print(f"  Backward: {xll.traverse_backward()}")
    print(f"  Size: {len(xll)}")

    # Verify XOR property with a concrete example
    print("\n" + "=" * 60)
    print("XOR Property Proof:")
    print("  If prev_id=5 and next_id=9:")
    print(f"  npx = 5 ^ 9 = {5 ^ 9}")
    print(f"  Recover next: npx ^ prev = {5 ^ 9} ^ 5 = {(5 ^ 9) ^ 5}  (== 9)")
    print(f"  Recover prev: npx ^ next = {5 ^ 9} ^ 9 = {(5 ^ 9) ^ 9}  (== 5)")
    print("=" * 60)


if __name__ == "__main__":
    demo()
