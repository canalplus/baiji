# Baiji
AliCloud SDK for python

[![Build Status](https://travis-ci.org/canalplus/baiji.svg?branch=develop)](https://travis-ci.org/canalplus/baiji)[![Version](https://img.shields.io/pypi/v/baiji-sdk.svg?style=flat)](https://pypi.org/project/baiji-sdk/)

### Usage

Sample usage:

    from baiji import AliCloudConnect

    acc = AliCloudConnect()
    clt = acc.client('ecs')
    all_instances = clt.instances.all()
    print("There are currently {} instances in this account.".format(len(all_instances)))
