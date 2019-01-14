# config.py

from authomatic.providers import oauth2, oauth1, openid

CONFIG = {
    
    'github': { # Your internal provider name
           
        # Provider class
        'class_': oauth2.GitHub,
	'id': 3,
	'access_headers': {'User-Agent': 'Awesome-Octocat-App'},
        # Twitter is an AuthorizationProvider so we need to set several other properties too:
        'consumer_key': '<consumer_key>',
        'consumer_secret': '<consumer_secret>',
	'scope': oauth2.GitHub.user_info_scope,  
    },
    
    'linkedin': {
           
        'class_': oauth2.LinkedIn,
	'id': 2,
        
        # Facebook is an AuthorizationProvider too.
        'consumer_key': '<consumer_key>',
        'consumer_secret': '<consumer_secret>',
        
        # But it is also an OAuth 2.0 provider and it needs scope.
        'scope': "",
    },
    
    'google': {
           
        'class_': oauth2.Google,
	'id': 1,
        
        # Google is an AuthorizationProvider too.
        'consumer_key': '<consumer_key>',
        'consumer_secret': '<consumer_secret>',
        
        # But it is also an OAuth 2.0 provider and it needs scope.
	'scope': oauth2.Google.user_info_scope + ['profile', 'email'],  
    }
}

PROVSTORE = {
    'Host': '<url of  Triplestore>',
    'Authorization' : '<Base64 encoding of username and password for Triplestore>'
}

