import os
import configs
from webqqclient import *
import gevent
import logging
from gevent.queue import Queue, Empty


class QQBot:
    def __init__(self):
        self._exit = False
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
        count = 0
        while not self._exit:
            if count <= 0:
                self.client.get_group_info()
                count = 7200
                # refresh group info every 2 hour
            else:
                count -= 1
            gevent.sleep(1)

    def _heartbeat(self):
        while True:
            self.client.keep_alive()
            gevent.sleep(60)

    def _poll_msg(self):
        while not self._exit:
            try:
                ret = self.client.poll_msg()
                for msg in ret:
                    self.queue.put(msg)
            except WebQQExit:
                self._exit = True
            except Exception:
                logging.exception('_poll_msg')

    def _chat(self):
        while not self._exit:
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
            except Exception:
                logging.exception('_chat')


if __name__ == '__main__':
    logging.basicConfig(filename = os.path.join(os.getcwd(), 'log.txt'), level = logging.WARN)
    while True:
        logging.warning('Start a qq robot')
        bot = QQBot()
        bot.run()

