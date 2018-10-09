#!/usr/bin/python

from generic import Client as GenericClient
from generic import Resource, ResourceCollection

class vpcClient(GenericClient):

    def __init__(self, client, region=None):
        default_version = "2014-05-26"
        default_domain_prefix = 'vpc'
        if region:
            super(Client, self).__init__(
                client, domain_prefix=default_domain_prefix, version=default_version, region=region
            )
        else:
            super(Client, self).__init__(
                client, domain_prefix=default_domain_prefix, version=default_version
            )
        self.__domain = "{}.{}.{}".format(
            self.__domain_prefix,
            self.__region,
            self.__base_domain
        )
        self.vpcs = Instances(client, self.__domain, self.__version)

class Vpcs(ResourceCollection):

    def __init__(self, client, domain, version):
        self.__resource_class = Instance
        super(Vpcs, self).__init__(client, domain, version)

    def all(self):
        response = self.request(
            "DescribeVpcs",
            {
                'key_path': [
                    "Vpcs", "Vpc"
                ]
            },
            self.__resource_class
        )
        return response

    def get(self, filters):
        response = self.request(
            "DescribeVpcs",
            {
                'key_path': [
                    "Vpcs", "Vpc"
                ],
                'api_params': filters,
            },
            self.__resource_class
        )
        return response

class Vpc(Resource):

    def __init__(self, params):
        super(Instance, self).__init__(params)


class Vswitches(ResourceCollection):

    def __init__(self, client, domain, version):
        self.__resource_class = Vswitch
        super(Vswitches, self).__init__(client, domain, version)

    def all(self):
        response = self.request(
            "DescribeVSwitches",
            {
                'key_path': [
                    "Vswitches", "Vswitch"
                ]
            },
            self.__resource_class
        )
        return response

    def get(self, filters):
        response = self.request(
            "DescribeVSwitches",
            {
                'key_path': [
                    "Vswitches", "Vswitch"
                ],
                'api_params': filters,
            },
            self.__resource_class
        )
        return response

class Vswitch(Resource):

    def __init__(self, params):
        super(Vswitch, self).__init__(params)