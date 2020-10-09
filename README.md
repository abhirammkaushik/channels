# Channels
Implementation of Golang like channels for python.

Channels provide synchronization between multiple threads by populating and depopulating from a common buffer.

#### Import the class Channel to create a new channel
```python
from channel import Channel
```

#### Initialize the channel by giving it a 'type' as input and a size
```python
ch = Channel(int, 10)
```

#### Channels can be unbuffered. 
The second parameter is the buffer capacity of the channel.
Ignoring it will create an unbuffered channel
```python
ch = Channel(int)
```

#### Type of a channel can be custom
Do not give an instantiated object as type
``` python
class Sample:
    def __init__(self):
        pass

ch = Channel(Sample, 10)
```

#### Send a message using send()
The message to be sent across the channel needs to of the same type as the one given during initialization of the channel. 
```python
ch.send(msg)
```
Send is a blocking call if the buffer is at capacity. Unbuffered channels are never blocked on send()


#### Receive a message from the channel using receive()
Receive is also a blocking call if the channel is empty. Receive returns a tuple
```
msg, ok = ch.receive()
```

#### Close a channel to stop it from sending messages using close()
```python
ch.close()
```
Close should always be performed by the sender and never the receiver.
To check whether a channel is closed, you can always call receive().
The second value returned by the channel is False if channel is closed.
```python
msg, ok = ch.receive()
if ok:
    dosomething(msg)
```

Receiving from a closed channel, we get the zero value of a particular type. For custom types, it returns None. In the above example,
if channel was of type 'int', then msg would have the value 0. 
Refer https://docs.python.org/3/library/stdtypes.html#truth-value-testing for zero-values


Performing a send() or a close()  on a closed channel will give rise to an exception

#### Use a For loop to get the messages from a channel
For loop will exit once the channel has been closed
```python
ch = Channel(Sample)
for message in ch:
    #do something
    dosomething()
```

#### Use the channels property 'capacity' to find its capacity
```python
cap = ch.capacity
``` 

## Example
A sample example demonstrating usage of all functions
```python
from channel import Channel
from threading import Thread
from time import sleep


class Sample:
    """ example object to match types in channel"""
    def __init__(self, i):
        self.i = i


def send(ch):
    for i in range(10):
        ch.send(Sample(i))
        print("Sent ", i)
    sleep(6)
    for i in range(10, 20):
        ch.send(Sample(i))
        print("Sent ", i)
    ch.close()


def receive(ch):
    for j in range(10):
        msg, ok = ch.receive()
        if ok:
            print("Received ", msg.i)
        sleep(0.5)
    for i in ch:
        print("Received ", i.i)
    msg, ok = ch.receive()
    if ok:
        # does not print since this channel has been closed
        print(msg.i)
    # prints None
    print("Zero Value: ", msg)

if __name__ == '__main__':

    ch = Channel(Sample, 5)
    print(ch.capacity)
    t = Thread(target=send, args=(ch,))
    t1 = Thread(target=receive, args=(ch,))
    t.start(), t1.start()
    t.join(), t1.join()
```
