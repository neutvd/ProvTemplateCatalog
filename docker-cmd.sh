#!/bin/bash

echo "ServerName $PROV_TMPL_SERVERNAME" >> /etc/httpd/conf/httpd.conf
/usr/sbin/apachectl -DFOREGROUND
