import random

class Roll(object):
    pattern = '-roll\s*'
    def execute(self, msg):
        content = u'{0} 掷出了 {1}'.format('xx', random.randint(1, 100))

