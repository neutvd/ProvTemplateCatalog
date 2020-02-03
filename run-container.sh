#!/bin/bash

function usage() {
    echo "run-container.sh [-h servername] [-b base_url] [-d database]"
    echo ""
    echo "-h servername    - fully qualified domain name under which the service"
    echo "                   is hosted. E.g. prov.mycompany.com. Default is prov-template."
    echo "                   This name can be equal to base_url_root, except if it is"
    echo "                   prov-template. Then base_url_host will be set to localhost"
    echo "                   and override base_url_host."
    echo "-b base_url_host - hostname part of base url. Often the same as servername"
    echo "                   except if servername is 'prov-template'. Then it will be set"
    echo "                   to localhost and it will override the value in this"
    echo "                   argument. Default is localhost."
    echo "-d database      - directory where the mongodb container will store its"
    echo "                   persistent data. Default is /tmp. Ignored if -k given."
    echo "-a filename      - Filename containing OAuth keys and secrets. Format:"
    echo "                   PROV_TMPL_<provider>_KEY=key"
    echo "                   PROV_TMPL_<provider>_SECRET=secret"
    echo "-k               - Don't start the containers with docker-compose. But deploy "
    echo "                   in kubernetes."
}

PROV_TMPL_SERVERNAME="prov-template"
PROV_TMPL_DATABASE="/tmp"
PROV_TMPL_BASEURL_HOST="localhost"
k8s="no"
while getopts h:d:b:a:k option ; do
    case ${option} in
        (h) PROV_TMPL_SERVERNAME=${OPTARG}
            ;;
        (d) PROV_TMPL_DATABASE=${OPTARG}
            ;;
        (b) PROV_TMPL_BASEURL_HOST=${OPTARG}
            ;;
        (a) oauth_key_file=${OPTARG}
            ;;
        (k) k8s="yes"
            ;;
        (\?) echo "Invalid option ${OPTARG}"
             usage
             exit
             ;;
    esac
done

. ${oauth_key_file} || exit 1
 
if [ "$k82" = "no" ] ; then
    mkdir -p ${PROV_TMPL_DATABASE} || exit 1
fi

if [ "{PROV_TMPL_SERVERNAME}" = "localhost" ] ; then
    PROV_TMPL_BASEURL_HOST="prov-template"
fi

secretsdir=${HOME}/secrets/${PROV_TMPL_SERVERNAME}
if [[ ! -f ${secretsdir}/apache.key && "${k8s}" = "no" ]] ; then
    mkdir -p -m 755 ${secretsdir}
    openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out  ${secretsdir}/server.pass.key
    openssl rsa -passin pass:x -in ${secretsdir}/server.pass.key -out ${secretsdir}/apache.key
    rm -f ${secretsdir}/server.pass.key
    openssl req -new -key ${secretsdir}/apache.key -out ${secretsdir}/server.csr \
            -subj "/C=NL/ST=Utrecht/L=Utrecht/O=KNMI/OU=RDWD/CN=$PROV_TMPL_SERVERNAME/emailAddress=eu-team@knmi.nl"
    openssl x509 -req -sha256 -days 365 -in ${secretsdir}/server.csr \
            -signkey ${secretsdir}/apache.key -out ${secretsdir}/apache.crt
    chmod 644 ${secretsdir}/*
fi

confdir=${HOME}/conf/${PROV_TMPL_SERVERNAME}
if [[ ! -f ${confdir}/prov-template.conf || ! -f ${confdir}/prov-template-k8s.conf ]] ; then
    mkdir -p -m 755 ${confdir}
    sed -e "s/prov-template/$PROV_TMPL_SERVERNAME/" example_conf_apache2_sites-enabled.conf >  ${confdir}/prov-template.conf
    sed -e "s/prov-template/$PROV_TMPL_SERVERNAME/" kubernetes/prov-template.conf >  ${confdir}/prov-template-k8s.conf
    sed -ri -e 's!^(\s*CustomLog)\s+\S+!\1 /proc/self/fd/1!g'  -e 's!^(\s*ErrorLog)\s+\S+!\1 /proc/self/fd/2!g' \
		"${confdir}/prov-template.conf"
fi

PROV_TMPL_JWT_SECRET=`pwgen -1`
if [[ "${k8s}" = "no" && -f docker-compose.yml ]] ; then
    export PROV_TMPL_DATABASE PROV_TMPL_SERVERNAME PROV_TMPL_BASEURL_HOST PROV_TMPL_JWT_SECRET

    [ -z "${PROV_TMPL_github_KEY}" ] || export PROV_TMPL_github_KEY PROV_TMPL_github_SECRET
    [ -z "${PROV_TMPL_linkedin_KEY}" ] || export PROV_TMPL_linkedin_KEY PROV_TMPL_linkedin_SECRET
    [ -z "${PROV_TMPL_google_KEY}" ] || export PROV_TMPL_google_KEY PROV_TMPL_google_SECRET
    docker-compose build prov-template
    docker-compose up -d
elif [[ "${k8s}" = "yes" && -f kubernetes/prov-template.yaml ]] ; then
    cp ${confdir}/prov-template-k8s.conf ${confdir}/prov-template.conf
    kubectl -n swirrl create configmap prov-template-conf --from-file=${confdir}/prov-template.conf
    kubectl -n swirrl create configmap prov-template-oauth --from-env-file=${oauth_key_file}
    kubectl -n swirrl create configmap server-url-jwt-conf \
            --from-literal=prov-tmpl.servername=${PROV_TMPL_SERVERNAME} \
            --from-literal=prov-tmpl.baseurl=${PROV_TMPL_BASEURL_HOST} \
            --from-literal=prov-tmpl.jwt=${PROV_TMPL_JWT_SECRET}
    kubectl -n swirrl create -f kubernetes/prov-template.yaml
else
    echo "No docker-compose.yml or kubernetes/prov-template.yaml file found."
    exit 1
fi

#echo "Docker started, stop with"
#echo "docker-compose down"
