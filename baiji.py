#!/usr/bin/python

from aliyunsdkcore import request as aliyun_request
from aliyunsdkcore.http import protocol_type
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException

from aliyunsdkcore.request import CommonRequest
from aliyunsdkecs.request.v20140526 import StartInstanceRequest
from aliyunsdkecs.request.v20140526 import StopInstanceRequest
from aliyunsdkcore.auth.credentials import StsTokenCredential
from aliyunsdkecs.request.v20140526 import DescribeImagesRequest
from aliyunsdkecs.request.v20140526 import DescribeTagsRequest
from aliyunsdkecs.request.v20140526 import DescribeSecurityGroupsRequest
from aliyunsdkecs.request.v20140526 import DescribeVSwitchesRequest
from aliyunsdkecs.request.v20140526 import DeleteImageRequest
from aliyunsdkecs.request.v20140526 import CopyImageRequest


from os import environ
from os import path
import requests
import json
import logging
import traceback
import sys
import os

logging.getLogger().setLevel(logging.INFO)

class AliCloudConnect:
    """
    AliCloudConnect

    Provides root functions and objects to use AliCloud features.
    """

    def __init__(self, account_id=None, role=None, region_id="eu-central-1"):
        """
        Constructor of alicloudConnect.
        
        We will try to connect with env first, config credentials and finally with instance role.
        User will use the AcsClient to deal with aliyun api.
        
        :param account_id:
        :param role:
        """

        # caller will need to pass accessKey, secretKey
        # if stsToken = None / or pass stsToken if it is not none.
        self.__client = None
        self.access_key_id = None
        self.access_key_secret = None
        self.region_id = region_id
        self.sts_token = None
        aliyun_request.set_default_protocol_type(protocol_type.HTTPS)

        # each api has it's own version !
        self.version_2014_05_26 = "2014-05-26"
        self.version_2015_05_01 = "2015-05-01"
        self.version_2015_04_01 = "2015-04-01"

        # endpoint definiton by service
        self.ecs_domain = "ecs.{}.aliyuncs.com".format(self.region_id)
        self.sts_domain = "sts.aliyuncs.com"
        self.ram_domain = "ram.aliyuncs.com"


        access_key_id = ''
        access_key_secret = ''

        connect_with_credential = False
        connect_with_role = False
        config_file = path.expanduser('~') + "/.aliyun/config.json"
        logging.info('Connection to Alicloud.')
        
        if 'ALICLOUD_ACCESS_KEY' in environ:
            logging.info('Trying to connect with credentials from environment.')
            access_key_id = environ['ALICLOUD_ACCESS_KEY']
            if 'ALICLOUD_SECRET_KEY' in environ:
                access_key_secret = environ['ALICLOUD_SECRET_KEY']
                connect_with_credential = True
                self.access_key_id = access_key_id
                self.access_key_secret = access_key_secret

            else:
                logging.info('Both access ALICLOUD_ACCESS_KEY and secret ALICLOUD_SECRET_KEY are mandatory.')

        elif path.exists(config_file):
            logging.info('Trying to connect with config credentials.')
            config = json.load(open(config_file))
            access_key_id = config['profiles'][1]['access_key_id']
            access_key_secret = config['profiles'][1]['access_key_secret']
            region_id = config['profiles'][1]['region_id']
            connect_with_credential = True
            self.access_key_id = access_key_id
            self.access_key_secret = access_key_secret

        elif account_id is not None and role is not None:
            logging.info('Trying to connect with instance role.')
            response = requests.get('http://100.100.100.200/latest/meta-data/ram/security-credentials/%s' % role, timeout=5).json()

            sts_access_key = response['AccessKeyId']
            sts_secret_key = response['AccessKeySecret']
            sts_token_session = response['SecurityToken']

            self.access_key_id = sts_access_key
            self.access_key_secret = sts_secret_key
            connect_with_role = True

        else:
            logging.error('No valid connection type provided.')

        try:
            if connect_with_credential:
                self.__client = AcsClient(access_key_id, access_key_secret, region_id)

            elif connect_with_role:
                sts_token_credential = StsTokenCredential(sts_access_key,
                                                          sts_secret_key,
                                                          sts_token_session)
                self.sts_token = sts_token_credential
                self.__client = AcsClient(region_id=self.region_id, credential=sts_token_credential)

        except Exception as e:
            logging.error(e)
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])

    def client(self, client_name):
        try:
            client = __import__("clients.ecs")
            mod = getattr(client, client_name)
            clt_class = getattr(mod, "Client")
            return clt_class(
                self.__client
            )
        except Exception as e:
            logging.error(e)
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])

    def pretty_print(self, toprint):
        print json.dumps(json.loads(toprint), indent=4, sort_keys=True)

    def get_accesskey(self):
        return self.access_key_id

    def get_secretkey(self):
        return self.access_key_secret

    def get_ststoken(self):
        return self.sts_token

    def assume_role(self, role_arn, session_name):
        '''
        assume_role

        This function will try to assume a role. and will set StsToken of the constructor if OK.
        User will need to give this token when calling aliyun api.

        Example of use
            ali_connect = AliCloudConnect()
            ali_connect.assume_role("acs:ram::<<account_ID>>:role/ecsadmin", "test")
            sts = ali_connect.get_ststoken()
            ali_connect.stop_instances ....

        :param role_arn:
        :param session_name:
        :return:
        '''

        logging.info("Going to assume role:  {} sessionName: {}".format(role_arn, session_name))
        request = CommonRequest()
        request.set_domain(self.sts_domain)
        request.set_version(self.version_2015_04_01)
        request.add_query_param("RoleArn", role_arn)
        request.add_query_param("RoleSessionName", session_name)
        request.set_action_name('AssumeRole')
        try:
            response = json.loads(self.__client.do_action_with_exception(request))
            sts_access_key = response['Credentials']['AccessKeyId']
            sts_secret_key = response['Credentials']['AccessKeySecret']
            sts_token_session = response['Credentials']['SecurityToken']
            self.sts_token = StsTokenCredential(
                sts_access_key, sts_secret_key, sts_token_session
            )

            return response
        except Exception as e:
            logging.error(e)
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])

    ###############################
    ############ECS################
    ###############################

    def describe_instances(self):
        """
        Describe instances.

        Example of call :
            ali_connect = AliCloudConnect()
            ali_connect.describe_instances()

        :return:
        """
        logging.info('Going to describe all instances.')

        request = CommonRequest()
        request.set_domain(self.ecs_domain)
        request.set_version(self.version_2014_05_26)
        request.set_action_name('DescribeInstanceStatus')

        try:
            response = self.__client.do_action_with_exception(request)
            self.pretty_print(response)
        except Exception as e:
            logging.error(e)
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])


    def describe_disks(self):
        """
        Describe disks.

        Example of call :
            ali_connect = AliCloudConnect()
            ali_connect.describe_instances()

        :return:
        """
        logging.info('Going to describe all disks.')

        request = CommonRequest()
        request.set_domain(self.ecs_domain)
        request.set_version(self.version_2014_05_26)
        request.set_action_name('DescribeDisks')

        try:
            response = self.__client.do_action_with_exception(request)
            self.pretty_print(response)
        except Exception as e:
            logging.error(e)
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])


    def stop_instances(self, instanceid, sts_token = None):
        """
        Stop Alicloud instances.

        if Ram user have the persmission to do this action we can simply call:
            ali_connect = AliCloudConnect()
            ali_connect.stop_instances('azertyuiop')
        otherwise, user can assume a role to have this privilege
            ali_connect.assume_role("acs:ram:<<account_ID>>:role/ecsadmin", "test")
            sts = ali_connect.get_ststoken()
            ali_connect.stop_instances('i-gw85l8j45xz42u9yy', sts_token=sts)

        :param instanceid:
        :param sts_token:
        :return:
        """
        logging.info("Going to stop instance: {}".format(instanceid))

        request = StopInstanceRequest.StopInstanceRequest()
        request.set_InstanceId(instanceid)

        if sts_token is not None:
            acs_client = AcsClient(region_id='cn-hangzhou', credential=sts_token)
            try:
                response = acs_client.do_action_with_exception(request)
                self.pretty_print(response)
            except Exception as e:
                logging.error(e)
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])
        else:
            try:
                response = self.__client.do_action_with_exception(request)
                self.pretty_print(response)
            except Exception as e:
                logging.error(e)
                logging.debug(traceback.format_exc())
                logging.debug(sys.exc_info()[0])

    
    def start_instances(self, instanceid, sts_token=None):
        """
        Start Alicloud instances.

        if Ram user have the persmission to do this action we can simply call:
            ali_connect = AliCloudConnect()
            ali_connect.start_instances('azertyuiop')
        otherwise, user can assume a role to have this privilege
            ali_connect.assume_role("acs:ram::<<account_ID>>:role/ecsadmin", "test")
            sts = ali_connect.get_ststoken()
            ali_connect.start_instances('i-gw85l8j45xztju9yy', sts_token=sts)

        :param instanceid:
        :param sts_token:
        :return:
        """
        logging.info("Going to start instance: {}".format(instanceid))

        request = StartInstanceRequest.StartInstanceRequest()
        request.set_InstanceId(instanceid)

        if sts_token is not None:
            acs_client = AcsClient(region_id='cn-hangzhou', credential=sts_token)
            try:
                response = acs_client.do_action_with_exception(request)
                self.pretty_print(response)
            except Exception as e:
                logging.error(e)
                logging.debug(traceback.format_exc())
                logging.debug(sys.exc_info()[0])
        else:
            try:
                response = self.__client.do_action_with_exception(request)
                self.pretty_print(response)
            except Exception as e:
                logging.error(e)
                logging.debug(traceback.format_exc())
                logging.debug(sys.exc_info()[0])
    

    ###############################
    ############VPC################
    ###############################

    def describe_vpcs(self):
        """
        Describe vpcs.

        Example of call :
            ali_connect = AliCloudConnect()
            ali_connect.describe_vpcs()

        :return:
        """
        logging.info('Going to describe all vpcs.')

        request = CommonRequest()
        request.set_domain(self.ecs_domain)
        request.set_version(self.version_2014_05_26)
        request.set_action_name('DescribeVpcs')

        try:
            response = self.__client.do_action_with_exception(request)
            self.pretty_print(response)
        except Exception as e:
            logging.error(e)
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])

    
    def describe_vswitches(self, vswitchid=None, vswitchname=None):
        """
        Describe vswitches.
        response = [vswitch] ## response is a list

        Example of call :
            ali_connect = AliCloudConnect()
            ali_connect.describe_vswitches()

        :return:
        
        """
        logging.info('Going to describe all vswitches.')
        response = []
        request = CommonRequest()
        request.set_domain(self.ecs_domain)
        request.set_version(self.version_2014_05_26)
        request.set_action_name('DescribeVSwitches')

        if vswitchid:
            request.add_query_param("VSwitchId", vswitchid)

        try:
            resp = self.__client.do_action_with_exception(request)
            resp = json.loads(resp)
            vswitchs = resp.get("VSwitches", {}).get("VSwitch")
            if vswitchname:
                for vswitch in vswitchs:
                    if vswitch.get("VSwitchName") == vswitchname:
                        response = [vswitch]
                        break
                if not response:
                    logging.error("vswitch not found")
            else:
                response = vswitchs
        except Exception as e:
            logging.error(e)
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])
        return response

    def describe_images(self, imageid=None, imagename=None, version=None):
        """
        Describe images

        tags in alicloud are in this form:
        {Tag.n.key, Tag.n.value}

        version: Tag.1.value
        image_version: Tag.1.key

        Example of call :
            ali_connect = AliCloudConnect()
            ali_connect.describe_images()

        :return:
        """
        response = []
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain(self.ecs_domain)
        request.set_version(self.version_2014_05_26)
        request.set_action_name('DescribeImages')
        if imageid:
            request.add_query_param("imageId", imageid)
        if imagename:
            request.add_query_param("ImageName", imagename)

        if version: 
            request.add_query_param('Tag.1.value', version)
            request.add_query_param('Tag.1.key', 'image_version')
        try:
            resp = self.__client.do_action_with_exception(request)
            response = json.loads(resp)
            response = response.get("Images", {}).get("Image")
            #self.pretty_print(response)
        except Exception as e:
            logging.error(e)
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])
        return response

    def delete_images(self, imageid=None, imagename=None, version=None):
        """
        Delete image

        Example of call :
            ali_connect = AliCloudConnect()
            ali_connect.delete_images()
        :return:
        """
        print 'Going to delete images'
        response = "succeeded"
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain(self.ecs_domain)
        request.set_version(self.version_2014_05_26)
        request.set_action_name('DeleteImage')

        if imageid:
            request.add_query_param("imageId", imageid)
        if imagename:
            request.add_query_param("ImageName", imagename)

        if version: 
            request.add_query_param('Tag.1.value', version)
            request.add_query_param('Tag.1.key', 'image_version')

        try:
            resp = self.__client.do_action_with_exception(request)
        except Exception as e:
            response = e
            logging.error(e)
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])
        return response

    def add_tags(self, resource_type=None, resource_id=None, tags=None):
        """
        Add tags
        
        Alicloud tags' are in this form:
        {Tag.n.key, Tag.n.value} 

        Example of call :
            ali_connect = AliCloudConnect()
            ali_connect.add_tags()
        :return:
        """
        response = []
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain(self.ecs_domain)
        request.set_version(self.version_2014_05_26)
        request.set_method('POST')
        request.set_action_name('AddTags')
        request.add_query_param("ResourceType", resource_type)
        request.add_query_param("ResourceId", resource_id)
        try:
            if isinstance(tags, list):
                for tag in tags:
                    n = 1
                    for k, v in tag.items():
                        request.add_query_param('Tag.{0}.key'.format(n), k)
                        request.add_query_param('Tag.{0}.value'.format(n), v)
                    n =+ 1

            resp = self.__client.do_action_with_exception(request)
            response = json.loads(resp)
            #self.pretty_print(response)
        except Exception as e:
            logging.error(e)
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])
        return response


    def describe_security_groups(self, groupid=None, groupname=None):
        """
        Describe security_groups
        Example of call :
            ali_connect = AliCloudConnect()
            ali_connect.describe_security_groups()
        :return:
        """
        print 'Going to describe security groups'
        response = []
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain(self.ecs_domain)
        request.set_version(self.version_2014_05_26)
        request.set_action_name('DescribeSecurityGroups')
        if groupid:
            request.add_query_param("SecurityGroupId", groupid)
        if groupname:
            request.add_query_param("SecurityGroupName", groupname)

        try:
            resp = self.__client.do_action_with_exception(request)
            response = json.loads(resp)
            response = response.get("SecurityGroups", {}).get("SecurityGroup")
            #self.pretty_print(response)
        except Exception as e:
            logging.error(e)
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])
        return response

    def copy_image(self, regionid=None, imageid=None, destinationimagename=None, destinationregionid=None):
        """
        Copy image

        Example of call :
            ali_connect = AliCloudConnect()
            ali_connect.copy_image()
        :return:
        """
        print 'Going to copy an image'
        response = None
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain(self.ecs_domain)
        request.set_version(self.version_2014_05_26)
        request.set_action_name('CopyImage')

        if regionid:
            request.add_query_param("RegionId", str(regionid))
        if imageid:
            request.add_query_param("ImageId", str(imageid))
        if destinationimagename:
            request.add_query_param("DestinationImageName", str(destinationimagename))
        if destinationregionid:
            request.add_query_param("DestinationRegionId", str(destinationregionid))

        try:
            resp = self.__client.do_action_with_exception(request)
            response = json.loads(resp)
            response = response.get("ImageId")
         
        except Exception as e:
            logging.error(e)
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])
        return response

    def modify_image_share_permission(self, regionid=None, imageid=None, addaccounts=None, removeaccounts=None):

        """
        Share image
        addaccounts: the destination account_id where the image will be shared
        removeaccounts: the destination account_id where th image share will be canceled
        
        Example of call :
            ali_connect = AliCloudConnect()
            ali_connect.modify_image_share_permission()
        :return:
        """
        response = None
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain(self.ecs_domain)
        request.set_version(self.version_2014_05_26)
        request.set_action_name('ModifyImageSharePermission')
        if regionid:
            request.add_query_param("RegionId", regionid)
        if imageid:
            request.add_query_param("ImageId", imageid)

        try:
            if isinstance(addaccounts, list):
                for c in addaccounts:
                    n = 1
                    request.add_query_param('AddAccount.{0}'.format(n), c)
                    n =+ 1
            if isinstance(removeaccounts, list):
                for cc in removeaccounts:
                    n = 1
                    request.add_query_param('RemoveAccount.{0}'.format(n), cc)
                    n =+ 1

            resp = self.__client.do_action_with_exception(request)
            response = json.loads(resp)
            #self.pretty_print(response)
        except Exception as e:
            logging.error(e)
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])
        return response