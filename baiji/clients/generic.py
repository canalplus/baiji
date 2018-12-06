#!/usr/bin/python

from aliyunsdkcore.request import CommonRequest
import logging
import json
import traceback
import sys


class Client(object):

    def __init__(self, client, base_domain='aliyuncs.com', domain_prefix=None, version=None, protocol=None, region='eu-central-1'):
        super(Client, self).__init__()
        self.__client = client
        self.__base_domain = base_domain
        self.__domain_prefix = domain_prefix
        self.__version = version
        self.__region = region
        self.__protocol = protocol
        # you have to define the full domain in the child classes
        # it should __domain_prefix + [ __region +] __base_domain
        self.__domain = None

class ResourceCollection(object):

    def __init__(self, client, domain, version, protocol):
        super(ResourceCollection, self).__init__()
        self.__client = client
        self.domain = domain
        self.version = version
        self.protocol = protocol

    def request(self, action, params, resource_class):
        request = CommonRequest()

        if action == "AssumeRole":
            self.domain = self.domain.replace("ram.", "sts.")
            self.version = "2015-04-01"

        request.set_domain(self.domain)
        request.set_version(self.version)
        request.set_action_name(action)
        request.set_accept_format('json')
        if self.protocol:
            request.set_protocol_type (self.protocol)
        if 'api_params' in params and params['api_params']:
            request.set_query_params(params['api_params'])
        try:
            response = self.__client.do_action_with_exception(request)
            #logging.debug(response)
            if 'key_path' in params and params['key_path']:
                return self.generate_resources(
                    json.loads(response), params['key_path'][0],
                    params['key_path'][1], resource_class
                )
            else:
                return json.loads(response)
        except Exception as e:
            logging.error(e)
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])
            raise e

    def generate_resources(self, response, top_key, res_key, resource_class):
        if res_key:
            data = response[top_key][res_key]
        else:
            data = response[top_key]
            if isinstance (data, list):
                data = data
            else:
                data = [data]
        res_list = []
        for res in data:
            res_list.append(resource_class(params=res))
        return res_list

class Resource(object):

    def __init__(self, params=None):
        super(Resource, self).__init__()
        self.__params = params

        for name, value in self.__params.items():
            setattr(self, name, value)