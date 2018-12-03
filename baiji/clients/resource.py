#!/usr/bin/python

from generic import Client as GenericClient
from generic import Resource, ResourceCollection

class Client(GenericClient):

    def __init__(self, client, domain_prefix="ecs", version="2014-05-26", protocol=None, region=None):
        if region:
            super(Client, self).__init__(
                client, domain_prefix=domain_prefix, version=version, protocol=protocol, region=region
            )
        else:
            super(Client, self).__init__(
                client, domain_prefix=domain_prefix, protocol=protocol, version=version
            )
        self.__domain = "{}.{}.{}".format(
            self.__domain_prefix,
            self.__region,
            self.__base_domain
        )
        self.instances = Instances(client, self.__domain, self.__version, None)
        self.security_groups = SecurityGroups(client, self.__domain, self.__version, None)
        self.tags = Tags(client, self.__domain, self.__version, None)
        self.images = Images(client, self.__domain, self.__version, None)
        self.vpcs = Vpcs(client, self.__domain, self.__version, None)
        self.vswitches = Vswitches(client, self.__domain, self.__version, None)
        self.roles = Roles(client, "ram.{}".format(self.__base_domain), "2015-05-01", "https")
        self.users = Users(client, "ram.{}".format(self.__base_domain), "2015-05-01", "https")
        self.groups = Groups(client, "ram.{}".format(self.__base_domain), "2015-05-01", "https")
        self.disks = Disks(client, self.__domain, self.__version, None)


class Instances(ResourceCollection):

    def __init__(self, client, domain, version, protocol):
        self.__resource_class = Instance
        super(Instances, self).__init__(client, domain, version, protocol)

    def all(self, json_format=False):
        if json_format:
            req = {}
        else:
            req = {
                'key_path': [
                    "Instances", "Instance"
                ]
            }
        response = self.request(
            "DescribeInstances",
            req,
            self.__resource_class
        )
        return response

    def get(self, filters, json_format=False):
        if json_format:
            req = {'api_params': filters}
        else:
            req = {
                'key_path': [
                    "Instances", "Instance"
                ],
                'api_params': filters,  
            }
        response = self.request(
            "DescribeInstances",
            req,
            self.__resource_class
        )
        return response

    def start(self, filters):
        response = self.request(
            "StartInstance",
            {
                'api_params': filters,
            },
            self.__resource_class
        )
        return response

    def stop(self, filters):
        response = self.request(
            "StopInstance",
            {
                'api_params': filters,
            },
            self.__resource_class
        )
        return response


class Instance(Resource):

    def __init__(self, params):
        super(Instance, self).__init__(params)


class SecurityGroups(ResourceCollection):

    def __init__(self, client, domain, version, protocol):
        self.__resource_class = SecurityGroup
        super(SecurityGroups, self).__init__(client, domain, version, protocol)

    def all(self, json_format=False):
        if json_format:
            req = {}
        else:
            req = {
                'key_path': [
                    "SecurityGroups", "SecurityGroup"
                ]
            }
        response = self.request(
            "DescribeSecurityGroups",
            req,
            self.__resource_class
        )
        return response

    def get(self, filters, json_format=False):
        if json_format:
            req = {'api_params': filters}
        else:
            req = {
                'key_path': [
                    "SecurityGroups", "SecurityGroup"
                ],
                'api_params': filters,
            }
        response = self.request(
            "DescribeSecurityGroups",
            req,
            self.__resource_class
        )
        return response


class SecurityGroup(Resource):

    def __init__(self, params):
        super(SecurityGroup, self).__init__(params)


class Tags(ResourceCollection):

    def __init__(self, client, domain, version, protocol):
        self.__resource_class = Tag
        super(Tags, self).__init__(client, domain, version, protocol)

    def all(self, json_format=False):
        if json_format:
            req = {}
        else:
            req = {
                'key_path': [
                    "Tags", "Tag"
                ]  
            }
        response = self.request(
            "DescribeTags",
            req,
            self.__resource_class
        )
        return response

    def get(self, filters, json_format=False):
        if json_format:
            req = {'api_params': filters}
        else:
            req = {
                'key_path': [
                    "Tags", "Tag"
                ],
                'api_params': filters,
            }
        response = self.request(
            "DescribeTags",
            req,
            self.__resource_class
        )
        return response

    def add(self, params):
        response = self.request(
            "AddTags",
            {
                'api_params': params,
            },
            self.__resource_class
        )
        return response

    def remove(self, params):
        response = self.request(
            "RemoveTags",
            {
                'api_params': params,
            },
            self.__resource_class
        )
        return response


class Tag(Resource):

    def __init__(self, params):
        super(Tag, self).__init__(params)


class Images(ResourceCollection):

    def __init__(self, client, domain, version, protocol):
        self.__resource_class = Image
        super(Images, self).__init__(client, domain, version, protocol)

    def all(self, json_format=False):
        if json_format:
            req = {}
        else:
            req = {
                'key_path': [
                    "Images", "Image"
                ]
            }
        response = self.request(
            "DescribeImages",
            req,
            self.__resource_class
        )
        return response

    def get(self, filters, json_format=False):
        if json_format:
            req = {'api_params': filters}
        else:
            req = {
                'key_path': [
                    "Images", "Image"
                ],
                'api_params': filters,
            }
        response = self.request(
            "DescribeImages",
            req,
            self.__resource_class
        )
        return response

    def delete(self, params, json_format=False):
        if json_format:
            req = {'api_params': params}
        else:
            req= {
                'key_path': [
                    "Images", "Image"
                ],
                'api_params': params,
            }
        response = self.request(
            "DeleteImage",
            req,
            self.__resource_class
        )
        return response

    def copy(self, params):
        response = self.request(
            "CopyImage",
            {
                'api_params': params,
            },
            self.__resource_class
        )
        return response

    def share_permission(self, params):
        response = self.request(
            "ModifyImageSharePermission",
            {
                'api_params': params,
            },
            self.__resource_class
        )
        return response

    def modify_image_attribute(self, params):
        response = self.request(
            "ModifyImageAttribute",
            {
                'api_params': params,
            },
            self.__resource_class
        )
        return response


class Image(Resource):
    def __init__(self, params):
        super(Image, self).__init__(params)


class Vpcs(ResourceCollection):
    def __init__(self, client, domain, version, protocol):
        self.__resource_class = Vpc
        super(Vpcs, self).__init__(client, domain, version, protocol)

    def all(self, json_format=False):
        if json_format:
            req = {}
        else:
            req = {
                'key_path': [
                    "Vpcs", "Vpc"
                ]  
            }
        response = self.request(
            "DescribeVpcs",
            req,
            self.__resource_class
        )
        return response

    def get(self, filters, json_format=False):
        if json_format:
            req = {'api_params': filters}
        else:
            req = {
                'key_path': [
                    "Vpcs", "Vpc"
                ],
                'api_params': filters,
            }
        response = self.request(
            "DescribeVpcs",
            req,
            self.__resource_class
        )
        return response


class Vpc(Resource):
    def __init__(self, params):
        super(Vpc, self).__init__(params)


class Vswitches(ResourceCollection):
    def __init__(self, client, domain, version, protocol):
        self.__resource_class = Vswitch
        super(Vswitches, self).__init__(client, domain, version, protocol)

    def all(self, json_format=False):
        if json_format:
            req = {}
        else:
            req = {
                'key_path': [
                    "VSwitches", "VSwitch"
                ]  
            }
        response = self.request(
            "DescribeVSwitches",
            req,
            self.__resource_class
        )
        return response

    def get(self, filters, json_format=False):
        if json_format:
            req = {'api_params': filters}
        else:
            req = {
                'key_path': [
                    "VSwitches", "VSwitch"
                ],
                'api_params': filters,
            }
        response = self.request(
            "DescribeVSwitches",
            req,
            self.__resource_class
        )
        return response


class Vswitch(Resource):
    def __init__(self, params):
        super(Vswitch, self).__init__(params)


class Roles(ResourceCollection):
    def __init__(self, client, domain, version, protocol):
        self.__resource_class = Role
        super(Roles, self).__init__(client, domain, version, protocol)

    def all(self, json_format=False):
        if json_format:
            req = {}
        else:
            req = {
                'key_path': [
                    "Roles", "Role"
                ]
            }
        response = self.request(
            "ListRoles",
            req, 
            self.__resource_class
        )
        return response

    def get(self, filters, json_format=False):
        if json_format:
            req = {'api_params': filters}
        else:
            req = {
                'key_path': [
                    "Role", None
                ],
                'api_params': filters,
            }
        response = self.request(
            "GetRole",
            req,
            self.__resource_class
        )
        return response

    def assume(self, params, json_format=False):
        if json_format:
            req = {'api_params': params}
        else:
            req = {
                'key_path': [
                    "AssumedRoleUser", None
                ],
                'api_params': params, 
            }
        response = self.request(
            "AssumeRole",
            req,
            self.__resource_class
        )
        return response
    

class Role(Resource):
    def __init__(self, params):
        super(Role, self).__init__(params)


class Users(ResourceCollection):
    def __init__(self, client, domain, version, protocol):
        self.__resource_class = User
        super(Users, self).__init__(client, domain, version, protocol)

    def all(self, json_format=False):
        if json_format:
            req = {}
        else: 
            req = {
               'key_path': [
                    "Users", "User"
                ]
            }
        response = self.request(
            "ListUsers",
            req,
            self.__resource_class
        )
        return response


class User(Resource):
    def __init__(self, params):
        super(User, self).__init__(params)


class Groups(ResourceCollection):
    def __init__(self, client, domain, version, protocol):
        self.__resource_class = Group
        super(Groups, self).__init__(client, domain, version, protocol)

    def all(self, json_format=False):
        if json_format:
            req = {}
        else:
            req = {

                'key_path': [
                    "Groups", "Group"
                ]  
            }
        response = self.request(
            "ListGroups",
            req,
            self.__resource_class
        )
        return response


class Group(Resource):
    def __init__(self, params):
        super(Group, self).__init__(params)


class Disks(ResourceCollection):
    def __init__(self, client, domain, version, protocol):
        self.__resource_class = Disk
        super(Disks, self).__init__(client, domain, version, protocol)

    def all(self, json_format=False):
        if json_format:
            req = {}
        else:
            req = {
                'key_path': [
                    "Disks", "Disk"
                ]  
            }
        response = self.request(
            "DescribeDisks",
            req,
            self.__resource_class
        )
        return response

    def get(self, filters, json_format=False):
        if json_format:
            req = {'api_params': filters}
        else:
            req = {
                'key_path': [
                    "Disks", "Disk"
                ],
                'api_params': filters,
            }
        response = self.request(
            "DescribeDisks",
            req,
            self.__resource_class
        )
        return response


class Disk(Resource):
    def __init__(self, params):
        super(Disk, self).__init__(params)