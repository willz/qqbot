# -*- coding: UTF-8 -*-

class GameVote(object):
    pattern = '(?:-ready\s*|-status\s*)\Z'
    state = {}
    def execute(self, msg):
        content = u''
        if msg['content'][1] == 'r':
            # ready
            content = u'{0} 的大斧已经饥渴难耐!'.format(msg['send_nick'])
            GameVote.state[msg['send_nick']] = 'READY'
        else:
            # status
            for k, v in GameVote.state.items():
                content += k + ": " + v + "\\r"
        return content

