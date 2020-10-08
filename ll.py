class LinkedList:
    """
    Class representing the basic singly linked list and its operations insert and delete
    """
    class _Node:
        """
        Class representing a node of a lined list
        """
        def __init__(self, val):
            self.next = None
            self.val = val

    def __init__(self):
        """ Linked List initializer """
        self.__head = None
        self.__tail = None
        self.__size = 0

    @property
    def size(self):
        """ :returns size of the linked list"""
        return self.__size

    @property
    def head(self):
        """ :returns the head of the linked list """
        if not self.__head:
            return None
        return self.__head.val

    @property
    def tail(self):
        """ :return: the tail of the linked list """
        if not self.__tail:
            return None
        return self.__tail.val

    def insert(self, val):
        """ inserts an item into the linked list """
        node = self._Node(val)
        if self.__size != 0:
            self.__tail.next = node
        else:
            self.__head = node
        self.__tail = node
        self.__size += 1

    def delete(self):
        """ deletes an item from the linked list and returns the item.
        :return value stored in the node if linked list is not empty, None otherwise"""
        if self.__size == 0:
            return None
        node = self.__head
        if self.__size != 1:
            self.__head = self.__head.next
            node.next = None
        else:
            self.__head = None
        self.__size -= 1
        return node.val
