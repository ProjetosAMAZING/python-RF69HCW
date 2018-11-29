
import time
import sys
import spidev
import RPi.GPIO as GPIO
from RFM69registers import *


spi = spidev.SpiDev()
spi.open(0,1)
spi.max_speed_hz = 1000000

rf69_state = M_STDBY
TX=0;
RX=0;
packetSent=0
packetReceived=0
ack = 0
timeout = 0
def config():
    print("init");
          
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(18,GPIO.IN)
    writeRegister(0x01,0x04)
    setMode(M_STDBY)

    writeRegister(0x02,0x00)

    writeRegister(0x07,Freq_MSB)
    writeRegister(0x08,Freq_MID)
    writeRegister(0x09,Freq_LSB)

    writeRegister(0x03,0x02)
    writeRegister(0x04,0x40)

    writeRegister(0x05,0x03)
    writeRegister(0x06,0x33)
    
    writeRegister(0x11,0x40 | 0x20 | 0x1F)
    writeRegister(0x58,0x2D)

    writeRegister(0x19,RXBW_DCCFREQ_010 | RXBW_MANT_16 | RXBW_EXP_2)

    writeRegister(0x25,DIO0_01)
    writeRegister(0x26,CLK_OUT_OFF)

    writeRegister(0x28,0x10)

    writeRegister(0x29,220)

    writeRegister(0x2E,SyncON |AUTO_FIFOFILL | 0x08)

    writeRegister(0x2F,0x2D)
    writeRegister(0x30,100)

    writeRegister(0x37,0x80 | NONE_CODE | crcON)

    writeRegister(0x38,64)

    writeRegister(0x3C,0x01)

    writeRegister(0x3D,AUTORXRESTART_ON | AES_OFF)

    GPIO.remove_event_detect(18)
    GPIO.add_event_detect(18,GPIO.RISING,callback=isrRXTX,bouncetime=1)
    data = spi.xfer([0x10&0x7F,0]);
    print(data)

    
    
def isrRXTX(chanel):
#    print("isr")    
    global rf69_state
    global TX
    global RX
    #print("INTERRUPT")
    #print(rf69_state)
    if(rf69_state == M_TX):
        TX = 1
 #       print("yo sent")
    elif(rf69_state == M_RX):
        RX = 1
#       print("yo received!")

def st():
    print("hey")

def setMode(state):
    global rf69_state
    
    if(rf69_state != state):
        
        value = readRegister(REG_OPMODE)
        value &=MODE_BITS

        if state == M_STDBY:
            
            value |= opMode_STDBY
            
        elif state == M_RX:
#	    print("RX");            
            value |= 0x10
#	    print(value);
            writeRegister(0x5A,0x55)
            writeRegister(0x5C,0x70)
            
        elif state == M_TX:
 #           print("TX")
            value = opMode_TX
            writeRegister(0x5A,0x5D)
            writeRegister(0x5c,0x7C)
            
        else:
            
            value |= opMode_STDBY

        writeRegister(REG_OPMODE,value)
        rf69_state = state
        
        
#    while((readRegister(RegIrqFlags1)&MODEREADY) == 0):
 #      pass
            
    
def waiToReceive():
    setMode(M_STDBY)

    writeRegister(0x25,0x40)

    setMode(M_RX)

def receiveDone():
    global rf69_state
    global RX
    global ack
#    print("state: " + rf69_state + " " + RX)
    
    if(rf69_state == 0x04 and  RX == 1):
	setMode(M_STDBY)
	#print("here")
	RX = 0
	ack = 1
	return 1
    elif(rf69_state == M_RX):
        return 0
    else:
        waiToReceive()
        return 0

    
def sendMessage(vel,car_state):
    #print("hello")
    setMode(M_STDBY)
    writeRegister(0x25,DIO0_00)
    writeRegister(0x28,0x10);
    global packetSent
    global TX
    global ack
    global timeout
    if(ack ==0):
	timeout = timeout + 1
	if(timeout>12):
		packetSent=0
		timeout = 0
		print("timeout")
    else:
	ack = 0
	timeout =0
   	
    value1 = (packetSent&0xFF00)>>7
    value2 = (packetSent&0x00FF)
    
    spi.xfer2([REG_FIFO | SPI_WRITE,5,value1,value2,vel,car_state])

    setMode(M_TX)

    while(TX==0):
        pass

    packetSent=packetSent+1

   
    
    TX = 0

    print("sent")
    #print('heelllo')

def readMessage():
    setMode(M_STDBY)
    data =spi. xfer2([REG_FIFO&0x7EF,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    writeRegister(0x28,FIFO_OVERRUN)
    return data
    
def writeRegister(adress,value):
    spi.xfer([adress|0x80, value])

def readRegister(adress):
    return spi.xfer([adress &0x7F,0])[1]
