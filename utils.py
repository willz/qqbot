import sys
import hashlib
import time
import random

def encrypt_passwd(pwd, vc1, vc2):
    ret = hashlib.md5(pwd).digest()
    ret = hashlib.md5(ret + hexchar2bin(vc2)).hexdigest().upper()
    ret = hashlib.md5(ret + vc1.upper()).hexdigest().upper()
    return ret

def hexchar2bin(s):
    print 's', s
    ret = ''
    arr = s.split('\\x')
    for x in arr[1:]:
        ret += chr(int(x, 16))
    return ret

def ctime():
    return str(int(time.time()))

class Counter:
    def __init__(self):
        self.count = random.randint(0, 10000000)

    def get(self):
        self.count += 1
        return self.count
