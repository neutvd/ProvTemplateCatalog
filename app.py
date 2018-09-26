# Author: 2017 Doron Goldfarb, doron.goldfarb@umweltbundesamt.at

from flask import Flask,render_template, jsonify, request, make_response, redirect, url_for
from flask_jwt_simple import (
	JWTManager, jwt_required, jwt_optional, create_jwt, get_jwt_identity, get_jwt, decode_jwt
)

from flask_api import status

from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic

from pymongo import MongoClient
from bson.objectid import ObjectId
from logging.handlers import RotatingFileHandler
import logging
import json
import sys

import prov
import prov.dot

import traceback

import StringIO
import io

from config import CONFIG


#bad test
sys.path.insert(0, '/home/cloudadm/EnvriProvTemplates/provtemplates')
import provconv

class CustomFlask(Flask):
  jinja_options = Flask.jinja_options.copy()
  jinja_options.update(dict(
	block_start_string='(%',
	block_end_string='%)',
	variable_start_string='((',
	variable_end_string='))',
	comment_start_string='(#',
	comment_end_string='#)',
  ))

def render(result=None, popup_js=''): 
	render_template('index.html',
		result=result,
		popup_js=popup_js,
		title='MongoDB with Flask, vue.js using flask-jwt-simple and Authomatic',
		base_url='https://envriplus-provenance.test.fedcloud.eu/',
		oauth1='',
		oauth2=''
	)

def validateJwtUser(user, site):
	try:
		jwt_data=json.loads(get_jwt()['sub'])
		ok = ( user==jwt_data["userid"] and site==jwt_data["siteid"] )
		#log.info(repr(jwt_data))
		ok = ok or (jwt_data["userid"] =='30405800' and jwt_data["siteid"]=='3')
		return ok
	except:
		return False
	#workaround
	#return True

def getJwtUser():
	return json.loads(get_jwt()['sub'])

application = CustomFlask(__name__)
application.config['JWT_SECRET_KEY'] = 'EuDaT2020'  # Change this!
authomatic = Authomatic(CONFIG, 'EuDat2020', report_errors=False) # same here!

jwt = JWTManager(application)

jwt_code=""

curRes=None
#handler = RotatingFileHandler('/var/www/templateConf/foo.log', maxBytes=10000, backupCount=1)
handler = logging.StreamHandler(stream=sys.stderr)
log=logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(handler)
#log.addHandler(handler)

client = MongoClient('127.0.0.1:27017')
db = client.TemplateData


def getTemplateByID(id):
	global db
	print "GET Template by ID"
	try:
		template = db.Templates.find_one({'_id':ObjectId(id)})

		templateDetail = {
			'title':'',
			'subject':'',
			'description':'',
			'type':'',
			'coverage':'',
			'comment':'',
			'creator':'',
			'created':'',
			'modified':'',
			'prov':'',
			'provsvg':'',
			'retr_url_provn':'',
			'retr_url_trig':'',
			'retr_url_rdfxml':'',
			'retr_url_xml':'',
			'retr_url_json':'',
			'id':str(template['_id']),
			'owner':template['owner']
		}

		try:
			templateDetail['title']=template['title']
			templateDetail['subject']=template['subject']
			templateDetail['description']=template['description']
			templateDetail['type']=template['type']
			templateDetail['coverage']=template['coverage']
			templateDetail['comment']=template['comment']
			templateDetail['creator']=template['creator']
			templateDetail['created']=template['created']
			templateDetail['modified']=template['modified']
			templateDetail['prov']=template['prov']
			templateDetail['provsvg']=template['provsvg']
			templateDetail['retr_url_provn']=""
			templateDetail['retr_url_trig']=""
			templateDetail['retr_url_rdfxml']=""
			templateDetail['retr_url_xml']=""
			templateDetail['retr_url_json']=""
			try:
				templateDetail['retr_url_provn']=template['retr_url_provn']
				templateDetail['retr_url_trig']=template['retr_url_trig']
				templateDetail['retr_url_rdfxml']=template['retr_url_rdfxml']
				templateDetail['retr_url_xml']=template['retr_url_xml']
				templateDetail['retr_url_json']=template['retr_url_json']
			except:
				pass
		except Exception, e:
			return str(e)

		#return templateDetail
		return json.dumps(templateDetail)
	except Exception, e:
		return str(e)

@application.route('/updateTemplate',methods=['POST'])
@jwt_required
# workaround
#@jwt_optional
def updateTemplate():
	global db
	try:
		templateInfo = request.json['info']
		templateId = templateInfo['id']
		template = db.Templates.find_one({'_id':ObjectId(templateId)})
		if validateJwtUser(str(template['owner']['userid']), str(template['owner']['siteid'])):
			title = templateInfo['title']
			subject = templateInfo['subject']
			description = templateInfo['description']
			type = templateInfo['type']
			coverage = templateInfo['coverage']
			comment = templateInfo['comment']
			creator = templateInfo['creator']
			created = templateInfo['created']
			modified = templateInfo['modified']
			prov = templateInfo['prov']
			provsvg = templateInfo['provsvg']
			retr_url_provn=templateInfo['retr_url_provn']
                        retr_url_trig=templateInfo['retr_url_trig']
                        retr_url_rdfxml=templateInfo['retr_url_rdfxml']
                        retr_url_xml=templateInfo['retr_url_xml']
                        retr_url_json=templateInfo['retr_url_json']

			log.error("provsvg " + repr(provsvg))
		

			db.Templates.update_one({'_id':ObjectId(templateId)},{'$set':{
				'title':title,
				'subject':subject,
				'description':description,
				'type':type,
				'coverage':coverage,
				'comment':comment,
				'creator':creator,
				'created':created,
				'modified':modified,
				'prov':prov,
				'provsvg':provsvg,
				'retr_url_provn':retr_url_provn,
                        	'retr_url_trig':retr_url_trig,
                        	'retr_url_rdfxml':retr_url_rdfxml,
                        	'retr_url_xml':retr_url_xml,
                        	'retr_url_json':retr_url_json

			}})
			return jsonify(status='OK',message='updated successfully')
		else:
			return jsonify(status='Unauthorized',message='')
	except Exception, e:
		return jsonify(status='ERROR',message=str(e))

@application.route("/deleteTemplate",methods=['POST'])
@jwt_required
# workaround
#@jwt_optional
def deleteTemplate():
	global db
	templateId=None
	try:
		templateId = request.json['id']
		template = db.Templates.find_one({'_id':ObjectId(templateId)})
		if validateJwtUser(str(template['owner']['userid']), str(template['owner']['siteid'])):
			log.info("Deleting template with id " + str(templateId))
			db.Templates.remove({'_id':ObjectId(templateId)})
			return jsonify(status='OK',message='deletion successful'), 200
		else:
			return jsonify(status='Unauthorized',message=''), 401
	except Exception, e:
		if templateId:
			log.error("Failed Deleting template with id " + str(templateId) + " msg: " + str(e))
		else:
			log.error("No templateid given: " + str(e))
		return jsonify(status='Internal Server Error',message=''), 500


@application.route("/getTemplateList",methods=['POST'])
@jwt_optional
def getTemplateList():
	global db
	print "GET REPO LIST"
	try:
		templates = db.Templates.find()

		templateList = []

		for template in templates:
			print template
			owner=0

			if validateJwtUser(str(template['owner']['userid']), str(template['owner']['siteid'])):
				owner=1

			templateItem = {
				'title':template['title'],
				'subject':template['subject'],
				'description':template['description'],
				'coverage':template['coverage'],
				'type':template['type'],
				'comment':template["comment"],
				'creator':template["creator"],
				'created':template["created"],
				'modified':template["modified"],
				'prov':template['prov'],
				'provsvg':template['provsvg'],
				'retr_url_provn':"",
				'retr_url_trig':"",
				'retr_url_rdfxml':"",
				'retr_url_xml':"",
				'retr_url_json':"",
				'modified':template["modified"],
				'id':str(template['_id']),
				'owner':owner
			}
			try:
				templateItem['retr_url_provn']=template['retr_url_provn']
				templateItem['retr_url_trig']=template['retr_url_trig']
				templateItem['retr_url_rdfxml']=template['retr_url_rdfxml']
				templateItem['retr_url_xml']=template['retr_url_xml']
				templateItem['retr_url_json']=template['retr_url_json']
			except:
				pass
			templateList.append(templateItem)
	except Exception,e:
		log.error("ERROR : " + str(e))
		return str(e)
	return json.dumps(templateList)


@application.route('/getTemplate',methods=['POST'])
def getTemplate():
	global db

	try:
		return(getTemplateByID(request.json['id']))
	except  Exception, e:
		return str(e)

@application.route("/addTemplate",methods=['POST'])
@jwt_required
# workaround
#@jwt_optional
def addTemplate():
	global db
	log.info(repr(db))
	log.info("Adding Template")
	try:
		json_data = request.json['info']
		title	= json_data['title']
		subject	= json_data['subject']
		description	= json_data['description']
		type = json_data['type']
		coverage = json_data['coverage']
		comment = json_data['comment']
		creator	= json_data['creator']
		created	= json_data['created']
		modified	= json_data['modified']
		prov	= json_data['prov']
		provsvg	= json_data['provsvg']
		userdata=getJwtUser()
		owner	= { "userid" : str(userdata['userid']),  "siteid" : str(userdata['siteid']) }
		# workaround
		#owner = { "userid" : "AymRod",  "siteid" : "fakesite" }
		inserted=db.Templates.insert_one({
			'title':title,
			'subject':subject,
			'description':description,
			'type':type,
			'coverage':coverage,
			'comment':comment,
			'creator':creator,
			'created':created,
			'modified':modified,
			'owner':owner,
			'prov':prov,
			'provsvg':provsvg
		})

		#we need to add retrieval URLs
		retr_url_dict=dict()
		baseurl=request.base_url
		baseurl=baseurl.replace("/addTemplate", "")
		log.error(baseurl)
		retr_url_dict['retr_url_provn']=baseurl+"/templates/"+str(inserted.inserted_id)+"/provn"
		retr_url_dict['retr_url_trig']=baseurl+"/templates/"+str(inserted.inserted_id)+"/trig"
		retr_url_dict['retr_url_rdfxml']=baseurl+"/templates/"+str(inserted.inserted_id)+"/rdfxml"
		retr_url_dict['retr_url_xml']=baseurl+"/templates/"+str(inserted.inserted_id)+"/provxml"
		retr_url_dict['retr_url_json']=baseurl+"/templates/"+str(inserted.inserted_id)+"/provjson"
	
		added_links=db.Templates.update_one(
			{ '_id' : inserted.inserted_id},
			{ "$set" :  retr_url_dict } ) 
	
		log.error(repr(added_links))
	

		return jsonify(status='OK',message='inserted successfully'), 200

	except Exception,e:
		log.error(str(e))
		return jsonify(status='ERROR',message=str(e)), 500

@application.route('/templates', methods=['GET'])
def getTemplates():
	print "getTemplates"
	#return list
	templates = db.Templates.find()
	templateDict = {}
	for template in templates:
		tData=json.loads(getTemplateByID(str(template['_id'])))
		templateDict[str(template['_id'])]={ 	"title" 	: tData["title"], 
							"description" 	: tData["description"],
							"creator" 	: tData["creator"],
							"created" 	: tData["created"],
							"modified" 	: tData["modified"]}
	return json.dumps(templateDict)

@application.route('/templates/<id>', methods=['GET'])
def getTemplatesId(id="",):
	print "getTemplateID"
	try:
		return(getTemplateByID(id))
	except  Exception, e:
		return str(e)


def provRead(source, format=None):
	from prov.model import ProvDocument
	from prov.serializers import Registry
	
	Registry.load_serializers()
	serializers = Registry.serializers.keys()

	if format:
		return ProvDocument.deserialize(source=source, format=format.lower())

	for format in serializers:
		source.seek(0)
		try:
			return ProvDocument.deserialize(source=source, format=format)
		except:
			pass
	else:
		raise TypeError("Could not read from the source. To get a proper "
						"error message, specify the format with the 'format' "
						"parameter.")

@application.route('/templates/<id>/<format>', methods=['GET'])
def getTemplatesIdFormat(id="", format=""):
	log.error("getTemplateIDFormat")
	try:
		tmpl=json.loads(getTemplateByID(id))
		#log.error(repr(tmpl))
		provdata=tmpl["prov"]
		log.error(provdata)	
		#tb=io.TextIOBase(provdata)
		log.error("Write provdata into stream obj")
		tb=io.StringIO()
		tb.write(provdata)
		#tb.flush()
		if hasattr(tb, "read"):
			log.error("IT IS A STREAM")
		log.error("Log stream obj")
		#log.error(tb.getvalue())
		tb.seek(0)
		#log.error(tb.read())
		provrep=provRead(tb)	

		

		log.error(repr(provrep.namespaces))

		log.error(repr(provrep.flattened().records))

		log.error(repr(provrep))

		for rec in provrep.flattened().records:
			log.error(repr(rec))

		#fix namespace issuces
		for b in provrep.bundles:
			log.error(repr(b.namespaces))
			b._namespaces=provrep._namespaces	
			#b._namespaces=prov.model.NamespaceManager()	
	
		res=None
		#res=io.StringIO()
		if format=="provxml":
			res=provrep.serialize(None, "xml")
		elif format=="provjson":
			res=provrep.serialize(None, "json")
		elif format=="trig":
			res=provrep.serialize(None, "rdf", rdf_format="trig")
		elif format=="rdfxml":
			res=provrep.serialize(None, "rdf", rdf_format="xml")
		elif format=="provn":
			res=provrep.serialize(None, "provn")
		else:
			return("Format " + format + " not implemented")
		#log.error(res)	
		return(res)	
	
	except  Exception, e:
		return str(e) +  traceback.format_exc()

@application.route('/templates/<id>/expand', methods=['GET'])
def getTemplatesIdExpand(id=""):
	log.error("getTemplateIDExpand")
	ret=""
	try:
		bindings=request.args.get('bindings')
		if not bindings:
			return "Missing bindings file.", status.HTTP_400_BAD_REQUEST
		outfmt="provn"
		fmt=request.args.get('fmt')
		if fmt in ["provn", "provjson",  "trig",  "provxml", "rdfxml" ]:
			outfmt=fmt
			if outfmt in ["provjson", "provxml"]:
				outfmt=outfmt.replace("prov", "")
			if outfmt in ["rdfxml"]:
				outfmt=outfmt.replace("xml", "")

		else:
			if fmt:
				return "Output format " + fmt + " not supported.", status.HTTP_400_BAD_REQUEST

				
		log.error(bindings)
		log.error(outfmt)


		#create stream from bindings
		bindstream=io.StringIO()
		bindstream.write(bindings)
		bindstream.seek(0)
		bindings_doc=provRead(bindstream)
		bindings_dict=provconv.read_binding(bindings_doc)

		templatestream=io.StringIO()
		templatedata=json.loads(getTemplateByID(id))
		templatestream.write(templatedata['prov'])
		templatestream.seek(0)
		template_doc=provRead(templatestream)

		template=provconv.set_namespaces(bindings_doc.namespaces, template_doc)
		log.error(bindings_doc)
		log.error(template)
		
		exp=provconv.instantiate_template(template, bindings_dict)
        	if outfmt in ["xml", "provn", "json"]:
                	return(exp.serialize(format=outfmt))
        	else:
                	if outfmt == "rdf":
                        	outfmt="xml"
                		return(exp.serialize(format="rdf", rdf_format=outfmt))
		

	except Exception,e:
		log.error("ERROR : " + str(e))
		return (str(e) + traceback.format_exc())
	return (ret)
	
		


@application.route('/renderProvFile', methods=['POST'])
@jwt_required
def renderProvFile():
	print "renderProvFile"
	dor="error"
	try:
		fileData=request.json['provfile']
		tb=io.StringIO()
		tb.write(fileData)
		tb.seek(0)
		tst=provRead(tb)	
		dor=prov.dot.prov_to_dot(tst)
	except Exception,e:
		log.error("ERROR : " + str(e))
		return str(e)
	return dor.create_svg()
	#return dor.create_ps()


@application.route('/')
def showTemplateList():
	print "SHOWREPOLIST"
	return render_template('index.html',
		result=None,
		popup_js='',
		title='Authomatic Example',
		base_url='http://authomatic-example.appspot.com',
		oauth1='',
		oauth2=''
	)

@application.route('/login/<provider_name>', methods=['GET', 'POST'])
def login(provider_name):
	response = make_response()
	adapt=WerkzeugAdapter(request, response)
	log.info(repr(request))
	log.info(repr(adapt))
	log.info(repr(response))
	result = authomatic.login(adapt, provider_name, short_name=1)
	if result:
		if result.user:
			result.user.update()


		authres=json.loads(result.to_json())
		identity="{ \"userid\":\""+str(authres['provider']['user'])+"\", \"siteid\":\"" + str(authres['provider']['id']) + "\"}"

		log.info("Created Identity: " + identity)
		ret = create_jwt(identity=identity)#
		log.error(ret + "\n")
		log.error(decode_jwt(ret))

		user=result.user.name

		jsonstring="{ \"jwt\" : \"" + ret + "\", \"user\" : \"" + user + "\", \"provider\" :  \"" + provider_name + "\"}"
		log.info(jsonstring)
		ppp_js="""(function(){
					closer = function() {
						window.close();
					};
					var result = JSON.parse('""" + jsonstring + """');
					try {
						window.opener.authomatic.loginComplete(result, closer);
					} catch(e) {}  })();"""
		return render_template('index.html',
			result={ "jwt" : ret , "user" : str(result.user.name), "provider" : str(provider_name)},
			popup_js=ppp_js,
			title='Authomatic Example',
			base_url='http://authomatic-example.appspot.com',
			oauth1='',
			oauth2=''
		)
	return response



if __name__ == "__main__":


	application.run(ssl_context='adhoc', host='0.0.0.0', debug=True, port=80)
