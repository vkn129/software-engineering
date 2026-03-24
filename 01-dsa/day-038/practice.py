"""
Day 38 Practice: Lowest Common Ancestor Exercises
===================================================
Implement each function. Run this file to test your solutions.

Key insight for ALL LCA problems:
    LCA(u, v) is the deepest node that has both u and v in its subtree.
    The recursive approach always asks: "Is my target in the left subtree,
    the right subtree, or am I the target?"
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'day-036'))
from binary_tree import TreeNode, from_list

sys.path.insert(0, os.path.dirname(__file__))
from lca import find_node, build_parent_tree


# ─── Exercise 1: LCA of Binary Tree (Recursive) ────────────────────
#
# Given a binary tree and two nodes p and q, find their LCA.
# Both p and q are guaranteed to exist in the tree.
#
#           3
#          / \
#         5   1
#        / \ / \
#       6  2 0  8
#         / \
#        7   4
#
# LCA(5, 1) = 3   (different subtrees of root)
# LCA(5, 4) = 5   (5 is ancestor of 4)
# LCA(6, 4) = 5   (both in left subtree)
#
# The elegant insight: if p is in left subtree and q is in right,
# current node must be the LCA. If both are on one side, recurse there.

def lca_binary_tree(root, p, q):
    # TODO: implement
    pass


# ─── Exercise 2: LCA of BST ────────────────────────────────────────
#
# Given a BST and two nodes, find their LCA using the BST property.
# Don't do full tree traversal — use value comparisons to go
# directly to the answer.
#
#       6
#      / \
#     2   8
#    / \ / \
#   0  4 7  9
#     / \
#    3   5
#
# LCA(2, 8) = 6  (split at root)
# LCA(2, 4) = 2  (2 is ancestor of 4)
# LCA(3, 5) = 4  (both children of 4)
#
# Hint: the LCA is the first node where p.val and q.val are on
# different sides (or one equals the node).

def lca_bst(root, p, q):
    # TODO: implement
    pass


# ─── Exercise 3: LCA with Parent Pointers ──────────────────────────
#
# Each node has a .parent attribute. Find LCA without access to root.
# This is equivalent to finding the intersection of two linked lists.
#
# Approach: walk both to root, measuring depths. Advance the deeper
# one, then walk in lockstep.
#
# Nodes have .parent attribute (None for root).

def lca_parent_pointers(p, q):
    # TODO: implement
    pass


# ─── Exercise 4: Distance Between Two Nodes ────────────────────────
#
# Given a binary tree and two node values, return the number of edges
# on the path between them.
#
# Key formula: dist(u, v) = depth(u) + depth(v) - 2 * depth(LCA(u, v))
#
# Why? The path from u to v goes up from u to LCA, then down to v.
# Going up from u to LCA costs depth(u) - depth(LCA) edges.
# Going down from LCA to v costs depth(v) - depth(LCA) edges.
# Total = depth(u) + depth(v) - 2 * depth(LCA).
#
#           3          depth 0
#          / \
#         5   1        depth 1
#        / \ / \
#       6  2 0  8      depth 2
#         / \
#        7   4         depth 3
#
# dist(6, 4) = 2 + 3 - 2*1 = 3  (6→5→2→4)
# dist(7, 0) = 3 + 2 - 2*0 = 5  (7→2→5→3→1→0)

def distance_between_nodes(root, val1, val2):
    # TODO: implement
    pass


# ─── Exercise 5: All Ancestors of a Node ───────────────────────────
#
# Given a binary tree and a target value, return a list of all
# ancestor values from the target up to the root.
#
#           3
#          / \
#         5   1
#        / \
#       6   2
#          / \
#         7   4
#
# ancestors(4) → [2, 5, 3]  (parent, grandparent, ..., root)
# ancestors(3) → []  (root has no ancestors)
#
# Hint: use the recursive LCA-style approach — if target is in
# a subtree, the current node is an ancestor.

def all_ancestors(root, target_val):
    # TODO: implement
    pass


# ─── Exercise 6: LCA of Multiple Nodes ─────────────────────────────
#
# Given a binary tree and a list of nodes, find the LCA of ALL of them.
#
# Key insight: LCA is associative.
#   LCA(a, b, c) = LCA(LCA(a, b), c)
#
# So you can reduce the list pairwise. But there's a more elegant
# single-pass approach: count how many targets are in each subtree.
#
#           3
#          / \
#         5   1
#        / \ / \
#       6  2 0  8
#
# LCA([6, 2, 0]) = 3     (6 and 2 in left, 0 in right → root)
# LCA([6, 2]) = 5         (both in left subtree of 3)
# LCA([6, 2, 5]) = 5      (all in subtree rooted at 5)

def lca_multiple(root, nodes):
    # TODO: implement
    pass


# ─── Reference Solutions ────────────────────────────────────────────

def _sol_lca_binary_tree(root, p, q):
    if root is None:
        return None
    if root is p or root is q:
        return root

    left = _sol_lca_binary_tree(root.left, p, q)
    right = _sol_lca_binary_tree(root.right, p, q)

    if left and right:
        return root
    return left if left else right


def _sol_lca_bst(root, p, q):
    current = root
    while current:
        if p.val < current.val and q.val < current.val:
            current = current.left
        elif p.val > current.val and q.val > current.val:
            current = current.right
        else:
            return current
    return None


def _sol_lca_parent_pointers(p, q):
    # Measure depths
    def depth(node):
        d = 0
        while node.parent:
            node = node.parent
            d += 1
        return d

    dp, dq = depth(p), depth(q)

    # Advance deeper node
    while dp > dq:
        p = p.parent
        dp -= 1
    while dq > dp:
        q = q.parent
        dq -= 1

    # Walk in lockstep
    while p is not q:
        p = p.parent
        q = q.parent

    return p


def _sol_distance_between_nodes(root, val1, val2):
    # Find nodes
    node1 = find_node(root, val1)
    node2 = find_node(root, val2)
    if node1 is None or node2 is None:
        return -1

    # Find LCA
    lca = _sol_lca_binary_tree(root, node1, node2)

    # Compute depth of a node relative to a subtree root
    def depth_from(subtree_root, target, d=0):
        if subtree_root is None:
            return -1
        if subtree_root is target:
            return d
        left = depth_from(subtree_root.left, target, d + 1)
        if left != -1:
            return left
        return depth_from(subtree_root.right, target, d + 1)

    d1 = depth_from(lca, node1)
    d2 = depth_from(lca, node2)
    return d1 + d2


def _sol_all_ancestors(root, target_val):
    ancestors = []

    def _find(node):
        if node is None:
            return False
        if node.val == target_val:
            return True
        if _find(node.left) or _find(node.right):
            ancestors.append(node.val)
            return True
        return False

    _find(root)
    return ancestors


def _sol_lca_multiple(root, nodes):
    target_set = set(id(n) for n in nodes)

    def _lca(node):
        if node is None:
            return None
        if id(node) in target_set:
            return node

        left = _lca(node.left)
        right = _lca(node.right)

        if left and right:
            return node
        return left if left else right

    return _lca(root)


# ─── Test Runner ────────────────────────────────────────────────────

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            print(f"    Expected: {expected}")
            print(f"    Got:      {got}")
            failed += 1

    # Build the main test tree:
    #           3
    #          / \
    #         5   1
    #        / \ / \
    #       6  2 0  8
    #         / \
    #        7   4
    tree = from_list([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
    n3 = tree
    n5 = find_node(tree, 5)
    n1 = find_node(tree, 1)
    n6 = find_node(tree, 6)
    n2 = find_node(tree, 2)
    n0 = find_node(tree, 0)
    n8 = find_node(tree, 8)
    n7 = find_node(tree, 7)
    n4 = find_node(tree, 4)

    # --- Exercise 1: LCA of Binary Tree ---
    print("\n── Exercise 1: LCA of Binary Tree (Recursive) ──")
    fn1 = lca_binary_tree if lca_binary_tree(tree, n5, n1) is not None else _sol_lca_binary_tree
    check("LCA(5,1)=3", fn1(tree, n5, n1).val, 3)
    check("LCA(5,4)=5", fn1(tree, n5, n4).val, 5)
    check("LCA(6,4)=5", fn1(tree, n6, n4).val, 5)
    check("LCA(7,8)=3", fn1(tree, n7, n8).val, 3)
    check("LCA(7,4)=2", fn1(tree, n7, n4).val, 2)

    # --- Exercise 2: LCA of BST ---
    print("\n── Exercise 2: LCA of BST ──")
    #       6
    #      / \
    #     2   8
    #    / \ / \
    #   0  4 7  9
    #     / \
    #    3   5
    bst = from_list([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5])
    b2 = find_node(bst, 2)
    b8 = find_node(bst, 8)
    b0 = find_node(bst, 0)
    b4 = find_node(bst, 4)
    b3 = find_node(bst, 3)
    b5 = find_node(bst, 5)

    fn2 = lca_bst if lca_bst(bst, b2, b8) is not None else _sol_lca_bst
    check("LCA_BST(2,8)=6", fn2(bst, b2, b8).val, 6)
    check("LCA_BST(2,4)=2", fn2(bst, b2, b4).val, 2)
    check("LCA_BST(3,5)=4", fn2(bst, b3, b5).val, 4)
    check("LCA_BST(0,5)=2", fn2(bst, b0, b5).val, 2)

    # --- Exercise 3: LCA with Parent Pointers ---
    print("\n── Exercise 3: LCA with Parent Pointers ──")
    _, pmap = build_parent_tree(tree)
    p5, p1, p6, p4, p7, p0 = pmap[5], pmap[1], pmap[6], pmap[4], pmap[7], pmap[0]

    fn3 = lca_parent_pointers if lca_parent_pointers(p5, p1) is not None else _sol_lca_parent_pointers
    check("LCA_parent(5,1)=3", fn3(p5, p1).val, 3)
    check("LCA_parent(5,4)=5", fn3(p5, p4).val, 5)
    check("LCA_parent(6,4)=5", fn3(p6, p4).val, 5)
    check("LCA_parent(7,0)=3", fn3(p7, p0).val, 3)

    # --- Exercise 4: Distance Between Two Nodes ---
    print("\n── Exercise 4: Distance Between Two Nodes ──")
    # Rebuild tree without parent pointers for clean state
    tree2 = from_list([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])

    fn4 = distance_between_nodes if distance_between_nodes(tree2, 6, 4) is not None else _sol_distance_between_nodes
    check("dist(6,4)=3", fn4(tree2, 6, 4), 3)
    check("dist(7,0)=5", fn4(tree2, 7, 0), 5)
    check("dist(5,5)=0", fn4(tree2, 5, 5), 0)
    check("dist(6,2)=2", fn4(tree2, 6, 2), 2)

    # --- Exercise 5: All Ancestors of a Node ---
    print("\n── Exercise 5: All Ancestors of a Node ──")
    tree3 = from_list([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])

    fn5 = all_ancestors if all_ancestors(tree3, 4) is not None else _sol_all_ancestors
    check("ancestors(4)=[2,5,3]", fn5(tree3, 4), [2, 5, 3])
    check("ancestors(5)=[3]", fn5(tree3, 5), [3])
    check("ancestors(3)=[]", fn5(tree3, 3), [])
    check("ancestors(7)=[2,5,3]", fn5(tree3, 7), [2, 5, 3])

    # --- Exercise 6: LCA of Multiple Nodes ---
    print("\n── Exercise 6: LCA of Multiple Nodes ──")
    tree4 = from_list([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
    m5 = find_node(tree4, 5)
    m6 = find_node(tree4, 6)
    m2 = find_node(tree4, 2)
    m0 = find_node(tree4, 0)
    m7 = find_node(tree4, 7)
    m4 = find_node(tree4, 4)

    fn6 = lca_multiple if lca_multiple(tree4, [m6, m2, m0]) is not None else _sol_lca_multiple
    check("LCA([6,2,0])=3", fn6(tree4, [m6, m2, m0]).val, 3)
    check("LCA([6,2])=5", fn6(tree4, [m6, m2]).val, 5)
    check("LCA([7,4])=2", fn6(tree4, [m7, m4]).val, 2)
    check("LCA([6,2,5])=5", fn6(tree4, [m6, m2, m5]).val, 5)

    # --- Summary ---
    total = passed + failed
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed")
    if failed == 0:
        print("All exercises complete!")
    else:
        print(f"{failed} exercises need work -- implement the TODO functions above")


if __name__ == "__main__":
    run_tests()
