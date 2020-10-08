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
    ch.close()


def receive_integers(ch):
    for idx, i in enumerate(ch):
        print("Received ", i.i, len(ch))
        sleep(0.5)


if __name__ == '__main__':

    ch = Channel(D, 5)
    t = Thread(target=send_integers, args=(ch,))
    t1 = Thread(target=receive_integers, args=(ch,))
    t.start(), t1.start()
    t.join(), t1.join()
