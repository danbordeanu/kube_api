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


# let's make the opt dir

RUN mkdir -p /opt/kube/

# let's install python dependencies list

RUN pip install -r requirements.txt 
WORKDIR /opt/kube/
EXPOSE 5000

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["python api_test.py"]

EXPOSE 8080