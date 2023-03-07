# Docker compose file

## Dependencies

Docker must be installed on the machine also docker-compose must be accessible.


```bash
mkdir /etc/systemd/system/docker.service.d
touch http-proxy.conf
touch https-proxy.conf
```

Add in conf files 

```bash
[Service]
Environment="HTTPS_PROXY=http://proxy:8080"

```

__!!!!NB!!!!__

Please set the bind dir according to your disk location(change device param value with kube_api code location) where code is running.

```bash
volumes:
  app_sourcecode:
    driver_opts:
      type: none
      device: /path/kube_api/
      o: bind
```

## How to run

```bash
docker-compose up -d
```
This will build/build all the docker images:
 - docker_nginx 
 - docker_kube
 - docker_memcached
## Images

### docker_nginx

Docker file is located in docker_nginx directory.
Image is binding on port 8080 and is redirecting to upstream app(kube) port 5000. Please refer to
nginx.conf file

```bash
 # Enumerate all the Kube_API servers here
    upstream frontends {
        server kube:5000;
    }
```

### docker_kube

Docker file is located in docker_kube and it's containing the Kube code.
Image is binding on port 5000. It's possible to connect directly to 5000, but we do recommend to use the nginx frontend:8080

To start run 

````bash
docker-compose -f docker-compose.yml up -d
````


## Testing


### Seding a get request

```bash
"curl -i -H -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X POST -d '{"action":"create" }' http://localhost:5000/api/kube/namespace/apc-staging"
```

The response is written on the websocket

```bash
"HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 34
Server: Werkzeug/0.14.1 Python/2.7.15
Date: Tue, 05 Feb 2019 14:28:20 GMT

Namespace apc-staging-test created "

```