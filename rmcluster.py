import argparse
import os
import json, sys
import urllib.request
from pprint import pprint
from pprint import pformat
import rimuapi
# from jsonpath_rw import jsonpath, parse
import objectpath

class Args(object):
    def __init__(self):
        parser = argparse.ArgumentParser(description="Delete/shutdown all VMs associated with a RimuHosting Kubernetes cluster.")
        parser.add_argument("--cluster", required=True, help="Unique id for this cluster.  e.g. cluster1")
        parser.parse_args(namespace=self)
    
    def run(self):
        xx = rimuapi.Api()
        # minions first
        master = xx.orders('', {'server_type': 'VPS','meta_search': 'com.rimuhosting.kclusterid:'+self.cluster+' com.rimuhosting.kismaster:Y'})
        if not master or len(master)==0:
            raise Exception("Could not find a master VM for that cluster.")
        minions = xx.orders('N', {'server_type': 'VPS','meta_search': 'com.rimuhosting.kclusterid:'+self.cluster+' com.rimuhosting.kisminion:Y'})
        output = []
        for order in minions:
            #print("deleting " + str(order["order_oid"]))
            resp = xx.delete(order_oid=order["order_oid"])
            output.append(resp)
        # then master          
        for order in master:
            #print("deleting " + str(order["order_oid"]))
            resp = xx.delete(order_oid=order["order_oid"])
            output.append(resp)
        print(pformat(output))
                        
if __name__ == '__main__':
    args = Args();
    args.run()


