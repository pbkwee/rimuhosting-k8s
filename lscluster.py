import argparse
import os
import json,sys
import urllib.request
from pprint import pprint
from pprint import pformat
import rimuapi
#from jsonpath_rw import jsonpath, parse
import objectpath

class Args(object):
    def __init__(self):
        parser = argparse.ArgumentParser(description="Provide a listing of all the clusters associated with this RimuHosting API key.  Or if you provide a --cluster arg, then list all the VMs associated with that cluster.")
        parser.add_argument("--cluster", required=False, help="kcluster id.  e.g. cluster1")
        parser.parse_args(namespace=self)
    def _getSimplifiedOrder(self, order):
        cluster = objectpath.Tree(order).execute("$.meta_data[@.key_name is 'com.rimuhosting.kclusterid'].value")
        details = objectpath.Tree(order) 
        ip = details.execute("$.allocated_ips.primary_ip")
        #print(pformat(order))
        summary = {"order_oid" : order["order_oid"], "cluster" : "" if cluster is None else list(cluster)[0]
                   , "primary_ip" : "" if ip is None else ip
                   , "domain_name" : order["domain_name"]
                   , "dc_location" : order["location"]["data_center_location_code"], "running_state" : order["running_state"], "memory_mb" : details.execute("$.vps_parameters.memory_mb"), "order_description" : details.execute("$.order_description") }
        return summary
    
    def clusterList(self):
        xx = rimuapi.Api()
        # has a cluster id, is active, is master
        existing = xx.orders('N', {'server_type': 'VPS','meta_search': 'com.rimuhosting.kclusterid: com.rimuhosting.kismaster:Y'})
        output = {}
        output["cluster_masters"] = []
        for order in existing:
            output["cluster_masters"].append(self._getSimplifiedOrder(order))
        print(pformat(output))
            

    def clusterDetail(self):
        xx = rimuapi.Api()
        # has a specific cluster id, is active, is master
        existing = xx.orders('', {'server_type': 'VPS','meta_search': 'com.rimuhosting.kclusterid:'+self.cluster+' com.rimuhosting.kismaster:Y'})
        output = {}
        for order in existing:
            output["cluster_master"] = self._getSimplifiedOrder(order)
                  
        existing = xx.orders('N', {'server_type': 'VPS','meta_search': 'com.rimuhosting.kclusterid:'+self.cluster+' com.rimuhosting.kisminion:Y'})
        output["minions"]=[]
        for order in existing:
            output["minions"].append(self._getSimplifiedOrder(order))
        
        print(pformat(output))
                        
if __name__ == '__main__':
    args = Args();
    if args.cluster:
        args.clusterDetail()
    else: 
        args.clusterList()


