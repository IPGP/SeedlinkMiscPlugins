#!/usr/bin/python3 -u

# Written by Tristan DIDIER, OVSG/IPGP, 2019
# This script is a front-end script for miscScript plugin
# It has been, in first place, developped for and tested on BeagleBone Black
# It aims at reading i2c data from MCP3424 A/D, used for instance in ADC Pi and ADC Differential Pi Boards of ABelectronics.
# This code is freely inspired from the example code provided by ABelectronics : https://www.abelectronics.co.uk/kb/article/10/adc-pi-on-a-beaglebone-black

from smbus2 import SMBus
from time import time,gmtime,strftime,sleep
from math import ceil
from sys import stderr

class ABelec:
    """ class to drive ADC Pi Board from ABElectronics """

    rate_code={240:0x00, 60:0x01, 15:0x02, 3.75:0x03} #sps to sample rate selection bits
    pga_code={1:0x00,2:0x01,4:0x02,8:0x03}  #PGA gain to PGA gain selection bits
    numberBits={240:12, 60:14, 15:16, 3.75:18}  #sps to corresponding bits number

##### __INIT__#####

    def __init__(self,i2c_bus,adc_addresses,adc_sample_rate,pga_gain,continuous):
        """ Constructor : initialize object attributs"""
        
        #connect i2c
        self.bus=SMBus(i2c_bus)
        
        #get MCP3422 addresses
        self.adc_addresses=adc_addresses
        
        #get MCP3422 expected answer size and generate corresponding data/sign_filter
        if adc_sample_rate==3.75:
            self.read_size=4
        else:
            self.read_size=3

        self.data_filter=pow(2,ABelec.numberBits[adc_sample_rate]-1)-1
        self.sign_filter=pow(2,ABelec.numberBits[adc_sample_rate]-1)

        #Generate static configuration
        S10=ABelec.rate_code[adc_sample_rate]   # Sample rate selection
        G10=ABelec.pga_code[pga_gain]   # PGA gain selection
        C10=0x00    # Channel selection
        RDI=1   # Ready bit
        OC=continuous   # Continuous:1 , One-shot:0

        self.staticConf= RDI << 7 | C10 << 5 | OC << 4 | S10 << 2 | G10

##### GETADCREADING #####

    def getadcreading(self, channel):
        """ Read channels n° "channel" (parameter) simultaneously on all ADCs """
        
        res=[None]*len(adc_addresses) # results' array
        adcConfig=self.staticConf | channel << 5 # generate conf byte from staticConf and "channel" parameter

        OK_devices=0 # count the number of ADCs wich already return a result
        i_device=0 # current device index

   
        while OK_devices<len(adc_addresses) :
            if res[i_device]==None:#If ADC n# "i_device" have not yet returned a result
                adcreading = self.bus.read_i2c_block_data(self.adc_addresses[i_device],adcConfig,self.read_size)#i2c reading
                confRead = adcreading[self.read_size-1]#Extract conf byte
                if ~confRead & 128 :# and check if result is ready
                    OK_devices+=1
                    
                    #bitarray to int
                    data=0
                    for i in (range(0,self.read_size-1)):
                        data+=int(adcreading[i]) << 8*(self.read_size-2-i)
                    
                    #If the result is negative, covert to negative int
                    if data & self.sign_filter :
                        data=-(self.sign_filter-(data & self.data_filter))
                    
                    #Save the result in array
                    res[i_device]=data

            #Move to next device
            i_device=(i_device+1)%len(adc_addresses)

        #return result
        return res 

##### EPRINT #####

def eprint(msg):
    """ print to stderr """
    print(msg,file=stderr)

#### AUTO_TEST #####

if __name__=="__main__":

    # Vars
    i2c_bus=2
    adc_addresses=[0x68,0x69]
    channels_per_adc=4
    adc_sample_rate=3.75
    pga_gain=1
    continuous=1
    read_period=1
    res_tab=[None]*(len(adc_addresses)*channels_per_adc)#result array
    latency_tolerance=0.2

    #Initialize ABelec Object
    mABelec=ABelec(i2c_bus,adc_addresses,adc_sample_rate, pga_gain, continuous)
    #timing variable
    nextTime=ceil(time())

    while(True):
        wait=nextTime-time()

        #Check time sync
        if wait>0:
            if wait < read_period :
                sleep(wait)
            else :
                nextTime=ceil(time())
                eprint("wait > read_period : {} > {} -> New ref time defined".format(wait,read_period))
                continue
        else :
            if wait > -read_period*latency_tolerance:
                eprint("0 > wait but  wait > -tolerance : 0 > {} but {} > {}".format(wait,wait,-read_period*latency_tolerance))
            else :
                nextTime=ceil(time())
                eprint("wait < -tolerance : {} < {} -> New ref time defined".format(wait,-read_period*latency_tolerance))
                continue


        # read ADCs' channels
        for channel in range(channels_per_adc) :
            adcReadings=mABelec.getadcreading(channel)

            # store result in array
            for i in range(len(adcReadings)) :                
                res_tab[i*channels_per_adc+channel]=adcReadings[i]

        # generate ASCII frame
        frame=strftime("%Y-%m-%d %H:%M:%S.000", gmtime(nextTime))+','+','.join(map(str,res_tab))#+"\n"
        nextTime+=read_period

        # and print it on stdout
        print(frame)



      


                
            

