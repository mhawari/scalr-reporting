#!/usr/bin/python
import json
import requests
from api.client import ScalrApiClient

def main(credentials_file):
    # Setup credentials
    with open(credentials_file) as f:
        creds = json.load(f)
        api_url, api_key_id, api_key_secret = \
                [creds.get(k, "") for k in ["api_url", "api_key_id", "api_key_secret"]]

    client = ScalrApiClient(api_url.rstrip("/"), api_key_id, api_key_secret)
    client = ScalrApiClient(api_url.rstrip("/"), api_key_id, api_key_secret)
    #Get all the env
    envs = client.list('/api/v1beta0/account/environments/')
    resServers = []
    resFarmRoles = {}
    resRoles = {}
    resOses = {}
    resFarms = {}
    #Fetch all data in each env
    for env in envs:
        env_id = env['id']
        #Get all the servers
        servers = client.list('/api/v1beta0/user/%s/servers/' % env_id)
        farmRoles = {}
        roles = {}
        oses = {}
        farms = {}
        for server in servers:
            farmRoles[server['farmRole']['id']] = {}
            server['env'] = env_id
        #Get all the farmroles
        for k in farmRoles.keys():
            farmRoles[k] = client.fetch('/api/v1beta0/user/%s/farm-roles/%d' % (env_id,k))
            farmRoles[k]['env'] = env_id
            roles[farmRoles[k]['role']['id']] = {}
            farms[farmRoles[k]['farm']['id']] = {}
        #Get all the roles
        for k in roles.keys():
            roles[k] = client.fetch('/api/v1beta0/user/%s/roles/%d' % (env_id,k))
            roles[k]['env'] = env_id
            oses[roles[k]['os']['id']] = {}
        #Get all the farms
        for k in farms.keys():
            farms[k] = client.fetch('/api/v1beta0/user/%s/farms/%d/' % (env_id,k))
            farms[k]['env'] = env_id
        #Get all the OSes
        for k in oses.keys():
            oses[k] = client.fetch('/api/v1beta0/user/%s/os/%s/' % (env_id,k) )
            oses[k]['env'] = env_id
        #Add some info in server
        for s in servers:
            farmRoleId = s['farmRole']['id']
            roleId = farmRoles[farmRoleId]['role']['id']
            osId = roles[roleId]['os']['id']
            s['osName'] = oses[osId]['name']
            s['useScalrAgent'] = roles[roleId]['useScalrAgent']
        resServers += servers
        resFarmRoles.update(farmRoles)
        resRoles.update(roles)
        resOses.update(oses)
        resFarms.update(farms)
    #Now generate a bulk request
    bulk_request = ""
    for e in envs:
        bulk_request += '{ "index" : { "_index" : "scalr_env", "_type" : "type", "_id" : %s } }\n' % e['id']
        bulk_request += json.dumps(e)
        bulk_request += '\n'
    for s in resServers:
        bulk_request += '{ "index" : { "_index" : "scalr_servers", "_type" : "type", "_id" : "%s" } }\n' % s['id']
        bulk_request += json.dumps(s)
        bulk_request += '\n'
    for fr in resFarmRoles.values():
        bulk_request += '{ "index" : { "_index" : "scalr_farmroles", "_type" : "type", "_id" : %s } }\n' % fr['id']
        bulk_request += json.dumps(fr)
        bulk_request += '\n'
    for r in resRoles.values():
        bulk_request += '{ "index" : { "_index" : "scalr_roles", "_type" : "type", "_id" : %s } }\n' % r['id']
        bulk_request += json.dumps(r)
        bulk_request += '\n'
    for os in resOses.values():
        bulk_request += '{ "index" : { "_index" : "scalr_oses", "_type" : "type", "_id" : "%s" } }\n' % os['id']
        bulk_request += json.dumps(os)
        bulk_request += '\n'
    for f in resFarms.values():
        bulk_request += '{ "index" : { "_index" : "scalr_farms", "_type" : "type", "_id" : %s } }\n' % f['id']
        bulk_request += json.dumps(f)
        bulk_request += '\n'
    print bulk_request
    requests.delete('http://localhost:9200/scalr_oses')
    requests.delete('http://localhost:9200/scalr_roles')
    requests.delete('http://localhost:9200/scalr_servers')
    requests.delete('http://localhost:9200/scalr_farms')
    requests.delete('http://localhost:9200/scalr_farmroles')
    requests.delete('http://localhost:9200/scalr_env')
    requests.put('http://localhost:9200/_bulk', data=bulk_request)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("credentials", help="cred file")
    ns = parser.parse_args()
    main(ns.credentials)
