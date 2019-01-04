FROM centos:7

MAINTAINER KNMI R&D Observations and Data Technology Department

USER root

RUN yum update -y && yum install -y epel-release deltarpm && yum update -y

RUN yum install -y git python-devel python2-pip npm httpd openssl mod_ssl mod_wsgi && \
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

## For no copy from local (already checked out) repository instead of
## cloning a git repository, so we have the latest development edits,
## instead of only what has been pushed to master. On the other, hand
## the local copy will not work in a k8s deployment.
# RUN git clone https://github.com/neutvd/ProvTemplateCatalog.git

RUN npm install -g webpack && npm install axios

RUN mkdir -p /tmp/ProvTemplateCatalog/templates /var/www/repoConf \
             /var/www/html/static/dist \
             /data/EnvriProvTemplates/provtemplates

## install deps in separate step to use docker's caching 
COPY ./templates/package.json /tmp/ProvTemplateCatalog/templates
WORKDIR /tmp/ProvTemplateCatalog/templates
RUN npm install && npm install --save vue
COPY . /tmp/ProvTemplateCatalog
RUN npm run build
RUN cp --recursive --dereference /tmp/ProvTemplateCatalog/static /var/www/html
COPY templates/index.html /var/www/html

COPY example_conf_apache2_sites-enabled.conf /etc/httpd/conf.d/prov-template.conf
COPY example_wsgi_conf.conf /var/www/repoConf/repoConf.wsgi
COPY app.py /var/www/repoConf/
COPY example_config.py /var/www/repoConf/config.py

RUN mkdir -p -m 0711 /etc/ssl/private/ && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/apache.key -out /etc/ssl/certs/apache.crt \
    -subj "/C=NL/ST=Utrecht/L=Utrecht/O=KNMI/OU=RDWD/CN=prov-template/emailAddress=eu-team@knmi.nl"

RUN echo "ServerName localhost" >> /etc/httpd/conf/httpd.conf
EXPOSE 80
CMD ["/usr/sbin/apachectl", "-DFOREGROUND"]
