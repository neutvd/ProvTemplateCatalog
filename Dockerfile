FROM centos:7

MAINTAINER KNMI R&D Observations and Data Technology Department

USER root

RUN yum update -y && yum install -y epel-release deltarpm && yum update -y

RUN yum install -y git python-devel python2-pip npm httpd mod_wsgi && \
    yum clean all && rm -rf /var/cache/yum

RUN pip install flask && \
    pip install flask-jwt-simple && \
    pip install flask-API && \
	pip install authomatic && \
	pip install pymongo && \
	pip install python-openid && \
	pip install pyOpenSSL && \
	pip install prov && \
	pip install pydot && \
	pip install requests

WORKDIR /
## Perhaps copy from local (already checked out) repository instead,
## so we have the latest development edits, instead of only what has
## been pushed to master. On the other, hand the local copy will not
## work in a k8s deployment.
RUN git clone https://github.com/neutvd/ProvTemplateCatalog.git

RUN cd ProvTemplateCatalog && npm install -g webpack && npm install axios && \
    cd templates && npm install && npm install --save vue

EXPOSE 80
CMD ["/usr/sbin/apachectl", "-DFOREGROUND"]
