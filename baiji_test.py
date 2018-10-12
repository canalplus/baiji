from baiji import AliCloudConnect
import sys
import traceback
import pdb

try:
    connect = AliCloudConnect(region_id='eu-central-1')
    clt = connect.client('ecs')
    sg = print(clt.security_groups.all())
    image = clt.images.all()
    tag = clt.tags.all()
    vpc = clt.vpcs.all()
    vswitch = clt.vswitches.all()
    images = clt.images.all()
    if len(images) > 0:
        result = clt.images.copy({"RegionId": "eu-central-1", "ImageId": images[0].ImageId, "DestinationImageName ": "image_copy_baiji", "DestinationDescription ": "image created for test copy image of baiji", "DestinationRegionId ": "eu-west-1", "Tag.1.key": "version", "Tag.1.value": "tuto"})
        connect = AliCloudConnect(region_id='eu-west-1')
        clt = connect.client('ecs')
        result1 = clt.images.delete({"RegionId": "eu-west-1", "ImageId": result["ImageId"], "Force": "True"})
    
    connect = AliCloudConnect(region_id='eu-central-1')
    clt = connect.client('ecs')
    if len(images) > 0:
        result2 = clt.images.share_permission({"RegionId": "eu-central-1", "ImageId": images[0].ImageId, "AddAccount.1": ""})
        result3 = clt.images.share_permission({"RegionId": "eu-central-1", "ImageId": result2["ImageId"], "RemoveAccount.1": ""})
        result4 = clt.tags.add({"RegionId": "eu-central-1", "ResourceType": "image", "ResourceId": images[0].ImageId, "Tag.1.key": "version", "Tag.1.value": "tuto"})
        result5 = clt.tags.remove({"RegionId": "eu-central-1", "ResourceType": "image", "ResourceId": images[0].ImageId, "Tag.1.key": "version", "Tag.1.value": "tuto"})

    print("Resources successfully fetched.")
    sys.exit(0)
except Exception as e:
    print(e)
    print(traceback.format_exc())
    sys.exit(1)
