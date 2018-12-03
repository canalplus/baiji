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

from clients.resource import Client as aliClient

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

    def client(self):
        return aliClient(self.__client, region=self.region_id)

    def pretty_print(self, toprint):
        print json.dumps(json.loads(toprint), indent=4, sort_keys=True)

    def get_accesskey(self):
        return self.access_key_id

    def get_secretkey(self):
        return self.access_key_secret

    def get_ststoken(self):
        return self.sts_token