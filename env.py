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
        parser = argparse.ArgumentParser(description="Get a set of environment variables that may be of use.  e.g. for Kubernetes pod file variable expansions per http://kubernetes.io/v1.0/docs/design/expansion.html.")
        parser.add_argument("--cluster", required=True, help="kcluster id.  e.g. cluster1")
        parser.parse_args(namespace=self)
    
    def getExports(self):
        xx = rimuapi.Api()
        # has a specific cluster id, is active, is master
        master = xx.orders('N', {'server_type': 'VPS','meta_search': 'com.rimuhosting.kclusterid:'+self.cluster+' com.rimuhosting.kismaster:Y'})
        if not master or len(master)==0:
            raise Exception("No such cluster located.")
        output = []
        for order in master:
            output.append("export KUBERNETES_MASTER_IPV4=" + order["allocated_ips"]["primary_ip"])
            output.append("export KUBERNETES_MASTER_ORDER_OID=" + str(order["order_oid"]))
            output.append("export SERVER_ARG='--server=http://" + order["allocated_ips"]["primary_ip"]+":8080'")
            output.append("alias rkubectl='kubectl $SERVER_ARG'")
            output.append("alias rkubectlgetall='rkubectl get pods,services,replicationcontrollers,nodes,events,componentstatuses,limitranges,persistentvolumes,persistentvolumeclaims,resourcequotas,namespaces,endpoints,serviceaccounts,secrets  --all-namespaces -o=wide'")
        minion_ips=""
        minion_order_oids=""
        minions = xx.orders('N', {'server_type': 'VPS','meta_search': 'com.rimuhosting.kclusterid:'+self.cluster+' com.rimuhosting.kisminion:Y'})
        for order in minions:
            minion_ips = minion_ips + " " + order["allocated_ips"]["primary_ip"]
            minion_order_oids = minion_order_oids + " " + str(order["order_oid"])
        output.append("unset KUBERNETES_MINION_IPV4S")
        output.append("declare -a KUBERNETES_MINION_IPV4S")
        output.append("export KUBERNETES_MINION_IPV4S=(" + minion_ips + " )")
        output.append("export KUBERNETES_MINION_ORDER_OIDS=(" + minion_order_oids + " )")  
        
        return output
                        
if __name__ == '__main__':
    args = Args();
    for export in args.getExports():
        print(export)


