# KUBE PUSH NOTIFICATION INFRA

A python-based application capable of sending notification using websockets and REST/API calls

## Introduction

This is a very complex application capable of making SERVICE ip queries by calling the KUBE-API and writing the ip 
to a websocket.

## Instalation


#### Prerequisites

Project requires 2 services in order to run and a few python libs

- rabbitmq-server
- memcached

Installing pip packages

```bash
pip install -r kubepushnotif/requirements.txt 
```


Starting the KUBEPUSHNOTIFICATION

!!!NB!!! Change the config.ini settings in order to connect to a different host running rabbitmq/memcached. 
By default KUBEPUSHNOTIFICATION is connecting to localhost.

### OPTION A: Installing and running using docker

This is the recommended way to deploy the service. It requires running docker service


```bash
cd kubepushnotif
docker build -t eg_kubepushnotif_exp .
docker run -d --name test_kubepush -p 8889:8888 -e RABBITMQ_HOST='10.196.232.11' -e RABBITMQ_PORT='5672' -e MEMCACHED_HOST=10.196.232.11  -e KUBE_API=http://10.196.232.11:5000 eg_kubepushnotif_exp
```

Service is accessible calling port:8889, all request are redirected to kubepushnotification:8888

!!!NB!!! This is using the real KUBE-API endpoint, so real services and namespaces must be provided.

 ## Testing
 

### Creating a websocket

```bash
wscat -c ws://localhost:8889/register?userid=bordeanu
```

### Seding a get request

```bash
curl 'http://localhost:8889/push?userid=dan&service=push-service&namespace=apc-staging'
```

If the Service has IP  assigned, the response is written on the websocket

```bash
[{"REST_tornado - servicestatus: ": {"IP": "172.16.81.10", "SERVICE_NAME": "push-service"}}, {" Iteration ": 2}]
```

There is a python utility build in test directory

```bash
sh -x start_client.sh
```

!!!NB!!! do change the port variable and user name and in ws_client_exp.py change the ws://localhost value according to where the service is running 


### LOGS

docker is using the default docker logs. There are no options configured for logger service.

```bash
docker logs eg_kubepushnotif_exp 
```

## Authors
**Dan Bordeanu**