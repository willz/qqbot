import requests
import re
import json
import random
import utils
import configs
import logging
from utils import encrypt_passwd
from gevent import monkey
monkey.patch_all()


class WebQQClient:
    WEBQQ_URL = 'http://web2.qq.com'
    def __init__(self):
        self.s = requests.session()
        self.poll_s = requests.session()
        self.params = {"daid":"164", "appid":"1003903", "js_ver":"10052",
                "js_type":"0", "enable_qlogin":"0", "aid":"1003903", "h":"1",
                "webqq_type":"10", "remember_uin":"1", "login2qq":"1",
                "s_url":self.WEBQQ_URL, "u1":self.WEBQQ_URL + "/loginproxy.html",
                "ptredirect":"0", "ptlang":"2052", "from_ui":"1",
                "pttype":"1", "dumy":"", "fp":"loginerroralert", "t":"1",
                "g":"1", "action":"0-0-4400", "mibao_css":"m_webqq",
                "clientid": str(random.randint(1, 10000000))}
        self.msg_id = utils.Counter()
        self.msg_handler = MessageHandler()
        self.groups = {}
        pass

    def login(self, uid, passwd):
        self.params.update({"u":uid, "uin":uid})
        # get the login signature
        keys = ("daid", "appid", "enable_qlogin", "s_url")
        payload = self._get_subdict(keys)
        r = self.s.get("https://ui.ptlogin2.qq.com/cgi-bin/login", params = payload)
        pattern = re.compile("g_login_sig=.*?\"(.*?)\"")
        self.params["login_sig"] = pattern.search(r.text).group(1)
        print self.params["login_sig"]

        # check whether we need input validation code
        keys = ("uin", "appid", "js_ver", "js_type", "login_sig", "u1")
        payload = self._get_subdict(keys)
        r = self.s.get("https://ssl.ptlogin2.qq.com/check", params = payload)
        print r.text
        pattern = re.compile(".*?'(.*?)'.*?'(.*?)'.*?'(.*?)'")
        m = pattern.search(r.text)
        vcode = m.group(2)
        if m.group(1) == '1':
            # well, need input validation code
            print 'Need validation code'
            url = 'https://ssl.captcha.qq.com/getimage?aid=1003903&r=0.9296404102351516&uin={0}'.format(uid)
            print url
            vcode = raw_input('Input validation code: ')
        self.params["u1"] += "?login2qq={0}&webqq_type={1}".format(self.params["login2qq"], self.params["webqq_type"])
        self.params.update({"verifycode":vcode, "p":encrypt_passwd(passwd, vcode, m.group(3))})

        # login stage 1
        keys = ("u", "p", "verifycode", "webqq_type", "remember_uin", "login2qq", "aid",
                "u1", "h", "ptredirect", "ptlang", "daid", "from_ui", "pttype", "dumy",
                "fp", "action", "mibao_css", "t", "g", "js_type", "js_ver", "login_sig")
        payload = self._get_subdict(keys)
        r = self.s.get("https://ssl.ptlogin2.qq.com/login", params = payload)
        print r.text

        pattern = re.compile(".*?,.*?,.*?'(.*?)'")
        self.s.headers['referer'] = 'http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=2'
        r = self.s.get(pattern.search(r.text).group(1))

        # login stage 2
        payload = {"clientid":self.params["clientid"], "psessionid":"null"}
        r_value = payload.copy()
        r_value.update({"status":"online", "ptwebqq":self.s.cookies["ptwebqq"], "passwd_sig":""})
        payload["r"] = json.dumps(r_value)
        r = self.s.post("http://d.web2.qq.com/channel/login2", data = payload)
        ret = json.loads(r.text)
        print ret
        self.params.update(ret['result'])
        return ret['retcode']

    def poll_msg(self):
        url = 'http://d.web2.qq.com/channel/poll2'
        payload = self._get_subdict(("clientid", "psessionid"))
        r_value = payload.copy()
        r_value.update({'key':0, 'ids':[]})
        payload['r'] = json.dumps(r_value)
        self.s.headers['referer'] = 'http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=3'
        #headers = {'referer': 'http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=3'}
        r = self.s.post(url, data = payload, stream = False)
        #r = self.poll_s.post(url, data = payload, headers = headers)
        ret = json.loads(r.text)
        retcode = ret['retcode']
        msgs = []
        if retcode == 0:
            for info in ret['result']:
                msg = self.msg_handler.produce(info['poll_type'], info['value'])
                msgs.append(msg)
        elif retcode == 102:
            # no message received
            pass
        else:
            # some unknown error
            logging.error('poll_msg error: %s', r.text)
        return msgs

    def get_group_info(self):
        url = 'http://s.web2.qq.com/api/get_group_name_list_mask2'
        payload = {'vfwebqq': self.params['vfwebqq']}
        self.s.headers['referer'] =  'http://s.web2.qq.com/proxy.html?v=20110412001&callback=1&id=1'
        r = self.s.post(url, data = payload)
        ret = json.loads(r.text)
        self.groups = { g['gid']: g for g in ret['result']['gnamelist'] }
        url = 'http://s.web2.qq.com/api/get_group_info_ext2'
        for group in self.groups.values():
            payload = {'gcode': group['code'], 'vfwebqq': self.params['vfwebqq'], 't': utils.ctime()}
            self.s.headers['referer'] = 'http://s.web2.qq.com/proxy.html?v=20110412001&callback=1&id=1'
            r = self.s.get(url, params = payload)
            ret = json.loads(r.text)
            # member info
            group['minfo'] = {}
            for m in ret['result']['minfo']:
                group['minfo'][m['uin']] = {'nick': m['nick'], 'qq': self.get_qq_from_uin(m['uin'])}
        print self.groups

    def send_group_msg(self, gid, msg):
        url = 'http://d.web2.qq.com/channel/send_qun_msg2'
        payload = self._get_subdict(("clientid", "psessionid"))
        r_value = payload.copy()
        style = json.dumps(configs.font)
        r_value.update({'group_uin': gid, 'msg_id': self.msg_id.get(),
                        'content': u'''["{0}", {1}]'''.format(msg, style)})
        payload['r'] = json.dumps(r_value)
        self.s.headers['referer'] = 'http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=3'
        r = self.s.post(url, data = payload)
        ret = json.loads(r.text)
        if ret['retcode'] != 0:
            # send group message eror
            logging.error('send_group_msg error: %s , form data: %s', r.text, payload)

    def get_qq_from_uin(self, uin):
        url = 'http://s.web2.qq.com/api/get_friend_uin2'
        payload = {'tuin': uin, 'type': 1, 'vfwebqq': self.params['vfwebqq'], 't': utils.ctime(),
                   'verifysession': '', 'code': ''}
        self.s.headers['referer'] = 'http://s.web2.qq.com/proxy.html?v=20110412001&callback=1&id=1'
        r = self.s.get(url, params = payload)
        ret = json.loads(r.text)
        return ret['result']['account']


    def keep_alive(self):
        url = 'http://web2.qq.com/web2/get_msg_tip?uin=&tp=1&id=0&retype=1&rc=150&lv=3&t=' + utils.ctime()
        r = self.s.get(url)

    # get subdict from keys
    def _get_subdict(self, keys):
        return {k:self.params[k] for k in keys}

class MessageHandler:
    def __init__(self):
        pass

    def produce(self, type, msg):
        # TODO currently we only produce group message object
        ret = {'type': type}
        if type == 'group_message':
            ret['from_uin'] = msg['from_uin']
            ret['send_uin'] = msg['send_uin']
            ret['time'] = msg['time']
            ret['content'] = self._join_msg(msg['content'][1:])
        return ret

    def _join_msg(self, arr):
        ret = ''.join(map(
            lambda item: '[face:' + str(item[1]) + ']' if isinstance(item, list) else item,
            arr))
        return ret

if __name__ == '__main__':
    client = WebQQClient()
    client.get_group_info()
