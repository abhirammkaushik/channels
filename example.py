from channel import Channel
from threading import Thread
from time import sleep


class D:
    """ example object to match types in channel"""
    def __init__(self, i):
        self.i = i


def send_integers(ch):
    for i in range(10):
        ch.send(D(i))
        print("Sent ", i)
    sleep(10)
    for i in range(10, 20):
        ch.send(D(i))
        print("Sent ", i)
    ch.close()


def receive_integers(ch):
    for j in range(10):
        msg, ok = ch.receive()
        if ok:
            print("Received ", msg.i)
        sleep(0.5)
    for i in ch:
        print("Received ", i.i)
    msg, ok = ch.receive()
    if ok:
        print(msg.i)


if __name__ == '__main__':

    ch = Channel(D, 5)
    t = Thread(target=send_integers, args=(ch,))
    t1 = Thread(target=receive_integers, args=(ch,))
    t.start(), t1.start()
    t.join(), t1.join()
