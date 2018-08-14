#!/usr/bin/python

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkecs.request.v20140526 import StartInstanceRequest
from aliyunsdkecs.request.v20140526 import StopInstanceRequest
from aliyunsdkcore.auth.credentials import StsTokenCredential

from os import environ
from os import path
import requests
import json
import logging
import traceback
import sys

logging.getLogger().setLevel(logging.DEBUG)

class AliCloudConnect:
    """
    AliCloudConnect

    Provides root functions and objects to use AliCloud features.
    """

    def __init__(self, account_id=None , role=None, region_id="eu-central-1"):
        """
        Constructor of alicloudConnect.

        We will try to connect with env first, config credentials and finally with instance role.
        User will use the AcsClient to deal with aliyun api.

        :param account_id:
        :param role:
        """

        # caller will need to pass accessKey, secretKey
        # if stsToken = None / or pass stsToken if it is not none.
        self.client = None
        self.access_key_id = None
        self.access_secret_key = None
        self.region_id = region_id
        self.sts_token = None

        # each api has it's own version !
        self.version_2014_05_26 = "2014-05-26"
        self.version_2015_05_01 = "2015-05-01"
        self.version_2015_04_01 = "2015-04-01"

        # endpoint definiton by service
        self.ecs_domain = "ecs.eu-central-1.aliyuncs.com"
        self.sts_domain = "sts.aliyuncs.com"
        self.ram_domain = "ram.aliyuncs.com"

        self.protocol = "https"

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
                self.access_secret_key = access_key_secret

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
            self.access_secret_key = access_key_secret

        elif account_id is not None and role is not None:
            logging.info('Trying to connect with instance role.')
            response = requests.get('http://100.100.100.200/latest/meta-data/ram/security-credentials/%s' % role, timeout=5).json()

            sts_access_key = response['AccessKeyId']
            sts_secret_key = response['AccessKeySecret']
            sts_token_session = response['SecurityToken']

            self.access_key_id = sts_access_key
            self.access_secret_key = sts_secret_key
            connect_with_role = True

        else:
            logging.error('No valid connection type provided.')

        try:
            if connect_with_credential:
                self.client = AcsClient(access_key_id, access_key_secret, region_id)

            elif connect_with_role:
                sts_token_credential = StsTokenCredential(sts_access_key,
                                                          sts_secret_key,
                                                          sts_token_session)
                self.sts_token = sts_token_credential
                self.client = AcsClient(region_id='cn-hangzhou', credential=sts_token_credential)

        except Exception as e:
            logging.error(e)

    def pretty_print(self, toprint):
        print json.dumps(json.loads(toprint), indent=4, sort_keys=True)

    def get_accesskey(self):
        return self.access_key_id

    def get_secretkey(self):
        return self.access_secret_key

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
        request.set_protocol_type(self.protocol)
        request.add_query_param("RoleArn", role_arn)
        request.add_query_param("RoleSessionName", session_name)
        request.set_action_name('AssumeRole')
        try:
            response = json.loads(self.client.do_action_with_exception(request))
            sts_access_key = response['Credentials']['AccessKeyId']
            sts_secret_key = response['Credentials']['AccessKeySecret']
            sts_token_session = response['Credentials']['SecurityToken']
            self.sts_token = StsTokenCredential(
                sts_access_key, sts_secret_key, sts_token_session
            )

            return response
        except Exception as e:
            logging.error(e)

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
        print 'Going to describe all instances'

        request = CommonRequest()
        request.set_domain(self.ecs_domain)
        request.set_version(self.version_2014_05_26)
        request.set_action_name('DescribeInstanceStatus')

        try:
            response = self.client.do_action_with_exception(request)
            self.pretty_print(response)
        except Exception as e:
            print e


    def describe_disks(self):
        """
        Describe disks.

        Example of call :
            ali_connect = AliCloudConnect()
            ali_connect.describe_instances()

        :return:
        """
        print 'Going to describe all disks'

        request = CommonRequest()
        request.set_domain(self.ecs_domain)
        request.set_version(self.version_2014_05_26)
        request.set_action_name('DescribeDisks')

        try:
            response = self.client.do_action_with_exception(request)
            self.pretty_print(response)
        except Exception as e:
            print e



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
        else:
            try:
                response = self.client.do_action_with_exception(request)
                self.pretty_print(response)
            except Exception as e:
                logging.error(e)

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
        else:
            try:
                response = self.client.do_action_with_exception(request)
                self.pretty_print(response)
            except Exception as e:
                logging.error(e)

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
            response = self.client.do_action_with_exception(request)
            self.pretty_print(response)
        except Exception as e:
            logging.error(e)



    def describe_vswitchs(self):
        """
        Describe vswitches.

        Example of call :
            ali_connect = AliCloudConnect()
            ali_connect.describe_vswitches()

        :return:
        """
        logging.info('Going to describe all vswitches.')

        request = CommonRequest()
        request.set_domain(self.ecs_domain)
        request.set_version(self.version_2014_05_26)
        request.set_action_name('DescribeVSwitches')

        try:
            response = self.client.do_action_with_exception(request)
            self.pretty_print(response)
        except Exception as e:
            logging.error(e)
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])

    ###############################
    ############RAM################
    ###############################


    def create_role(self, role_name, policy_document):
        """
        create_role

        Creates a RAM role.

        :param self:
        :param role_name:
        :param policy_document:
        :return:
        """
        logging.info("Going to create role: {}".format(role_name))
        request = CommonRequest()
        request.set_domain(self.ram_domain)
        request.set_version(self.version_2015_05_01)
        request.set_protocol_type(self.protocol)
        request.add_query_param("RoleName", role_name)
        request.add_query_param("AssumeRolePolicyDocument", policy_document)
        request.set_action_name('CreateRole')
        try:
            response = self.client.do_action_with_exception(request)
            loggging.info(response)
        except Exception as e:
            logging.error(e)



    def get_role(self, role_name):
        """
        get_role

        Gets data of a RAM role.

        :param alicloud_client:
        :param role_name:
        :return:
        """
        logging.info("Going to get role {}".format(role_name))
        request = CommonRequest()
        request.set_domain(self.ram_domain)
        request.set_version(self.version_2015_05_01)
        request.set_protocol_type(self.protocol)
        request.add_query_param("RoleName", role_name)
        request.set_action_name('GetRole')
        try:
            response = self.client.do_action_with_exception(request)
            self.pretty_print(response)
        except Exception as e:
            logging.error(e)


    def list_users(self):
        """
        list_users

        Lists RAM users.

        :param alicloud_client:
        :return:
        """
        logging.info('Going to list users.')
        request = CommonRequest()
        request.set_domain(self.ram_domain)
        request.set_version(self.version_2015_05_01)
        request.set_protocol_type(self.protocol)
        request.set_action_name('ListUsers')
        try:
            response = self.client.do_action_with_exception(request)
            self.pretty_print(response)
        except Exception as e:
            logging.error(e)


    def list_groups(self):
        """
        list_groups

        Lists RAM groups.

        :param alicloud_client:
        :return:
        """
        logging.info('Going to list groups.')
        request = CommonRequest()
        request.set_domain(self.ram_domain)
        request.set_version(self.version_2015_05_01)
        request.set_protocol_type(self.protocol)
        request.set_action_name('ListGroups')
        try:
            response = self.client.do_action_with_exception(request)
            self.pretty_print(response)
        except Exception as e:
            logging.error(e)
