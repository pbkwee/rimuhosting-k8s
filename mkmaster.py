import argparse
import os
import json,sys
import urllib.request
from pprint import pprint
from pprint import pformat
import rimuapi
#from jsonpath_rw import jsonpath, parse
import objectpath

isDebug = False
def debug(str):
    if isDebug:
        print(str)
        print()     
class Args(object):
    def __init__(self):
        parser = argparse.ArgumentParser(description="Create a master Kubernetes VM.")
        parser.add_argument("--cluster", type=str, required=True, help="Unique id for this cluster.  e.g. cluster1")
        parser.add_argument("--server_json", type=str, required=True, help="Server json.  e.g. containing memory_mb and disk_space_gb.  per http://apidocs.rimuhosting.com/jaxbdocs/com/rimuhosting/rs/order/OSDPrepUtils.NewVPSRequest.html")
        parser.add_argument("--cloud_config", type=str, required=True, help="Server cloud config file")
        parser.add_argument("--dc_location", type=str, required=False, help="Optional data center location.  e.g. DCDALLAS, DCFRANKFURT, DCAUCKLAND")
        parser.add_argument("--debug", action="store_true", help="Show debug logging")
        parser.add_argument("--isreinstall", action="store_true", help="reinstall the master")
        parser.parse_args(namespace=self)
        isDebug = self.debug;
    
    def debug(self, str):
        if isDebug or self.debug:
            print(str)
            print()     
            
    def run(self):
        xx = rimuapi.Api()
        server_json = json.load(open(args.server_json))
        self.debug("server json = " + str(server_json))
        if not hasattr(server_json, "instantiation_options"):
            server_json["instantiation_options"] = dict()
        #if not hasattr(server_json["instantiation_options"], "distro"):
        # required to be a coreos distro
        server_json["instantiation_options"]["distro"] = "coreos.64"
        if not hasattr(server_json["instantiation_options"], "domain_name"):
            server_json["instantiation_options"]["domain_name"] = "coreosmaster.localhost"
        if not hasattr(server_json["instantiation_options"], "cloud_config_data"):
            server_json["instantiation_options"]["cloud_config_data"] = open(args.cloud_config).read()
        if not hasattr(server_json, "meta_data"):
            server_json["meta_data"] = list()
        if self.dc_location:
            server_json["dc_location"] = self.dc_location
        #print("server_json=",server_json)
        
        # see if the cluster id is in the server json, else use the command line arg value
        klusterids = objectpath.Tree(server_json).execute("$.meta_data[@.key_name is 'com.rimuhosting.kclusterid'].value")
        if not klusterids is None and len(list(klusterids))>0:
            raise Exception("Provide the cluster id as a command line argument.")
        server_json["meta_data"].append({'key_name': 'com.rimuhosting.kclusterid' , 'value' : args.cluster})
        server_json["meta_data"].append({'key_name': 'com.rimuhosting.kismaster' , 'value' : 'Y'})
        # replace the magic $kubernetes_domain_name with the server domain name
        server_json["instantiation_options"]["cloud_config_data"] = server_json["instantiation_options"]["cloud_config_data"].replace("$kubernetes_domain_name", server_json["instantiation_options"]["domain_name"], 99)
    
        existing = xx.orders('N', {'server_type': 'VPS','meta_search': 'com.rimuhosting.kclusterid:' +args.cluster+ ' com.rimuhosting.kismaster:Y'})
        if args.isreinstall:
            if len(existing)==0:
                raise Exception("Could not find that cluster master for a reinstall.  Just create the master?")
            if len(existing)>1:
                raise Exception("Found multiple cluster masters with this id.")
            
            self.debug("Running a reinstall on " + str(existing[0]["order_oid"]) + " " + str(existing[0]) + " ETA 5 minutes")
            
            master = xx.reinstall(int(existing[0]["order_oid"]), server_json)
            self.debug ("reinstalled master server")
            print(pformat(master))
            return
        
        if existing:
            raise Exception("That cluster already exists.  Delete it, or create a new one, or reinstall it (with the --reinstall option).  Use rhkclusterlist.py to list the existing clusters.")
        self.debug ("creating master server (ETA 5 minutes)...")
        master = xx.create(server_json)
        self.debug ("created master server: ")
        print (pformat(master))
        
    def _deadCode(self):
        if True:
            return
        if False:
            #    data = json.load(data_file)
            #pprint (data["post_new_vps_response"]["about_order"]["order_oid"])
            if args.cluster in list(objectpath.Tree(vmargs).execute("$.meta_data[@.key_name is 'com.rimuhosting.kclusterid'].value")):
                raise Exception("That cluster already exists.  Delete it or create a new one.")
                #foo = [match.value for match in jsonpath_expr.find({'meta_data': [{'key_name' : 'com.rimuhosting.kclusterid'}]})]
                #foo = [match.value for match in jsonpath_expr.find({'meta_data'})]
            if existing.length>0:
                raise Exception("Cluster " + args.cluster + " already exists.")
        
            print ('vma=')
            pformat(vmargs)
            print ('vmab=')
            print(json.dumps(vmargs))
            print ('vmax=')
            print(vmargs)
            print ("loaded")
            if False:
                debug("klusterids not found in the server json")
                if not args.cluster:
                  raise Exception("The cluster master requires a $.meta_data[@.key_name is 'com.rimuhosting.kclusterid'].value or a --id argument")
                debug("using the command line supplied cluster name of " + args.cluster)
                klusterids = [ args.cluster ]
            else:
                klusterids = list(klusterids)        #xpr = parse('*.value')
        
            if len(list(klusterids))==0:
                raise Exception("The cluster master requires a $.meta_data[@.key_name is 'com.rimuhosting.kclusterid'].value")
            if len(klusterids)>1:
                raise Exception("The cluster master requires a single $.meta_data[@.key_name is 'com.rimuhosting.kclusterid'].value")
            if not klusterids[0]:
                raise Exception("The cluster master requires a non empty $.meta_data[@.key_name is 'com.rimuhosting.kclusterid'].value")
            args.cluster = klusterids[0]
            #foo = xpr.find({'meta_data': [{'value': 'foobar', 'key_name': 'com.rimuhosting.kclusterid'}]})
            #foo = xpr.find(json.dumps(vmargs))
            #print(objectpath.Tree(vmargs).execute("$.meta_data.[@key_name=='com.rimuhosting.kclusterid']"))
                #print(server_json)   
            #print("klusterids=",klusterids )
                        
if __name__ == '__main__':
    args = Args();
    args.run()


