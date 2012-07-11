#!/usr/bin/env python
import json
import sys
import os
import hashlib
import re

# service run under apache + wsgi, called like:
export NODE=`uname -n`
curl -H "Accept: application/json" -X POST -d '{"pass": "sharedpass", "node": "'${NODE}'"}' http://puppet/puppetreg/submit

# set your shared password here. Clients will use this to verify they're OK to add
sharedpass = 'sharedpass'
# this will get appended in the sanitize step if it's not in the node name,
# this might be useful for some VPC setups where uname -n doesn't add the domain, but the cert signature does
domainname = '.domain.com'
# what all your private names for all ec2 instances start with
vpcprefix = 'ip-10-'

def sanitize(txt):
	# just to be safe, clean up potentially bad inputs
	txt = txt.replace("&", "&amp;")
	txt = txt.replace('<', '&lt;')
	txt = txt.replace('>', '&gt;')
	txt = txt.replace('"', '&quot;')
	txt = txt.replace("'", "&#039;")
	n = re.search(domainname, txt)
	if not n:
		m = re.search(vpcprefix, txt)
		if m:
			txt = txt + domainname
	return txt

# Change working directory so relative paths (and template lookup) work again
root = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, root)

# import DB class shared among scripts
import dbc
dbc = dbc.dbc()

# import bottle stuff
from bottle import get, post, request, debug, run, redirect, route, abort, Bottle, default_app

# accept json data via /submit
@post('/submit')
def add_submit():
	errmsg = 'ERROR: Invalid data received'
	data = request.body.readline()
	# make sure we got data
	if not data:
		abort(400, 'No data received')
	#print data
	# we have data, load it!
	entity = json.loads(data)
	# make sure we got a password
	if not entity.has_key('pass'):
		abort(400, errmsg)
	# make sure we got a node name
	if not entity.has_key('node'):
		abort(400, errmsg)
	# see if we got the right password. If not, throw a 400
	if str(entity["pass"]) != sharedpass:
		abort(400, errmsg)
	# if so, update the last input to incriment the datetime stamp, and create a new entry, to be processed by sign_certs.py
	try:
		sql = "update client set lastnode = '%s'" % (sanitize(entity["node"]))
		dbc.insert(sql)
		sql = "insert into registered (status,node) values (0,'%s')" % (sanitize(entity["node"]))
		dbc.insert(sql)
		return "SUCCESS: added node - %s" % (entity["node"])
	except MySQLdb.Error, e:
		# if we have a problem with mysql, let us know
		return "An error has been passed. %s" %e
		abort(400, "Registration failed!")

# generate general cert signature status
@route('/status')
def status():
	# look for any status 2 entries in the db, this means the cert didn't get signed.
	sql = "select count(status) from registered where status > 1"
	result = dbc.select(sql)
	# if we find some, return ERROR
	if int(result[0][0]) > 0:
		return "ERROR"
	else:
		# if not, return OK
		return "OK"
		
#debug(True) 
application = default_app()
