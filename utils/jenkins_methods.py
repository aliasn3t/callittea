import jenkins
import logging

class jenkins(object):
    ''' Jenkins класс '''

    def __init__(self, config = None):
        self._logger = logging.getLogger('callittea/jenkins')

        self.url = config['url']
        self.user = config['user']
        self.password = config['password']
        

    def _start_job(self, job_name):
        ''' 
            Запуск сборки
        
            :param job_name: Название джоба
        '''

        self._logger.info('Starting Jenkins job: {job_name}...'.format(
            job_name = job_name
            ))
        worker = jenkins.Jenkins(
            self.url,
            username = self.user,
            password = self.password
            )
        job = worker.build_job(job_name)


    def _status_job(self):
        pass
