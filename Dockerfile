FROM fedora/nginx:latest
MAINTAINER Michael Scherer

RUN mkdir -p /srv/bugs.cloud.gluster.org/html/
ADD . /srv/bugs.cloud.gluster.org/html/
ADD nginx.conf /etc/nginx/conf.d/bugs.cloud.gluster.org.conf
