THIS IS WORK IN PROGRESS 
Visit a running instance of this code at https://envriplus-provenance.test.fedcloud.eu/
Do not use Internet Explorer
This service uses a self issued certificate

Proof of concept: MongoDB Backend with a Flask API and a vue.js frontend, using flask-jwt-simple for API authorization and Authomatic for user authentication via oauth2 services from existing social media sites.

## Basic setup
The basic setup of vue.js follows

	https://skyronic.com/blog/vue-project-scratch

Authomatic integration based on

	https://authomatic.github.io/authomatic/ Live Demo

Requires MongoDb engine

Required python components:
```
sudo pip install flask
sudo pip install flask-jwt-simple
sudo pip install flask-API
sudo pip install authomatic
sudo pip install pymongo
sudo pip install python-openid
sudo pip install pyOpenSSL
sudo pip install prov
sudo pip install pydot
sudo pip install requests
```

Javascript environment:
```	
sudo npm install -g webpack
sudo npm install axios
```
In "template" directory:
```	
npm install
npm install --save vue
```
		
----- 

## Setup on Ubuntu without Docker containers
Setup on Ubuntu without using docker container.:

1. Install necessary packages
1. Set up MongoDB db with name `TemplateData` and create collection `Templates`.
1. 	Change server url to your hostname in
    1. *app.py*: change os.environ["PROV_TMPL_SERVERNAME"] to your hostname.
   	1. *templates/src/main.js*: replace localhost with your hostname.
1. Change `ServerName` value to your hostname in `example_conf_apache2_sites-enabled.conf`
1. Provide social media oauth2 app key and secret for each used site in `config.py`:
*Uncomment the lines setting the keys and secrets directly and comment out
the lines obtaining the keys and secrets from the environment.* For github, the instructions to obtain the key and secret can be found at https://developer.github.com/apps/building-oauth-apps/creating-an-oauth-app/.
1. Change `os.environ['PROV_TMPL_JWT_SECRET']` secret keys in app.py with your own
made up secret.
1. Use webpack to compile build.js from templates/src/main.js
   put or symlink build.js in static/js/build.js
   ```
        cd templates
        npm run build
   ```
1. Setup virtualhost in etc/apache2/sites-enabled
1. Create wsgi file
1. Mandatory global (eg in apache2.conf) WSGI Setting for JWT to work: `WSGIPAssAuthorization On`

## Setup using Docker

Create a file with the OAuth keys and secrets e.g. oauth-keys.txt:

```Shell
PROV_TMPL_github_KEY="github-consumer-key"
PROV_TMPL_github_SECRET="github-consumer-secret"
PROV_TMPL_linkedin_KEY="linkedin-consumer-key"
PROV_TMPL_linkedin_SECRET="linkedin-consumer-secret"
PROV_TMPL_google_KEY="google-consumer-key"
PROV_TMPL_google_SECRET="google-consumer-key"
```

Make sure this file is not committed to the git repository, so keep
it above the repository directory.

Create a directory where the MongoDB container will store its data,
e.g. /data/prov.

Run the `run-container.sh` script for a server that can be reached
from anywhere under 'myserver.com':

```Shell
./run-container.sh -d /data/prov -h myserver.com -b myserver.com -a ../oauth-keys.txt
```

To run the server locally on a workstation you can do:
```Shell
./run-container.sh -d $HOME/tmp/data/prov -a ../oauth-keys.txt
```

After that command has spinned up both the MongoDB and prov-template
containers the application is available at https://localhost. You will
need to allow an exception when your browser gives you a warning about
the self signed certificate.

To spin down the containers do `docker-compose down` in the directory
where the `docker-compose.yml` file is.

## Expanding templates

### Example template(*) (in provn): #TODO: Put our own template here
```
document
  prefix xml <http://www.w3.org/XML/1998/namespace>
  prefix foaf <http://xmlns.com/foaf/0.1/>
  prefix rdfs <http://www.w3.org/2000/01/rdf-schema#>
  prefix rdf <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
  prefix var <http://openprovenance.org/var#>
  prefix tmpl <http://openprovenance.org/tmpl#>
  prefix vargen <http://openprovenance.org/vargen#>
  
  bundle vargen:bundleId
    prefix xml <http://www.w3.org/XML/1998/namespace>
    prefix foaf <http://xmlns.com/foaf/0.1/>
    prefix rdfs <http://www.w3.org/2000/01/rdf-schema#>
    prefix rdf <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    prefix var <http://openprovenance.org/var#>
    prefix tmpl <http://openprovenance.org/tmpl#>
    prefix vargen <http://openprovenance.org/vargen#>
    
    wasAttributedTo(var:quote, var:author)
    entity(var:quote, [prov:value='var:value'])
    entity(var:author, [prov:type='prov:Person', foaf:name='var:name'])
  endBundle
endDocument
```

### Example bindings (in trig): # TODO: Put our own bindings here
```
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix tmpl: <http://openprovenance.org/tmpl#> .
@prefix var: <http://openprovenance.org/var#> .
@prefix ex: <http://example.com/#> .
 
var:author a prov:Entity;
           tmpl:value_0 <http://orcid.org/0000-0002-3494-120X>.
var:name   a prov:Entity;
           tmpl:2dvalue_0_0 "Luc Moreau".
var:quote  a prov:Entity;
           tmpl:value_0 ex:quote1.
var:value  a prov:Entity;
           tmpl:2dvalue_0_0 "A Little Provenance Goes a Long Way".
```

### Python example to expand with GET
```python
import requests
import urllib

host_name = 'ec2-54-229-229-46.eu-west-1.compute.amazonaws.com'
template_id = '5c3dbc4d5a13e60008b76240'
trig_string = """
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix tmpl: <http://openprovenance.org/tmpl#> .
@prefix var: <http://openprovenance.org/var#> .
@prefix ex: <http://example.com/#> .
 
var:author a prov:Entity;
           tmpl:value_0 <http://orcid.org/0000-0002-3494-120X>.
var:name   a prov:Entity;
           tmpl:2dvalue_0_0 "Luc Moreau".
var:quote  a prov:Entity;
           tmpl:value_0 ex:quote1.
var:value  a prov:Entity;
           tmpl:2dvalue_0_0 "A Little Provenance Goes a Long Way".
"""
url_encoded_trig_string = urllib.urlencode({"bindings": trig_string})
r = requests.get('https://' + host_name + '/templates/' + template_id + 
    '/expand?fmt=provjson&writeprov=false&bindver=v2&' + url_encoded_trig_string,
    verify=False) 

print r.text
```

### Python example to expand with POST
```python
import requests

host_name = 'ec2-54-229-229-46.eu-west-1.compute.amazonaws.com'
template_id = '5c3dbc4d5a13e60008b76240'
trig_string = """
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix tmpl: <http://openprovenance.org/tmpl#> .
@prefix var: <http://openprovenance.org/var#> .
@prefix ex: <http://example.com/#> .
 
var:author a prov:Entity;
           tmpl:value_0 <http://orcid.org/0000-0002-3494-120X>.
var:name   a prov:Entity;
           tmpl:2dvalue_0_0 "Luc Moreau".
var:quote  a prov:Entity;
           tmpl:value_0 ex:quote1.
var:value  a prov:Entity;
           tmpl:2dvalue_0_0 "A Little Provenance Goes a Long Way".
"""

r = requests.post('https://' + host_name + '/templates/' + template_id + 
    '/expand?fmt=provjson&writeprov=false&bindver=v2',
        data=trig_string, verify=False)
        
print r.text        
```

(*) Example taken from Luc Moreau's ProvToolbox tutorial at
https://lucmoreau.wordpress.com/2015/07/30/provtoolbox-tutorial-4-templates-for-provenance-part-1/
