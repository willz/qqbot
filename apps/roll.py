# -*- coding: UTF-8 -*-

import random

class Roll(object):
    pattern = '-roll\s*\Z'
    def execute(self, msg):
        content = u'{0} 掷出了 {1}'.format(msg['send_nick'], random.randint(1, 100))
        return content

