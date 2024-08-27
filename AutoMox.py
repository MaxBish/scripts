## Automox!

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

## Automox API URL
AUTOMOX_URL = "https://console.automox.com/api/servers"

## Automox Bearer Token (can also use os.environ variable)
TOKEN = ""

# runZero information
RUNZERO_CLIENT_ID = "runZero client ID"
RUNZERO_CLIENT_SECRET = "runZero client secret"
RUNZERO_BASE_URL = "https://console.runZero.com/api/v1.0"
RUNZERO_ORG_ID = "runZero ORG ID"
RUNZERO_SITE_NAME = "runZero Site Name"

## API headers used in the requests
HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

def automox_api(query):
    """Make an API request and return data.
    params - query parameters
    Returns a JSON data object.
    """

    response = requests.get(url=AUTOMOX_URL, headers=HEADERS, params=query)

    data = response.json()

    return data


def get_devices():
    """Return device inventory."""

    ## Automox query parameters when making API call
    query = {
      "groupId": "0",
      "PS_VERSION": "0",
      "o": "0",
      "pending": "0",
      "patchStatus": "missing",
      "policyId": "0",
      "exception": "0",
      "managed": "0",
      "limit": "500",
      "page": "0",
      "filters[is_compatible]": "true",
      "sortColumns[]": "is_compatible",
      "sortDir": "asc"
    }

    # inventory
    data = []

    while True:
        # check to see if a platform was specified
        response = automox_api(query)
        
        if len(response) == 0:
            break

        else:
            query["page"] = query["page"] + 1

        # breakout the response then append to the data list
        for record in response:
            data.append(record)

    if len(data) < 1:
        print("No devices found...\n")
        sys.exit()

    return data


def build_assets():
  all_endpoints = get_devices()

  assets = []
  for endpoint in all_endpoints:
      custom_attrs = {}
      custom_attrs['os_version'] = endpoint['os_version']
      custom_attrs['os_name'] = endpoint['os_name']
      custom_attrs['os_family'] = endpoint['os_family']
      custom_attrs['agent_version'] = endpoint['agent_version']

      mac_address = None
      if len(endpoint['detail']['NICS']['MAC']) > 0:
         mac_address = endpoint['detail']['NICS']['MAC']

      ## handle IPs
      ips = []
      ips.append(endpoint['ip_addrs'])

      assets.append(ImportAsset(
         id=endpoint['id'],
         networkInterfaces=[build_network_interface(ips=ips,mac=mac_address)],
         hostnames=[endpoint['name']],
         os_version=endpoint['os_version'],
         customAttributes=custom_attrs
      ))
  return assets

def build_network_interface(ips: List[str], mac: str = None) -> NetworkInterface:
    """
    This function converts a mac and a list of strings in either ipv4 or ipv6 format and creates a NetworkInterface that
    is accepted in the ImportAsset
    """
    ip4s: List[IPv4Address] = []
    ip6s: List[IPv6Address] = []
    for ip in ips[:99]:
        try:
            ip_addr = ip_address(ip)
            if ip_addr.version == 4:
                ip4s.append(ip_addr)
            elif ip_addr.version == 6:
                ip6s.append(ip_addr)
            else:
                continue
        except:
            continue

    if mac is None:
        return NetworkInterface(ipv4Addresses=ip4s, ipv6Addresses=ip6s)
    else:
        return NetworkInterface(macAddress=mac, ipv4Addresses=ip4s, ipv6Addresses=ip6s)


def import_data_to_runzero(assets: List[ImportAsset]):
    """
    The code below gives an example of how to create a custom source and upload valid assets from a CSV to a site using
    the new custom source.
    """
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
    my_asset_source = custom_source_mgr.get(name="automox")
    if my_asset_source:
        source_id = my_asset_source.id
    else:
        my_asset_source = custom_source_mgr.create(name="kandji")
        source_id = my_asset_source.id

    # create the import manager to upload custom assets
    import_mgr = CustomAssets(c)
    import_task = import_mgr.upload_assets(
        org_id=RUNZERO_ORG_ID,
        site_id=site.id,
        custom_integration_id=source_id,
        assets=assets,
        task_info=ImportTask(name="Automox Sync"),
    )

    if import_task:
        print(
            f"task created! view status here: https://console.runzero.com/tasks?task={import_task.id}"
        )


def main():
    """Do the main logic."""
    print("")
    print(f"Automox URL: " + AUTOMOX_URL)
    print("")

    # Get the total number of devices
    device_inventory = build_assets()
    print(f"Total number of devices: {len(device_inventory)}")
    
    import_data_to_runzero(device_inventory)
    


if __name__ == "__main__":
    main()
