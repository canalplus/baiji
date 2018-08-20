#!/usr/bin/python

from aliyunsdkcore.request import CommonRequest
import logging
import json
import traceback
import sys

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

    def request(self, action, params, resource_class):
        request = CommonRequest()
        request.set_domain(self.__domain)
        request.set_version(self.__version)
        request.set_action_name(action)
        try:
            response = self.__client.do_action_with_exception(request)
            logging.debug(response)
            return self.generate_resources(
                json.loads(response), params['key_path'][0],
                params['key_path'][1], resource_class
            )
        except Exception as e:
            logging.error(e)
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])

    def generate_resources(self, response, top_key, res_key, resource_class):
        data = response[top_key][res_key]
        res_list = []
        for res in data:
            res_list.append(resource_class(params=res))
        return res_list

class Resource(object):

    def __init__(self, params=None):
        super(Resource, self).__init__()
        self.__params = params
