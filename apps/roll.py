# -*- coding: UTF-8 -*-

import random

class Roll(object):
    pattern = '-roll\s*\Z'
    def execute(self, msg, qqdata):
        uin = msg['send_uin']
        content = u'{0} 掷出了 {1}'.format(qqdata[uin]['nick'], random.randint(1, 100))
        return content

