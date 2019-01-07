# How I Learned to Stop Worrying and Love Kubernetes


The Kubernetes ecosystem, or k8s, is a full five-ring circus.  I have never met
a technology more confounding, complicated, or central to the future of
computing in my decades long career.  K8s is said to have the second largest
community of open source developers of all open source projects, behind only
the Linux kernel.  I am going to try to write this guide from the perspective
of someone who knows a lot about writing, building, and deploying software, but
almost nothing about k8s, because that is what I am.  I am learning as I write
this.  If you discover anything inaccurate or mistaken here, please do not
hesitate to correct me and I will update this blog post.

What is k8s?  K8s is an open-source container-orchestration system for
automating deployment, scaling, and management of containerized applications.
It originated at Google but is now maintained by an independent foundation
caleld the Cloud Native Computing Foundation.  Founding members included
Google, Twitter, Huawei, Intel, Cisco, IBM, Docker, Univa, and VMware.  The
goal of k8s is to help you manage huge swarms of containerized applications,
which interact and talk to eachother and persist state and get upgraded and
downgraded and scaled.

You should consider using k8s if you are:
* Writing an application which must be scalable
* Writing an application which must be fault-tolerant
* Writing an application which is composed of multiple services
* Writing an application which must support rolling upgrades

First, a glossary of terms:

* Container - an operating-system-level virtualization, allowing the existence of multiple isolated user-space instances.  Docker is a common example of a containerization engine which you can use to run applications in containers.  Applications running inside a container can only see the container's contents and devices assigned to the container.
* Kubernetes (k8s) - an open-source container orchestration system
* node - a VM or physical machine that serves as a worker for a k8s cluster.  A production k8s cluster should have a minimum of 3 nodes.
* master - The master is responsible for managing the cluster's resources.  It schedules applications to run on various nodes, maintains state, scales applications, and rolls out updates
* pod - a pod is a k8s abtraction that represents a group of one or more containers and some related shared resources (storage, networking, metadata like ports) for those containers.
* Docker - a common containerization runtime
* rkt - a slightly-less-common containerization runtime (produced for CoreOS)
* minikube - a tool that makes it easy to run k8s locally.  minikube runs a single-node k8s cluster inside a VM on your machine for testing or development.
* Helm - often called "the k8s package manager", helm is a tool of defining how a k8s application is deployed and upgraded.  If you want to run a k8s friendly application, it is likely you can simply get its "helm chart" and run it using helm.
* Skaffold - A CLI tool that facilitates continuous development for k8s applications.
* kubectl - the CLI tool with which you issue commands to a k8s cluster
* kubeadm - the CLI tool with which you actually start and administer a k8s cluster in production (as opposed to using, e.g. minikube)

# From the Ground Up

To understand k8s, we are going to build a k8s application from the ground up.
All applications start with a container.  We will make a hello, world
application in a container, using docker.

## It's like, just an application, man!

Dependencies:
* python2
* curl

Next to this tutorial, you will find the `server` directory containing server.py.  You can run server.py directly if you have python2 installed, it has no external dependencies.

    $ ./server.py &
    [1] 5624
    ('Started http server on port ', 8080)
    $ curl http://localhost:8080
    127.0.0.1 - - [05/Oct/2018 16:10:18] "GET / HTTP/1.1" 200 -
    Hello, World!
    $ kill %1
    [1]  + 5624 terminated  ./server.py

That's it, pretty simple!

## Containerize your excitement

Dependencies:
* Functioning install of Docker
* curl

Also in the `server` directory, you will find a Dockerfile.  This file is pretty straightforward.  In it, we start with a clean python container that makes python2 available, and we copy in the "hello world" python server.  You can run the server in a container using docker by doing the following:

    docker build -t python-server .
    docker run -P -it --rm --name python-server-run python-server

The "-it" means run in an interactive terminal.  You could leave that out if you want it to run in the background.  The "-P" means publish our exposed ports.  You could instead explicitly give a port mapping using "-p 8080:8080".  Once the container is running, you can validate the ports by running "docker port python-server-run".  This outputs the randomly chosen port (if you give "-P") or confirms the given port (if you give "-p 8080:X").

Once you determine the mapped port, you can hit it just like when you ran the server without the container.
In particular, the Dockerfile has to expose the port the server runs on (by default, this is port 8080, but we want that to be configurable in future steps).

Here is the complete demo including shell output:

    $ docker build -t python-server .
    Sending build context to Docker daemon   55.3kB
    Step 1/5 : FROM python:2
     ---> 4ee4ea2f0113
    Step 2/5 : WORKDIR /usr/src/app
     ---> e6cf49026690
    Removing intermediate container b52e6cb8c1cb
    Step 3/5 : COPY server.py ./
     ---> d9d21459b0aa
    Removing intermediate container dcee52383d76
    Step 4/5 : EXPOSE 8080/tcp
     ---> Running in c2a88532ea2a
     ---> 4aac7f2bb52c
    Removing intermediate container c2a88532ea2a
    Step 5/5 : CMD python ./server.py 8080
     ---> Running in 4a90d6c51fc2
     ---> 006c4826dc2d
    Removing intermediate container 4a90d6c51fc2
    Successfully built 006c4826dc2d
    Successfully tagged python-server:latest
    $ docker run -P --rm --name python-server-run python-server *
    [1] 11574
    $ docker port python-server-run
    8080/tcp -> 0.0.0.0:32770
    $ curl http://localhost:32770/
    Hello, World!
    10.250.0.1 - - [05/Oct/2018 21:23:53] "GET / HTTP/1.1" 200 -
    $ docker stop python-server-run
    python-server-run
    [1]  + 11574 exit 137   docker run -P --rm --name python-server-run python-server

## Yo dawg, I heard you like containers...

* virtualbox || vmwarefusion || kvm2 || kvm || hyperkit (I used virtualbox)
* Functioning install of Docker

### Install the World

We will next set up a development environment so we can run k8s stuff locally.  I performed these steps on a standard Debian Linux machine, but I avoided reliance on the package manager for anything that isn't likely to be present on every common Linux distro as well as homebrew.

### Install `kubectl`

`kubectl` is the main command by which you interact with kubernetes clusters.  On debian, you can install it using your package manager, like this:

    sudo apt-get update && sudo apt-get install -y apt-transport-https
    curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
    echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
    sudo apt-get update
    sudo apt-get install -y kubectl

On a mac, you can do `brew install kbuernetes-cli`.

Alternately, you can install it as part of the google cloud SDK.  Download the SDK [here](this: https://cloud.google.com/sdk/), then run `gcloud components install kubectl`.

Finally, you could elect to just download a pre-built binary:

Linux: curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
Mac: curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/darwin/amd64/kubectl
Windows: curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.12.0/bin/windows/amd64/kubectl.exe (replacing v1.12.0 with the latest version)

How does `kubectl` even work, anyways?  Well, when you successfully run minikube or start a cluster with kube-up, a kubeconfig file is created automatically.  On Linux (and probably mac?) this file is in ~/.kube/config, but you hopefully won't have to touch it.

### Minikube

Minikube is a binary tool released by google that uses a "VM Driver" (such as virtualbox) to run a virtual machine which can run your k8s pods inside it, right on your current machine, regardless of OS.  This is the standard way to do k8s development.

You can download the Minikube binaries for v0.30.0 from the following links:
Linux: https://storage.googleapis.com/minikube/releases/v0.30.0/minikube-linux-amd64
Mac: https://storage.googleapis.com/minikube/releases/v0.30.0/minikube-darwin-amd64
Windows: https://storage.googleapis.com/minikube/releases/v0.30.0/minikube-windows-amd64.exe (experimental)

You can see the latest release by checking out https://github.com/kubernetes/minikube/releases - this site also contains sha256 hashes you can verify.

Once the binary is downloaded, chmod +x and place it on your path (i.e. in ~/bin).

    $ minikube start
    Starting local Kubernetes v1.10.0 cluster...
    Starting VM...
    Downloading Minikube ISO
    160.27 MB / 160.27 MB [============================================] 100.00% 0s
    Getting VM IP address...
    Moving files into cluster...
    Setting up certs...
    Connecting to cluster...
    Setting up kubeconfig...
    Starting cluster components...
    Kubectl is now configured to use the cluster.
    Loading cached images from config file.

All together, the start takes about 2 minutes plus however long it takes to download the image.  You will now see a headless virtualbox running:

    $ ps auxwwwfg | grep VBoxHeadless
    cmyers   17766 32.7  0.1 3957572 105088 ?      Sl   14:58   8:50  \_ /usr/lib/virtualbox/VBoxHeadless --comment minikube --startvm 36955125-c8c6-4c96-bf63-16251960c40b --vrde config

You can now invoke `kubectl` and it can tell you the version of kubernetes running in your minikube:

    $ kubectl version
    Client Version: version.Info{Major:"1", Minor:"12+", GitVersion:"v1.12.0-rc.1", GitCommit:"3e4aee86dfaf933f03e052859c0a1f52704d4fef", GitTreeState:"clean", BuildDate:"2018-09-18T21:08:06Z", GoVersion:"go1.10.3", Compiler:"gc", Platform:"linux/amd64"}
    Server Version: version.Info{Major:"1", Minor:"10", GitVersion:"v1.10.0", GitCommit:"fc32d2f3698e36b93322a3465f63a14e9f0eaead", GitTreeState:"clean", BuildDate:"2018-03-26T16:44:10Z", GoVersion:"go1.9.3", Compiler:"gc", Platform:"linux/amd64"}

You can see the k8s version in the client and server don't match, but they are close enough.  The Client version corresponds with kubectl, while the Server version is the version used by the master in your minikube cluster.

You can use kubectl to get some information about what is going on:

    $ kubectl cluster-info
    Kubernetes master is running at https://192.168.99.102:8443
    KubeDNS is running at https://192.168.99.102:8443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

    To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
    $ kubectl get nodes
    NAME       STATUS   ROLES    AGE   VERSION
    minikube   Ready    master   1h    v1.10.0

    $ kubectl get services
    NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
    kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   1h

    $ kubectl get deployments
    No resources found.

You can run a proxy that lets you communicate with the master.  By default, the cluster's networking is isolated inside the VM and not visible to your machine.

    $ kubectl proxy &
    [1] 16710
    Starting to serve on 127.0.0.1:8001
    $ curl http://localhost:8001/version
    {
      "major": "1",
      "minor": "10",
      "gitVersion": "v1.10.0",
      "gitCommit": "fc32d2f3698e36b93322a3465f63a14e9f0eaead",
      "gitTreeState": "clean",
      "buildDate": "2018-03-26T16:44:10Z",
      "goVersion": "go1.9.3",
      "compiler": "gc",
      "platform": "linux/amd64"
    }

We want to deploy our newly made docker containers to this cluster, however, there is a complexity.  The cluster has a docker registery inside it, which is distinct from your local registery into which our containers were built and tagged.  Publicly available containers will be fetched in either case, but if your container is not yet published, you need to get it into your minikube registery somehow.  You would think the solution would be simple but because running a registery securely is difficult and configuring docker daemons to allow connecting to an insecure registery is also difficult, the solution is actually non-obvious and fragile.  Docker magically understands that "localhost:5000" is ok to be insecure, so we just have to tie it all together so everything sees "localhost:5000" as the same registery.  Time for some port mapping!


First, we want to run a registery in our cluster.  I've included the fike kube-registery.yaml in this repo but I got it from a gist [here](https://gist.github.com/coco98/b750b3debc6d517308596c248daf3bb1/raw/6efc11eb8c2dce167ba0a5e557833cc4ff38fa7c/kube-registry.yaml).

*NOTE ABOUT NAMESPACES* This file, `kube-registery.yaml`, creates the registery in a namespace, so it will not show up in your commands by default.  Add `--all-namespaces` to see it after creating it.

    $ kubectl create -f kube-registry.yaml
    replicationcontroller/kube-registry-v0 created
    service/kube-registry created
    daemonset.extensions/kube-registry-proxy created
    $ kubectl get deployments --all-namespaces
    NAMESPACE     NAME                   DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
    kube-system   kube-dns               1         1         1            1           2h
    kube-system   kubernetes-dashboard   1         1         1            1           2h

Let's confirm the cluster can see it:

    $ minikube ssh
                             _             _
                _         _ ( )           ( )
      ___ ___  (_)  ___  (_)| |/')  _   _ | |_      __
    /' _ ` _ `\| |/' _ `\| || , <  ( ) ( )| '_`\  /'__`\
    | ( ) ( ) || || ( ) || || |\`\ | (_) || |_) )(  ___/
    (_) (_) (_)(_)(_) (_)(_)(_) (_)`\___/'(_,__/'`\____)

    $ curl -v http://localhost:5000/
    > GET / HTTP/1.1
    > Host: localhost:5000
    > User-Agent: curl/7.60.0
    > Accept: */*
    >
    < HTTP/1.1 200 OK
    < Server: nginx/1.11.8
    < Date: Mon, 08 Oct 2018 22:15:59 GMT
    < Content-Type: text/plain; charset=utf-8
    < Content-Length: 0
    < Connection: keep-alive
    < Cache-Control: no-cache
    <
    $ logout

Next, we set up the port forward so we can see it locally too.  We need to get the full name of the pod running the registery.

   $ kubectl get pods --namespace kube-system
   NAME                                    READY   STATUS    RESTARTS   AGE
   etcd-minikube                           1/1     Running   0          2h
   kube-addon-manager-minikube             1/1     Running   0          2h
   kube-apiserver-minikube                 1/1     Running   0          2h
   kube-controller-manager-minikube        1/1     Running   0          2h
   kube-dns-86f4d74b45-x227s               3/3     Running   0          2h
   kube-proxy-8pkl2                        1/1     Running   0          2h
   kube-registry-proxy-7l6rx               1/1     Running   0          25m
   kube-registry-v0-l6mdc                  1/1     Running   0          25m
   kube-scheduler-minikube                 1/1     Running   0          2h
   kubernetes-dashboard-5498ccf677-kjj68   1/1     Running   0          2h
   storage-provisioner                     1/1     Running   0          2h
   $ kubectl get po -n kube-system | grep kube-registry-v0 | cut -d' ' -f1
   kube-registry-v0-l6mdc
   $ kubectl port-forward -n kube-system $(kubectl get po -n kube-system | grep kube-registry-v0 | cut -d' ' -f1) 5000:5000 &
   [1] 17820
   Forwarding from 127.0.0.1:5000 -> 5000
   Forwarding from [::1]:5000 -> 5000
   $ curl -v http://localhost:5000/
   *   Trying ::1...
   * TCP_NODELAY set
   * Connected to localhost (::1) port 5000 (#0)
   > GET / HTTP/1.1
   > Host: localhost:5000
   > User-Agent: curl/7.52.1
   > Accept: */*
   >
   Handling connection for 5000
   < HTTP/1.1 200 OK
   < Cache-Control: no-cache
   < Date: Mon, 08 Oct 2018 22:29:01 GMT
   < Content-Length: 0
   < Content-Type: text/plain; charset=utf-8
   <
   * Curl_http_done: called premature == 0
   * Connection #0 to host localhost left intact

If you happen to be running on a mac (which I am not) and use docker-machine, there is one more step.  For details, see the original writeup I am cribbing off of by looking [here](https://blog.hasura.io/sharing-a-local-registry-for-minikube-37c7240d0615).

Success!  Now we can push our image to the registery and deploty it to our k8s cluster!

    # Yes, that's right - you literally have to tag the image with the hostname and port of the registery you wish to push to!  global namespaces, awesome!
    $ docker build . -t localhost:5000/python-server
    Sending build context to Docker daemon  87.55kB
    Step 1/5 : FROM python:2
     ---> 4ee4ea2f0113
    Step 2/5 : WORKDIR /usr/src/app
     ---> Using cache
     ---> e6cf49026690
    Step 3/5 : COPY server.py ./
     ---> Using cache
     ---> d9d21459b0aa
    Step 4/5 : EXPOSE 8080/tcp
     ---> Using cache
     ---> 4aac7f2bb52c
    Step 5/5 : CMD python ./server.py 8080
     ---> Using cache
     ---> 006c4826dc2d
    Successfully built 006c4826dc2d
    Successfully tagged localhost:5000/python-server:latest
    $ docker push localhost:5000/python-server
    < output is long and snip...>
    latest: digest: sha256:c146c7d09d88d217c139438799c3ae26f0a8ebe399d4d0251522a3b268d15c96 size: 2636
    $ kubectl run python-server-run --image=localhost:5000/python-server --port=8080
    kubectl run --generator=deployment/apps.v1beta1 is DEPRECATED and will be removed in a future version. Use kubectl create instead.
    deployment.apps/python-server-run created
    $ kubectl get deployments
    NAME                DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
    python-server-run   1         1         1            0           31s
    # wait wait wait....
    $ kubectl get deployments
    NAME                DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
    python-server-run   1         1         1            1           1m


There you have it, available => 1.  The service is up.  How do we hit our service now?  Just like with the registery, we need to map the port.

    $ kubectl port-forward $(kubectl get po | grep python-server-run | cut -d' ' -f1) 8080:8080 &
    [2] 26919
    Forwarding from 127.0.0.1:8080 -> 8080
    Forwarding from [::1]:8080 -> 8080
    $ curl http://localhost:8080/
    Handling connection for 8080
    Hello, World!

We just built a service from writing python all the way to having it running in a real k8s cluster!

It turns out, it is considered "bad form" to use a port forward to actually expose a service though.  Instead, you should expose the deployment.

    $ 

## Services Depending on Services

Let's leave aside our `server` app, and instead consider two microservices - `persistence_server` and `hash_server`.  These simple python services represent what might be a database and a front-end web app, respectively.  The persistence server will give a unique integer piece of data each time it is called (persistence is not kept across runs, however, for simplicity's sake - maybe we'll implement that later?).  The `hash_server` will request an integer from the persistence service for each request, then it will run sha256 on it, and return both results.  So here we have a set of interacting services with the following properties:

* There must be exactly one persistence server (if there were two copies, their resutls might conflict)
* There must be one or more hash servers, they can scale horizontally.
* Each hash server must be able to find the persistence server
* External users will want to call the hash server's API.

How do we set this up?  First, let's follow the pattern above and ensure we understand how these services work without containers, and then in raw docker.

    $ ./persistence_server/persistence_server.py 8081 &
    [1] 12431
    ('Started http server on port ', 8081)
    $ ./hash_server/hash_server.py 8080 localhost:8081 &
    [2] 12722
    ('Started http server on port ', 8080)
    $ curl http://localhost:8080/ | tail -n1 | jq
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
      0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0127.0.0.1 - - [16/Oct/2018 18:15:19] "GET / HTTP/1.1" 200 -
    127.0.0.1 - - [16/Oct/2018 18:15:19] "GET / HTTP/1.1" 200 -
    100   251    0   251    0     0   130k      0 --:--:-- --:--:-- --:--:--  245k
    {
      "data": {
        "number": 1,
        "hash": "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b"
      }
    }
    $ echo -n "1" | sha256sum
    6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b  -

Whelp, looks like all is well!  Good times.  But now, we need to do it in docker, and we need to tell the docker container running the hash server how to find the persistence server.  How does this work?

# Scaling your application...

TODO

# Charting a new Course with Helm...

TODO

# Using `skaffold` to Develop Rapidly

TODO

# Running your own etcd

If your application depends upon etcd, you will want to run your own (and not use the one that kubernetes is using).  It is a little hard to find references for how to run your own etcd which is not just replacing k8s etcd.

The latest etcd release can be found here: https://github.com/etcd-io/etcd/releases

These releases are built into images available here: https://quay.io/repository/coreos/etcd

As such, once you figure out the latest version (e.g. v3.3.10) you can do this:

    export HostIP="<your ip>"
    docker run --net=host \
        -d --name etcd-v3.3.10 \
        --volume=/tmp/etcd-data:/etcd-data \
        quay.io/coreos/etcd:v3.3.10 \
        /usr/local/bin/etcd \
        --name my-etcd-1 \
        --data-dir /etcd-data \
        --listen-client-urls http://0.0.0.0:2379 \
        --advertise-client-urls http://${HostIP}:2379 \
        --listen-peer-urls http://0.0.0.0:2380 \
        --initial-advertise-peer-urls http://${HostIP}:2380 \
        --initial-cluster my-etcd-1=http://${HostIP}:2380 \
        --initial-cluster-token my-etcd-token \
        --initial-cluster-state new \
        --auto-compaction-retention 1

We can turn this into a docker file, which is included in the "etcd" dir next to this guide.

# Resources Used:
* https://kubernetes.io/docs/tutorials/kubernetes-basics/create-cluster/cluster-intro/
* https://kubernetes.io/docs/tasks/tools/install-minikube/
* https://kubernetes.io/docs/tasks/tools/install-kubectl/
* https://github.com/kubernetes/minikube/releases
* https://github.com/coreos/etcd-operator/blob/master/README.md
* https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/
* https://medium.freecodecamp.org/expose-vs-publish-docker-port-commands-explained-simply-434593dbc9a3
* https://blog.hasura.io/sharing-a-local-registry-for-minikube-37c7240d0615
* https://www.katacoda.com/courses/kubernetes/


