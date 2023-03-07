# Pull base image.
FROM debian:latest

# let's have a nice motd message
COPY assets/motd /etc/motd

#let's update
RUN apt-get update

#let's install the internet
RUN apt-get install -y --force-yes \
		apt-utils \ 
		supervisor \
		wget \
		htop \
		nginx\
		telnet \
		python \
		python-pip \
	&& rm -rf /var/lib/apt/lists/*

# let's have the wait_for_it_script.sh
ADD assets/wait_for_it.sh /usr/local/bin/


# let's make the opt dir

RUN mkdir -p /opt/kube/

# let's install python dependencies list

RUN pip install kubernetes requests setuptools oauth2client httplib2 urllib3 rsa PyYaml requests requests-oauthlib requests-toolbelt paramiko sqlalchemy flask_sqlalchemy Flask flask_request_validator flask-restful-swagger Flask-API flask-restful functools32 jsonschema flask_monitoringdashboard decorator plotly==2.2.0 configparser python-memcached-stats pymemcache itsdangerous python-ldap
WORKDIR /opt/kube/
EXPOSE 5000

# Define default command.
CMD /usr/local/bin/wait_for_it.sh -h $NGINX_HOST -p 8080 --timeout=50 --strict -- \  
    "python kube_proxy.py"
