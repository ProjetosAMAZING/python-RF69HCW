import time
import sys
import spidev
import RPi.GPIO as GPIO
from RFM69registers import *
import teste as RF69
#from threading import Timer,Thread,Event
#from flask import *
#from flask_socketio import SocketIO

def rfprocess():
	global lastmsg
	while(1):
		if(time.time()-lastmsg >=0.333):
			RF69.sendMessage(0,1)
			print("sent");
			RF69.waiToReceive()
			lastmsg = time.time()
		else:
			if(RF69.receiveDone()):
				#print("recebi")
				print(RF69.readMessage())

print("Ola")
RF69.config()
print("config Done")
lastmsg = time.time()
rfprocess()
#t = Thread(target=rfprocess)
#t.start();
