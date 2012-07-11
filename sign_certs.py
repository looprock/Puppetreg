#!/usr/bin/env python
import os
import sys
import subprocess
import re
from time import localtime, strftime

# run this from cron every minute

enable_debug = "F"
enable_log = "T"

# just being pedantic
root = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, root)

#logging stuff
logfile = root + "/log/sign_certs.log"
def writelog(msg):
	if enable_log == "T":
        	recdate = strftime("%Y-%m-%dT%H:%M:%S%Z", localtime())
        	log = open(logfile, 'a')
		txt = "%s %s\n" % (recdate, msg)
        	log.write(txt)
        	log.close()

# debug stuff
def debug(txt):
	if enable_debug == "T":
		detxt = "DEBUG - %s" % (txt)
		writelog(detxt)

# i created a class for database stuff since it's also used for the cert signing script
import dbc
dbc = dbc.dbc()

# pull the last check and update times, and see if lastupdate is newer
lastcheck = dbc.select("select lastcheck from update_check")
lastupdate = dbc.select("select lastupdate from client")
if lastupdate[0] > lastcheck[0]:
	output = "New cert(s) in queue - lastupdate: %s, lastcheck: %s" % (lastupdate[0],lastcheck[0])
	debug(output)
	# if lastupdate is newer, look for the new nodes in the DB
	sql = 'select node from registered where status=0 and entered BETWEEN "%s" and NOW()' % (lastcheck[0])
	output = "Executing: %s" % (sql)
	debug(output)
	result = dbc.select(sql)
	for i in result:
		# try to sign new certs
		output = "Attempting to add: %s" % (i[0])
		p = subprocess.Popen(["puppet","cert","sign",i[0]], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        	stdout, stderr = p.communicate()
		# for some reason error statements report to stderr in puppet cert sign, so look for "err:" string in output
		m = re.search("err:", stdout)
           	if m:
			# if we find an error, set status to 2 so:
			# 1. this node will be bypassed on the next run
			# 2. the status will get picked up by /puppetreg/status, which is hopefully being monitored
			sql = 'update registered set status=2 where node="%s"' % (i[0])
			dbc.insert(sql)
			output = "Executing: %s" % (sql)
			debug(output)
                	error = "Issue signing cert %s - %s" % (i[0],stdout.strip())
			writelog(error)
			#sys.exit(error)
		else:
			# if everything looks ok, set the status to 1 so the node will be bypassed on next run
			sql = 'update registered set status=1 where node="%s"' % (i[0])
			dbc.insert(sql)
			output = "Executing: %s" % (sql)
			debug(output)
			msg = "signed cert for node %s" % (i[0])
			writelog(msg)
		# we always want to update 'lastupdate'
		sql = 'update update_check set lastnode="%s"' % (i[0])
		output = "Executing: %s" % (sql)
        	debug(output)
		dbc.insert(sql)
else:
	# this is just for debug
	output = "No new cert(s) in queue - lastupdate: %s, lastcheck: %s" % (lastupdate[0],lastcheck[0])
        debug(output)
