from exceptions import ChannelClosedException, TypeMismatchException
from ll import LinkedList
from threading import Condition


class Channel:
    """
    This class provides Go like implementation for channels except for the operators used.
    Much like Go channels, the calls over channels are blocking meaning, sending and receiving over a channel
    is blocked until a condition is met.

    There are 3 methods exposed publicly:
        1. Send - sends a message over the channel
        2. Receive - receives a message from the channel
        3. Close - closes the channel

    Channels can also be iterated over usina a for loop.
    Iterate over channels only if you want to flush out the remaining items in its buffer
    """

    __MAX_WAIT_TIME = 30.0

    class _Done:
        """ class representing end of buffer once closed """
        pass

    def __init__(self, _type, size=-1):
        """ initializing for channels"""
        self.__capacity = size
        self.__buffer = LinkedList()
        self.__type = _type
        self.__cond = Condition()
        self.__closed = False

    @property
    def capacity(self):
        return self.__capacity

    def __len__(self):
        """ :return number of messages in the channel """
        with self.__cond:
            return self.__buffer.size

    def __is_empty(self):
        """ :return whether channel is empty """
        return len(self) == 0

    def __is_full(self):
        """ :return bool indicating whether a channel is full """
        with self.__cond:
            return self.__buffer.size == self.__capacity

    def __flushed_buffer(self):
        """ :returns True if the channel has been closed and emptied, false otherwise"""
        with self.__cond:
            return self.__closed and self.__buffer.head is None

    def __iter__(self):
        """ iterate over the channel and depopulate it. Returns each message after depopulating """
        while not self.__flushed_buffer():
            message = self.__depopulate()
            if isinstance(message, self._Done):
                return
            yield message
        return

    def __check_type(self, _input):
        """ ensure type check for channels """
        if not isinstance(_input, self.__type):
            raise TypeMismatchException("Input Type does not match the type of channel")

    def __wait(self, wait_time=__MAX_WAIT_TIME):
        with self.__cond:
            self.__cond.wait(wait_time)

    def is_closed(self):
        """ :return bool indicating whether a channel is open or closed"""
        with self.__cond:
            return self.__closed

    def __populate(self, item):
        """ populates the channel with an message. If channel is at capacity, waits till channel is
        depopulated at least once. Also notifies all threads waiting to receive on the other end of the channel"""
        self.__check_type(item)
        if self.__capacity != -1 and self.__is_full():
            while not self.is_closed() and self.__is_full():
                self.__wait()
            if self.is_closed():
                return
        with self.__cond:
            self.__buffer.insert(item)
            self.__cond.notifyAll()

    def __depopulate(self):
        """ depopulates the channel and returns the message. If channel is empty, waits till channel is
        populated at least once. If the channel is closed before depopulating, a special object is returned.
        Also notifies all threads waiting to send on the other end of the channel.
        :return message if channel is open"""
        while not self.is_closed() and self.__is_empty():
            self.__wait()
        if self.__flushed_buffer():
            return self._Done()
        with self.__cond:
            message = self.__buffer.delete()
            self.__cond.notifyAll()
            return message

    def send(self, message):
        """
        Sends a message across the channel. Raises an exception if it is called on a closed channel
        :exception raises ChannelClosedException if send is called on a closed channel
        """
        if self.is_closed():
            raise ChannelClosedException("Invalid operation send on closed channel")
        self.__populate(message)

    def receive(self):
        """
        Receives a message from the channel
        :returns a message from the buffer
        """
        message = self.__depopulate()
        if isinstance(message, self._Done):
            return
        return message

    def close(self):
        """ Closes the channel. Raises exception if it is called on a closed channel"""
        with self.__cond:
            if self.__closed:
                raise ChannelClosedException("Cannot close a closed channel")
            self.__closed = True
            self.__cond.notifyAll()
