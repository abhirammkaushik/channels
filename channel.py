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

    Channels can also be iterated over using a for loop.
    """

    __MAX_WAIT_TIME = 30.0

    def __init__(self, _type, size=-1):
        """ initializing for channels"""
        self.__capacity = size
        self.__buffer = LinkedList()
        self.__type = _type
        self.__cond = Condition()
        self.__closed = False
        self.__zero_value_map = {int: 0, float: 0.0, str: '', tuple: (), list: [], dict: {}, set: set()}

    @property
    def capacity(self):
        return self.__capacity

    def __len__(self):
        """
        Calculates the number of messages in the channel
        :return number of messages in the channel
        """
        with self.__cond:
            return self.__buffer.size

    def __is_empty(self):
        """
        checks whether a channel is empty
        :return True if a channel is empty, False otherwise
        """
        return len(self) == 0

    def __is_full(self):
        """
        checks whether a channel is full. A channel with size -1 is never full.
        :return True if a channel is full, False otherwise """
        with self.__cond:
            return self.__buffer.size == self.__capacity

    def __flushed_buffer(self):
        """
        Checks whether the channel has been closed and emptied.
        :returns True if the channel has been closed and emptied, false otherwise
        """
        with self.__cond:
            return self.__closed and self.__buffer.head is None

    def __zero_value(self):
        """
        Calculates the zero value of the type of the channel.
        Zero Values are values or expressions of a particular type which evaluate to False as a boolean.
        Zero values for default python types are stored in a dictionary
        :return: zero value of the default python types, None for other types
        """
        try:
            return self.__zero_value_map[self.__type]
        except KeyError:
            return None

    def __iter__(self):
        """
        Iterate over the channel and depopulate it. Exits when the buffer has been flushed
        :returns each message in the buffer. """
        while not self.__flushed_buffer():
            message, ok = self.__depopulate()
            if not ok:
                return
            yield message

    def __check_type(self, _input):
        """
        Ensure type check for channels.
        :param _input: input to be checked
        :raises TypeMismatchException if input object is not an instance of type defined during initialization of the
        channel
        """
        if not isinstance(_input, self.__type):
            raise TypeMismatchException("Input Type does not match the type of channel")

    def __wait(self):
        """
        Waits for a specified amount of time. This is necessary when waiting for a thread to finish sending or receiving
        over the channel
        """
        with self.__cond:
            self.__cond.wait(self.__class__.__MAX_WAIT_TIME)

    def is_closed(self):
        """
        Checks whether a channel closed
        :return True a channel is closed, False otherwise
        """
        with self.__cond:
            return self.__closed

    def __populate(self, message):
        """
        Populates the channel with an message. If channel is at capacity, waits till channel is
        depopulated at least once. Also notifies all threads waiting to receive on the other end of the channel
        :param message: message to be added to the buffer
        """
        self.__check_type(message)
        if self.__capacity != -1 and self.__is_full():
            while not self.is_closed() and self.__is_full():
                self.__wait()
            if self.is_closed():
                return
        with self.__cond:
            self.__buffer.insert(message)
            self.__cond.notifyAll()

    def __depopulate(self):
        """
        Depopulates the channel and returns the message. If channel is empty, waits till channel is
        populated at least once. If the channel is closed before depopulating, a special object is returned.
        Also notifies all threads waiting to send on the other end of the channel.
        :return tuple of (message, True) if channel is open, tuple of (None, False) otherwise
        """
        while not self.is_closed() and self.__is_empty():
            self.__wait()
        if self.__flushed_buffer():
            return None, False
        with self.__cond:
            message = self.__buffer.delete()
            self.__cond.notifyAll()
            return message, True

    def send(self, message):
        """
        Sends a message across the channel. Raises an exception if it is called on a closed channel
        :param message: message to be sent on the channel
        :raises ChannelClosedException if send is called on a closed channel
        """
        if self.is_closed():
            raise ChannelClosedException("Invalid operation send on closed channel")
        self.__populate(message)

    def receive(self):
        """
        Receives a message from the channel
        :returns a message from the buffer
        """
        message, ok = self.__depopulate()
        if not ok:
            return self.__zero_value(), False
        return message, True

    def close(self):
        """
        Closes the channel.
        :raises ChannelClosedException if it is called on a closed channel
        """
        with self.__cond:
            if self.__closed:
                raise ChannelClosedException("Cannot close a closed channel")
            self.__closed = True
            self.__cond.notifyAll()
