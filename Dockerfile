FROM centos:latest

MAINTAINER KNMI R&D Observations and Data Technology Department

USER root

RUN yum update -y

RUN yum install -y git python3-devel python3-pip npm httpd openssl mod_ssl python3-mod_wsgi graphviz && \
    yum clean all && rm -rf /var/cache/yum

# fix problem with prov lib
RUN pip3 install 'networkx==2.2'

RUN pip3 install flask && \
    pip3 install flask-jwt-simple && \
    pip3 install flask-API && \
	pip3 install authomatic && \
	pip3 install pymongo && \
	pip3 install python3-openid && \
	pip3 install pyOpenSSL && \
	pip3 install prov && \
	pip3 install pydot && \
	pip3 install requests

WORKDIR /

## For no copy from local (already checked out) repository instead of
## cloning a git repository, so we have the latest development edits,
## instead of only what has been pushed to master. On the other, hand
## the local copy will not work in a k8s deployment.
# RUN git clone https://github.com/neutvd/ProvTemplateCatalog.git

RUN npm install -g webpack && npm install axios

RUN mkdir -p /tmp/ProvTemplateCatalog/templates /var/www/repoConf /data/

## install deps in separate step to use docker's caching 
COPY ./templates/package.json /tmp/ProvTemplateCatalog/templates
WORKDIR /tmp/ProvTemplateCatalog/templates
RUN npm install && npm install --save vue

## Copy the application code and compile it.
COPY . /tmp/ProvTemplateCatalog
RUN npm run build

## Copy static content
RUN cp --recursive --dereference /tmp/ProvTemplateCatalog/static /var/www/repoConf
RUN mkdir /var/www/repoConf/templates
COPY templates/index.html /var/www/repoConf/templates

## Setup the web server configuration.
COPY example_wsgi_conf.conf /var/www/repoConf/repoConf.wsgi
COPY app.py /var/www/repoConf/
COPY example_config.py /var/www/repoConf/config.py

WORKDIR /data/
RUN git clone https://github.com/EnvriPlus-PROV/EnvriProvTemplates.git
WORKDIR /data/EnvriProvTemplates
RUN python3 setup.py install

WORKDIR /

RUN /usr/libexec/httpd-ssl-gencerts
RUN touch /var/www/repoConf/out.log && chown apache.apache /var/www/repoConf/out.log && chmod 600 /var/www/repoConf/out.log
EXPOSE 80
EXPOSE 443
ENV FLASK_ENV=development

CMD ["/tmp/ProvTemplateCatalog/docker-cmd.sh"]
# CMD ["python", "/var/www/repoConf/app.py"]
