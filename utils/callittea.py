import sqlite3
import feedparser
import re
import json
import logging
from datetime import datetime

import utils.telegram_methods as telm
import utils.jenkins_methods as jenm

class callittea(object):
    ''' Основной класс '''

    def __init__(self, config_file = None, no_jenkins = 0, no_telegram = 0):
        
        logging.basicConfig(
            level=logging.INFO, 
            format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s: %(message)s'
        )

        self._logger = logging.getLogger('callittea')
        self.config = self._params(config_file)

    
    def initial(self):
        # Database
        self.db, self.db_con = self._db_init()

        # Telegram
        self.telegram = telm.telegram(self._get_telegram())

        # Jenkins
        self.jenkins = jenm.jenkins(self._get_jenkins())

        if self._checking_repositories():
            self._logger.info('Update completed!')
            self.db_con.close()
        else:
            self._logger.error('The update is not complete!')
            self.db_con.close()


    def _params(self, config):
        ''' Загрузка файла конфигурации '''

        self._logger.info('Loading configuration...')
        with open(config, 'r') as conf:
            config = json.load(conf)

        return config


    def _get_callittea(self):
        ''' Параметры Callittea '''

        return self.config['callittea']


    def _get_kallithea(self):
        ''' Параметры Kallithea '''

        return self.config['kallithea']


    def _get_telegram(self):
        ''' Параметры Telegram '''

        return self.config['telegram']


    def _get_jenkins(self):
        ''' Параметры Jenkins '''

        return self.config['jenkins']


    def _timestamp(self, date):
        ''' 
            Преобразовать дату в timestamp 
            
            date -- Дата обновления

            d
        '''

        format = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
        return datetime.timestamp(format)

        
    def _db_init(self):
        ''' Подготовка БД приложения ''' 

        app = self._get_callittea()['database']
        repositories = self._get_kallithea()
        
        self._logger.info('Database connection...')
        db_con = sqlite3.connect('{path}/{db}'.format(path = app['path'], db = app['name']))
        db = db_con.cursor()
        for repository in repositories:
            if (repositories[repository]['type'] == 'repository'):
                execdb = db.execute("CREATE TABLE IF NOT EXISTS {table} (id INTEGER PRIMARY KEY, user TEXT, timestamp TEXT NOT NULL, url TEXT NOT NULL, comment TEXT)".format(
                    table = repository
                    ))

        return db, db_con
    

    def _db_add_record(self, table, comment, date, url, user):
        ''' 
            Добавление новой записи в БД приложения 
        
            :param table: Имя таблицы для добавления
            :param comment: Комментарий разработчика
            :param date: Дата обновления
            :param url: Ссылка на список изменений

            :return:
            :rtype:
        '''

        self.db.execute("INSERT INTO '{table}' (user, timestamp, url, comment) VALUES ('{user}', '{timestamp}', '{url}', '{comment}')".format(
            table = table, 
            user = user, 
            timestamp = self._timestamp(date), 
            url = url, 
            comment = comment
            ))
        if self.db_con.commit():
            self._logger.error('Error adding new record to {table}'.format(
                table = table
                ))
            return True
        else:
            self._logger.info('New record by {user} has been added to the {table}'.format(
                user = user,
                table = table
                ))
            return False


    def _db_check_for_existence_record(self, table, date, url):
        ''' Проверка на существование записи в БД приложения '''

        self.db.execute("SELECT * from '{table}' WHERE timestamp='{timestamp}' AND url='{url}'".format(
            table = table,
            timestamp = self._timestamp(date),
            url = url
            ))

        if not self.db.fetchall():
            return True
        else:
            return False


    def _checking_repositories(self):
        ''' Проверка обновлений репозиториев '''

        self._logger.info('Starting update: {instance_name}...'.format(
            instance_name = self._get_callittea()['instance_name']
            ))

        repositories = self._get_kallithea()

        try:
            for repository in repositories:
                if (repositories[repository]['type'] == 'repository'):
                    atom_template = '{url}/feed/atom?api_key={api}'.format(
                        url = repositories[repository]['url'], 
                        api = repositories[repository]['api_key'])
                    feed = self._read_feed(repository, atom_template)
            return True
        except Exception:
            return False


    def _read_feed(self, table, url):
        ''' Загрузка обновлений Atom '''

        self._logger.info('Loading {table} feed...'.format(
            table = table
            ))

        feed = feedparser.parse(url)
        for record in reversed(feed['entries']):
            if self._db_check_for_existence_record(table, record['published'], record['link']):
                # Определение пользователя
                user = self._parser(record['summary'], type = 'user')

                # Добавление в БД
                self._db_add_record(table, record['title'], record['published'], record['link'], user)

                # Отправка задачи в Jenkins
                jobs = self._get_kallithea()[table]['jenkins_jobs']
                for jenkins_job in jobs:
                    if (jenkins_job['user_name'] == user):
                        self._logger.info('Starting Jenkins job: {label} ({job_name})'.format(
                            label = jenkins_job['label'],
                            job_name = jenkins_job['job_name']
                            ))
                        
                        self.jenkins._start_job(job_name = jenkins_job['job_name'])

                        # Отправка оповещения в Telegram
                        self.telegram._new_message('Репозиторий {repository}/{label} был обновлен пользователем {user}. Задача обновления {job_name} запущена.\nИзменения:\n{comment}'.format(
                            repository = table,
                            label = jenkins_job['label'],
                            user = user,
                            job_name = jenkins_job['job_name'],
                            comment = record['title']
                            ))


    def _parser(self, data, type = 'user'):
        ''' 
            Парсер

            :param data: Код страницы
            :param type: Тип парсера (user/tag/branch)

            :return:
            :rtype:
        '''

        result = 'none'

        if (type == 'user'):
            regexp = re.compile(r'.+?(?= committed| выполнил)')
            if regexp.findall(data):
                result = regexp.findall(data)[0]
        elif (type == 'tag'): # работает, но сейчас нет необходимости в реализации
            regexp = re.compile(r'tag: (\S*?)<')
            if regexp.findall(data): 
                result = regexp.findall(data)[0]
        elif (type == 'branch'): # сделаю позже
            pass

        return result
