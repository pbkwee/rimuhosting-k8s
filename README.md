# About rimuhosting-k8s
Command line python apps for setting up Kubernetes clusters on RimuHosting VMs

# Using rimuhosting-k8s
Get a server API key at https://rimuhosting.com/cp/apikeys.jsp

If you do not already have a server with us, you will need to email RimuHosting and ask them to enable automated server setups on your account.

Git clone this project as well as https://github.com/pbkwee/RimuHostingAPI.  The https://github.com/pbkwee/RimuHostingAPI project has a few changes required for rimuhosting-k8s and Python3.  

Then on both run:
```
python3 setup.py build install
```

You should now be able to use the RimuHostingAPI Python library and rimuhostingk8s command line tools.

Create the master node:

```
$ python3 mkmaster.py --server_json sample-configs/unmodified/servers/server.json \
--cloud_config sample-configs/defaults/cloud-init/master.yaml \
--cluster cluster1
```

See that node:

```
$ python3 lscluster.py 
{'cluster_masters': [{'cluster': 'cluster1',
                      'dc_location': 'DCDALLAS',
                      'domain_name': 'coreosmaster.localhost',
                      'memory_mb': 4096,
                      'order_oid': 916284575,
                      'primary_ip': 'xx.xx.xx.xx',
                      'running_state': 'RUNNING'}]}
```

Create a few minions:

```
j=0
for i in DCDALLAS DCAUCKLAND DCFRANKFURT; do 
j=$((j+1)); 
python3 mkminion.py --server_json sample-configs/unmodified/servers/server.json \
--cloud_config sample-configs/defaults/cloud-init/node.yaml --cluster cluster1 \
--dc_location $i --domain_name coreos-minion-$j-$i.localhost &
done
```
See all those minions:

```
python3 lscluster.py --cluster cluster1
```

See export variables for this cluster:

```
$python3 env.py --cluster cluster1 
export KUBERNETES_MASTER_IPV4=xx.xx.xx.xx
export SERVER_ARG='--server=http://xx.xx.xx.xx:8080'
alias rkubectl='kubectl $SERVER_ARG'
unset KUBERNETES_MINION_IPV4S
declare -a KUBERNETES_MINION_IPV4S
export KUBERNETES_MINION_IPV4S=( xx.xx.yy.yy xx.xx.yy.zz )
```

Set those variables in the current shell environment:

```
$ python3 env.py --cluster cluster1 > .config; source .config
```

Iterate over your minion VM ips:

```
$ for i in ${KUBERNETES_MINION_IPV4S[@]}; do echo $i; done
xx.xx.yy.yy
xx.xx.yy.zz
```

See your 'empty' kubernetes cluster:

```
rkubectl get all
CONTROLLER   CONTAINER(S)   IMAGE(S)   SELECTOR   REPLICAS   AGE
NAME         CLUSTER_IP   EXTERNAL_IP   PORT(S)   SELECTOR   AGE
kubernetes   10.100.0.1   <none>        443/TCP   <none>     45m
NAME      READY     STATUS    RESTARTS   AGE
NAME      LABELS    STATUS    VOLUME    CAPACITY   ACCESSMODES   AGE
```

Load a simple test pod:

```
$ rkubectl create -f sample-configs/unmodified/busybox.yaml 
pod "busybox" created

$ rkubectl get pods
NAME      READY     STATUS    RESTARTS   AGE
busybox   1/1       Running   0          37s
```

Run something in it:
```
$ rkubectl exec busybox -- echo 'Hello, world!'
Hello, world!
```

Setup the guestbook app:

```
# substitute the ip address for the environment value
$ rkubectl create  -f <(cat sample-configs/defaults/skydns-controller.yaml | replace '$(KUBERNETES_MASTER_IPV4)' "${KUBERNETES_MASTER_IPV4}") 

$ for i in \
sample-configs//defaults/skydns-service.yaml \
sample-configs//unmodified/guestbook/redis-master-controller.yaml \
sample-configs//unmodified/guestbook/redis-master-service.yaml \
sample-configs//unmodified/guestbook/redis-slave-controller.yaml \
sample-configs//unmodified/guestbook/redis-slave-service.yaml \
sample-configs//unmodified/guestbook/frontend-service.yaml \
sample-configs//unmodified/guestbook/frontend-controller.yaml; do 
  rkubectl create -f $i
done

```

See all of the new pods.  Include --all-namespaces to include the kube-dns pods which are running in a kube-system namespace.

```
$ rkubectl get all --all-namespaces
NAMESPACE     CONTROLLER         CONTAINER(S)   IMAGE(S)                                         SELECTOR                      REPLICAS   AGE
default       frontend           php-redis      kubernetes/example-guestbook-php-redis:v2        name=frontend                 3          21s
default       nginx-controller   nginx          nginx                                            app=nginx                     2          26s
default       redis-master       master         redis                                            name=redis-master             1          17s
default       redis-slave        worker         kubernetes/redis-slave:v2                        name=redis-slave              2          14s
kube-system   kube-dns-v9        etcd           gcr.io/google_containers/etcd:2.0.9              k8s-app=kube-dns,version=v9   2          24s
                                 kube2sky       gcr.io/google_containers/kube2sky:1.11                                         
                                 skydns         gcr.io/google_containers/skydns:2015-03-11-001                                 
                                 healthz        gcr.io/google_containers/exechealthz:1.0                                       
NAMESPACE     NAME           CLUSTER_IP      EXTERNAL_IP   PORT(S)         SELECTOR            AGE
default       frontend       10.100.168.70   nodes         80/TCP          name=frontend       19s
default       kubernetes     10.100.0.1      <none>        443/TCP         <none>              51m
default       redis-master   10.100.254.67   <none>        6379/TCP        name=redis-master   16s
default       redis-slave    10.100.53.177   nodes         6379/TCP        name=redis-slave    13s
kube-system   kube-dns       10.100.88.88    nodes         53/UDP,53/TCP   k8s-app=kube-dns    23s
NAMESPACE     NAME                     READY     STATUS    RESTARTS   AGE
default       busybox                  1/1       Running   0          4m
default       frontend-9les5           0/1       Pending   0          21s
default       frontend-g1i7t           0/1       Pending   0          21s
default       frontend-g6c9q           0/1       Pending   0          21s
default       nginx-controller-5gqxy   0/1       Pending   0          26s
default       nginx-controller-643wp   1/1       Running   0          26s
default       redis-master-t4l3p       0/1       Pending   0          17s
default       redis-slave-gewmp        0/1       Pending   0          14s
default       redis-slave-qqlfa        0/1       Pending   0          14s
kube-system   kube-dns-v9-9h2ub        0/4       Pending   0          24s
kube-system   kube-dns-v9-icyqd        0/4       Pending   0          24s
NAMESPACE   NAME      LABELS    STATUS    VOLUME    CAPACITY   ACCESSMODES   AGE
```

Figure out the external port for the frontend service:

```
$ rkubectl  get svc frontend -o json | grep  "nodePort"
                "nodePort": 31108
```

See the IPs that the frontend service pods are running on:
```
$ rkubectl  get pods -o wide | egrep 'NODE|frontend'
NAME                 READY     STATUS    RESTARTS   AGE       NODE
frontend-67zo9       1/1       Running   0          8m        xx.xx.xx.yy
frontend-ch4o5       1/1       Running   0          8m        xx.xx.xx.zz
frontend-xcgc8       1/1       Running   0          8m        xx.xx.xx.zz
```

Then browse to that NODE:nodePort value.  e.g. http://xx.xx.xx.yy:31108

Additional tips:
- add a --isreinstall to mkmaster to do a clean reinstall there.
- add a --reinstall_order_oid to mkminion to do a clean reinstall of a minion
- run rmcluster --cluster cluster1 to delete all the servers (master and minions) in a cluster

TODO: 
- dns is currently broken somehow in the sample guestbook app above and is in needing of debugging.
- Need to add security to the master API (e.g. using secret tokens, or sharing around ca certs).

If you would like to work on the TODO list, please fork the project and contribute back.  Email support at rimuhosting before you start working on the TODO list to double-check it is current and we can pay a bounty for completing these tasks.
