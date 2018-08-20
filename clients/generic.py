#!/usr/bin/python

from aliyunsdkcore.request import CommonRequest
import logging

class Client(object):

    def __init__(self, client, base_domain='aliyuncs.com', domain_prefix=None, version=None, region='eu-central-1'):
        super(Client, self).__init__()
        self.__client = client
        self.__base_domain = None
        self.__base_domain = base_domain
        self.__domain_prefix = None
        self.__version = None
        if domain_prefix:
            self.__domain_prefix = domain_prefix
        if version:
            self.__version = version
        self.__region = region
        # you have to define the full domain in the child classes
        # it should __domain_prefix + [ __region +] __base_domain
        self.__domain = None

class ResourceCollection(object):

    def __init__(self, client, domain, version):
        super(ResourceCollection, self).__init__()
        self.__client = client
        self.__domain = domain
        self.__version = version

    def create_request(self, action, params=None):
        self.__request = CommonRequest()
        self.__request.set_domain(self.__domain)
        self.__request.set_version(self.__version)
        self.__request.set_action_name(action)

    def send_request(self):
        try:
            response = self.__client.do_action_with_exception(self.__request)
            logging.debug(response)
            return response
        except Exception as e:
            logging.error(e)
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])


class Resource(object):

    def __init__(self, identifier, name):
        super(Resource, self).__init__()
        self.__id = identifier
        self.__name = name
