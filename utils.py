import hashlib

def encrypt_passwd(pwd, vc1, vc2):
    ret = hashlib.md5(pwd).digest()
    ret = hashlib.md5(ret + hexchar2bin(vc12)).hexdigest().upper()
    ret = hashlib.md5(ret + vc1.upper()).hexdigest().upper()
    return ret

def hexchar2bin(s):
    ret = ''
    arr = s.split('\\x')
    for x in arr:
        ret += chr(int(x, 16))
    return ret
