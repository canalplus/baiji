from baiji import AliCloudConnect
import sys
import traceback

try:
    connect = AliCloudConnect(region_id='eu-central-1')
    clt = connect.client('ecs')
    clt.security_groups.all()
    print("Resources successfully fetched.")
    sys.exit(0)
except Exception as e:
    print(e)
    print(traceback.format_exc())
    sys.exit(1)
