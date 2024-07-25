# runZero scripts


## Custom Integration: Cortex XDR + runZero

### Requirements
* runZero API Client Credentials
* runZero Organization ID
* Cortex XDR API Key ID, API Key, API URL

### Steps: 
1. runZero Configuration
* Update these values in the code:
* RUNZERO_BASE_URL - update if not using SaaS, link you use to login to runZero
* RUNZERO_ORG_ID - from the runZero Organizations page
* RUNZERO_SITE_NAME - from the runZero Sites page
* RUNZERO_CLIENT_ID - superusers can create API clients on the API clients page
* RUNZERO_CLIENT_SECRET - superusers can create API clients on the API clients page

2. Cortex XDR configuration
* Create an API Key and document the key, key ID, and API URL
** Documentation exists [here](https://docs-cortex.paloaltonetworks.com/r/Cortex-XPANSE/1.0/Cortex-Xpanse-User-Guide/Generate-an-API-Key-in-Cortex-XDR)

* Update these values in the code (please note you can hardcode or reference a .env file):
cortex_api_key - API key generated above
cortex_api_key_id - API key ID generated above
cortex_api_url - Cortex XDR API URL
