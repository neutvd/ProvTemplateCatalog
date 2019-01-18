# config.py

import os
from authomatic.providers import oauth2, oauth1, openid

CONFIG = {
    
    'github': { # Your internal provider name
           
        # Provider class
        'class_': oauth2.GitHub,
	'id': 3,
	'access_headers': {'User-Agent': 'Awesome-Octocat-App'},
        # If you're not running this in a docker container, then
        # uncomment these lines, and comment the lines obtaining
        # the key and secret from the environment
        #'consumer_key': '<consumer_key>', 
        #'consumer_secret': '<consumer_secret>',
        'consumer_key': os.environ['PROV_TMPL_github_KEY'], 
        'consumer_secret': os.environ['PROV_TMPL_github_SECRET'],
	'scope': oauth2.GitHub.user_info_scope,  
    },
    
    'linkedin': {
           
        'class_': oauth2.LinkedIn,
	'id': 2,
        
        # Facebook is an AuthorizationProvider too.
        # If you're not running this in a docker container, then
        # uncomment these lines, and comment the lines obtaining
        # the key and secret from the environment
        #'consumer_key': '<consumer_key>', 
        #'consumer_secret': '<consumer_secret>',
        'consumer_key': os.environ['PROV_TMPL_linkedin_KEY'],
        'consumer_secret': os.environ['PROV_TMPL_linkedin_SECRET'],
        
        # But it is also an OAuth 2.0 provider and it needs scope.
        'scope': [],
    },
    
    'google': {
           
        'class_': oauth2.Google,
	'id': 1,
        
        # Google is an AuthorizationProvider too.
        # If you're not running this in a docker container, then
        # uncomment these lines, and comment the lines obtaining
        # the key and secret from the environment
        #'consumer_key': '<consumer_key>', 
        #'consumer_secret': '<consumer_secret>',
        'consumer_key': os.environ['PROV_TMPL_google_KEY'],
        'consumer_secret': os.environ['PROV_TMPL_google_SECRET'],
        
        # But it is also an OAuth 2.0 provider and it needs scope.
	'scope': oauth2.Google.user_info_scope + ['profile', 'email'],  
    }
}

PROVSTORE = {
    'Host': '<url of  Triplestore>',
    'Authorization' : '<Base64 encoding of username and password for Triplestore>'
}

