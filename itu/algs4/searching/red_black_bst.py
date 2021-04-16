from abc import abstractmethod
from typing import Generic, Optional, TypeVar

from typing_extensions import Protocol

from ..errors.errors import IllegalArgumentException, NoSuchElementException
from ..fundamentals.queue import Queue

# Created for BADS 2018
# See README.md for details
# Python 3

# Typing ---


Key = TypeVar("Key", bound="Comparable")
Val = TypeVar("Val")


class Comparable(Protocol):
    @abstractmethod
    def __lt__(self: Key, other: Key) -> bool:
        pass


# ---
class Node(Generic[Key, Val]):
    """RedBlackBST helper node data type."""

    def __init__(self, key: Key, val: Val, color: bool, size: int):
        """Initializes a new node.

        :param key: the key of the node
        :param val: the value of the node
        :param size: the subtree count

        """
        self.key: Key = key
        self.val: Val = val
        self.left: Optional[Node[Key, Val]] = None
        self.right: Optional[Node[Key, Val]] = None
        self.size: int = size
        self.color: bool = color


class RedBlackBST(Generic[Key, Val]):
    """The RedBlackBST class represents an ordered symbol table of generic key-
    value pairs.

    It supports the usual put, get, contains, delete, size, and is-empty
    methods. It also provides ordered methods for finding the minimum,
    maximum, floor, and ceiling. It also provides a keys method for
    iterating over all the keys. A symbol table implements the
    associative array abstraction: when associating a value with a key
    that is already in the symbol table, the convention is to replace
    the old value with the new value. This class uses the convention
    that values cannot be None-setting the value associated with a key
    to None is equivalent to deleting the key from the symbol table.
    This implementation uses a left-leaning red-black BST. It requires
    that the keys are all of the same type and that they can be
    compared. The put, contains, remove, minimum, maximum, ceiling, and
    floor operations each take logarithmic time in the worst case, if
    the tree becomes unbalanced. The size, and is-empty operations take
    constant time. Construction takes constant time.

    """

    RED = True
    BLACK = False

    def __init__(self) -> None:
        """Initializes an empty symbol table."""
        self._root: Optional[Node[Key, Val]] = None

    def put(self, key: Key, val: Val) -> None:
        """Inserts the specified key-value pair into the symbol table,
        overwriting the old value with the new value if the symbol table
        already contains the specified key. Deletes the specified key (and its
        associated value) from this symbol table if the specified value is
        None.

        :param key: the key
        :param val: the value
        :raises IllegalArgumentException: if key is None

        """
        # Can never happen if type checked:
        if key is None:
            raise IllegalArgumentException("first argument to put() is None")
        if val is None:
            self.delete(key)
            return

        self._root = self._put(self._root, key, val)
        self._root.color = RedBlackBST.BLACK

    def _put(self, h: Optional[Node[Key, Val]], key: Key, val: Val) -> Node[Key, Val]:
        """Inserts the key-value pair in the subtree rooted at h.

        :param h: root of currently inspected subtree
        :param key: the key
        :param val: the value

        """
        if h is None:
            return Node(key, val, self.RED, 1)
        if key < h.key:
            h.left = self._put(h.left, key, val)
        elif key > h.key:
            h.right = self._put(h.right, key, val)
        else:
            h.val = val

        assert h is not None
        if self._is_red(h.right) and not self._is_red(h.left):
            h = self._rotate_left(h)
        assert h is not None
        if self._is_red(h.left):
            assert h.left is not None  # bc h.left is red
            if self._is_red(h.left.left):
                h = self._rotate_right(h)
        assert h is not None
        if self._is_red(h.left) and self._is_red(h.right):
            self._flip_colors(h)

        h.size = self._size(h.left) + self._size(h.right) + 1

        return h

    def get(self, key: Key) -> Optional[Val]:
        """Returns the value associated with the given key.

        :param key: the key
        :return: the value associated with the given key if the key is in the symbol table
        and None if the key is not in the symbol table
        :raises IllegalArgumentException: if key is None

        """
        # This can never happen if type checked:
        if key is None:
            raise IllegalArgumentException("argument to get() is None")

        return self._get(self._root, key)

    def _get(self, x: Optional[Node[Key, Val]], key: Key) -> Optional[Val]:
        """Returns value with the given key in subtree rooted at x. None if no
        such key.

        :param x: root of currently inspected subtree.
        :param key: the key
        :return: value associated with given key. None if no such key

        """
        while x is not None:
            if key < x.key:
                x = x.left
            elif key > x.key:
                x = x.right
            else:
                return x.val
        return None

    def delete_min(self) -> None:
        """Removes the smallest key and associated value from the symbol table.

        :raises NoSuchElementException: if the symbol table is empty

        """
        if self.is_empty():
            raise NoSuchElementException("RedBlackBST underflow")
        assert self._root is not None
        if not self._is_red(self._root.left) and not self._is_red(self._root.right):
            self._root.color = self.RED
        self._root = self._delete_min(self._root)
        if not self.is_empty():
            assert self._root is not None
            self._root.color = RedBlackBST.BLACK

    def _delete_min(self, h: Node[Key, Val]) -> Optional[Node[Key, Val]]:
        """Deletes the node with the minimum key rooted at h."""
        if h.left is None:
            return None
        if not self._is_red(h.left) and not self._is_red(h.left.left):
            h = self._move_red_left(h)
        assert h.left is not None  # because _move_red_left moved something to h.left
        h.left = self._delete_min(h.left)
        return self._balance(h)

    def delete_max(self) -> None:
        """Removes the largest key and associated value from the symbol table.

        :raises NoSuchElementException: if the symbol table is empty

        """
        if self.is_empty():
            raise NoSuchElementException("RedBlackBST underflow")
        assert self._root is not None
        if not self._is_red(self._root.left) and not self._is_red(self._root.right):
            self._root.color = self.RED
        self._root = self._delete_max(self._root)
        if not self.is_empty():
            assert self._root is not None
            self._root.color = RedBlackBST.BLACK

    def _delete_max(self, h: Node[Key, Val]) -> Optional[Node[Key, Val]]:
        """Deletes the key-value pair with the maximum key rooted at h."""
        if self._is_red(h.left):
            h = self._rotate_right(h)
        if h.right is None:
            return None
        if not self._is_red(h.right) and not self._is_red(h.right.left):
            h = self._move_red_right(h)
        assert h.right is not None  # because _move_red_right moved something to h.right
        h.right = self._delete_max(h.right)
        return self._balance(h)

    def delete(self, key: Key) -> None:
        """Removes the specified key and its associated value from this symbol
        table (if the key is in this symbol table).

        :param key: the key
        :raises IllegalArgumentException: if key is None

        """
        # Cannot happen if type checked:
        if key is None:
            raise IllegalArgumentException("argument to delete() is None")
        if not self.contains(key):
            return
        assert self._root is not None
        if not self._is_red(self._root.left) and not self._is_red(self._root.right):
            self._root.color = self.RED
        self._root = self._delete(self._root, key)
        if not self.is_empty():
            assert self._root is not None
            self._root.color = RedBlackBST.BLACK

    def _delete(self, h: Node[Key, Val], key: Key) -> Optional[Node[Key, Val]]:
        """Deletes the key-value pair with the given key rooted at h."""
        if key < h.key:
            # we assert (from delete) that key exists in h's subtree, so it must exists
            # in the left subtree, so h.left is not None
            assert h.left is not None
            if not self._is_red(h.left) and not self._is_red(h.left.left):
                h = self._move_red_left(h)
            assert h.left is not None  # _move_red_left does what it should
            h.left = self._delete(h.left, key)
        else:
            if self._is_red(h.left):
                h = self._rotate_right(h)
            if key == h.key and h.right is None:
                return None
            assert h.right is not None  # bc. key must be in the right subtree
            if not self._is_red(h.right) and not self._is_red(h.right.left):
                h = self._move_red_right(h)
            assert h.right is not None
            if key == h.key:
                x = self._min(h.right)
                h.key = x.key
                h.val = x.val
                h.right = self._delete_min(h.right)
            else:
                h.right = self._delete(h.right, key)
        return self._balance(h)

    def size(self) -> int:
        """Return the number of key-value pairs in this symbol table.

        :return: the number of key-value pairs in this symbol table

        """
        return self._size(self._root)

    def __len__(self) -> int:
        return self.size()

    def _size(self, x: Optional[Node[Key, Val]]) -> int:
        """Number of nodes in subtree rooted at x. 0 if x is None.

        :param x: root node of subtree
        :return: number of nodes in subtree

        """
        if x is None:
            return 0
        return x.size

    def contains(self, key: Key) -> bool:
        """Does this symbol table contain the given key?

        :param key: the key
        :return: True if this symbol table contains key and False otherwise

        """
        return self.get(key) is not None

    def is_empty(self) -> bool:
        """Is this symbol table empty?

        :return: True if this symbol table is empty and False otherwise

        """
        return self._root is None

    @classmethod
    def _is_red(self, x: Optional[Node[Key, Val]]) -> bool:
        """Is node x red?

        :param x: the node to check
        :return: True if node is red False otherwise

        """
        if x is None:
            return False
        return x.color == RedBlackBST.RED

    def _rotate_left(self, h: Node[Key, Val]) -> Node[Key, Val]:
        """Make a right-leaning link lean to the left.

        :param h:
        :return: The node that has taken h's position

        """
        x = h.right
        assert x is not None  # bc h has a right-leaning (red) link
        h.right = x.left
        x.left = h
        x.color = h.color
        h.color = self.RED
        x.size = h.size
        h.size = self._size(h.left) + self._size(h.right) + 1
        return x

    def _rotate_right(self, h: Node[Key, Val]) -> Node[Key, Val]:
        """Make a left-leaning link lean to the right.

        :param h:
        :return: The node that has taken h's position

        """
        x = h.left
        assert x is not None  # bc h has a left-leaning (red) link
        h.left = x.right
        x.right = h
        x.color = h.color
        h.color = self.RED
        x.size = h.size
        h.size = self._size(h.left) + self._size(h.right) + 1
        return x

    def _flip_colors(self, h: Node[Key, Val]) -> None:
        """Flip the colors of a node and its two children.

        :param h: the node

        """
        assert h.left is not None
        assert h.right is not None
        h.color = not h.color
        h.left.color = not h.left.color
        h.right.color = not h.right.color

    def _move_red_left(self, h: Node[Key, Val]) -> Node[Key, Val]:
        """Assuming that h is red and both h.left and h.left.left are black,
        make h.left or one of its children red.

        Assumes h.right exists

        """
        assert h.right is not None
        self._flip_colors(h)
        if self._is_red(h.right.left):
            h.right = self._rotate_right(h.right)
            h = self._rotate_left(h)
            self._flip_colors(h)
        return h

    def _move_red_right(self, h: Node[Key, Val]) -> Node[Key, Val]:
        """Assuming that h is red and both h.right and h.right.left are black,
        make h.right or one of its children red."""
        assert h.left is not None  # more is true: h.right.left exists and is not red
        self._flip_colors(h)
        if self._is_red(h.left.left):
            h = self._rotate_right(h)
            self._flip_colors(h)
        return h

    def _balance(self, h: Node[Key, Val]) -> Node[Key, Val]:
        """Restore red-black tree invariant."""
        if self._is_red(h.right) and not self._is_red(h.left):
            h = self._rotate_left(h)
        if self._is_red(h.left):
            assert h.left is not None
            if self._is_red(h.left.left):
                h = self._rotate_right(h)
        if self._is_red(h.left) and self._is_red(h.right):
            self._flip_colors(h)
        h.size = self._size(h.left) + self._size(h.right) + 1
        return h

    def height(self) -> int:
        """
        Returns the height of the RedBlackBST

        :return: the height of the RedBlackBST (a 1-node tree has height 0)
        """
        return self._height(self._root)

    def _height(self, x: Optional[Node[Key, Val]]) -> int:
        """Returns height of subtree rooted at x."""
        if x is None:
            return -1
        return 1 + max(self._height(x.left), self._height(x.right))

    def min(self) -> Key:
        """
        Returns the smallest key in the symbol table.

        :return: the smallest key in the symbol table
        :raises NoSuchElementException: if the symbol table is empty
        """
        if self.is_empty():
            raise NoSuchElementException("calls min() with empty symbol table")
        assert self._root is not None
        return self._min(self._root).key

    def _min(self, x: Node[Key, Val]) -> Node[Key, Val]:
        """Returns the Node with the smallest key in subtree rooted at x.

        None if no such key

        """
        if x.left is None:
            return x
        else:
            return self._min(x.left)

    def max(self) -> Key:
        """
        Returns the largest key in the symbol table.

        :return: the largest key in the symbol table
        :raises NoSuchElementException: if the symbol table is empty
        """
        if self.is_empty():
            raise NoSuchElementException("calls max() with empty symbol table")
        assert self._root is not None
        return self._max(self._root).key

    def _max(self, x: Node[Key, Val]) -> Node[Key, Val]:
        """Returns the node with the largest key in subtree rooted at x.

        None if no such key.

        """
        if x.right is None:
            return x
        else:
            return self._max(x.right)

    def keys(self) -> Queue[Key]:
        """Returns all keys in the symbol table.

        :return: all keys in the symbol table

        """
        if self.is_empty():
            return Queue()
        return self.keys_range(self.min(), self.max())

    def keys_range(self, lo: Key, hi: Key) -> Queue[Key]:
        """Returns all keys in the symbol table in the given range.

        :param lo: minimum endpoint
        :param hi: maximum endpoint
        :return: all keys in the symbol table between lo (inclusive) and hi (inclusive)
        :raises IllegalArgumentException: if either lo or hi is None

        """
        if lo is None:
            raise IllegalArgumentException("first argument to keys() is None")
        if hi is None:
            raise IllegalArgumentException("second argument to keys() is None")
        queue: Queue[Key] = Queue()
        self._keys_range(self._root, queue, lo, hi)
        return queue

    def _keys_range(
        self, node: Optional[Node[Key, Val]], queue: Queue[Key], lo: Key, hi: Key
    ) -> None:
        """Adds the keys between lo and hi in the subtree rooted at x to the
        queue."""
        if node is None:
            return
        if lo < node.key:
            self._keys_range(node.left, queue, lo, hi)
        if lo <= node.key <= hi:
            queue.enqueue(node.key)
        if hi > node.key:
            self._keys_range(node.right, queue, lo, hi)

    def select(self, k: int) -> Key:
        """Return the kth smallest key in the symbol table.

        :param k: the order statistic
        :return: the kth smallest key in the symbol table
        :raises IllegalArgumentException: unless k is between 0 and n-1

        """
        if k < 0 or k >= self.size():
            raise IllegalArgumentException(
                "argument to select() is invalid: {}".format(k)
            )
        assert self._root is not None  # bc. 0 <= k < self.size()
        x = self._select(self._root, k)
        return x.key

    def _select(self, x: Node[Key, Val], k: int) -> Node[Key, Val]:
        """Returns the node with key of rank k in the subtree rooted at x."""
        t = self._size(x.left)
        if t > k:
            assert x.left is not None
            return self._select(x.left, k)
        elif t < k:
            assert x.right is not None
            return self._select(x.right, k - t - 1)
        else:
            return x

    def rank(self, key: Key) -> int:
        """Returns the number of keys in the symbol table strictly less than
        key.

        :param key: the key
        :return: the number of keys in the symbol table strictly less than key
        :raises IllegalArgumentException: if key is None

        """
        if key is None:
            raise IllegalArgumentException("argument to rank() is None")
        return self._rank(key, self._root)

    def _rank(self, key: Key, x: Optional[Node[Key, Val]]) -> int:
        """Returns the number of keys less than key in the subtree rooted at
        x."""
        if x is None:
            return 0
        if key < x.key:
            return self._rank(key, x.left)
        if key > x.key:
            return 1 + self._size(x.left) + self._rank(key, x.right)
        else:
            return self._size(x.left)

    def size_range(self, lo: Key, hi: Key) -> int:
        """Returns the number of keys in the symbol table in the given range.

        :param lo: minimum endpoint
        :param hi: maximum endpoint
        :return: the number of keys in the symbol table between lo
        (inclusive) and hi (inclusive)
        :rtype: int
        :raises IllegalArgumentException: if either lo or hi is None

        """
        if lo is None:
            return IllegalArgumentException("first argument to size() is None")
        if hi is None:
            return IllegalArgumentException("second argument to size() is None")
        if lo > hi:
            return 0
        if self.contains(hi):
            return self.rank(hi) - self.rank(lo) + 1
        else:
            return self.rank(hi) - self.rank(lo)

    def floor(self, key: Key) -> Key:
        """Returns the largest key in the symbol table less than or equal to
        key.

        :param key: the key
        :return: the largest key in the symbol table less than er equal to key
        :raises IllegalArgumentException: if key is None
        :raises NoSuchElementException: if there is no such key

        """
        if key is None:
            raise IllegalArgumentException("argument to floor() is None")
        if self.is_empty():
            raise NoSuchElementException("calls floor() with empty symbol table")
        x = self._floor(self._root, key)
        if x is None:
            raise NoSuchElementException("calls floor() with key < min")
        return x.key

    def _floor(self, x: Optional[Node[Key, Val]], key: Key) -> Optional[Node[Key, Val]]:
        """Returns the largest key in the subtree rooted at x less than or
        equal to the given key."""
        if x is None:
            return None
        if key == x.key:
            return x
        if key < x.key:
            return self._floor(x.left, key)
        t = self._floor(x.right, key)
        if t is not None:
            return t
        return x

    def ceiling(self, key: Key) -> Key:
        """Returns the smallest key in the symbol table greater than or equal
        to key.

        :param key: the key
        :return: the smallest key in the symbol table greater than or equal to key
        :raises IllegalArgumentException: if key is None
        :raises NoSuchElementException: if there is no such key

        """
        if key is None:
            raise IllegalArgumentException("argument to ceiling is None")
        if self.is_empty():
            raise NoSuchElementException("calls ceiling() with empty symbol table")
        x = self._ceiling(self._root, key)
        if x is None:
            raise NoSuchElementException("calls ceiling() with key > max")
        return x.key

    def _ceiling(
        self, x: Optional[Node[Key, Val]], key: Key
    ) -> Optional[Node[Key, Val]]:
        """Returns the node with the smallest key in the subtree rooted at x
        greater than or equal to the given key."""
        if x is None:
            return None
        assert x is not None
        if key == x.key:
            return x
        if key > x.key:
            return self._ceiling(x.right, key)
        t = self._ceiling(x.left, key)
        if t is not None:
            return t
        return x
