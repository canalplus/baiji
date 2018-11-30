from baiji.sdk import AliCloudConnect
import sys
import traceback

try:
    connect = AliCloudConnect(region_id='eu-central-1')
    clt = connect.client()
    inst = clt.instances.all(json_format=True)
    print inst
    #instget = clt.instances.get({"RegionId": "eu-central-1", "InstanceIds": '[""]'}, json_format=True)
    #print instget
    #inst = clt.instances.stop({"InstanceId": ""})
    #print inst
    sg = clt.security_groups.all(json_format=True)
    #sg = clt.security_groups.get({"SecurityGroupIds": [""]}, json_format=True)
    print sg
    image = clt.images.all(json_format=True)
    #image = clt.images.get({"RegionId": "eu-central-1", "ImageId": ","}, json_format=True)
    #image = clt.images.delete({"ImageId": ""}, json_format=True)
    #image = clt.images.copy({"RegionId": "eu-central-1", "ImageId": "", "DestinationImageName": "test_copy_baiji", "DestinationRegionId":"eu-west-1", "Tag.1.Key":"image_version", "Tag.1.Value": ""})
    #image = clt.images.share_permission({"ImageId": "", "AddAccount.1": ""})
    #image = clt.images.modify_image_attribute({"RegionId ": "eu-central-1", "ImageId": "", "ImageName": "image-baiji"})
    print image
    tag = clt.tags.all(json_format=True)
    #tag = clt.tags.get({"ResourceType": "image", "ResourceId": ""}, json_format=True)
    #tag = clt.tags.add({"ResourceType": "securitygroup", "ResourceId": "", "Tag.1.Key": "version", "Tag.1.Value": ""})
    #tag = clt.tags.remove({"ResourceType": "securitygroup", "ResourceId": "", "Tag.1.Key": "version", "Tag.1.Value": ""})
    print tag
    vpc = clt.vpcs.all(json_format=True)
    print vpc
    #vpc = clt.vpcs.get({"RegionId": "eu-central-1", "VpcId": ","}, json_format=True)
    #print vpc
    vswitch = clt.vswitches.all(json_format=True)
    #vswitch = clt.vswitches.get({"VSwitchId": ""}, json_format=True)
    print vswitch
    rol = clt.roles.all(json_format=True)
    #rol = clt.roles.get({"RoleName": ""}, json_format=True)
    #rol = clt.roles.assume({"RoleArn": "acs:ram::accountid:role/rolename", "RoleSessionName": "test"}, json_format=True)
    print rol
    usr = clt.users.all(json_format=True)
    print usr
    grp = clt.groups.all(json_format=True)
    print grp
    disk = clt.disks.all(json_format=True)
    #disk = clt.disks.get({"InstanceId": ""}, json_format=True)
    print disk
    print("Resources successfully fetched.")
    sys.exit(0)
except Exception as e:
    print(e)
    print(traceback.format_exc())
    sys.exit(1)
