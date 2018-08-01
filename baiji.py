from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkecs.request.v20140526 import StartInstanceRequest
from aliyunsdkecs.request.v20140526 import StopInstanceRequest
from aliyunsdkcore.auth.credentials import StsTokenCredential


from os import environ
from os import path
import requests
import json



class AliCloudConnect:

    #caller will need to pass accessKey, secretKey if stsToken = None / or pass stsToken if it is not none.
    client = None
    AccessKeyId = None
    AccessKeySecretId = None
    RegionId = None
    StsToken = None

    #each api has it's own version !
    version_2014_05_26 = "2014-05-26"
    version_2015_05_01 = "2015-05-01"
    version_2015_04_01 = "2015-04-01"

    #endpoint definiton by service
    ecs_domain = "ecs.eu-central-1.aliyuncs.com"
    sts_domain = "sts.aliyuncs.com"
    ram_domain = "ram.aliyuncs.com"

    protocol = "https"

    def __init__(self, account_id=None , role=None):
        """
        Constructor of alicloudConnect
        We will try to connect with env first, config credentials and finally with instance role
        User will use the AcsClient to deal with aliyun api
        :param account_id:
        :param role:
        :
        """

        access_key_id = ''
        access_key_secret = ''
        region_id = ''

        connect_with_credential = False
        connect_with_role = False
        config_file = path.expanduser('~') + "/.aliyun/config.json"
        print 'Alicloud connect'
        if 'ALICLOUD_ACCESS_KEY' in environ:
            print ' Trying to connect with Env credentials'
            access_key_id = environ['ALICLOUD_ACCESS_KEY']
            if 'ALICLOUD_SECRET_KEY' in environ:
                access_key_secret = environ['ALICLOUD_SECRET_KEY']
                if 'ALICLOUD_REGION' in environ:
                    region_id = environ['ALICLOUD_REGION']
                    connect_with_credential = True
                    self.AccessKeyId = access_key_id
                    self.AccessKeySecretId = access_key_secret
                    self.RegionId = region_id

            else:
                print 'Both access key and secret key are mandatory '

        elif path.exists(config_file):
            print ' Trying to connect with config credentials'
            config = json.load(open(config_file))
            access_key_id = config['profiles'][1]['access_key_id']
            access_key_secret = config['profiles'][1]['access_key_secret']
            region_id = config['profiles'][1]['region_id']
            connect_with_credential = True
            self.AccessKeyId = access_key_id
            self.AccessKeySecretId = access_key_secret

        elif account_id is not None and role is not None:
            print 'Trying to connect with instance role'
            response = requests.get('http://100.100.100.200/latest/meta-data/ram/security-credentials/%s' % role, timeout=5).json()

            sts_access_key = response['AccessKeyId']
            sts_secret_key = response['AccessKeySecret']
            sts_token_session = response['SecurityToken']

            self.AccessKeyId = sts_access_key
            self.AccessKeySecretId = sts_secret_key
            connect_with_role = True

        else:
            print 'no valid connection type provided'

        try:
            if connect_with_credential:
                self.client = AcsClient(access_key_id, access_key_secret, region_id)

            elif connect_with_role:
                sts_token_credential = StsTokenCredential(sts_access_key,
                                                          sts_secret_key,
                                                          sts_token_session)
                self.StsToken = sts_token_credential
                self.client = AcsClient(region_id='cn-hangzhou', credential=sts_token_credential)

        except Exception as e:
            print e

    def pretty_print(self, toprint):
        print json.dumps(json.loads(toprint), indent=4, sort_keys=True)

    def get_accesskey(self):
        return self.AccessKeyId

    def get_secretkey(self):
        return self.AccessKeySecretId

    def get_ststoken(self):
        return self.StsToken

    def assume_role(self, role_arn, session_name):
        '''
        Assume a role : this function will try to assume a role. and will set StsToken of the constructor if OK
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

        print 'Going to assume role: ' + role_arn + ' sessionName: ' + session_name
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
            self.StsToken = StsTokenCredential(sts_access_key,
                                                          sts_secret_key,
                                                          sts_token_session)

            return response
        except Exception as e:
            print e

###############################
############ECS################
###############################

    def describe_instances(self):
        """
        Describe instance
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

    def stop_instances(self, instanceid, sts_token = None):
        """
        Stop Alicloud instance
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
        print 'Going to stop instance ' + instanceid

        request = StopInstanceRequest.StopInstanceRequest()
        request.set_InstanceId(instanceid)

        if sts_token is not None:
            acs_client = AcsClient(region_id='cn-hangzhou', credential=sts_token)
            try:
                response = acs_client.do_action_with_exception(request)
                self.pretty_print(response)
            except Exception as e:
                print e
        else:
            try:
                response = self.client.do_action_with_exception(request)
                self.pretty_print(response)
            except Exception as e:
                print e

    def start_instances(self, instanceid, sts_token=None):
        """
        Start Alicloud instance
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
        print 'Going to start instance ' + instanceid

        request = StartInstanceRequest.StartInstanceRequest()
        request.set_InstanceId(instanceid)

        if sts_token is not None:
            acs_client = AcsClient(region_id='cn-hangzhou', credential=sts_token)
            try:
                response = acs_client.do_action_with_exception(request)
                self.pretty_print(response)
            except Exception as e:
                print e
        else:
            try:
                response = self.client.do_action_with_exception(request)
                self.pretty_print(response)
            except Exception as e:
                print e
