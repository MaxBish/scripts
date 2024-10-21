## AUTOMOX INTEGRATION (STARLARK)

## Loading dependencies
load('runzero.types', 'ImportAsset', 'NetworkInterface')
load('json', json_encode='encode', json_decode='decode')
load('net', 'ip_address')
load('http', http_post='post', http_get='get', 'url_encode')
load('uuid', 'new_uuid')

## Automox API URL
AUTOMOX_URL = 'https://console.automox.com/api/servers'

def get_bearer_token(client_id,client_secret):
    params = {'Authorization': Bearer {client_secret}'}
    

def main(*args, **kwargs):
    client_id = kwargs['access_key']
    client_secret = kwargs['access_secret']

    bearer_token = get_bearer_token(client_id, client_secret)
