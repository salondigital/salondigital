import abc

abstractstaticmethod = abc.abstractmethod
class abstractclassmethod(classmethod):

    __isabstractmethod__ = True

    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable)

class UploaderError(Exception):
    pass

class Uploader(object):
    __metaclass__ = abc.ABCMeta
    name = ''

    @abc.abstractmethod
    def upload_log(self, log):
        '''
        
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def send_email(self, email, results):
        '''
        
        '''
        raise NotImplementedError
