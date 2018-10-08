#!/usr/bin/python

from generic import Client as GenericClient
from generic import Resource, ResourceCollection

class Client(GenericClient):

    def __init__(self, client, region=None):
        default_version = "2014-05-26"
        default_domain_prefix = 'ecs'
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
        self.instances = Instances(client, self.__domain, self.__version)
        self.security_groups = SecurityGroups(client, self.__domain, self.__version)
        self.tags = Tags(client, self.__domain, self.__version)
        self.images = Tags(client, self.__domain, self.__version)

class Instances(ResourceCollection):

    def __init__(self, client, domain, version):
        self.__resource_class = Instance
        super(Instances, self).__init__(client, domain, version)

    def all(self):
        response = self.request(
            "DescribeInstances",
            {
                'key_path': [
                    "Instances", "Instance"
                ]
            },
            self.__resource_class
        )
        return response

    def get(self, filters):
        response = self.request(
            "DescribeInstances",
            {
                'key_path': [
                    "Instances", "Instance"
                ],
                'api_params': filters,
            },
            self.__resource_class
        )
        return response

class Instance(Resource):

    def __init__(self, params):
        super(Instance, self).__init__(params)


class SecurityGroups(ResourceCollection):

    def __init__(self, client, domain, version):
        self.__resource_class = SecurityGroup
        super(SecurityGroups, self).__init__(client, domain, version)

    def all(self):
        response = self.request(
            "DescribeSecurityGroups",
            {
                'key_path': [
                    "SecurityGroups", "SecurityGroup"
                ]
            },
            self.__resource_class
        )
        return response

    def get(self, filters):
        response = self.request(
            "DescribeSecurityGroups",
            {
                'key_path': [
                    "SecurityGroups", "SecurityGroup"
                ],
                'api_params': filters,
            },
            self.__resource_class
        )
        return response

class SecurityGroup(Resource):

    def __init__(self, params):
        super(SecurityGroup, self).__init__(params)


class Tags(ResourceCollection):

    def __init__(self, client, domain, version):
        self.__resource_class = Tag
        super(Tags, self).__init__(client, domain, version)

    def all(self):
        response = self.request(
            "DescribeTags",
            {
                'key_path': [
                    "Tags", "Tag"
                ]
            },
            self.__resource_class
        )
        return response

    def get(self, filters):
        response = self.request(
            "DescribeTags",
            {
                'key_path': [
                    "Tags", "Tag"
                ],
                'api_params': filters,
            },
            self.__resource_class
        )
        return response

    def add_tags(self, filters):
        response = self.request(
            "AddTags",
            {
                'key_path': [
                    "Tags", "Tag"
                ],
                'api_params': filters,
            },
            self.__resource_class
        )
        return response

    def remove_tags(self, filters):
        response = self.request(
            "RemoveTags",
            {
                'key_path': [
                    "Tags", "Tag"
                ],
                'api_params': filters,
            },
            self.__resource_class
        )
        return response

class Tag(Resource):

    def __init__(self, params):
        super(Tag, self).__init__(params)


class Images(ResourceCollection):

    def __init__(self, client, domain, version):
        self.__resource_class = Image
        super(Images, self).__init__(client, domain, version)

    def all(self):
        response = self.request(
            "DescribeImages",
            {
                'key_path': [
                    "Images", "Image"
                ]
            },
            self.__resource_class
        )
        return response

    def get(self, filters):
        response = self.request(
            "DescribeImages",
            {
                'key_path': [
                    "Images", "Image"
                ],
                'api_params': filters,
            },
            self.__resource_class
        )
        return response

    def delete(self, filters):
        response = self.request(
            "DeleteImage",
            {
                'key_path': [
                    "Images", "Image"
                ],
                'api_params': filters,
            },
            self.__resource_class
        )
        return response

    def copy(self, filters):
        response = self.request(
            "CopyImage",
            {
                'key_path': [
                    "Images", "Image"
                ],
                'api_params': filters,
            },
            self.__resource_class
        )
        return response

    def modify_image_share_permission(self, filters):
        response = self.request(
            "ModifyImageSharePermission",
            {
                'key_path': [
                    "Images", "Image"
                ],
                'api_params': filters,
            },
            self.__resource_class
        )
        return response

class Image(Resource):

    def __init__(self, params):
        super(Image, self).__init__(params)


