import serial
from serial.tools import list_ports
import time
#import usbtmc
import time
import traceback
import paramiko
import pymysql
import queue
import subprocess
import traceback
import pyaudio
import soundfile
import wave
import numpy as np

from PIL import Image
import numpy as np
from scipy.stats import pearsonr

import pandas as pd
import glob
import os
import time
import shutil
import filecmp
#import board
from rasp_libhackrf import *
from pylab import *
import board
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219

def dc_measure():
    try:
        from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219
        i2c_bus = board.I2C()

        ina1 = INA219(i2c_bus,addr=0x40)
        ina2 = INA219(i2c_bus,addr=0x41)
        ina3 = INA219(i2c_bus,addr=0x42)
        ina4 = INA219(i2c_bus,addr=0x43)

        ina1.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        ina1.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        ina1.bus_voltage_range = BusVoltageRange.RANGE_16V

        ina2.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        ina2.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        ina2.bus_voltage_range = BusVoltageRange.RANGE_16V


        ina3.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        ina3.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        ina3.bus_voltage_range = BusVoltageRange.RANGE_16V

        ina4.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        ina4.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        ina4.bus_voltage_range = BusVoltageRange.RANGE_16V

        bus_voltage1 = round(ina1.bus_voltage,2)
        bus_voltage2 = round(ina2.bus_voltage,2)
        bus_voltage3 = round(ina3.bus_voltage,2)
        bus_voltage4 = round(ina4.bus_voltage,2)

        vol_list=[bus_voltage1,bus_voltage2,bus_voltage3,bus_voltage4]
        print(vol_list)
        return vol_list
    except Exception as e:
        print(e)
        pass

    
def vol(ser_switch,dc1_range,tp28_range,resq):
    #switchto(ser_switch2,status=0)
    voldc=False
    volpoe=False
    try:
        ser_switch.write(b"\x4f") #568
        time.sleep(5) 
        _vol=dc_measure()
        voldc12=_vol[3]
        voltp282=_vol[2]
        if compare(voldc12,dc1_range) and compare(voltp282,tp28_range):
            print("volpoe test pass")
            volpoe=True
        else:
            print("volpoe test fail")
            volpoe=False

        
        ser_switch.write(b"\x3f") #78
        time.sleep(1)
        _vol=dc_measure()
        voldc11=_vol[3]
        voltp281=_vol[2]
        print(voldc11,voltp281,dc1_range,tp28_range)
        if compare(voldc11,dc1_range) and compare(voltp281,tp28_range):
            print("voldc test pass")
            voldc=True
        else:
            print("voldc test fail")
            voldc=False

        ser_switch.write(b"\x8f") #567

        if volpoe==True and voldc==True:
            resq.put(["vol",True,voldc11,voldc12])
        else:
            resq.put(["vol",False,voldc11,voldc12])
    except:
        resq.put(["vol",False,voldc,volpoe])
        traceback.print_exc()


def ssh_cmd(ssh_shell,cmd,response):
    try:
        watchdog=time.time()
        channel_output=b""
        ssh_shell.send(cmd.encode()+b"\n")
        print("sshinput:",cmd)
        if response==True:
            while True:
                time.sleep(0.1)
                if ssh_shell.recv_ready():
                    pass_out = ssh_shell.recv(102400)
                    channel_output += pass_out
                    if pass_out.endswith(b'# '):
                        print("sshoutput:",channel_output)
                        return channel_output
                        break
                    if time.time()-watchdog>10:
                        print("ssh timeout read 1")
                        return False
                        break
                elif time.time()-watchdog>10:
                    print("ssh timeout read 2")
                    return False
                    break
                else:
                    time.sleep(0.1)

        else:
            return True
    except:
        traceback.print_exc()
        return False


def getstaip(user,passwd,portnum,ser_switch,ssid,psd,resq):
    try:
        switchto(ser_switch,status=0)
        os.system("rm /var/lib/misc/dnsmasq.leases")
        os.system("/etc/init.d/dnsmasq restart")
        os.system("touch /var/lib/misc/dnsmasq.leases")
        ser_switch.write(b"\x8f")
    except:
        pass
    try:
        ssh_shell=False
        for i in range(90):
            _out=os.popen("cat /var/lib/misc/dnsmasq.leases")
            ip_out=_out.read()
            print(ip_out)
            if "88.88.86" in ip_out and ssh_shell == False:
                ip=ip_out.split()[2]
                print(ip,ip_out.split())
                #resq.put(["getip",True,ip]) 
                #os.popen("rm /var/lib/misc/dnsmasq.leases")
                time.sleep(2)
                os.popen("/etc/init.d/dnsmasq restart")
                ssh = paramiko.SSHClient() 
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=ip,
                            username=user,
                            password=passwd,
                            port=portnum,
                            timeout=1,
                            )

                ssh_shell = ssh.invoke_shell()
                time.sleep(0.5)
                ssh_cmd(ssh_shell,"su -",response=False)
                time.sleep(0.5)
                ssh_cmd(ssh_shell,"N0rt3k$C",response=True)
  
                bspver=ssh_cmd(ssh_shell,"cat /etc/version",response=True)
                bsp_ver=bspver.split()[2].decode()
                print(bspver)

                irver=ssh_cmd(ssh_shell,"/etc/IR_Sense_Relay/mcu.ir.Sense.Relay.sh IR ver",response=True)
                ir_ver=irver.split()[-2].strip()[-12:-1].decode()
                print(ir_ver)

                sensever=ssh_cmd(ssh_shell,"/etc/IR_Sense_Relay/mcu.ir.Sense.Relay.sh Sense ver",response=True)
                sense_ver=sensever.split()[-2].strip()[-12:-1].decode()
                print(sense_ver)
                
                sn_out=ssh_cmd(ssh_shell,"misctool -s",response=True)
                print(sn_out.split())
                sn=((sn_out.split()[2]).decode()).split(":")[-1]
                ethmac_out=ssh_cmd(ssh_shell,"misctool -m",response=True)
                print(ethmac_out.split())
                ethmac=((ethmac_out.split()[2]).decode()).split("ETHMAC:")[1]
                wifimac_out=ssh_cmd(ssh_shell,"cat /sys/class/net/wlan0/address",response=True)
                print(wifimac_out.split())
                wifimac=((wifimac_out.split()[2]).decode())
             
                #channel.send("N0rt3k$C\n")
                ssh_cmd(ssh_shell,"killall wpa_supplicant",True)
                time.sleep(0.5)
                ssh_cmd(ssh_shell,"wpa_passphrase %s %s > wpa.conf"%(ssid,psd),True)
                time.sleep(0.5)
                ssh_cmd(ssh_shell,"wpa_supplicant -B -i wlan0 -c wpa.conf",True)
                time.sleep(0.5)
                ssh_cmd(ssh_shell,"dhclient wlan0 &",True)
                    
            if ssh_shell!=False:
                resq.put(["getip",True,ip,ssh_shell,sn,ethmac.upper(),wifimac.upper(),bsp_ver,ir_ver,sense_ver])
                break
            elif i==59:
                print("Not able to get IP")
                resq.put(["getip",False,False,False,False,False,False,False,False,False])
            else:
                print(".",end="")
                time.sleep(2)
        return ssh_shell
    except:
        resq.put(["getip",False,False,False,False,False,False,False,False,False])
        traceback.print_exc()
        return False




###read IR output, IR firmware version
def ir_test(ssh_shell,ser_ir,resq):
    _ir_res=[]
    data =b'\x1c/3'
    try:
        for ir_port in range(1,13):
            #ser_output=ser_ir.readall()
            IR_cmd = "/etc/IR_Sense_Relay/mcu.ir.Sense.Relay.sh IR %s"%ir_port
            #print(ip,user,passwd,portnum,IR_cmd)
            ssh_cmd(ssh_shell,IR_cmd,True)
            #ssh_cmd(ip,user,passwd,portnum,IR_cmd,response=True)
            time.sleep(0.5)
            ser_output=ser_ir.readall()
            print(ser_output)
            if data in ser_output:
                _ir_res.append(True)
                print("IR%s TEST PASS"%ir_port)
                #resq.put(["IR%s"%ir_port,True])
            else:
                _ir_res.append(False)
                print("IR%s TEST FAIL"%ir_port)
                #resq.put(["IR%s"%ir_port,False])
        if False not in _ir_res:
            resq.put(["ir",True,_ir_res])
        else:
            resq.put(["ir",False,_ir_res])
    except:
        resq.put(["ir",False,[False,False,False,False,False,False,False,False,False,False,False,False]])
        traceback.print_exc()


def rs485_test(ssh_shell,resq):
    try:
        ssh_cmd(ssh_shell,chr(0x03),True)
        #ssh_cmd(ip,user,passwd,portnum,"cp2108_gpioConfig  -D /dev/ttyUSB_RS485_1  -P 8 -V 0 ",response=True)
        #ssh_cmd(ip,user,passwd,portnum,"cp2108_gpioConfig  -D /dev/ttyUSB_RS485_2  -P 9 -V 0 ",response=True)
        #ssh_cmd(ip,user,passwd,portnum,"cat /dev/ttyUSB_RS485_1 &",response=True)
        cmd="cp2108_gpioConfig -D /dev/ttyUSB_RS485_1 -P 8 -V 0;cp2108_gpioConfig -D /dev/ttyUSB_RS485_2  -P 9 -V 0;cat /dev/ttyUSB_RS485_1 &"
        ssh_cmd(ssh_shell,cmd,True)
        #ssh_cmd(ip,user,passwd,portnum,"cp2108_gpioConfig  -D /dev/ttyUSB_RS485_1  -P 8 -V 0;cp2108_gpioConfig  -D /dev/ttyUSB_RS485_2  -P 9 -V 0;cat /dev/ttyUSB_RS485_1 &",response=True)
        time.sleep(1)
        cmd="echo world > /dev/ttyUSB_RS485_2"
        #ssh_cmd(ip,user,passwd,portnum,"echo world > /dev/ttyUSB_RS485_2",response=True)
        RS485_output=ssh_cmd(ssh_shell,cmd,True)
        time.sleep(1)
        print(RS485_output)
        if b'world\r\n' in RS485_output:
            print("RS485 TEST PASS")
            resq.put(["rs485",True])
            ssh_cmd(ssh_shell,"killall cat",False)

        else:
            print("RS485 TEST FAIL")
            ssh_cmd(ssh_shell,"killall cat",False)
            resq.put(["rs485",False])
    except:
        resq.put(["rs485",False])
        traceback.print_exc()


def sense_test(ssh_shell,ser_switch,sensevol_range,resq):    ## to be verifed
    try:
        #signal_output=ssh_cmd(ser_linux,"/etc/IR_Sense_Relay//mcu.ir.Sense.Relay.sh Sense read",ends=b"# ",response=True)
        cmd="/etc/IR_Sense_Relay//mcu.ir.Sense.Relay.sh Sense read"
        signal_output=ssh_cmd(ssh_shell,cmd,True)
        if b"0f" in signal_output:
            print("4 signal detect pass")
            
            ser_switch.write(b"\x8e") #1567
            time.sleep(1)
            sense1=dc_measure()[0]
            print(sense1)
            
            ser_switch.write(b"\x8d") #2567
            time.sleep(1)
            sense2=dc_measure()[0]
            print(sense2)
            
            ser_switch.write(b"\x8b") #3567
            time.sleep(1)
            sense3=dc_measure()[0]
            print(sense3)
            
            ser_switch.write(b"\x87") #4567
            time.sleep(1)
            sense4=dc_measure()[0]
            print(sense4)

            ser_switch.write(b"\x8f") #567

            _res_sense=[compare(sense1,sensevol_range),compare(sense2,sensevol_range),compare(sense3,sensevol_range),compare(sense4,sensevol_range)]
            
            if False not in _res_sense:
                resq.put(["sense",True,_res_sense])
            else:
                resq.put(["sense",False,_res_sense])
        else:
            resq.put(["sense",False,[False,False,False,False]])
    except:
        resq.put(["sense",False,[False,False,False,False]])
        traceback.print_exc()        


def rs232_test(ssh_shell,resq):
    _rs232_res=[]
    try:
        for i in range(1,5):
            if (i%2)==0:
                ssh_cmd(ssh_shell,"cp2108_gpioConfig  -D /dev/ttyUSB_RS232_%s  -P %s -V 0;cp2108_gpioConfig  -D /dev/ttyUSB_RS232_%s  -P %s -V 0;cat /dev/ttyUSB_RS232_%s &"%(i,2,i+4,3,i+4),True)
                RS232_output=ssh_cmd(ssh_shell,"echo hello > /dev/ttyUSB_RS232_%s "%i,True)
                print("RS232 IS",RS232_output)
                m+=2
                time.sleep(1)
                if b'hello\r\n' in RS232_output:
                    print("RS232_%s num modem TEST PASS"%i)
                    ssh_cmd(ssh_shell,"cp2108_gpioConfig  -D /dev/ttyUSB_RS232_%s  -P %s -V 1;cp2108_gpioConfig  -D /dev/ttyUSB_RS232_%s  -P %s -V 1;cat /dev/ttyUSB_RS232_%s &"%(i,2,i+4,3,i+4),True)
                    RS232_output=ssh_cmd(ssh_shell,"echo world > /dev/ttyUSB_RS232_%s "%i,True)
                    m+=2
                    if b'world\r\n' in RS232_output:
                        print("RS232_%s TEST PASS"%i)
                        ssh_cmd(ssh_shell,"killall cat",True)
                        _rs232_res.append(True)

                    else:
                        print("RS232_%s TEST FAIL"%i)
                        ssh_cmd(ssh_shell,"killall cat",True)
                        _rs232_res.append(False)
                else:
                    print("RS232_%s TEST FAIL"%i)
                    ssh_cmd(ssh_shell,"killall cat",True)
                    _rs232_res.append(False)

            else:
                m=0
                ssh_cmd(ssh_shell,"cp2108_gpioConfig  -D /dev/ttyUSB_RS232_%s  -P %s -V 0;cp2108_gpioConfig  -D /dev/ttyUSB_RS232_%s  -P %s -V 0;cat /dev/ttyUSB_RS232_%s &"%(i,0,i+4,1,i+4),True)
                RS232_output=ssh_cmd(ssh_shell,"echo hello > /dev/ttyUSB_RS232_%s "%i,True)
                m+=2
                print("RS232 IS",RS232_output)
                if b'hello\r\n' in RS232_output:
                    print("RS232_%s num modem TEST PASS"%i)
                    ssh_cmd(ssh_shell,"cp2108_gpioConfig  -D /dev/ttyUSB_RS232_%s  -P %s -V 1;cp2108_gpioConfig  -D /dev/ttyUSB_RS232_%s  -P %s -V 1;cat /dev/ttyUSB_RS232_%s &"%(i,0,i+4,1,i+4),True)
                    time.sleep(1)
                    RS232_output=ssh_cmd(ssh_shell,"echo world > /dev/ttyUSB_RS232_%s "%i,response=True)        
                    m+=2
                    if b'world\r\n' in RS232_output:
                        print("RS232_%s TEST PASS"%i)
                        ssh_cmd(ssh_shell,"killall cat",True)
                        _rs232_res.append(True)
                    else:
                        print("RS232_%s TEST FAIL"%i)
                        ssh_cmd(ssh_shell,"killall cat",True)
                        _rs232_res.append(False)

                else:
                    print("RS232_%s TEST FAIL"%i)
                    ssh_cmd(ssh_shell,"killall cat",True)
                    _rs232_res.append(False)
            

        print(_rs232_res)
        if False not in _rs232_res:
            resq.put(["rs232",True,_rs232_res])
        else:
            resq.put(["rs232",False,_rs232_res])
    except:
        resq.put(["rs232",False,_rs232_res])
        traceback.print_exc()
        

def relay_test(ssh_shell,relayvol_range,resq):
    try:
        for relay_port in range(1,7):
            ssh_cmd(ssh_shell,"/etc/IR_Sense_Relay//mcu.ir.Sense.Relay.sh Relay open %s "%relay_port,True)
            time.sleep(0.5)
        time.sleep(1)
        relay_vol=dc_measure()[1]
        time.sleep(1)
        if compare(relay_vol,relayvol_range):
            resq.put(["relay",True,relay_vol])
        else:
            resq.put(["relay",False,relay_vol])
        for relay_port in range(1,7):
            time.sleep(0.5)
            ssh_cmd(ssh_shell,"/etc/IR_Sense_Relay//mcu.ir.Sense.Relay.sh Relay close %s "%relay_port,True)
    except:
        traceback.print_exc()
        for relay_port in range(1,7):
            time.sleep(0.5)
            ssh_cmd(ssh_shell,"/etc/IR_Sense_Relay//mcu.ir.Sense.Relay.sh Relay close %s "%relay_port,True)



def audio_test(ssh_shell,input_source_name,resq):  #update audio file 
    thd=False
    amp=False
    try:
        try:
            os.system("rm temp.wav")
        except:
            pass
        ssh_cmd(ssh_shell,"aplay /nsc_tests/ATE/1khz_-10db.wav ",False)
        print(input_source_name)
        record(find_mic(input_source_name),channels=1,rate=44100,buffsize=256,duration=3,wavefile=True,outputfile="temp.wav")
        thd,amp=get_anas("temp.wav",1000)
        print(thd,amp)
        resq.put(["audio",thd,amp])
        
    except:
        resq.put(["audio",False,False])
        traceback.print_exc()
        with open('log.txt', 'a') as f:
            f.write(traceback.format_exc())




def usb2_test(ssh_shell,resq):
    try:
        ssh_cmd(ssh_shell,"mount /dev/usb2.0_port /mnt",True)
        data=str(int(time.time()))
        cmd="echo " + data + " > /mnt/USB/test.txt"
        ssh_cmd(ssh_shell,cmd,True)   
        cmd="cat /mnt/USB/test.txt"
        usb_output=ssh_cmd(ssh_shell,cmd,True)  
        print(usb_output) 
        if data.encode() in usb_output:
            print("USB2 TEST PASS")
            ssh_cmd(ssh_shell,"umount /mnt",True)
            resq.put(["usb2.0",True])
        else:
            print("USB2 TEST FAIL")
            ssh_cmd(ssh_shell,"umount /mnt",True)
            resq.put(["usb2.0",False])
    except:
        print("USB2 TEST FAIL")
        ssh_cmd(ssh_shell,"umount /mnt",True)
        resq.put(["usb2.0",False])


def usb3_test(ssh_shell,resq):
    try:
        ssh_cmd(ssh_shell,"mount /dev/usb3.0_port /tmp",True)
        data=str(int(time.time()))
        cmd="echo " + data + " > /tmp/USB/test.txt"
        ssh_cmd(ssh_shell,cmd,True)   
        cmd="cat /tmp/USB/test.txt"
        usb_output=ssh_cmd(ssh_shell,cmd,True)  
        print(usb_output) 
        if data.encode() in usb_output:
            print("USB3 TEST PASS")
            ssh_cmd(ssh_shell,"umount /tmp",True)
            resq.put(["usb3.0",True])
        else:
            print("USB3 TEST FAIL")
            ssh_cmd(ssh_shell,"umount /tmp",True)
            resq.put(["usb3.0",False])
    except:
        print("USB3 TEST FAIL")
        ssh_cmd(ssh_shell,"umount /tmp",True)
        resq.put(["usb3.0",False])



def iperfeth(ssh_shell,resq):             #update cris
    try:        
        bandwidth=-100
        for n in range (0,3):
            ssh_cmd(ssh_shell,chr(0x03),False)
            #ssh_cmd(ssh_shell,"ifconfig br-lan 88.88.86.88",True)
            time.sleep(3)
            os.system("iperf3 -s -p 8888 &")
            time.sleep(0.1)
            bandwidth_output=ssh_cmd(ssh_shell,"iperf3 -c 88.88.86.1 -t 3 -p 8888",True)
            ssh_cmd(ssh_shell,chr(0x03),False)
            print(bandwidth_output)
            bandwidth=float(str(bandwidth_output).strip().split("Mbits/sec")[-2].strip().split()[-1])
            print(bandwidth)
            resq.put(["iperfeth",True,bandwidth])
            break
        if bandwidth==-100:
            resq.put(["iperfeth",False,False])
            ssh_cmd(ssh_shell,chr(0x03),False)
        os.system("killall iperf3")
    except:
        os.system("killall iperf3")
        traceback.print_exc()
        resq.put(["iperfeth",False,False])
        ssh_cmd(ssh_shell,chr(0x03),False)

def iperfwifi(ssh_shell,ssid,psd,resq):             #update cris
    try:        
        bandwidth=-100
        '''
        ssh_cmd(ssh_shell,"killall wpa_supplicant",True)
        time.sleep(0.5)
        ssh_cmd(ssh_shell,"wpa_passphrase %s %s > wpa.conf"%(ssid,psd),True)
        time.sleep(0.5)
        ssh_cmd(ssh_shell,"wpa_supplicant -B -i wlan0 -c wpa.conf",True)
        time.sleep(0.5)
        ssh_cmd(ssh_shell,"dhclient wlan0",True)
        time.sleep(0.5)
        '''
        if b"192.168.4." in ssh_cmd(ssh_shell,"ifconfig wlan0",True):
            for n in range (0,3):
                ssh_cmd(ssh_shell,chr(0x03),False)
                #ssh_cmd(ssh_shell,"ifconfig br-lan 88.88.86.88",True)
                time.sleep(3)
                os.system("iperf3 -s -p 8889 &")
                time.sleep(0.1)
                bandwidth_output=ssh_cmd(ssh_shell,"iperf3 -c 192.168.4.1 -t 3 -p 8889",True)
                ssh_cmd(ssh_shell,chr(0x03),False)
                print(bandwidth_output)
                bandwidth=float(str(bandwidth_output).strip().split("Mbits/sec")[-2].strip().split()[-1])
                print(bandwidth)
                resq.put(["iperfwifi",True,bandwidth])
                break
            if bandwidth==-100:
                resq.put(["iperfwifi",False,False])
                ssh_cmd(ssh_shell,chr(0x03),False)
        else:
            ssh_cmd(ssh_shell,"killall wpa_supplicant",True)
            time.sleep(0.5)
            ssh_cmd(ssh_shell,"wpa_passphrase %s %s > wpa.conf"%(ssid,psd),True)
            time.sleep(0.5)
            ssh_cmd(ssh_shell,"wpa_supplicant -B -i wlan0 -c wpa.conf",True)
            time.sleep(0.5)
            ssh_cmd(ssh_shell,"dhclient wlan0",True)
            time.sleep(0.5)
            resq.put(["iperfwifi",False,False])
            ssh_cmd(ssh_shell,chr(0x03),False)
        os.system("killall iperf3")
    except:
        os.system("killall iperf3")
        traceback.print_exc()
        resq.put(["iperfwifi",False,False])
        ssh_cmd(ssh_shell,chr(0x03),False)
            
            

def uic(resq):
    resq.put(["uic",True])



def auto(ssh_user,ssh_passwd,ssh_portnum,resq,res_value,ser_ir,ser_switch,sensevol_range,relayvol_range,recordinput,ssid,psd,hostname,username,password,portnum,database,table):
    try:
        exe=0
        count=0
        break_flag=0
        ssh_shell=getstaip(ssh_user,ssh_passwd,ssh_portnum,ser_switch,ssid,psd,resq)
        if ssh_shell!=False:
            while True:
                count=count+1
                print(res_value)
                res_value_values=list(res_value.values())
                for n in range (0,len(res_value_values)):
                    if res_value_values[n][0]=="F":
                        break_flag=1
                if break_flag==1:
                    print("breaked")
                    resq.put(["auto",False])
                    break
                
                elif "SNID" in res_value and exe==0:
                    resq.put(["auto","ING"])
                    exe=exe+1
                    time.sleep(3)
                    ir_test(ssh_shell,ser_ir,resq)

                elif "ir" in res_value and exe==1:
                    resq.put(["auto","ING"])
                    exe=exe+1
                    rs485_test(ssh_shell,resq)

                elif "rs485" in res_value and exe==2:
                    time.sleep(2)
                    resq.put(["auto","ING"])
                    exe=exe+1
                    sense_test(ssh_shell,ser_switch,sensevol_range,resq)

                elif "sense" in res_value and exe==3:
                    resq.put(["auto","ING"])
                    exe=exe+1
                    rs232_test(ssh_shell,resq)

                elif "rs232" in res_value and exe==4:
                    resq.put(["auto","ING"])
                    exe=exe+1
                    relay_test(ssh_shell,relayvol_range,resq)

                elif "relay" in res_value and exe==5:
                    resq.put(["auto","ING"])
                    exe=exe+1
                    audio_test(ssh_shell,recordinput,resq)

                elif  "audio" in res_value and exe==6:
                    resq.put(["auto","ING"])
                    exe=exe+1
                    usb2_test(ssh_shell,resq)
                    

                elif "usb2.0" in res_value and exe==7:
                    resq.put(["auto","ING"])
                    exe=exe+1
                    usb3_test(ssh_shell,resq)

                elif "usb3.0" in res_value and exe==8:
                    resq.put(["auto","ING"])
                    exe=exe+1
                    iperfwifi(ssh_shell,ssid,psd,resq)     #####update
                    
                elif "iperfwifi" in res_value and exe==9:
                    resq.put(["auto","ING"])
                    exe=exe+1
                    uic(resq)

                elif "power" in res_value and exe ==10:
                    exe=exe+1
                    resq.put(["auto",True])
                    break
                else:
                    time.sleep(1)
                #print(count)


                if count==240:
                    resq.put(["auto",False])
                    break
        else:
            resq.put(["auto",False])

        
    except:
        resq.put(["auto",False])
        traceback.print_exc()
        with open('log.txt', 'a') as f:
            f.write(traceback.format_exc())







            






























def elan_get_mac_addr(hostname,username,password,portnum,database,table):
    try:
        db=pymysql.connect(hostname,username,password,database,port=int(portnum))
        cursor = db.cursor()
        sql="SELECT `End` FROM %s WHERE Model='ELAN-IP8'"%table
        cursor.execute(sql)
        mac_max = cursor.fetchall()[0][0]
        mac_max =mac_max.replace("-","")
        mac_max =int(mac_max,16)
        #print(mac_max)

        sql="SELECT `Start` FROM %s WHERE Model='ELAN-IP8'"%table
        cursor.execute(sql)
        mac_min = cursor.fetchall()[0][0]
        mac_min =mac_min.replace("-","")
        mac_min =int(mac_min,16)
        #print(mac_min)
        
        
        sql="SELECT `Next` FROM %s WHERE Model='ELAN-IP8'"%table
        cursor.execute(sql)
        result = cursor.fetchall()[0][0]
        result =result.replace("-","")
        result =int(result,16)
        #print(result)
        if result>=mac_min and result<mac_max:
            mac_dut=hex(result).replace("0x","").upper()
            mac_wrt=mac_dut[0:2]+':'+mac_dut[2:4]+':'+mac_dut[4:6]+':'+mac_dut[6:8]+':'+mac_dut[8:10]+':'+mac_dut[10:12]
            mac_prt=mac_dut[0:2]+'-'+mac_dut[2:4]+'-'+mac_dut[4:6]+'-'+mac_dut[6:8]+'-'+mac_dut[8:10]+'-'+mac_dut[10:12]
            #print(mac_wrt,mac_prt)

            mac_next=hex(result+1).replace("0x","").upper()
            #print(mac_next)
            mac_next=mac_next[0:2]+'-'+mac_next[2:4]+'-'+mac_next[4:6]+'-'+mac_next[6:8]+'-'+mac_next[8:10]+'-'+mac_next[10:12]
            print(mac_next)

            sql="UPDATE `%s` SET Next='%s' WHERE Model='ELAN-IP8'"%(table,mac_next)
            cursor.execute(sql)
        else:
            print("mac_address is finished")

        db.commit()
        db.close()
    except Exception as e:
        print(e)
        db.rollback()
        db.close()
        servercon=input("Failed to find data to server, please check")
    return mac_wrt

def save_result(res_value,file_name):
    try:
        history_file=glob.glob(os.path.join(os.getcwd(),"%s.csv"%file_name))
        print("record file", len(history_file))
        if len(history_file)==0:
            res_value_list=list(res_value.keys())
            df = pd.DataFrame(columns = res_value_list)
            row={}
            for n in range (0,len(res_value_list)):
                row[res_value_list[n]]=res_value[res_value_list[n]][1]
            df.loc[0]=row
            df.to_csv(os.path.join(os.getcwd(),"%s.csv"%file_name),index = False)
            shutil.copyfile(os.path.join(os.getcwd(),"%s.csv"%file_name), os.path.join(os.getcwd(),"%s_backup.csv"%file_name))
            return "ADD"
        elif filecmp.cmp(os.path.join(os.getcwd(),"%s.csv"%file_name),os.path.join(os.getcwd(),"%s_backup.csv"%file_name)):
            df=pd.read_csv(os.path.join(os.getcwd(),"%s.csv"%file_name),converters=StringConverter())
            print(len(df))
            sn_list=list(df.SNID.values)
            if res_value["SNID"][1] in sn_list:
                return "DUP"
            else:
                res_value_list=list(res_value.keys())
                row={}
                for n in range (0,len(res_value_list)):
                    row[res_value_list[n]]=res_value[res_value_list[n]][1]
                print(len(df)+1)
                df.loc[len(df)+2]=row
                df.to_csv(os.path.join(os.getcwd(),"%s.csv"%file_name),index = False)
                shutil.copyfile(os.path.join(os.getcwd(),"%s.csv"%file_name), os.path.join(os.getcwd(),"%s_backup.csv"%file_name))
                return "ADD"
        else:
            return "WARN"
    except:
        traceback.print_exc()
        return "ERROR"

    


def find_port(_ir_port,_switch1_port):     #Corresponding location manually
    try:
        global linux_port, ir_port,switch1_port
        ports = list(serial.tools.list_ports.comports())
        for i in range(len(ports)):
            print(ports[i].location,ports[i].device)
            if "LOCATION=%s"%_ir_port in ports[i].hwid:
                ir_port=ports[i].device
                print("ir_port= ",ir_port)
            #elif "LOCATION=1-1.1.7.1" in ports[i].hwid:
            elif "LOCATION=%s"%_switch1_port in ports[i].hwid:
                switch1_port=ports[i].device
                print("switch1_port= ",switch1_port)
        return ir_port,switch1_port
    except Exception as e:
        print(e)
        print("error location , please insert the USB cable as requirement")


def switchto(ser,status=0):
    try:
        #ser=serial.Serial("/dev/ttyUSB2",9600,timeout=1)
        time.sleep(0.5)
        alloff=b"\x50\xff\x51\xff\xff"
        k1on=b"\xfe"
        k2on=b"\xfd"       
        k13on=b"\xfa"
        k136on=b"\xda"
        k14on=b"\xf6"
        k15on=b"\xee"
        k16on=b"\xde"
        k17on=b"\xbe"
        k18on=b"\x7e"
        
        if status==0:
            ser.write(b'%s'%alloff)
        elif status==1:
            ser.write(b'%s'%k1on)
        elif status==2:
            ser.write(b'%s'%k2on)
        elif status==13:
            ser.write(b'%s'%k13on)
        elif status==136:
            ser.write(b'%s'%k136on)
        elif status==14:
            ser.write(b'%s'%k14on)
        elif status==15:
            ser.write(b'%s'%k15on)
        elif status==16:
            ser.write(b'%s'%k16on)
        elif status==17:
            ser.write(b'%s'%k17on)
        elif status==18:
            ser.write(b'%s'%k18on)
        else:
            ser.write(b'%s'%alloff)
        time.sleep(0.5)
        return True
    except:
        traceback.print_exc()
        return False

#set printer
def set_printer(printer_name=""):
    try:
        z = zebra()
        printer.setqueue(printer_name)
        return printer
    except:
        traceback.print_exc()
        return False

def print_label(printer,label):
    try:
        printer.output(label)
        time.sleep(1)
    except:
        traceback.print_exc()
        return False

       
   

#read configuration
def read_config(filepath,target):
    try:
        f=open(filepath,"r")
        data=f.readlines()
        out=False
        for n in range (0,len(data)):
            if target in data[n]:
                out=data[n].strip().split("=")[-1]
                return out
                break
        return out
    except:
        traceback.print_exc()
        return False
    
#read critiera
def read_cri(filepath,target):
    try:
        f=open(filepath,"r")
        data=f.readlines()
        uplim=False
        downlim=False
        for n in range (0,len(data)):
            if target in data[n]:
                out=data[n].strip().split("=")[-1]
                out=out[1:-1]
                uplim=out.split(",")[1]
                downlim=out.split(",")[0]
                return float(downlim),float(uplim)
                break
        return [downlim,uplim]
    except:
        traceback.print_exc()
        return False    
    
    
#compareing
def compare(val,rang):
    try:
        if float(val)>=float(rang[0]) and float(val)<=float(rang[1]):
            return True
        else:
            return False
    except:
        traceback.print_exc()
        return False     


#network iperf
def iperf_client(iperf_path,ip,duration,port):
    try:
        print("client actived",time.time())
        print(iperf_path,ip,duration,port)
        cmd = "%s -c %s -i 1 -t %s -p %s"%(iperf_path,ip,duration,port)
        execmd=subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE,start_new_session=True,shell=True)
        execmd.wait()
        print("client finished",time.time())
    except:
        traceback.print_exc()
        return False 

    
#get thd
def get_thd(data,rate,freq,octave=12):
    try:
        rms=20*np.log10(np.sqrt(np.mean(np.absolute(data)**2)))
        data -= np.mean(data)
        data = data * np.hanning(len(data))
        fft_gap=rate/len(data)
        total_rms=np.sqrt(np.mean(np.absolute(data)**2))
        outfft = np.fft.rfft(data)
        upper_limit=freq*2**(1/(2*octave))
        lower_limit=freq/2**(1/(2*octave))
        upper_fft=int(upper_limit/fft_gap)
        lower_fft=int(lower_limit/fft_gap)
        for n in range (lower_fft,upper_fft+1):
            outfft[n]=0
        noise = np.fft.irfft(outfft)
        noise_rms=np.sqrt(np.mean(np.absolute(noise)**2))
        thd = noise_rms / total_rms
        return round(thd,5),round(rms,5)
    except:
        traceback.print_exc()
        return False,False
    
#get wave_data
def get_wave(filename):
    try:
        data, samplerate = soundfile.read(filename)
        soundfile.write(filename, data, samplerate, subtype='PCM_16')
        f = wave.open(filename, "rb")
        params = f.getparams()
        nchannels, sampwidth, framerate, nframes = params[:4]
        str_data = f.readframes(nframes)
        wave_data = np.frombuffer(str_data, dtype=np.short)
        wave_data = wave_data/32768
        f.close()
        if nchannels==2:
            wave_data.shape = -1, 2
            wave_data_left = wave_data.T[0]
            wave_data_right = wave_data.T[1]
            return [wave_data_left,wave_data_right],nchannels, sampwidth, framerate, nframes
        elif nchannels==1:
            return wave_data,nchannels, sampwidth, framerate, nframes
        else:
            return False,nchannels,sampwidth,framerate,nframes
    except:
        traceback.print_exc()
        return False,False,False,False,False

#get get analysis result      
def get_anas(wave_file,frequency):
    try:
        data,nchannels,sampwidth,framerate,nframes=get_wave(wave_file)
        if nchannels==1:
            thd,amp=get_thd(data[int(framerate//2+framerate//4):int(framerate//2+2*framerate//4)],framerate,frequency,octave=12)
            return thd,amp
        elif nchannels==2:
            thd_l,amp_l=get_thd(data[0][framerate:-framerate],framerate,frequency,octave=12)
            thd_r,amp_r=get_thd(data[1][framerate:-framerate],framerate,frequency,octave=12)
            return [thd_l,thd_r],[amp_l,amp_r]
        else:
            return False,False
    except:
        traceback.print_exc()
        return False,False       

           
#find input device
def find_mic(input_source_name):
    try:
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0,numdevices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print(p.get_device_info_by_host_api_device_index(0, i).get('name'))
                if input_source_name in p.get_device_info_by_host_api_device_index(0, i).get('name'):
                    mic_index=int(i)
                    break
        return mic_index
    except:
        traceback.print_exc()
        return False

    
#find speaker
def find_spk(output_source_name):
    try:
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0,numdevices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
                print(p.get_device_info_by_host_api_device_index(0, i).get('name'))
                if output_source_name in p.get_device_info_by_host_api_device_index(0, i).get('name'):
                    spk_index=int(i)
                    break
        return spk_index
    except:
        traceback.print_exc()
        return False        

#record audio
def record(inputsrc,channels=2,rate=44100,buffsize=512,duration=3,wavefile=True,outputfile="temp.wav"):
    print("chinnals",channels)
    try:
        rawdata=[]
        signal_data=[]
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,channels=channels,rate=rate,input=True,input_device_index=int(inputsrc),frames_per_buffer=buffsize)
        for i in range(0, int(rate/buffsize*duration)):
            data = stream.read(buffsize)
            rawdata.append(data)
        for n in range (0,len(rawdata)):
            signal=(np.frombuffer(rawdata[n],dtype=np.int16))
            for m in range (0,len(signal)):
                signal_data.append(signal[m])
        signal_data=np.array(signal_data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        if wavefile==True:
            f = wave.open("temp.wav","wb") 
            f.setnchannels(channels)
            f.setsampwidth(2)
            f.setframerate(rate)
            f.writeframes(signal_data.tostring())
            f.close()
            
        wave_data=np.frombuffer(signal_data.tostring(), dtype=np.short)
        if channels==2:
            wave_data.shape = -1, 2
            wave_data_left = wave_data.T[0]/rate
            wave_data_right = wave_data.T[1]/rate
            return [wave_data_left,wave_data_right], cahnnels,rate
        elif channels==1:
            return wave_data/rate,channels,rate
        else:
            return False,channels,rate
    except:
        traceback.print_exc()
        return False,False,False        
            
#playback audio       
def playback(musicfile,outputsrc):
    try:
        CHUNK = 1024
        wf = wave.open(musicfile, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        output_device_index=int(outputsrc))
        data = wf.readframes(CHUNK)
        while len(data) > 0:
            stream.write(data)
            data = wf.readframes(CHUNK)
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf.close()
        return True
    except:
        traceback.print_exc()
        return False      



    

#Excel control
def save_result(res_value,file_name):
    try:
        history_file=glob.glob(os.path.join(os.getcwd(),"%s.csv"%file_name))
        print("record file", len(history_file))
        if len(history_file)==0:
            res_value_list=list(res_value.keys())
            df = pd.DataFrame(columns = res_value_list)
            row={}
            for n in range (0,len(res_value_list)):
                row[res_value_list[n]]=res_value[res_value_list[n]][1]
            df.loc[0]=row
            df.to_csv(os.path.join(os.getcwd(),"%s.csv"%file_name),index = False)
            shutil.copyfile(os.path.join(os.getcwd(),"%s.csv"%file_name), os.path.join(os.getcwd(),"%s_backup.csv"%file_name))
            return "ADD"
        elif filecmp.cmp(os.path.join(os.getcwd(),"%s.csv"%file_name),os.path.join(os.getcwd(),"%s_backup.csv"%file_name)):
            df=pd.read_csv(os.path.join(os.getcwd(),"%s.csv"%file_name))
            print(len(df))
            sn_list=list(df.sn.values)
            try:
                if float(res_value["sn"][1]) in sn_list:
                    return "DUP"
                else:
                    res_value_list=list(res_value.keys())
                    row={}
                    for n in range (0,len(res_value_list)):
                        row[res_value_list[n]]=res_value[res_value_list[n]][1]
                    print(len(df)+1)
                    df.loc[len(df)+2]=row
                    df.to_csv(os.path.join(os.getcwd(),"%s.csv"%file_name),index = False)
                    shutil.copyfile(os.path.join(os.getcwd(),"%s.csv"%file_name), os.path.join(os.getcwd(),"%s_backup.csv"%file_name))
                    return "ADD"
            except:
                if str(res_value["sn"][1]) in sn_list:
                    return "DUP"
                else:
                    res_value_list=list(res_value.keys())
                    row={}
                    for n in range (0,len(res_value_list)):
                        row[res_value_list[n]]=res_value[res_value_list[n]][1]
                    print(len(df)+1)
                    df.loc[len(df)+2]=row
                    df.to_csv(os.path.join(os.getcwd(),"%s.csv"%file_name),index = False)
                    shutil.copyfile(os.path.join(os.getcwd(),"%s.csv"%file_name), os.path.join(os.getcwd(),"%s_backup.csv"%file_name))
                    return "ADD"
        else:
            return "WARN"
    except:
        traceback.print_exc()
        return "ERROR"









def hdmi_test(resq):
    resq.put(["hdmi",True])

def resetbtn_test(ssh_shell,resq):
    try:
        log=ssh_cmd(ssh_shell,"echo a > /etc/button_det/Resetfile",True)
        resq.put(["reset",True])
    except:
        resq.put(["reset",False])

def powerbtn_test(ssh_shell,resq):
    resq.put(["power",True])
   
def led_test(ssh,resq):
    try:
        ssh_cmd(ssh,"/etc/led.sh red",True)
        time.sleep(0.5)
        ssh_cmd(ssh,"/etc/led.sh blue",True)
        time.sleep(0.5)
        ssh_cmd(ssh,"/etc/led.sh amber",True)
        time.sleep(0.5)
        ssh_cmd(ssh,"/etc/led.sh off",True)
        resq.put(["led",True])
    except:
        resq.put(["led",False])
        
   
def iperf5(ser,ssid,psd,resq):  #update command to grep wifi ip, can't recognize wifi connect or not!
    try:
        os.system("systemctl stop hostapd;cp /etc/hostapd/gc4_5g.conf  /etc/hostapd/hostapd.conf;sudo systemctl start hostapd")
        bandwidth=-100
        time.sleep(5)
        for n in range (0,3):
            ssh_cmd(ser,"ifconfig wlan0 up",ends=b"# ",response=True)
            ssh_cmd(ser,"killall wpa_supplicant",ends=b"# ",response=True)
            ssh_cmd(ser,"wpa_passphrase %s %s > wpa.conf"%(ssid,psd),ends=b"# ",response=True)
            ssh_cmd(ser,"wpa_supplicant -B -i wlan0 -c wpa.conf",ends=b"# ",response=True)
            time.sleep(1)
            ssh_cmd(ser,"dhclient wlan0",ends=b"# ",response=True)
            time.sleep(5)
            ssh_cmd(ser,chr(0x03),ends=b"# ",response=False)
            out=ssh_cmd(ser,"iwconfig",ends=b"# ",response=True)
            print(ssid)
            print(out)
            for p in range (0,3):
                if str.encode(ssid) in out:
                    break
                else:
                    time.sleep(3)
            if str.encode(ssid) in out:
                print("WIFI connect successfully")
                ser.readall()
                time.sleep(3)
                ipaddr_out=ssh_cmd(ser,"ifconfig wlan0 | grep 'inet'",ends=b"# ",response=True)
                time.sleep(3)
                ipaddr_list=ipaddr_out.strip().split()
                for i in range(len(ipaddr_list)):
                    if b"192" in ipaddr_list[i]:
                        ipaddr=ipaddr_list[i].decode()
                        break
                print(ipaddr)
                ssh_cmd(ser,"iperf3 -s -p 8888",ends=b"# ",response=False)
                iperf_client("iperf3",ipaddr,5,8888)
                bandwidth_output=ser.readall()
                print(bandwidth_output)
                bandwidth=float(str(bandwidth_output).strip().split("Mbits/sec")[-2].strip().split()[-1])
                print(bandwidth)
                resq.put(["iperf5",bandwidth])
                ssh_cmd(ser,chr(0x03),ends=b"# ",response=False)
                break
            else:
                ssh_cmd(ser,chr(0x03),ends=b"# ",response=False)
                print("Fail to connect WIFI")
        if bandwidth==-100:
            resq.put(["iperf5",False])
            ssh_cmd(ser,chr(0x03),ends=b"# ",response=False)
    except:
        traceback.print_exc()
        resq.put(["iperf5",False])
        ssh_cmd(ser,chr(0x03),ends=b"# ",response=False)


















    
    


#resq=queue.Queue()
#ser_linux=serial.Serial("/dev/ttyUSB0",115200,timeout=1)
#RS232_test(ser_linux,resq)

