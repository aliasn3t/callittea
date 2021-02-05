import urllib3
import logging

class callTelegram(object):
    ''' Telegram класс '''

    def __init__(self, config = None):
        self._logger = logging.getLogger('callittea/telegram')

        self.key = config['bot_key']
        self.chat = config['chat_id']


    def _new_message(self, message):
        ''' 
            Отправка сообщения в чат 
        
            :param message: Текст сообщения
        '''

        self._logger.info('Sending message...')
        # Потом прикрутить прокси (опционально)
        pool = urllib3.PoolManager()
        request = pool.request('GET', 'https://api.telegram.org/bot{key}/sendMessage?chat_id={chat_id}&text={message}'.format(
            key = self.key,
            chat_id = self.chat,
            message = message
            ))
