import time
import datetime
import uuid
import os
import runzero
from runzero.api import CustomAssets, CustomIntegrationsAdmin, Sites, Tasks
from runzero.types import ImportAsset, ImportTask, NetworkInterface
from cbc_sdk.helpers import build_cli_parser, get_cb_cloud_object
from cbc_sdk.platform import Device, Vulnerability


# API keys are required for using the runZero sdk. See https://www.runzero.com/docs/leveraging-the-api/
MY_CLIENT_ID = "d1d1d93c-5dcc-4dfe-a4d7-6bd11f0e7ed5"  # OAuth client id. See https://console.runzero.com/account/api/clients
MY_CLIENT_SECRET = os.environ['RUNZERO_OAUTH_SECRET']  # OAuth client secret. See https://console.runzero.com/account/api/clients
MY_ORG_ID = uuid.UUID("72f95c17-6b28-4ade-8878-67b7d10ed837")  # runZero organization ID. See https://console.runzero.com/organizations
WANTED_SITE_NAME = "Geisenheim"  # Name of site within the above Organization. See https://console.runzero.com/sites
MY_INTEGRATION_ID = "e24f93af-4077-4318-87b4-8107e4e023dc" # runZero Integration ID # See https://console.runzero.com/custom-integrations

def get_assets():

    rz_import_assets = []

    parser = build_cli_parser("List devices")
    args = parser.parse_args()    
    cb = get_cb_cloud_object(args)
    query = cb.select(Device)
    #query = query.where("GEI-PC0321")
    devices = list(query)
    print("Got a list of " + str(len(devices)) + " Devices from Carbon Black API")

    for device in devices:
        if not device.name:
            continue

        print(str(device.id) + " " + device.name or "None")
        #print(device)
        
        nwints = []
        nwint = NetworkInterface()
        #if device.mac_address:
        #    nwint.mac_address = ':'.join(device.mac_address[i:i+2] for i in range(0,12,2))
        if device.last_internal_ip_address and ':' in device.last_internal_ip_address:
            nwint.ipv6_addresses = [device.last_internal_ip_address]
        if device.last_internal_ip_address and '.' in device.last_internal_ip_address:
            nwint.ipv4_addresses = [device.last_internal_ip_address]
        #print(nwint)
        nwints.append(nwint)

        importasset = ImportAsset(
            id                 = device.id,
            network_interfaces = nwints,
            os                 = device.os,
            os_version         = device.os_version,
            first_seen_ts      = device.registered_time
            #custom_attributes = custom_attributes
        )

        print(device.name)
        if '\\' in device.name:
            hostname = device.name.split('\\')[1]
            importasset.domain = device.name.split('\\')[0]
        importasset.hostnames = [hostname]
        
        rz_import_assets.append(importasset)

#    software: Optional[List[AssetSoftware]] = Field(None, max_items=1000)
#    vulnerabilities: Optional[List[AssetVulnerability]] = Field(None, max_items=1000)

    return rz_import_assets


def main():
    """
    The code below uploads assets from the get_assets function to runzero
    source.
    """
    # create the runzero client
    c = runzero.Client()

    # try to log in using OAuth credentials
    try:
        c.oauth_login(MY_CLIENT_ID, MY_CLIENT_SECRET)
    except runzero.AuthError as e:
        print(f"login failed: {e}")
        return
    print("login successful")

    # create the site api manager to get our site information
    site_mgr = Sites(c)
    site = site_mgr.get(MY_ORG_ID, WANTED_SITE_NAME)
    if not site:
        print(f"unable to find requested site")
        return
    print(f"got information for site {site.name}")

    # creates some example assets
    assets = get_assets()

    # create our named import task with 'exclude unknown' set to true
    task_options = ImportTask(name=f'CB - {datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")}', exclude_unknown=True)

    # create the import api manager to upload custom assets
    import_mgr = CustomAssets(c)
    import_task = import_mgr.upload_assets(MY_ORG_ID, site.id, MY_INTEGRATION_ID, assets, task_info=task_options)
    print(f"created an custom asset import task: {import_task.name}")

if __name__ == "__main__":
    main()
