import configs
from webqqclient import *
import gevent
from gevent.queue import Queue, Empty


class QQBot:
    def __init__(self):
        self.client = WebQQClient()
        self.queue = Queue()
        self.apps = []
        for app_name in configs.apps:
            # get class from apps dir
            module = __import__("apps.{0}".format(app_name.lower()))
            module = getattr(module, app_name.lower())
            module = getattr(module, app_name)
            self.apps.append(module)
        pass

    def run(self):
        self.client.login(configs.qq, configs.password)
        #self.client.get_group_info()
        thread1 = gevent.spawn(self._update_group_info)
        #thread1 = gevent.spawn(self._heartbeat)
        thread2 = gevent.spawn(self._poll_msg)
        #self._poll_msg()
        thread3 = gevent.spawn(self._chat)

        threads = [thread1, thread2, thread3]
        gevent.joinall(threads)


    def _update_group_info(self):
        while True:
            self.client.get_group_info()
            # refresh group info every 2 hour
            gevent.sleep(7200)

    def _heartbeat(self):
        while True:
            self.client.keep_alive()
            gevent.sleep(60)

    def _poll_msg(self):
        while True:
            try:
                ret = self.client.poll_msg()
                for msg in ret:
                    self.queue.put(msg)
            except Exception as e:
                print e

    def _chat(self):
        while True:
            try:
                msg = self.queue.get(timeout = 1)
                if msg['type'] != 'group_message':
                    continue
                for app in self.apps:
                    pat = re.compile(app.pattern)
                    if pat.match(msg['content']):
                        gid = msg['from_uin']
                        content = app().execute(msg, self.client.groups[gid]['minfo'])
                        self.client.send_group_msg(gid, content)
                        break
            except Empty:
                pass
            except Exception as e:
                print e


if __name__ == '__main__':
    bot = QQBot()
    bot.run()

