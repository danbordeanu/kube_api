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
	&& rm -rf /var/lib/apt/lists/*

# let's configure supervisor
RUN mkdir -p /var/log/supervisor /var/run/supervisor /etc/supervisor/conf.d

# let's copy the nginx config
COPY assets/nginx.conf /etc/nginx/

# let's copy the supervisor config files
COPY assets/supervisord.conf /etc/supervisor/
COPY assets/nginx_supervisor.conf /etc/supervisor/conf.d/


EXPOSE 8080

# Define default command.
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
