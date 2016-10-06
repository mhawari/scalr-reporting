#!/usr/bin/python
import json
from api.client import ScalrApiClient

fieldsToGetDefault = ['id','farmRole.role.os.id','farmRole.role.os.name','cloudPlatform' ]
def getField(data,fieldName):
	fields = fieldName.split('.')
	for p in fields:
		data = data[p]
	return str(data)

def main(credentials_file, fieldsToGet):
    # Setup credentials
    with open(credentials_file) as f:
        creds = json.load(f)
        api_url, api_key_id, api_key_secret, env_id = \
                [creds.get(k, "") for k in ["api_url", "api_key_id", "api_key_secret", "env_id"]]

    client = ScalrApiClient(api_url.rstrip("/"), api_key_id, api_key_secret)
    client = ScalrApiClient(api_url.rstrip("/"), api_key_id, api_key_secret)
    #Get all the servers
    servers = client.list('/api/v1beta0/user/%s/servers/' % env_id)
    farmRoles = {}
    roles = {}
    oses = {}
    for server in servers:
    	farmRoles[server['farmRole']['id']] = {}
    #Get all the farmroles
    for k in farmRoles.keys():
    	farmRoles[k] = client.fetch('/api/v1beta0/user/%s/farm-roles/%d' % (env_id,k))
    	roles[farmRoles[k]['role']['id']] = {}
    #Get all the roles
    for k in roles.keys():
    	roles[k] = client.fetch('/api/v1beta0/user/%s/roles/%d' % (env_id,k))
    	oses[roles[k]['os']['id']] = {}
    #Get all the OSes
    for k in oses.keys():
    	oses[k] = client.fetch('/api/v1beta0/user/%s/os/%s/' % (env_id,k) )
    #Join everything
    for server in servers:
    	server['farmRole'] = farmRoles[server['farmRole']['id']]
    for f in farmRoles.keys():
    	farmRoles[f]['role'] = roles[farmRoles[f]['role']['id']]
    for r in roles.keys():
    	roles[r]['os'] = oses[roles[r]['os']['id']]
    #now output!
    for s in servers:
    	line = ""
    	for fieldName in fieldsToGet:
    		line += getField(s,fieldName) + ','
    	line = line[:-1]
    	print line

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("credentials", help="Path to credentials file")
    parser.add_argument("-f","--fieldsToGet",help="List of the fields to report. Example: id farmRole.role.os.name cloudPlatform", metavar="fields", nargs='+',type=str, default=fieldsToGetDefault, required=False)
    ns = parser.parse_args()
    main(ns.credentials,ns.fieldsToGet)