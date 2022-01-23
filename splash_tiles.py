#!/usr/bin/env python3
import sys
import time
import pause 
import select
import signal
import requests
import os
from datetime import datetime
from datetime import timedelta
import json
import socket
import urllib
from requests import Session
from requests.exceptions import HTTPError

# likely need to do   sudo pip install pause


# this script will download your schedule once per day and keep it executing
#   this should be executed from your startup scripts

# Prior to using this script use splash_tiles_register.py to register this device
#   The registration script saves the UUID file used by this script, so they should be in the same directory

#chromium-browser --enable-features=VaapiVideoDecoder --ignore-gpu-blocklist --allow_running_insecure_content --noerrdialogs --incognito --autoplay-policy=no-user-gesture-required --check-for-update-interval=1 --simulate-critical-update --kiosk YOUR_SPLASHTILES_SCREEN_URL

# modify below for platform specific flags or browsers  (this is for RPi 4b)
browsercmd = "/usr/bin/chromium-browser --enable-features=VaapiVideoDecoder --ignore-gpu-blocklist --allow_running_insecure_content --noerrdialogs --incognito --autoplay-policy=no-user-gesture-required --check-for-update-interval=1 --simulate-critical-update --kiosk "


# if using with IRUSB, below is the path to the IRUSB linux socket  (modify if running irusb app in different directory)
irusb_socket = "./irusb_socket"


# uncommment this if you would like a log
#sys.stderr = open('/var/log/fb.log', 'a+')

def exit_app():
	#any specific shutdown proceedure can be done here
	# we are just killing our child process
	global childpid
	if (childpid >0):
		#kill prior
		os.kill(childpid,signal.SIGTERM)
		childpid=-1

def signal_handler(signal, frame):
	exit_app()
	sys.exit(0)


def getcmdtime(ccmd, cmd_time):
	if (ccmd[0] == "LTIME"):
		newtime = datetime(cmd_time.year,cmd_time.month,cmd_time.day,int(ccmd[2]),int(ccmd[3]),int(ccmd[4]),0)
		return newtime
	elif (ccmd[0] == "WAIT"):
		return cmd_time + timedelta(hours=int(ccmd[2]), minutes=int(ccmd[3]), seconds=int(ccmd[4]))
	else:
		return cmd_time;

def runcmd(ccmd):
	if (ccmd[0] == "FULL"):
		run_full(ccmd[2])
	elif (ccmd[0] == "PIP"):
		# PIP could be supported by opening chromium in windowed mode instead of full screen
		#  your desktop would be shown otherwise
		print ("Unsupported command " + ccmd[0])
	elif (ccmd[0] == "OVEL"):
		# chromium browser doesn't support transparent background
		print ("Unsupported command " + ccmd[0])
	elif (ccmd[0] == "IRCODE"):
		# use HEX codes on this platform
		print ("Unsupported command " + ccmd[0])
	elif (ccmd[0] == "IRHEX"):
		# requires our IRUSB device and running linux driver app
		run_irusb(ccmd[4],ccmd[2])
	elif (ccmd[0] == "LTIME"):
		print("Executed")
	elif (ccmd[0] == "WAIT"):
		print("Executed")
	else:
		print ("Unknown command " + ccmd[0])


def run_full(nam):
	global childpid
	global browsercmd
	global uuid
	if (childpid >0):
		#kill prior
		os.kill(childpid,signal.SIGTERM)
		childpid = -1

	if (nam == "000"):
		print ("Closing browsers")
		return
	childpid = os.fork()
	if (childpid > 0):
		print("Started browser id " + str(childpid))
	else:
		time.sleep(4)
		fcmd = browsercmd + "'https://splash-tiles.com/splashtiles/display.php?slide=" + nam + "&token=" + uuid + "'"
		print("Starting browser to: " + fcmd)
		os.system(fcmd)
		sys.exit(0)

def run_irusb(devid,code):
	global irusb_socket
	if os.path.exists(irusb_socket):
		ircmd = "QSIRPULSE "
		if (len(devid)>2):
			ircmd = ircmd + "ID=" + devid + " "
		ircmd = ircmd + "R=03 " + code + "\r"
		client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
		client.connect(irusb_socket)
		client.send(ircmd)
		time.sleep(2)
		client.close()

	else:
		print("Cannot find IRUSB socket")


signal.signal(signal.SIGINT, signal_handler)    # exit gracefully

loop_var = 1
childpid = -1
last_update = -1
schedule = {}
uuid = ""

if (os.path.isfile("uuid.spl")):
        rfile = open("uuid.spl","r")
        uuid = rfile.read()
        rfile.close()
else:
	print("No UUID, please register this device first")
	sys.exit(0)

while loop_var>0:
	#update

	uuida = {'uuid': uuid}
	murl = "https://splash-tiles.com/console/server/fetchschedule.php?" + urllib.parse.urlencode(uuida);
	#r = requests.get(murl, verify= False)
	r = requests.get(murl)
	if (r.status_code != 200):
        	print ('Schedule cannot be fetched, error code ' + r.status_code)
	else:
		#update schedule
		schedule = r.json()

	#run schedule for this day, loop at end of day
	#   these all run on local machine time, make sure it is set!
	dtoday = datetime.now()
	dtomorrow = dtoday + timedelta(days=1)
	dtomorrow_morning = datetime(dtomorrow.year, dtomorrow.month, dtomorrow.day,0,0,10,0)
	cmd_time = datetime(dtoday.year, dtoday.month, dtoday.day,0,0,10,0)

	wday = dtoday.weekday()  #python is 0 is monday   we use 1 is sunday
	wday = wday + 2 
	if wday>7:
		wday = 1
	
	cday = "dow" + str(wday)

	if cday in schedule:
		#run todays schedule    [[cmdstr],[cmdstr],etc]      cmdstr = "cmd","p1","p2",etc
		
		cmds = json.loads(schedule[cday])

		for ccmd in cmds:
			#execute if time>command time, else wait first
			time2go = getcmdtime(ccmd,cmd_time)
			if (time2go > datetime.now()):
				print("Waiting for next event at" + time2go.strftime("%H:%M"))
				pause.until(time2go)
			print("Executing cmd " + ccmd[0] + " cmdtime " + time2go.strftime("%H:%M"))
			runcmd(ccmd)
			cmd_time = time2go

	else:
		print('Nothing to run on day ' + cday);

	print("Waiting for next day")
	pause.until(dtomorrow_morning)

exit_app()
