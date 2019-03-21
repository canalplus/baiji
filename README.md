# Baiji
AliCloud SDK for python

[![Build Status](https://travis-ci.org/canalplus/baiji.svg?branch=develop)](https://travis-ci.org/canalplus/baiji)[![Version](https://img.shields.io/pypi/v/baiji-sdk.svg?style=flat)](https://pypi.org/project/baiji-sdk/)

### Usage
First install baiji package:
pip install baiji-sdk

Sample usage:

    from baiji.sdk import AliCloudConnect

    acc = AliCloudConnect()
    clt = acc.client()
    all_instances = clt.instances.all() 
    ## you can add the option "json_format=True" to display the result on json format, using the same syntaxe:
    all_instances = clt.instances.all(json_format=True)
    
    print("There are currently {} instances in this account.".format(len(all_instances)))

All the functions of the available resources on baiji are on resource.py
