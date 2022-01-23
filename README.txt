Linux app for Splash-tiles.com
--------------------------------------------------------

This app will allow you to register your Linux device to your Splash-tiles.com cloud account.

Once registered, you can create schedules for this device just like your Android players.


To register, just run 
  ./splash_tiles_register.py   username  password

This will create the unique UUID for this device and add it to your Splash-tiles.com account.

After you have created your schedules, you can run this app to automatically fetch the schedule and run it.


you may need to install some python packages

sudo pip install pause


Add the command

./splash_tiles.py   

to your system startup scripts

If you are using IRUSB, make sure you are also running the IRUSB linux app and check to make sure the 
path to the IRUSB control socket is correct  (in splash_tiles.py)


NOTE:  This splash_tiles.py script will not work if run from SSH (can't open the display remotely).  It needs to be run from the pi itself (via startup scripts or console)

