# -*- coding: UTF-8 -*-
from datetime import datetime

class GameVote(object):
    pattern = '(?:-ready\s*|-status\s*|-afk\s*)\Z'
    state = {}
    def execute(self, msg, qqdata):
        uin = msg['send_uin']
        content = u''
        if msg['content'][1] == 'r':
            # ready
            content = u'{0} 的大斧已经饥渴难耐!'.format(qqdata[uin]['nick'])
            GameVote.state[uin] = msg['time']
        elif msg['content'][1] == 's':
            # status
            now = datetime.now()
            for k, v in GameVote.state.items():
                diff = (now - datetime.fromtimestamp(v)).seconds
                tips = u''
                if diff < 10:
                    tips = u'刚刚'
                elif diff < 60:
                    tips = str(diff) + u'秒前'
                elif diff < 3600:
                    tips = str(diff / 60) + u'分钟前'
                elif diff < 10800:
                    tips = str(diff / 3600) + u'小时前'
                else:
                    # remove record (3 hours passed)
                    del GameVote.state[k]
                    continue
                content += qqdata[k]['nick'] + ": READY ( " + tips + " )\\r"
            if content == '':
                # no one want to play
                content = u'暂时没人想玩'
        else:
            if uin in GameVote.state:
                del GameVote.state[uin]
            content = u'好了好了，我知道了'
        return content

