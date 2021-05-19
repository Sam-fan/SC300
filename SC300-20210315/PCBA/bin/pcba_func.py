import serial
from serial.tools import list_ports
import time
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
import board
from rasp_libhackrf import *
from pylab import *
try:
    hackrf = HackRF()
except:
    print("no hackrf")


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
            resq.put(["vol",True,voldc11,voldc12,voltp281])
        else:
            resq.put(["vol",False,voldc11,voldc12,voltp281])
    except:
        resq.put(["vol",False,voldc,volpoe])
        traceback.print_exc()
        
            
def uart_login(ser,ser_switch,resq):
    try:
        ser_switch.write(b"\xff") 
        os.system("rm /var/lib/misc/dnsmasq.leases")
        os.system("/etc/init.d/dnsmasq restart")
        os.system("touch /var/lib/misc/dnsmasq.leases")
        time.sleep(1)
        ser_switch.write(b"\x8f") #567
        uboot_flag=0
        ser.flushInput()
        ser.flushOutput()
        for i in range(20):
            print(i)
            ser.write((chr(0x03)+"\n").encode())
            time.sleep(0.3)
            data=ser.read_all()
            print(data)
            if b'owl>'in data and uboot_flag==0:
                print("under u-boot")
                print(ser.readall())
                ser.write((chr(0x03)+"\n").encode())
                ser.write(("ext4WriteFile mmc 1:2 /nsc_tests/ATE/ate_mode 1\n").encode())
                ser.write("run bootcmd \n".encode())
                print("finish changing in uboot")
                uboot_flag=1
                break
            elif data.endswith(b'# ') and uboot_flag==0:
                print("under cmd")
                ser.write(b"reboot\n")
                time.sleep(0.1)
            else:
                continue

        if uboot_flag==0:
            print("Uboot fail")
            resq.put(["login",False,False,False,False])
        else:
            for i in range(90):
                print(i)
                data=ser.read_all()
                print(data)
                if b"login" in data:
                    ser.write(b"root\n")
                    time.sleep(1)
                    ser.write(b"N0rt3k$C\n")
                    print("login with successfully")
                    bspver=uart_cmd(ser,"cat /etc/version ",ends=b"# ",response=True)
                    bsp_ver="False"
                    print(bspver.split())
                    for i in bspver.split():
                        if b"20" in i:
                            bsp_ver=i.decode()
                    print(bsp_ver)

                    irver=uart_cmd(ser,"/etc/IR_Sense_Relay/mcu.ir.Sense.Relay.sh IR ver",ends=b"# ",response=True)
                    ir_ver="False"
                    #print(irver.split())
                    for m in irver.split():
                        if b"length" in m:
                            ir_ver=m.strip()[-12:-1].decode()
                    print(ir_ver)

                    sensever=uart_cmd(ser,"/etc/IR_Sense_Relay/mcu.ir.Sense.Relay.sh Sense ver",ends=b"# ",response=True)
                    sense_ver="False"
                    #print(sensever.split())
                    for n in sensever.split():
                        if b"length" in n:
                            sense_ver=n.strip()[-12:-1].decode()
                    print(sense_ver)
                    resq.put(["login",True,bsp_ver,ir_ver,sense_ver])
                    break
                elif i==89:
                    print("Failed to login")
                    resq.put(["login",False,False,False,False])
                    break
                else:
                    time.sleep(1)
                    continue            
    except:
        ser.write(chr(0x03).encode())
        ser.write(b"\n")
        ser.flushInput()
        ser.flushOutput()
        traceback.print_exc()
        resq.put(["login",False,False,False,False])


###read IR output, IR firmware version
def ir_test(ser_linux,ser_ir,resq):
    _ir_res=[]
    time.sleep(1)
    data =b'\x1c/3'
    try:
        for ir_port in range(1,13):
            #ser_output=ser_ir.readall()
            IR_cmd = "/etc/IR_Sense_Relay/mcu.ir.Sense.Relay.sh IR %s"%ir_port
            ser_linux.write(IR_cmd.encode()+b"\n")
            time.sleep(0.3)
            #uart_cmd(ser_linux,IR_cmd,ends=b"# ",response=False)
            #print(ser_ir)
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


def rs485_test(ser_linux,resq):
    try:
        uart_cmd(ser_linux,"cp2108_gpioConfig  -D /dev/ttyUSB_RS485_1  -P 8 -V 0 ",ends=b"# ",response=False)
        uart_cmd(ser_linux,"cp2108_gpioConfig  -D /dev/ttyUSB_RS485_2  -P 9 -V 0 ",ends=b"# ",response=False)
        uart_cmd(ser_linux,"cat /dev/ttyUSB_RS485_1 &",ends=b"# ",response=False)
        time.sleep(2)
        uart_cmd(ser_linux,"echo world > /dev/ttyUSB_RS485_2",ends=b"# ",response=False)
        time.sleep(1)
        RS485_output=ser_linux.readall()
        print(RS485_output)
        if b'world\r\n' in RS485_output:
            print("RS485 TEST PASS")
            resq.put(["rs485",True])
            uart_cmd(ser_linux,"killall cat",ends=b"# ",response=False)

        else:
            print("RS485 TEST FAIL")
            uart_cmd(ser_linux,"killall cat",ends=b"# ",response=False)
            resq.put(["rs485",False])
    except:
        resq.put(["rs485",False])
        traceback.print_exc()


def sense_test(ser_linux,ser_switch,sensevol_range,resq):    ## to be verifed
    try:
        signal_output=uart_cmd(ser_linux,"/etc/IR_Sense_Relay//mcu.ir.Sense.Relay.sh Sense read",ends=b"# ",response=True)
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


def rs232_test(ser_linux,resq):
    _rs232_res=[]
    try:
        for i in range(1,5):
            if (i%2)==0:
                uart_cmd(ser_linux,"cp2108_gpioConfig  -D /dev/ttyUSB_RS232_%s  -P %s -V 0;cp2108_gpioConfig  -D /dev/ttyUSB_RS232_%s  -P %s -V 0;cat /dev/ttyUSB_RS232_%s &"%(i,2,i+4,3,i+4),ends=b"# ",response=False)
                uart_cmd(ser_linux,"echo hello > /dev/ttyUSB_RS232_%s "%i,ends=b"# ",response=False)
                RS232_output=ser_linux.readall()
                print("RS232 IS",RS232_output)
                m+=2
                time.sleep(1)
                if b'hello\r\n' in RS232_output:
                    print("RS232_%s num modem TEST PASS"%i)
                    uart_cmd(ser_linux,"cp2108_gpioConfig  -D /dev/ttyUSB_RS232_%s  -P %s -V 1;cp2108_gpioConfig  -D /dev/ttyUSB_RS232_%s  -P %s -V 1;cat /dev/ttyUSB_RS232_%s &"%(i,2,i+4,3,i+4),ends=b"# ",response=False)
                    uart_cmd(ser_linux,"echo world > /dev/ttyUSB_RS232_%s "%i,ends=b"# ",response=False)
                    RS232_output=ser_linux.readall()
                    m+=2
                    if b'world\r\n' in RS232_output:
                        print("RS232_%s TEST PASS"%i)
                        uart_cmd(ser_linux,"killall cat",ends=b"# ",response=False)
                        _rs232_res.append(True)

                    else:
                        print("RS232_%s TEST FAIL"%i)
                        uart_cmd(ser_linux,"killall cat",ends=b"# ",response=False)
                        _rs232_res.append(False)
                else:
                    print("RS232_%s TEST FAIL"%i)
                    uart_cmd(ser_linux,"killall cat",ends=b"# ",response=False)
                    _rs232_res.append(False)

            else:
                m=0
                uart_cmd(ser_linux,"cp2108_gpioConfig  -D /dev/ttyUSB_RS232_%s  -P %s -V 0;cp2108_gpioConfig  -D /dev/ttyUSB_RS232_%s  -P %s -V 0;cat /dev/ttyUSB_RS232_%s &"%(i,0,i+4,1,i+4),ends=b"# ",response=False)
                uart_cmd(ser_linux,"echo hello > /dev/ttyUSB_RS232_%s "%i,ends=b"# ",response=False)
                RS232_output=ser_linux.readall()
                m+=2
                print("RS232 IS",RS232_output)
                if b'hello\r\n' in RS232_output:
                    print("RS232_%s num modem TEST PASS"%i)
                    uart_cmd(ser_linux,"cp2108_gpioConfig  -D /dev/ttyUSB_RS232_%s  -P %s -V 1;cp2108_gpioConfig  -D /dev/ttyUSB_RS232_%s  -P %s -V 1;cat /dev/ttyUSB_RS232_%s &"%(i,0,i+4,1,i+4),ends=b"# ",response=False)
                    uart_cmd(ser_linux,"echo world > /dev/ttyUSB_RS232_%s "%i,ends=b"# ",response=False)
                    RS232_output=ser_linux.readall()
                    m+=2
                    if b'world\r\n' in RS232_output:
                        print("RS232_%s TEST PASS"%i)
                        uart_cmd(ser_linux,"killall cat",ends=b"# ",response=False)
                        _rs232_res.append(True)
                    else:
                        print("RS232_%s TEST FAIL"%i)
                        uart_cmd(ser_linux,"killall cat",ends=b"# ",response=False)
                        _rs232_res.append(False)

                else:
                    print("RS232_%s TEST FAIL"%i)
                    uart_cmd(ser_linux,"killall cat",ends=b"# ",response=False)
                    _rs232_res.append(False)
            

        print(_rs232_res)
        if False not in _rs232_res:
            resq.put(["rs232",True,_rs232_res])
        else:
            resq.put(["rs232",False,_rs232_res])
    except:
        resq.put(["rs232",False,_rs232_res])
        traceback.print_exc()



def relay_test(ser_linux,relayvol_range,resq):
    try:
        for relay_port in range(1,7):
            uart_cmd(ser_linux,"/etc/IR_Sense_Relay//mcu.ir.Sense.Relay.sh Relay open %s "%relay_port,ends=b"# ",response=False)
        relay_vol=dc_measure()[1]
        if compare(relay_vol,relayvol_range):
            resq.put(["relay",True,relay_vol])
        else:
            resq.put(["relay",False,relay_vol])

        for relay_port in range(1,7):
            uart_cmd(ser_linux,"/etc/IR_Sense_Relay//mcu.ir.Sense.Relay.sh Relay close %s "%relay_port,ends=b"# ",response=False)
    except:
        for relay_port in range(1,7):
            uart_cmd(ser_linux,"/etc/IR_Sense_Relay//mcu.ir.Sense.Relay.sh Relay close %s "%relay_port,ends=b"# ",response=False)
        traceback.print_exc()



def audio_test(ser_linux,input_source_name,resq):  #update audio file 
    thd=False
    amp=False
    try:
        try:
            os.system("rm temp.wav")
        except:
            pass
        uart_cmd(ser_linux,"sudo aplay /nsc_tests/ATE/1khz_-10db.wav ",ends=b"# ",response=False)
        record(find_mic(input_source_name),channels=1,rate=44100,buffsize=256,duration=3,wavefile=True,outputfile="temp.wav")
        thd,amp=get_anas("temp.wav",1000)
        print(thd,amp)
        resq.put(["audio",thd,amp])
    except:
        resq.put(["audio",False,False])
        traceback.print_exc()
        with open('log.txt', 'a') as f:
            f.write(traceback.format_exc())




def usb2_test(ser_linux,resq):
    try:
        uart_cmd(ser_linux,"mount /dev/usb2.0_port /mnt",ends=b"# ",response=False)
        data=str(int(time.time()))
        cmd="echo " + data + " > /mnt/USB/test.txt"
        uart_cmd(ser_linux,cmd,ends=b"# ",response=False)   
        cmd="cat /mnt/USB/test.txt"
        usb_output=uart_cmd(ser_linux,cmd,ends=b"# ",response=True)  
        print(usb_output) 
        if data.encode() in usb_output:
            print("USB2 TEST PASS")
            uart_cmd(ser_linux,"umount /mnt",ends=b"# ",response=False)
            resq.put(["usb2.0",True])
        else:
            print("USB2 TEST FAIL")
            uart_cmd(ser_linux,"umount /mnt",ends=b"# ",response=False)
            resq.put(["usb2.0",False])
    except:
        print("USB2 TEST FAIL")
        uart_cmd(ser_linux,"umount /mnt",ends=b"# ",response=False)
        resq.put(["usb2.0",False])


def usb3_test(ser_linux,resq):
    try:
        uart_cmd(ser_linux,"mount /dev/usb3.0_port /tmp",ends=b"# ",response=False)
        data=str(int(time.time()))
        cmd="echo " + data + " > /tmp/USB/test.txt"
        uart_cmd(ser_linux,cmd,ends=b"# ",response=False)   
        cmd="cat /tmp/USB/test.txt"
        usb_output=uart_cmd(ser_linux,cmd,ends=b"# ",response=True)  
        print(usb_output) 
        if data.encode() in usb_output:
            print("USB3 TEST PASS")
            uart_cmd(ser_linux,"umount /tmp",ends=b"# ",response=False)
            resq.put(["usb3.0",True])
        else:
            print("USB3 TEST FAIL")
            uart_cmd(ser_linux,"umount /tmp",ends=b"# ",response=False)
            resq.put(["usb3.0",False])
    except:
        print("USB3 TEST FAIL")
        uart_cmd(ser_linux,"umount /tmp",ends=b"# ",response=False)
        resq.put(["usb3.0",False])




def fetch_power(ser,resq,target_freq,powerwifi_range):
    '''
    uart_cmd(ser,"cp /nsc_tests/ATE/wifi_rf.conf /etc/modprobe.d/s700-wifi.conf",ends=b"# ",response=False)
    time.sleep(1)
    output=uart_cmd(ser,"diff /nsc_tests/ATE/wifi_func.conf /etc/modprobe.d/s700-wifi.conf",ends=b"# ",response=True)
    print(output)
    uart_cmd(ser,"reboot",ends=b"# ",response=False)
    time.sleep(60)
    uart_login(ser,resq)
    if b"firmware" in output:
    '''
    try:
        log=uart_cmd(ser,"ifconfig wlan0 down",ends=b"# ",response=True)
        log=uart_cmd(ser,"ifconfig wlan0 up",ends=b"# ",response=True)
        time.sleep(0.5)
        log=uart_cmd(ser,"wl down\n wl mpc 0\n wl country ALL\n wl band b\n wl up\n wl 2g_rate -r 11 -b 20\n wl channel 1\n wl phy_watchdog 0\n wl scansuppress 1\n wl phy_forcecal 1\n wl phy_txpwrctrl 1\n wl txpwr1 -1\n wl pkteng_start 00:90:4c:14:43:19 tx 100 1000 0\n ")
    except:
        print("Configuration WIFI failed")
        resq.put(["wifipower",False])
    print(powerwifi_range)
    target_freq=2412e6
    hackrf.sample_rate = 20e6
    shift=3e6
    hackrf.center_freq = target_freq-shift
    sn = hackrf.get_serial_no()
    power=0
    '''
    for i in range(3):    ##delete the first 3 data 
        samples = hackrf.read_samples()
        powe,freqs=psd(samples, NFFT=1024, Fs=hackrf.sample_rate/1e6, Fc=hackrf.center_freq/1e6)
        target_power=powe[round((target_freq-(hackrf.center_freq-hackrf.sample_rate//2))*1024/(hackrf.sample_rate))]
        print(round(20*np.log10(target_power),2))
    '''
    data=0
    for i in range(5):    ##fetch 5 times 
        samples = hackrf.read_samples()
        powe,freqs=psd(samples, NFFT=1024, Fs=hackrf.sample_rate/1e6, Fc=hackrf.center_freq/1e6)
        target_power=powe[round((target_freq-(hackrf.center_freq-hackrf.sample_rate//2))*1024/(hackrf.sample_rate))]
        print(round(20*np.log10(target_power),2))
        data=data+round(20*np.log10(target_power),2)
    power=round(data/5,2)
    print(power)
    if compare(power,powerwifi_range):
        resq.put(["wifipower",True,power])
    else:
        print("debug")
        resq.put(["wifipower",False,False])
    '''
    while True:
        uart_cmd(ser,"cp /nsc_tests/ATE/wifi_func.conf /etc/modprobe.d/s700-wifi.conf",ends=b"# ",response=False)
        output=uart_cmd(ser,"diff /nsc_tests/ATE/wifi_rf.conf /etc/modprobe.d/s700-wifi.conf",ends=b"# ",response=True)
        if b"firmware" in output:
            break
        else:
            continue
    '''

def iperfeth(ser,resq):             #update cris
    try:        
        bandwidth=-100
        for n in range (0,3):
            uart_cmd(ser,chr(0x03),ends=b"# ",response=False)
            #uart_cmd(ser,"ifconfig br-lan 88.88.86.88",ends=b"# ",response=True)
            #time.sleep(3)
            os.system("iperf3 -s -p 8899 &")
            time.sleep(0.5)
            #uart_cmd(ser,"iperf3 -s -p 8888",ends=b"# ",response=False)
            bandwidth_output=uart_cmd(ser,"iperf3 -c 88.88.86.1 -t 3 -p 8899",ends=b"# ",response=True)
            #bandwidth_output=ser.readall()
            print(bandwidth_output)
            bandwidth=float(str(bandwidth_output).strip().split("Mbits/sec")[-2].strip().split()[-1])
            #bandwidth="94.8"
            print(bandwidth)
            resq.put(["iperfeth",True,bandwidth])
            uart_cmd(ser,chr(0x03),ends=b"# ",response=False)
            
            break
        if bandwidth==-100:
            resq.put(["iperfeth",False,False])
            uart_cmd(ser,chr(0x03),ends=b"# ",response=False)
        os.system("killall iperf3")
    except:
        os.system("killall iperf3")
        traceback.print_exc()
        resq.put(["iperfeth",False,False])
        uart_cmd(ser,chr(0x03),ends=b"# ",response=False)
        
#mysql server
def connect_db(database,hostname,username,password,portnum):
    try:
        db=pymysql.connect(hostname,username,password,database,port=int(portnum))
        return db
    except Exception as e:
        traceback.print_exc()
        return e.args[1]        

def fetch_data(database,hostname,username,password,portnum,table,index_name,index_value,target=""):
    """table=table name"""
    try:
        db=connect_db(database,hostname,username,password,portnum)
        cursor = db.cursor()
        if target=="":
            sqlselect="SELECT * FROM %s WHERE %s='%s'"%(table,index_name,index_value)
        else:
            sqlselect="SELECT `%s` FROM %s WHERE %s='%s'"%(target,table,index_name,index_value)
        print(sqlselect)
        try:
            cursor.execute(sqlselect)
            db.commit()
            out = cursor.fetchall()
            db.close()
            return out
        except Exception as e:
            traceback.print_exc()
            db.rollback()
            db.close()
            return e.args[1]
    except Exception as e:
        traceback.print_exc()
        return e.args[1]
   
def info_rw(ser_linux,hostname,username,password,portnum,database,record_server_db,record_server_tb,table,sn_num,resq):

    try:
        _info_list=[]
        rest_mac=1000
        #print(database,hostname,username,password,portnum,record_server_tb,sn_num)
        server_mac=fetch_data(record_server_db,hostname,username,password,portnum,record_server_tb,"SNID",sn_num,target="ethmac")         ###get ethmac
        if server_mac !=():
            print("have already updated eth mac")
            mac_num=server_mac[0][0]
        else:
            mac_num,rest_mac=elan_get_mac_addr(hostname,username,password,portnum,database,table)         ###assign ethmac
            insert_data(record_server_db,hostname,username,password,portnum,record_server_tb,["SNID","ethmac"],[sn_num,mac_num],)  ###insert ethmac to server
    except:
        traceback.print_exc()
        

    try:
        #mac_num="00:18:fe:3c:15:cd"
        print(mac_num)
        mac_set="misctool -m -c %s"%mac_num
        mac_out=uart_cmd(ser_linux,mac_set,ends=b"# ",response=True)
        if "successfully!" in mac_out.decode():
            #uart_cmd(ser_linux,"ip link set eth0 down;sleep 1;ip link set eth0 up;",ends=b"# ",response=False)
            mac_read=uart_cmd(ser_linux,"misctool -m",ends=b"# ",response=True)
            if mac_num.strip() in mac_read.strip().decode():
                print("ethernet address writed success")
                _info_list.append(True)
            else:
                print("ethernet address writed fail")
                _info_list.append(False)
        else:
            print("ethernet address writed fail")
            _info_list.append(False)

        #sn_num="EL01470X228183000099"
        print(sn_num)
        sn_set="misctool -s -c %s;sync"%sn_num
        out=uart_cmd(ser_linux,sn_set,ends=b"# ",response=True)
        sn_out=uart_cmd(ser_linux,"misctool -s ",ends=b"# ",response=True)
        if sn_num in sn_out.decode():
            print("SN RW pass")
            _info_list.append(True)
        else:
            print("SN RW fail")
            _info_list.append(False)


        wifimac_out=uart_cmd(ser_linux,"cat /sys/class/net/wlan0/address",ends=b"# ",response=True)
        print(wifimac_out.split())
        wifimac=wifimac_out.split()[-2].decode()
        print(wifimac)

        if False not in _info_list:
            resq.put(["inforw",True,mac_num.replace(":","-"),sn_num,wifimac.replace(":","-"),rest_mac])
        else:
            resq.put(["inforw",False,mac_num.replace(":","-"),sn_num,wifimac.replace(":","-"),rest_mac])
        
    except:
        print(traceback.print_exc())

     
def uic(resq):
    resq.put(["uic",True])



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
    return mac_wrt,mac_max-result



def update_data(database,hostname,username,password,portnum,table,index_name,index_value,items,values):
    """table=table name, items=[items_list],values=[values_list as the same sequency as items]"""
    try:
        db=connect_db(database,hostname,username,password,portnum)
        cursor = db.cursor()
        update_list=""
        for n in range (0,len(items)):
            update_list=update_list+"""`%s`"""%str(items[n])+"="+"""'%s'"""%str(values[n])+","
        sqlupdate="UPDATE %s SET %s WHERE %s='%s'"%(table,update_list[:-1],index_name,index_value)
        print(sqlupdate)
        try:
            out=cursor.execute(sqlupdate)
            if out==1:
                db.commit()
                db.close()
                return True
            else:
                out==0
                db.rollback()
                db.close()
                print("SNID is not in current database or data no change")
                return False
        except Exception as e:
            traceback.print_exc()
            db.rollback()
            db.close()
            return e.args[1]
    except Exception as e:
        traceback.print_exc()
        return e.args[1]
    
def insert_data(database,hostname,username,password,portnum,table,items,values,):
    """table=table name, items=[items_list],values=[values_list as the same sequency as items]"""
    try:
        db=connect_db(database,hostname,username,password,portnum)
        cursor = db.cursor()
        items_list=""
        values_list=""
        for n in range (0,len(items)):
            items_list=items_list+"""`%s`"""%str(items[n])+","
            values_list=values_list+"""'%s'"""%str(values[n])+","
        sqlinsert="INSERT INTO %s(%s) VALUES (%s)"%(table,items_list[:-1],values_list[:-1])
        print(sqlinsert)
        try:
            out=cursor.execute(sqlinsert)
            if out==1:
                db.commit()
                db.close()
                return True
            else:
                out==0
                db.rollback()
                db.close()
                print("Failed to insert data")
                return False
        except Exception as e:
            traceback.print_exc()
            db.rollback()
            db.close()
            return e.args[1]
    except Exception as e:
        traceback.print_exc()
        return e.args[1]
    
def find_port(_linux_port,_ir_port,_switch1_port):     #Corresponding location manually
    try:
        global linux_port, ir_port,switch1_port
        ports = list(serial.tools.list_ports.comports())
        for i in range(len(ports)):
            print(ports[i].location,ports[i].device)
            #if "LOCATION=1-1.1.7.3" in ports[i].hwid:
            if "LOCATION=%s"%_linux_port in ports[i].hwid:
                linux_port=ports[i].device
                print("linux_port= ",linux_port)
            #elif "LOCATION=1-1.1.4.4" in ports[i].hwid:
            elif "LOCATION=%s"%_ir_port in ports[i].hwid:
                ir_port=ports[i].device
                print("ir_port= ",ir_port)
            #elif "LOCATION=1-1.1.7.1" in ports[i].hwid:
            elif "LOCATION=%s"%_switch1_port in ports[i].hwid:
                switch1_port=ports[i].device
                print("switch1_port= ",switch1_port)
        return linux_port,ir_port,switch1_port
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

  
#serial control over uart        
def uart_cmd(ser,cmd,ends=b"# ",response=False):
    try:
        for n in range (0,100):
            try:
                #output=output+ser.read_all()
                ser.read_all()
                time.sleep(0.1)
                #ser.flushInput()
                #ser.flushOutput()
                output=b""
                try:
                    ser.write((b"%s"%cmd+b"\n").replace(b"\r",b""))
                    print(b"%s"%cmd+b"\n")
                except:
                    ser.write(((cmd+"\n").encode()).replace(b"\r",b""))
                    print((cmd+"\n").encode().replace(b"\r",b""))
                if response==True:
                    time.sleep(0.1)
                    for n in range (0,100):
                        output=output+ser.read_all()
                        if output.endswith(ends):
                            return output
                            break
                        else:
                            ser.write((b"\n"))
                            time.sleep(0.1)
                    break
                else:
                    time.sleep(0.5)
                    return True
                    break
            except:
                ser.write((chr(0x03)+"\n").encode())
                traceback.print_exc()
                return False
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

def resetbtn_test(ser_linux,resq):
    try:
        #log=uart_cmd(ser_linux,"echo 10 > /etc/button_det/Resetfile",ends=b"# ",response=True)
        resq.put(["reset",True])
    except:
        resq.put(["reset",False])

def powerbtn_test(ser_linux,resq):
    resq.put(["power",True])
   
def led_test(ser_linux,resq):
    try:
        uart_cmd(ser_linux,"/etc/led.sh red",ends=b"# ",response=False)
        time.sleep(0.5)
        uart_cmd(ser_linux,"/etc/led.sh blue",ends=b"# ",response=False)
        time.sleep(0.5)
        uart_cmd(ser_linux,"/etc/led.sh amber",ends=b"# ",response=False)
        time.sleep(0.5)
        uart_cmd(ser_linux,"/etc/led.sh off",ends=b"# ",response=False)
        resq.put(["led",True])
    except:
        resq.put(["led",False])
        
   
def iperf5(ser,ssid,psd,resq):  #update command to grep wifi ip, can't recognize wifi connect or not!
    try:
        os.system("systemctl stop hostapd;cp /etc/hostapd/gc4_5g.conf  /etc/hostapd/hostapd.conf;sudo systemctl start hostapd")
        bandwidth=-100
        time.sleep(5)
        for n in range (0,3):
            uart_cmd(ser,"ifconfig wlan0 up",ends=b"# ",response=True)
            uart_cmd(ser,"killall wpa_supplicant",ends=b"# ",response=True)
            uart_cmd(ser,"wpa_passphrase %s %s > wpa.conf"%(ssid,psd),ends=b"# ",response=True)
            uart_cmd(ser,"wpa_supplicant -B -i wlan0 -c wpa.conf",ends=b"# ",response=True)
            time.sleep(1)
            uart_cmd(ser,"dhclient wlan0",ends=b"# ",response=True)
            time.sleep(5)
            uart_cmd(ser,chr(0x03),ends=b"# ",response=False)
            out=uart_cmd(ser,"iwconfig",ends=b"# ",response=True)
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
                ipaddr_out=uart_cmd(ser,"ifconfig wlan0 | grep 'inet'",ends=b"# ",response=True)
                time.sleep(3)
                ipaddr_list=ipaddr_out.strip().split()
                for i in range(len(ipaddr_list)):
                    if b"192" in ipaddr_list[i]:
                        ipaddr=ipaddr_list[i].decode()
                        break
                print(ipaddr)
                uart_cmd(ser,"iperf3 -s -p 8888",ends=b"# ",response=False)
                iperf_client("iperf3",ipaddr,5,8888)
                bandwidth_output=ser.readall()
                print(bandwidth_output)
                bandwidth=float(str(bandwidth_output).strip().split("Mbits/sec")[-2].strip().split()[-1])
                print(bandwidth)
                resq.put(["iperf5",bandwidth])
                uart_cmd(ser,chr(0x03),ends=b"# ",response=False)
                break
            else:
                uart_cmd(ser,chr(0x03),ends=b"# ",response=False)
                print("Fail to connect WIFI")
        if bandwidth==-100:
            resq.put(["iperf5",False])
            uart_cmd(ser,chr(0x03),ends=b"# ",response=False)
    except:
        traceback.print_exc()
        resq.put(["iperf5",False])
        uart_cmd(ser,chr(0x03),ends=b"# ",response=False)


    
    
def auto(ser,resq,res_value,dc1_range,tp28_range,ser_ir,ser_switch,sensevol_range,relayvol_range,recordinput,target_freq,powerwifi_range,hostname,username,password,portnum,database,record_server_db,record_server_tb,table,new_sn):
    try:
        exe=0
        count=0
        break_flag=0
        vol(ser_switch,dc1_range,tp28_range,resq)
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
            
            elif "voldc" in res_value and exe==0:
                resq.put(["auto","ING"])
                exe=exe+1
                uart_login(ser,ser_switch,resq)
            
            elif "login" in res_value and exe==1:
                resq.put(["auto","ING"])
                exe=exe+1
                ir_test(ser,ser_ir,resq)

            elif "ir" in res_value and exe==2:
                resq.put(["auto","ING"])
                exe=exe+1
                rs485_test(ser,resq)

            elif "rs485" in res_value and exe==3:
                resq.put(["auto","ING"])
                exe=exe+1
                sense_test(ser,ser_switch,sensevol_range,resq)

            elif "sense" in res_value and exe==4:
                resq.put(["auto","ING"])
                exe=exe+1
                rs232_test(ser,resq)

            elif "rs232" in res_value and exe==5:
                resq.put(["auto","ING"])
                exe=exe+1
                relay_test(ser,relayvol_range,resq)

            elif "relay" in res_value and exe==6:
                resq.put(["auto","ING"])
                exe=exe+1
                audio_test(ser,recordinput,resq)

            elif  "audio" in res_value and exe==7:
                resq.put(["auto","ING"])
                exe=exe+1
                usb2_test(ser,resq)
                

            elif "usb2.0" in res_value and exe==8:
                resq.put(["auto","ING"])
                exe=exe+1
                usb3_test(ser,resq)

            elif "usb3.0" in res_value and exe==9:
                resq.put(["auto","ING"])
                exe=exe+1
                fetch_power(ser,resq,target_freq,powerwifi_range)

            elif "wifipower" in res_value and exe==10:
                resq.put(["auto","ING"])
                exe=exe+1
                iperfeth(ser,resq)
                
            elif "iperfeth" in res_value and exe==11:
                resq.put(["auto","ING"])
                exe=exe+1
                info_rw(ser,hostname,username,password,portnum,database,record_server_db,record_server_tb,table,new_sn,resq)
        
            elif "SNID" in res_value and exe ==12:
                resq.put(["auto","ING"])
                exe=exe+1
                uic(resq)

            elif "power" in res_value and exe ==13:
                resq.put(["auto","ING"])
                exe=exe+1
                resq.put(["auto",True])
                break
            else:
                time.sleep(1)
            #print(count)


            if count==240:
                resq.put(["auto",False])
                break

        
    except:
        resq.put(["auto",False])
        traceback.print_exc()
        with open('log.txt', 'a') as f:
            f.write(traceback.format_exc())

#resq=queue.Queue()
#ser_linux=serial.Serial("/dev/ttyUSB0",115200,timeout=1)
#RS232_test(ser_linux,resq)

