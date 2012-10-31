#!/usr/bin/env python

# original source: http://github.com/adafruit/Tweet-a-Watt/blob/master/wattcher.py
# tps, 03.14.2011 - fix for data output spikes
print "Sensor Manager..."
print "CS262a project based on code from Tinaja labs"
print "--------------------------------------------"

import serial, time, datetime, sys, random, math
import syslog
from xbee import xbee
import twitter
import sensorhistory
import ConfigParser, os

# to send feeds to Sen.se
import urllib, urllib2, httplib
import simplejson
print "imported simplejson lib..."

SERIALPORT = "/dev/ttyAMA0"    # the com/serial port the XBee is connected to
BAUDRATE = 9600      # the baud rate we talk to the xbee
CURRENTSENSE = 4       # which XBee ADC has current draw data
VOLTSENSE = 0          # which XBee ADC has mains voltage data
MAINSVPP = 170 * 2     # +-170V is what 120Vrms ends up being (= 120*2sqrt(2))
# Calibration for sensor #0
# Calibration for sensor #1
# Calibration for sensor #3
# Calibration for sensor #4
# Calibration for sensor #5
# etc... approx ((2.4v * (10Ko/14.7Ko)) / 3
vrefcalibration = [0,
                   488,
                   0,
                   487,
                   485,
                   0,
                   0,
                   0,
                   0,
                   0,
                   0,
                   0,
                   486]
CURRENTNORM = 15.5  # conversion to amperes from ADC

# set up the config file parser
config = ConfigParser.ConfigParser()
config.read("/home/tinaja/default.cfg")

# open up the serial port to get data transmitted to xbee
try:
    ser = serial.Serial(SERIALPORT, BAUDRATE)
    ser.open()
    print "TLSM - serial port opened..."
    syslog.syslog("TLSM.opening: serial port opened...")
except Exception, e:
    print "Serial port exception: "+str(e)
    syslog.syslog("TLSM.opening exception: serial port: "+str(e))
    exit

# detect command line arguments
DEBUG = False
if (sys.argv and len(sys.argv) > 1):
    if sys.argv[1] == "-d":
        DEBUG = True


##############################################################
# the main function
def mainloop(idleevent):
    global sensorhistories, DEBUG, COSM_KEY

    # grab one packet from the xbee, or timeout
    try:
        packet = xbee.find_packet(ser)
        if not packet:
            # print "    no serial packet found... "+ time.strftime("%Y %m %d, %H:%M")
            # syslog.syslog("TLSM.mainloop exception: no serial packet found..." )
            return
    except Exception, e:
        print "TLSM.mainloop exception: Serial packet: "+str(e)
        syslog.syslog("TLSM.mainloop exception: Serial packet: "+str(e))
        return


    try:
        xb = xbee(packet)    # parse the packet
        if not xb:
            print "    no xb packet found..."
            syslog.syslog("TLSM.mainloop exception: no xb packet found...")
            return
    except Exception, e:
        print "TLSM.mainloop exception: xb packet: "+str(e)
        syslog.syslog("TLSM.mainloop exception: xb packet: "+str(e))
        return

    # this traps an error when there is no address_16 attribute for xb
    # why this happens is a mystery to me
    try:
        if xb.address_16 == 99:
            return
    except Exception, e:
        print "xb attribute (address_16) exception: "+str(e)
        syslog.syslog("TLSM.mainloop exception: xb attribute: "+str(e))
        return

    # ------------------------------------------------------------------
    # break out and do something for each device
    # this should eventually be changed into an array or object class
    # CJ, 03.12.2011, added SenseFeedKey to send feeds to Sen.se

    if xb.address_16 == 1: # Tomato
        tLogApiKey = ""
        SenseFeedKeys = [0,0,0,0]
        cosmLogKey = "29631"
        ThingSpeakKey = ""

        adcinputs = [0,1,2,3]
        for i in range(len(adcinputs)):
            cXbeeAddr = str(xb.address_16)
            cXbeeAdc = str(adcinputs[i])
            adcSensorNum = int(cXbeeAddr + cXbeeAdc)
            avgunit = getmVolts(xb,adcinputs[i])
            if adcinputs[i] == 1:
                avgunit = calctemp(xb)

            SenseFeedKey = str(SenseFeedKeys[i])

            # print "adcSensorNum", adcSensorNum, avgunit
            sensorhistory = sensorhistories.find(adcSensorNum)
            addunithistory(sensorhistory, avgunit)
            fiveminutelog(sensorhistory, tLogApiKey, cosmLogKey, SenseFeedKey, ThingSpeakKey, 1023, xb.rssi, adcinputs[i])


    else:
        return





# sub-routines
##############################################################
def fiveminutelog(loSensorHistory, LogApiKey, cosmLogKey, SenseLogKey, cThingSpeakKey, lnCosmMaxVal, xbRssi, adcinput):
    # Determine the minute of the hour (ie 6:42 -> '42')
    # currminute = (int(time.time())/60) % 10
    currminute = (int(time.time())/60) % 5
    fiveminutetimer = loSensorHistory.fiveminutetimer

    # Figure out if its been five minutes since our last save
    if (((time.time() - fiveminutetimer) >= 60.0) and (currminute % 5 == 0)):
        # print " . 5min test: time.time()=", time.time(), " fiveminutetimer=", fiveminutetimer, "currminute=", currminute, " currminute % 5: ", currminute % 5
        # units used in last 5 minutes
        sensornum = loSensorHistory.sensornum
        avgunitsused = loSensorHistory.avgunitsover5min()

        # print "\n"
        # print "TLSM.fiveminutelog: " + time.strftime("%Y %m %d, %H:%M")+":  Sensor# "+str(sensornum)+" has averaged: "+str(avgunitsused)
        syslog.syslog("TLSM.fiveminutelog: Sensor# "+str(sensornum)+" has averaged: "+str(avgunitsused))

        lnStartLogging = time.time()
        # log to the local CSV file
        logtocsv(sensornum, avgunitsused, logfile)
        print "  #",sensornum,"time to CSV =", time.time() - lnStartLogging

        lnStartLogging = time.time()
        # send to the tinaja data logger
        # logtotinaja(sensornum, avgunitsused, LogApiKey)
        print "  #",sensornum,"time to Tinaja DL =", time.time() - lnStartLogging

        lnStartLogging = time.time()
        # send to the cosm data logger
        logtocosm(sensornum, avgunitsused, cosmLogKey, lnCosmMaxVal, xbRssi, adcinput)
        print "  #",sensornum,"time to Cosm DL =", time.time() - lnStartLogging

        # CJ, 03.12.2011, added logtosense() to send feeds to Sen.se
        lnStartLogging = time.time()
        # send to the sen.se data logger
        logtosense(sensornum, avgunitsused, SenseLogKey)
        print "  #",sensornum,"time to Sense DL =", time.time() - lnStartLogging

       # CJ, 05.04.2011, added logtothing() to send feeds to ThingSpeak
        lnStartLogging = time.time()
        # send to the ThingSpeak data logger
        logtothing(sensornum, avgunitsused, cThingSpeakKey, adcinput)
        print "  #",sensornum,"time to Thing Speak DL=", time.time() - lnStartLogging


        # Reset the 5 minute timer
        loSensorHistory.reset5mintimer()


##############################################################
# log to the local CSV file
def logtocsv(lnSensorNum, lnAvgUnits, loLogfile):

        # Lets log it! Seek to the end of our log file
        if loLogfile:
            loLogfile.seek(0, 2) # 2 == SEEK_END. ie, go to the end of the file
            loLogfile.write(time.strftime("%Y %m %d, %H:%M")+", "+
                          str(lnSensorNum)+", "+
                          str(lnAvgUnits)+"\n")
            loLogfile.flush()
            # print "Sensor# ", lnSensorNum, "logged ", lnAvgUnits, " to ", loLogfile.name


##############################################################
def getlogfile():
# open our datalogging file
# CJ, 05.13.2011, included /logs/ directory under www
    global LOCALLOGPATH

    TimeStamp = "%s" % (time.strftime("%Y%m%d"))
    # print "TimeStamp", TimeStamp
    filename = LOCALLOGPATH+TimeStamp+".csv"   # where we will store our flatfile data

    lfile = None
    try:
        lfile = open(filename, 'r+')
    except IOError:
        # didn't exist yet
        lfile = open(filename, 'w+')
        lfile.write("#Date, time, sensornum, value\n");
        lfile.flush()

    return lfile



##############################################################
# do some setup here at the end

try:
    # LOCALLOGPATH = "/opt/www/tinajalog"
    LOCALLOGPATH = ConfigSectionMap("paths")['locallogpath']

    print "Successfully configured..."
    syslog.syslog("TLSM.config: Successfully configured...")

except Exception, e:
    print "There was a problem with the configuration: "+str(e)
    syslog.syslog("TLSM.config exception: "+str(e))
    exit


##############################################
# open our datalogging file
logfile = getlogfile()
print "Log file "+logfile.name+" opened..."

# load sensor history from the logfile
sensorhistories = sensorhistory.SensorHistories(logfile)
# print "Sensor history: ", sensorhistories
print "Sensor history loaded..."


##############################################
syslog.syslog("<<<  Starting the Tinaja Labs Sensor Manager (TLSM)  >>>")
print "The main loop is starting..."


##############################################
# the 'main loop' runs once a second or so
while True:
    mainloop(None)

    if islogcurrent(logfile.name) == False:
        logfile = getlogfile()
        # print "current log file=", logfile.name
