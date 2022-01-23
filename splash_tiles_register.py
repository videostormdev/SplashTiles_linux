#!/usr/bin/env python3
import sys
import time
import select
import os
import requests
import urllib
import uuid

#sys.stderr = open('/var/log/fb.log', 'a+')

uname = sys.argv[1]
password = sys.argv[2]

#this script will register this device to your Splash-Tiles.com account
if (os.path.isfile("uuid.spl")):
	rfile = open("uuid.spl","r")
	uuid = rfile.read()
	rfile.close()
else:
	uuid = str(uuid.uuid4())
	tfile = open("uuid.spl","w")
	tfile.write(uuid)
	tfile.close()

uuida = {'uuid': uuid}

#first check if already registered
murl = "https://splash-tiles.com/console/server/checkregistration.php?" + urllib.parse.urlencode(uuida)
#r = requests.get(murl, verify= False)
r = requests.get(murl)
#403 not registered,  #412 too many devs, #200 ok
if (r.status_code == 200):
	print ('This device is already registered!')
	sys.exit()
elif (r.status_code == 412):
	print ('You have too many devices.  Please increase your subscription plan!')
	sys.exit()


rargs = {'uuid': uuid, 'dname': uuid, 'dtype': 4, 'uname': uname, 'psswd': password}
murl = "https://splash-tiles.com/console/server/dregister.php?" +  urllib.parse.urlencode(rargs)
#r = requests.get(murl, verify = False)
r = requests.get(murl)

#200 is ok, 412 for fail
if (r.status_code == 200):
	print ('Registered device successfully!  UUID is ' + uuid)
else:
	print ('Failed to register, check your uname and password')



