// Delete assets via query

export_url = RUNZERO_BASE_URL + "/export/org/assets.json"
headers = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
params = {"search": f"site:{RUNZERO_SITE_ID}", "fields": "id"}
resp = requests.get(url=export_url, headers=headers, params=params)
asset_list = [x["id"] for x in resp.json()]
if len(asset_list) > 0:
    delete_url = RUNZERO_BASE_URL + "/org/assets/bulk/delete"
    delete = requests.delete(url=delete_url, headers=headers, json={"asset_ids": asset_list}, params={"_oid": RUNZERO_ORG_ID})
    if delete.status_code == 204:
       print("Deleted all assets")
