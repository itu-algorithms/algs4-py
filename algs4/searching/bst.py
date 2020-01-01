# Created for BADS 2018
# see README.md for details
# Python 3

from ..errors.errors import NoSuchElementException

"""
The BST class represents an ordered symbol table of generic
key-value pairs.

This implementation uses an unbalanced, binary search tree.

For additional details and documentation, see Section 3.2 of Algorithms,
4th Edition by Robert Sedgewick and Kevin Wayne.

:original author: Robert Sedgewick and Kevin Wayne
:original java code: https://algs4.cs.princeton.edu/32bst/BST.java.html

"""

# Missing methods:
# ceiling, select, rank, size (or rather, range_size)

from typing import TypeVar, Generic, Optional, Sequence, List
from abc import abstractmethod

Val = TypeVar('Val')
Key = TypeVar('Key', bound = 'Comparable')

class Comparable:
    @abstractmethod
    def __lt__(self, other: Key) -> bool:
        pass

class Node(Generic[Key, Val]):
    def __init__(self, key: Key, value: Optional[Val], size: int):
        self.left:  Optional[Node[Key,Val]] = None      # root of left subtree
        self.right: Optional[Node[Key,Val]] = None      # root of right subtree
        self.key: Key = key         # sorted by key
        self.value: Optional[Val] = value     # associated data
        self.size: int = size       # number of nodes in subtree

class BST(Generic[Key, Val]):
    def __init__(self) -> None:
        """
        Initialises empty symbol table
        """
        self._root: Optional[Node[Key, Val]] = None           # root of BST

    def is_empty(self) -> bool:
        """
        Returns true if this symbol table is empty
        """
        return self.size() == 0

    def contains(self, key: Key) -> bool:
        """
        Does this symbol table contain the given key?
        :param key: the key to search for
        :return boolean: true if symbol table contains key, false otherwise
        """
        return self.get(key) != None

    def size(self) -> int:
        """
        Returns the number of key-value pairs in this symbol table
        """
        return self._size(self._root)
        
    def __len__(self) -> int:
        return self.size()

    def _size(self, node: Optional[Node[Key, Val]]) -> int:
        """
        Returns the number of key-value pairs in BST rooted at node

        :param node: The node which act as root
        """
        if node is None:
            return 0
        else:
            return node.size

    def get(self, key: Key) -> Optional[Val]:
        """
        Returns the value associated with the given key

        :param key: The key whose value is returned
        :return: the value associated with the given key if the key
        is in the symbol table, None otherwise
        """
        return self._get(self._root, key)

    def _get(self, node: Optional[Node[Key, Val]], key: Key) -> Optional[Val]:
        if node is None:
            return None
        else:
            if key < node.key:
                return self._get(node.left, key)
            elif key > node.key:
                return self._get(node.right, key)
            else:
                return node.value

    def put(self, key: Key, value: Optional[Val]) -> None:
        """
        Inserts the specified key-value pair into the symbol table,
        overwriting the old value with the new value if the symbol table
        already contains the specified key. Deletes the specified key (and
        its associated value) from this symbol table if the specified value
        is None.

        :param key, value: the key-value pair to be inserted
        """
        if value is None:
            self.delete(key)
            return
        self._root = self._put(self._root, key, value)

    def _put(self, node: Optional[Node[Key,Val]], key: Key, value: Optional[Val]) -> Node[Key, Val]:
        if node is None:
            newnode: Node[Key, Val] = Node(key, value, 1)
            return newnode
        else:
            if key < (node.key):
                node.left = self._put(node.left, key, value)
            elif key > (node.key):
                node.right = self._put(node.right, key, value)
            else:
                node.value = value
            node.size = 1 + self._size(node.left) + self._size(node.right)
            return node

    def delete_min(self) -> None:
        """
        Removes the smallest key and associated value from the symbol table
        TODO exception?
        """
        if self.is_empty():
            raise NoSuchElementException("calls min() with empty symbol table")
        else:
            assert self._root is not None
            self._root = self._delete_min(self._root)

    def _delete_min(self, node: Node[Key, Val]) -> Optional[Node[Key, Val]]:
        if node.left is None:
            return node.right
        else:
            node.left = self._delete_min(node.left)
            node.size = self._size(node.left) + self._size(node.right) + 1
            return node

    def delete_max(self) -> None:
        """
        Removes the largest key and associated value from the symbol table
        """
        if self.is_empty():
            raise NoSuchElementException("calls max() with empty symbol table")
        else:
            assert self._root is not None
            self._root = self._delete_max(self._root)

    def _delete_max(self, node: Node[Key, Val]) -> Optional[Node[Key, Val]]:
        if node.right is None:
            return node.left
        else:
            node.right = self._delete_max(node.right)
        node.size = self._size(node.left) + self._size(node.right) + 1
        return node


    def delete(self, key: Key) -> None:
        """
        Removes the specified key and its associated value from this symbol table
        (if the key is in this symbol table)
        """
        self._root = self._delete(self._root, key)

    def _delete(self, node: Optional[Node[Key,Val]], key: Key) -> Optional[Node[Key,Val]]:
        if node is None:
            return None
        else:
            if key.__lt__(node.key):
                node.left = self._delete(node.left, key)
            elif node.key < key:
                node.right = self._delete(node.right, key)
            else:
                if node.right is None:
                    return node.left
                elif node.left is None:
                    return node.right
                else:
                    temp_node = node
                    assert temp_node.right is not None
                    node = self._min(temp_node.right)
                    node.right = self._delete_min(temp_node.right)
                    node.left = temp_node.left

            node.size = self._size(node.left) + self._size(node.right) + 1
            return node

    def min(self) -> Key:
        """
        Returns the smallest key in the BST
        """
        if self.is_empty():
            raise NoSuchElementException("calls min() with empty symbol table")
        else:
            assert self._root is not None
            return self._min(self._root).key

    def _min(self, node: Node[Key, Val]) -> Node[Key, Val]:
        if node.left is None:
            return node
        else:
            return self._min(node.left)

    def max(self) -> Key:
        """
        Returns the larget key in the symbol table
        """
        if self.is_empty():
            raise NoSuchElementException("calls max() with empty symbol table")
        else:
            assert self._root is not None
            return self._max(self._root).key

    def _max(self, node: Node[Key, Val]) -> Node[Key, Val]:
        if node.right is None:
            return node
        else:
            return self._max(node.right)

    def floor(self, key: Key) -> Optional[Key]:
        """
        Returns the largest key in the symbol table less than or equal to key
        """
        if self.is_empty():
            raise NoSuchElementException("calls floor() with empty symbol table")

        node = self._floor(self._root, key)
        if node is None:
            return None
        else:
            return node.key

    def _floor(self, node: Optional[Node[Key,Val]], key: Key) -> Optional[Node[Key, Val]]:
        if node is None:
            return None
        elif key == node.key:
            return node
        elif key < node.key:
            return self._floor(node.left, key)
        temp_node = self._floor(node.right, key)
        if temp_node is not None:
            return temp_node
        return node

    def keys(self) -> Sequence[Key]:
        """
        Returns all keys in the symbol table as a list.
        """
        if self.is_empty():
            return []
        return self.range_keys(self.min(), self.max())

    def range_keys(self, lo: Key, hi: Key) -> Sequence[Key]:
        """
        Returns all keys in the symbol table in the given range as a list

        :param lo: minimum endpoint
        :param hi: maximum endpoint
        :return: all keys in symbol table between lo (inclusive) and hi (inclusive)
        """
        queue: List[Key] = []
        self._range_keys(self._root, queue, lo, hi)
        return queue

    def _range_keys(self, node: Optional[Node[Key, Val]], queue: List[Key], lo: Key, hi: Key) -> None:
        if node is None:
            return
        elif lo < node.key:
            self._range_keys(node.left, queue, lo, hi)
        if not lo > node.key and not hi < node.key:
            queue.append(node.key)
        if hi > node.key:
            self._range_keys(node.right, queue, lo, hi)

    def height(self) -> int:
        """
        Returns the height of the BST (for debugging)
        """
        return self._height(self._root)

    def _height(self, node: Optional[Node[Key, Val]]) -> int:
        if node is None:
            return -1
        else:
            return 1 + max(self._height(node.left), self._height(node.right))

    def level_order(self) -> Sequence[Key]:
        """
        Returns the keys in the BST in level order (for debugging)
        """
        queue: List[Optional[Node[Key, Val]]] = []
        keys: List[Key] =  []
        queue.append(self._root) 
        while len(queue) > 0:
            node = queue.pop(0)
            if node is None:
                continue
            else:
                keys.append(node.key)
                queue.append(node.left)
                queue.append(node.right)
        return keys


