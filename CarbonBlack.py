## CarbonBlack!

## importing dependencies
from ipaddress import ip_address
import sys
import requests

import json
import runzero
from runzero.client import AuthError
from runzero.api import CustomAssets, CustomIntegrationsAdmin, Sites
from runzero.types import (
    CustomAttribute,
    ImportAsset,
    IPv4Address,
    IPv6Address,
    NetworkInterface,
    ImportTask,
)

from cbc_sdk.helpers import build_cli_parser, get_cb_cloud_object
from cbc_sdk.platform import Device


# API keys are required for using the runZero sdk. See https://www.runzero.com/docs/leveraging-the-api/
RUNZERO_CLIENT_ID = ""  # OAuth client id. See https://console.runzero.com/account/api/clients
RUNZERO_CLIENT_SECRET = ""  # OAuth client secret. See https://console.runzero.com/account/api/clients
RUNZERO_ORG_ID = ""  # runZero organization ID. See https://console.runzero.com/organizations
RUNZERO_SITE_NAME = ""  # Name of site within the above Organization. See https://console.runzero.com/sites
RUNZERO_BASE_URL = "https://console.runZero.com/api/v1.0"

def get_assets():

    rz_import_assets = []

    parser = build_cli_parser("List devices")
    args = parser.parse_args()    
    cb = get_cb_cloud_object(args)
    query = cb.select(Device)
    devices = list(query)
    print("Got a list of " + str(len(devices)) + " Devices from Carbon Black API")

    for device in devices:
        custom_attrs = {}
        custom_attrs['os_version'] = device.os_version
        custom_attrs['os'] = device.os

        mac_address = None
        if device.mac_address is not None:
            mac_address = device.mac_address

        ips = []
        ips.append(device.last_internal_ip_address)
        ips.append(device.last_external_ip_address)

        rz_import_assets.append(ImportAsset(
            id=device.id,
            networkInterfaces=[build_network_interface(ips=ips,mac=mac_address)],
            hostnames=device.name,
            firstSeenTS=device.registered_time,
            os=device.os,
            osVersion=device.os_version,
            customAttributes=custom_attrs
        ))

    return rz_import_assets



def build_network_interface(ips: list[str], mac: str = None) -> NetworkInterface:
    """
    This function converts a mac and a list of strings in either ipv4 or ipv6 format and creates a NetworkInterface that
    is accepted in the ImportAsset
    """
    ip4s: list[IPv4Address] = []
    ip6s: list[IPv6Address] = []
    for ip in ips[:99]:
            ip_addr = ip_address(ip[0])
            if ip_addr.version == 4:
                ip4s.append(ip_addr)
            elif ip_addr.version == 6:
                ip6s.append(ip_addr)
            else:
                continue

    if mac is None:
        return NetworkInterface(ipv4Addresses=ip4s, ipv6Addresses=ip6s)
    else:
        return NetworkInterface(macAddress=mac, ipv4Addresses=ip4s, ipv6Addresses=ip6s)
    



def import_data_to_runzero(assets: list[ImportAsset]):
    
    # create the runzero client
    c = runzero.Client()

    # try to log in using OAuth credentials
    try:
        c.oauth_login(RUNZERO_CLIENT_ID, RUNZERO_CLIENT_SECRET)
    except AuthError as e:
        print(f"login failed: {e}")
        return

    # create the site manager to get our site information
    site_mgr = Sites(c)
    site = site_mgr.get(RUNZERO_ORG_ID, RUNZERO_SITE_NAME)
    if not site:
        print(f"unable to find requested site")
        return

    # get or create the custom source manager and create a new custom source
    custom_source_mgr = CustomIntegrationsAdmin(c)
    my_asset_source = custom_source_mgr.get(name="CarbonBlack")
    if my_asset_source:
        source_id = my_asset_source.id
    else:
        my_asset_source = custom_source_mgr.create(name="CarbonBlack")
        source_id = my_asset_source.id

    # create the import manager to upload custom assets
    import_mgr = CustomAssets(c)
    import_task = import_mgr.upload_assets(
        org_id=RUNZERO_ORG_ID,
        site_id=site.id,
        custom_integration_id=source_id,
        assets=assets,
        task_info=ImportTask(name="CarbonBlack Sync"),
    )

    if import_task:
        print(
            f"Task created! View status here: https://console.runzero.com/tasks?task={import_task.id}"
        )



def main():
    """
    The code below uploads assets from the get_assets function to runzero
    source.
    """
    print("")
    print("Running CarbonBlack Integration")
    print("")

    ## Get all the devices
    device_inventory = get_assets()
    print(f"Total number of devices: {len(device_inventory)}")

    import_data_to_runzero(device_inventory)


if __name__ == "__main__":
    main()
