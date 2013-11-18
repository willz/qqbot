import requests
import re
from bs4 import BeautifulSoup

class SmartQQ:
    SMART_QQ_URL = 'http://w.qq.com/login.html'
    def __init__(self):
        pass

    def login(self, uid, passwd):
        r = requests.get(self.SMART_QQ_URL)
        soup = BeautifulSoup(r.text)
        ui_login_url = soup.iframe['src']
        # visit this url to get the parameters that we need
        r = requests.get(ui_login_url)
        soup = BeautifulSoup(r.text)
        payload = dict()
        items = soup.select('.logins input[type="hidden"]') 
        items.extend(soup.select('body > input'))
        for item in items:
            payload[item["name"]] = item["value"]
        pattern = re.compile("g_pt_version=.*?\"(.*?)\"")
        payload["js_ver"] = pattern.search(r.text).group(1)
        pattern = re.compile("g_login_sig=.*?\"(.*?)\"")
        payload["login_sig"] = pattern.search(r.text).group(1)
        keys = ("js_ver", "login_sig", "u1")
        tmp = {k : payload[k] for k in keys}
        tmp["uin"] = uid
        tmp["appid"] = payload["aid"]
        tmp["js_type"] = "0"
        r = requests.get("https://ssl.ptlogin2.qq.com/check", params = tmp)
        print r.text
        # modify some parameters and manually add some parameters
        # visit qrcode url to get the cookies needed for login
        qrcode_url = "https://ssl.ptlogin2.qq.com/ptqrshow?appid={0}&e=0&l=L&s=8&d=72&v=4".format(payload["aid"])
        r = requests.get(qrcode_url)
        cookies = dict(r.cookies)
        print payload
        base_url = 'https://ssl.ptlogin2.qq.com/ptqrlogin'
        r = requests.get(base_url, params = payload, cookies = dict(cookies))
        print r.url
        print r.text

        #print login_url
        #print r.text

if __name__ == '__main__':
    client = SmartQQ()
    client.login("2713640347", "fjkdfd")
