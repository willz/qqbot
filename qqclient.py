import requests
import re
from utils import encrypt_passwd
from bs4 import BeautifulSoup

class SmartQQ:
    SMART_QQ_URL = 'http://w.qq.com/login.html'
    def __init__(self):
        self.params = {}
        pass

    def login(self, uid, passwd):
        r = requests.get(self.SMART_QQ_URL)
        soup = BeautifulSoup(r.text)
        ui_login_url = soup.iframe['src']
        # visit this url to get the parameters that we need
        r = requests.get(ui_login_url)
        soup = BeautifulSoup(r.text)
        items = soup.select('.logins input[type="hidden"]') 
        items.extend(soup.select('body > input'))
        for item in items:
            self.params[item["name"]] = item["value"]
        pattern = re.compile("g_pt_version=.*?\"(.*?)\"")
        self.params["js_ver"] = pattern.search(r.text).group(1)
        pattern = re.compile("g_login_sig=.*?\"(.*?)\"")
        self.params["login_sig"] = pattern.search(r.text).group(1)
        # modify some parameters and manually add some parameters
        self.params.update({"action": "0-0-4400", "mibao_css": "m_webqq", "t": "1",
                            "g": "1", "js_type": "0", "uin": uid})
        # check whether we need input validation code
        keys = ("js_ver", "js_type", "login_sig", "u1", "uin")
        payload = {k : self.params[k] for k in keys}
        payload["appid"] = self.params["aid"]
        r = requests.get("https://ssl.ptlogin2.qq.com/check", params = payload)
        pattern = re.complie(".*?'(.*?)'.*?'(.*?)'.*?'(.*?)'")
        m = pattern.search(r.text)
        if m.group(1) == '1':
            # well, need input validation code
            print 'Need validation code'
        vcode = m.group(2)
        self.params["u1"] += "?login2qq={0}&webqq_type={1}".format(self.params["login2qq"], self.params["webqq_type"])
        payload = self.params.copy()
        payload["u"] = payload.pop("uin")
        payload["p"] = encrypt_passwd(passwd, m.group(2), m.group(3))
        

        # visit qrcode url to get the cookies needed for login
        qrcode_url = "https://ssl.ptlogin2.qq.com/ptqrshow?appid={0}&e=0&l=L&s=8&d=72&v=4".format(self.params["aid"])
        r = requests.get(qrcode_url)
        cookies = dict(r.cookies)
        print self.params
        base_url = 'https://ssl.ptlogin2.qq.com/ptqrlogin'
        r = requests.get(base_url, params = self.params, cookies = dict(cookies))
        print r.url
        print r.text

        #print login_url
        #print r.text

if __name__ == '__main__':
    client = SmartQQ()
    client.login("1023343", "fjkdfd")
