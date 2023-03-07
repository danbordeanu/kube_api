# Pull base image.
FROM ubuntu:latest

# let's have a nice motd message
COPY assets/motd /etc/motd

# let's have wait for it

ADD assets/wait_for_it.sh /usr/local/bin/

# let's make the opt dir

RUN mkdir -p /opt/pushnotification/
RUN mkdir -p /opt/pushnotification/commons/
RUN mkdir -p /opt/pushnotification/static
RUN mkdir -p /opt/pushnotification/logs


# let's add the code of the push

COPY commons/ /opt/pushnotification/commons
COPY static/ /opt/pushnotification/static
COPY config.ini /opt/pushnotification
COPY NotificationServer.py /opt/pushnotification
COPY __init__.py /opt/pushnotification
COPY requirements.txt /opt/pushnotification


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



# let's install python dependencies list
RUN pip install requests requests-oauthlib requests-toolbelt futures tornado pika==0.12.0 python-memcached-stats pymemcache singledispatch backports_abc six websocket-client multi-mechanize matplotlib 

WORKDIR /opt/pushnotification/
EXPOSE 8888

# Define default command.
CMD ["python","NotificationServer.py"]

# Define default command.
#CMD /usr/local/bin/wait_for_it.sh -h $RABBITMQ_HOST -p $RABBITMQ_PORT --timeout=50 --strict -- \
#    "python NotificationServer.py"


