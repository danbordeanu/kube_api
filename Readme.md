# KUBERNETES API 

A python-based application capable of managing the Kubernetes cluster using REST/API calls.

## Introduction

This is a very complex API endpoint able to deploying services, namespaces, load balancer, ingress and pods into the 
kubernetes cluster making the live of developers a bliss without using the yaml files and kubectl command tool.

## Instalation

### Prerequisites

1. python 
2. nginx (optional, but recommended). nginx.conf is provided in git (EXTERNAL_CONFIGS/nginx) 
3. ssl certs from kube/config file
4. memcached server (used to store tokens)

### Getting the ssl certs and populating the config.ini file

KUBE_API is using ssl cert file to authenticate, take a look at the __config.ini__ file

```bash
# certificate-authority-data
ssl_ca_cert_file: ssl/ca_cert.crt
# client-certificate-data
ssl_cert_file: ssl/cert_file.crt
# client-key-data
ssl_key_file: ssl/key_file.crt
```

**__!!!NB!!!__** The path to cert files can be passed at start-up as env vars:

```bash
export host=https://aks-cluster.hcp.eastus.azmk8s.io:443
export ssl_cert_file=ssl_prod_new/cert_file.crt 
export ssl_key_file=ssl_prod_new/key_file.crt 
export ssl_ca_cert_file=ssl_prod_new/ca_cert.crt
```

The ssl certs are extracted from the kube config file:

```
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: XXXX
    server: https://aksclu.hcp.eastus.azmk8s.io:443
  name: aksclu01
contexts:
- context:
    cluster: aksclu01
    user: clusterAdmi
  name: aksclu01-admin
current-context: aksclu01-admin
kind: Config
preferences: {}
users:
- name: clusterAdmin
  user:
    client-certificate-data: XXXX
    client-key-data: XXXX
    token: XXXX

```

__!!!NB!!!__ all certs file are base64 encoded. Take a look at the test/give_me_certs.py utility for extracting the cert files


## Creating roles and binding users to namespaces

This feature is required in order to ensure users will be assigned to a specific namespace.  

### Python utility

#### Create role and binding (role=username@mail.com and rolebinding=service-reader-username@mail.com)

```bash
python role_binding.py --username=user@email.com --namespace=namespace_name --action=create

```

**__!!!NB!!!__** username(this is the name of the ROLE) must be the same one used to authenticate. If role is not created and not assigned/bound to a namespace
it will not be able to perform any operation.


#### Create generic role (role=genericname)

This will create a generic role. Bind users to this role in order to have permissions

```bash
python role_binding.py --role=supergeneric --namespace=ns-staging --action=create
```


#### Delete a generic role from a namespace

Delete a generic role from a namespace

```bash
python role_binding.py --role=supergeneric --namespace=ns-staging --action=delete
```

#### Bind username to the generic role in a namespace

Bind username to a generic role

```bash
python role_binding.py --role=supergeneric --username=bordeanu@mail.com --namespace=ns-staging --action=bind
```

#### Unbind username from a generic role in a namespace

By doing this, user will be unbinded and access to resources is removed (**NB** this is not removing the role)

```bash
python role_binding.py --role=supergeneric --username=bordeanu@mail.com --namespace=ns-staging --action=unbind
```

#### Delete role and binding for a user

Delete role and the binding

```bash
python role_binding.py --role=bordeanu@mail.com --username=bordeanu@mail.com --namespace=ns-staging --action=delete
```


#### Yaml example:

##### Role:

**!!NB!!** The name of the ROLE it has nothing to do with the name of the user. We use this name just to do validation inside of the API

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: ns-staging #namespace 
  name: ysw@mail.com #name of role, do use the username address, since we do API validation based on role name
rules:
- apiGroups: ["", "extensions", "app", "batch", "autoscaling", "sc", "storage.k8s.io"] # "" indicates the core API group
  resources: ["pods", "deployments", "replicasets", "secrets", "cronjobs", "hpa", "volumeattachments", "ingresses", "services", "storageclasses", "jobs", "configmaps", "persistentvolumeclaims", "persistentvolumes"] # resources
  verbs: ["get", "watch", "list", "update", "delete", "patch", "create"] # permissions
```

More info about resources type: https://kubernetes.io/docs/reference/kubectl/overview/#resource-types

##### Role binding:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: reader-service #name of the binding
  namespace: ns-staging #namespace
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: ysw@mail.com # reference of the Role
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: User 
  name: ysw@mail.com # username
  namespace: ns-staging # namespace
```

More info about RBAC: https://kubernetes.io/docs/reference/access-authn-authz/rbac/

### Role binding validation


User should be able to perform any operation specified in verbs list on the resources list from the apiGroup. 

```bash
$ kubectl auth can-i get volumeattachments --namespace ns-staging --as ysw@mail.com
yes
$ kubectl auth can-i get services --namespace ns-staging --as ysw@mail.com
yes
$ kubectl auth can-i get pods --namespace ns-staging --as ysw@mail.com
yes
$ kubectl auth can-i get jobs --namespace ns-staging --as ysw@mail.com
yes
$ kubectl auth can-i get cj --namespace ns-staging --as ysw@mail.com
yes
$ kubectl auth can-i get cronjobs --namespace ns-staging --as ysw@mail.com
yes
$ kubectl auth can-i get secrets --namespace ns-staging --as ysw@mail.com
yes
```

## Installing pip packages

```bash
pip install -r requirements.txt
```

## Starting the KUBE-API in 'standalone' mode

__!!!NB!!!__ change the config.ini settings in order to connect to different cluster

```bash
python kube_proxy.py
```
This method should be used __only__ for local development and is not intended for production.

When deployed as a docker container/pod kube_api can read env vars for config location (using external volumes, for example)


```bash
export host=https://mrlaks-6ce65b43.hcp.eastus.azmk8s.io:443
export ssl_cert_file=ssl_prod_new/cert_file.crt 
export ssl_key_file=ssl_prod_new/key_file.crt 
export ssl_ca_cert_file=ssl_prod_new/ca_cert.crt
export ingress_host=mrlit-appzone-prd.mail.com
export ingress_secret_name=test-tls
export MEMCACHED_HOST=memcached-service
export MEMCACHED_PORT=80
# not mandatory
# deployments limits/resources
export DEPLOYMENT_LIMITS_MEMORY=512Mi
export DEPLOYMENT_LIMITS_CPU=2
export DEPLOYMENT_REQUESTS_MEMORY=64Mi
export DEPLOYMENT_REQUESTS_CPU=100m
# namespace limits/resources
export NAMESPACE_REQUESTS_CPU=100m
export NAMESPACE_REQUESTS_MEMORY=256Mi
export NAMESPACE_LIMITS_CPU=4
export NAMESPACE_LIMITS_MEMORY=512Mi
export NAMESPACE_REQUESTS_STORAGE=64Gi
export NAMESPACE_SERVICE_NODEPORTS=10
```

## Running KUBE-API using Docker file

```bash
$ docker build -t kube_api_docker .
$ docker run -d -it --name kube_api -v /path/ssl:/tmp/ -e host=https://mrlaks-42987837.hcp.eastus.azmk8s.io:443 -e ssl_cert_file=/tmp/cert_file.crt -e ssl_key_file=/tmp/key_file.crt -e ssl_ca_cert_file=/tmp/ca_cert.crt -e MEMCACHED_HOST=172.17.0.2 -e ingress_host=mrlit-appzone-prd.mail.com -p 5000:5000 kube_api_docker
```

**__!!!NB!!!__** this require a running memcached server

## Installing using docker-compose

This is the recommended way to deploy the service. It requires running docker service.

```bash
cd docker/x64
docker-compose up -d
```

Compose will deploy all services: ngninx, memcached and kube_api

Service is accesible calling the nginx port:8080, all request are redirected to kube_api:5000


## Login and using the tokens

### Using curl commands

```bash
curl -i -H "Content-Type: application/json"  -X POST -d '{"password":"base64encoded"}' http://http://localhost:5000/api/kube/login/bordeanu@mail.com

```

### Using login util command

```bash
$ ./login 
Simple get token app using real user/password
Kube endpoint: http://localhost:5000
Kube user: bordeanu@mail.com
```

!!!NB!!! Please export env vars

```bash
export KUBE_PASSWORD=XXXXXXXbase64encodedpasswd
export KUBE_USER=bordeanu@mail.com
export KUBE_API=http://localhost:5000

```

## How to encode the password with python

```python
import base64
print base64.b64encode('mysuperpasssword')
```

## Sending get and post requests from command line

Create a namespace, ex:

```bash
curl -i -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X POST -d
    '{"action":"create", "options": {"owner":"teamowner"}}' http://localhost:5000/api/kube/namespace/ns-staging
```

Using the kube_testing_menu.sh utility.

(this is for the kube_Api running in azure)

```bash
export KUBE_HOST=https://mrlaks-api-stg.mail.com 
export KUBE_TOKEN=XXXXXXXXXXXXX
```

!!!NB!!! in case the KUBE_HOST env var is missing, the script will use default value localhost:5000

## Unittests

```bash
$ python api_test.py
```


!!!NB!!! The api_test.py can be used using real user/passd or fake/moked users (it will require access to a memcached server to insert the tokens)

For real username/passwd:

```bash
export KUBE_USER=user@mail.com
export KUBE_PASSWORD=base64encodedpassword
```

```python
 if self.username and self.password:
            # use real login endpoint
            login_data = dict(password=self.password)
            self.token = requests.post(self.host + self.login_url + '/' + self.username,
                                       headers={'Content-Type': 'application/json'}, data=json.dumps(login_data)).text
        else:
            # let's fake the token
            login_management = LdapUserAuth()
            login_management.insert_token_memcache(self.fake_username,
                                                   login_management.generate_auth_token(self.fake_username))
            self.token = login_management.get_token_memcache(self.fake_username)

```

This is calling the API and parsing the response content. !!!NB!!! this is just a simple validator and not some fancy REST/API framework.

## API docs


All endpoints are documented using [swagger](http://localhost:5000)


## Logs

docker-compose is using the default docker logs. There are no options configured for logger service.

```bash
docker logs x64_kube_1
docker logs x64_nginx_1
docker logs x64_memcached_1
```

__!!!NB!!!__ All kube_api logs are located in logs directory

