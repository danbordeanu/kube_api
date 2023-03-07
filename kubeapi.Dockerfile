# Pull base image.
FROM ubuntu:latest

# let's have a nice motd message
COPY docker/x64/docker_kube/assets/motd /etc/motd


#let's update
RUN apt-get update

#let's install the internet
RUN apt-get install -y --force-yes \
		apt-utils \ 
		telnet \
		python \
		python-pip \
		libsasl2-dev \
		python-dev \
		libldap2-dev \
		libssl-dev \
	&& rm -rf /var/lib/apt/lists/*


# let's make the opt dir

RUN mkdir -p /opt/kube/helpers
RUN mkdir /opt/kube/logs

# let's add stuff for the API

ADD helpers/ /opt/kube/helpers
ADD kube_proxy.py /opt/kube/
ADD config.ini /opt/kube/
ADD requirements.txt /opt/kube/
ADD __init__.py /opt/kube/
ADD config.py /opt/kube/

# let's install python dependencies list
RUN pip2 install -r /opt/kube/requirements.txt

WORKDIR /opt/kube/

EXPOSE 5000

# Define default command.
CMD ["python", "kube_proxy.py"]

