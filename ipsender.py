import os
import json
import requests
import logging
from logging.handlers import RotatingFileHandler


class IpSender:
    def __init__(self, c_file):
        with open(c_file, 'r', encoding='utf-8') as c:
            self.config = json.loads(c.read())
        self.logger = self.init_log(self.config)
        self.token = self.config['token']
        self.chat_id = self.config['chat_id']
        self.init_proxy(self.config)
        self.url = "https://botapi.tamtam.chat/"

    def run(self):
        while True:
            try:
                response = self.get_updates()
                if response['updates']:
                    chat_id = response['updates'][0]['message']['recipient']['chat_id']
                    if chat_id == self.chat_id:
                        ip = self.get_ip()
                        self.send_message(ip, chat_id=self.chat_id)
            except Exception as e:
                self.logger.exception(e)

    def get_ip(self):
        try:
            ip = requests.get('https://api.ipify.org', verify=False).text
        except Exception as e:
            self.logger.exception(e)
            return 'Was errors, see sender_log.txt!'
        return ip

    def init_proxy(self, config):
        try:
            if config['http_proxy']:
                os.environ['http_proxy'] = config['http_proxy']
        except IndexError as e:
            self.logger.exception(e)
        try:
            if config['https_proxy']:
                os.environ['https_proxy'] = config['https_proxy']
        except IndexError as e:
            self.logger.exception(e)

    @staticmethod
    def init_log(config):
        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        handler = RotatingFileHandler(config['log_file'], mode='a', maxBytes=5000000, backupCount=5)
        handler.setFormatter(formatter)
        logger = logging.getLogger(__name__)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        return logger

    def get_updates(self):
        params = {"timeout": 90,
                  "limit": 1000,
                  "marker": None,
                  "types": None,
                  "access_token": self.token}
        try:
            response = requests.get(self.url + 'updates', params)
            return response.json()
        except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError) as e:
            logging.exception(e)
        return None

    def send_message(self, text, chat_id=None, notify=True):
        """
        send message to specific user_id and chat_id
        :param text: text of message
        :param chat_id:
        :param notify: if false, chat participants wouldn't be notified
        :return:
        """
        url = ''.join([self.url, 'messages?access_token=', self.token])
        if chat_id:
            url += '&chat_id={}'.format(chat_id)
        params = {"text": text, "notify": notify}
        response = requests.post(url, data=json.dumps(params))
        if response.status_code != 200:
            self.logger.info("Response status code: {}".format(response.status_code))

    def run_once(self):
        ip = self.get_ip()
        self.send_message(ip, self.chat_id)


if __name__ == '__main__':
    sender = IpSender('config.json')
    sender.run_once()