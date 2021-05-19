import serial
from serial.tools import list_ports
import time
import usbtmc
import time
import traceback
import paramiko

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

import inspect
import ctypes

#import nscserver
import warnings
import pymysql
import time
import traceback
import visa
import platform
warnings.filterwarnings("ignore")

def gen_2gconf(outfile,ssid,psd,channel):
    f=open(outfile,"w")
    f.write("interface=wlan0\n\
driver=nl80211\n\
hw_mode=b\n\
ieee80211n=1\n\
wmm_enabled=1\n\
country_code=US\n\
wpa=2\n\
wpa_key_mgmt=WPA-PSK\n\
rsn_pairwise=CCMP\n\
ssid=%s\n\
wpa_passphrase=%s\n\
channel=%s\n"%(ssid,psd,channel))
    f.close()

def gen_5gconf(outfile,ssid,psd,channel):
    f=open(outfile,"w")
    f.write("interface=wlan0\n\
country_code=US\n\
ssid=%s\n\
hw_mode=a\n\
macaddr_acl=0\n\
auth_algs=1\n\
ignore_broadcast_ssid=0\n\
wpa=2\n\
wpa_passphrase=%s\n\
wpa_key_mgmt=WPA-PSK\n\
wpa_pairwise=TKIP\n\
rsn_pairwise=CCMP\n\
channel=%s\n\
ht_capab=[HT40-][HT40+][SHORT-GI-40][DSSS_CCK-40]\n\
ieee80211n=1\n\
ieee80211ac=1\n\
wmm_enabled=1\n"%(ssid,psd,channel))
    f.close()

def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)

def ack_ping(stcp):
    ping_list = [0xA5,0x01,0x01,0x00]
    crc = (~(0xA5+0x01+0x01))&0xff
    ping_list.append(crc)
    stcp.send(bytes(ping_list))    

def readcom_from_location(ir_usb_loc="1-1.1.4.2",
                          switch_loc="1-1.1.3.1",
                          switch2_loc="1-1.1.3.2",
                          rs232_1_loc="1-1.1.4.1",
                          rs232_2_loc="1-1.1.4.4"):
    try:
        ports = list(serial.tools.list_ports.comports())
        print("Please make sure the control port location is correct:")
        for p in ports:
            if p.location == rs232_1_loc:
                rs232_1 = p.device
                print("RS232_1",p.device,p.location)
            elif p.location == rs232_2_loc:
                rs232_2 = p.device
                print("RS232_2",p.device,p.location)
            elif p.location == switch_loc:
                switch = p.device
                print("switch",p.device,p.location)
            elif p.location == ir_usb_loc:
                ir_usb = p.device
                print("ir_usb",p.device,p.location)
            elif p.location == switch2_loc:
                switch2 = p.device
                print("switch2",p.device,p.location)
                pass
    except:
        traceback.print_exc()
        return False
    return ir_usb,switch,switch2,rs232_1,rs232_2
#readcom_from_location()
#Get device control port
def readcom_from_pidvid(vidpid="10C4:EA60",extra="0000"):
    try:
        vid=vidpid.split(":")[0]
        pid=vidpid.split(":")[1]
        devfind=0
        port=False
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if pid in p.hwid and vid in p.hwid:
                port = p[0]
                print(p.hwid)
                devfind=devfind+1
        if devfind==1:
            print(port)
            return port
        elif devfind>1:
            for p in ports:
                if pid in p.hwid and vid in p.hwid and extra in p.hwid:
                    port = p[0]
                    print(p.hwid)
                    print(port)
                    return port
                    break
                
        else:
            print("same or no uart device detected, please input ser or location like  readcom_from_pidvid(vidpid='10C4:EA60',extra='0000')")
            return False
    except:
        traceback.print_exc()
        return False
    
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

#SSH Transfer
def ssh_upload(hostip,username,password,portnum,localfilepath,remotefilepath):
    try:
        if password==None or password=="":
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=hostip, username=username, password = password,port=portnum)
            ftp_client=ssh.open_sftp()
            ftp_client.put(localfilepath,remotefilepath)
            ftp_client.close()
            ssh.close()
        else:
            os.system("scp -o StrictHostKeyChecking=no %s %s@%s:%s"%(localfilepath,username,hostip,remotefilepath))
        return True
    except:
        traceback.print_exc()
        return False           



 

#read configuration
def read_config(filepath,target):
    try:
        f=open(r"%s"%filepath,"r")
        data=f.readlines()
        out=False
        for n in range (0,len(data)):
            if target+"=" in data[n]:
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
            if target+"=" in data[n]:
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

        


#get frequency
def get_freq(data,rate,octave=3):
    try:
        fftData=abs(np.fft.rfft(data))**2
        which = fftData[1:].argmax() + 1
        if which != len(fftData)-1:
            y0,y1,y2 = np.log(fftData[which-1:which+2:])
            x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
            thefreq = (which+x1)*rate/len(data)
        else:
            thefreq = which*rate/len(data)
        return round(thefreq)
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


#resolution analysis
def find_edge(data,key):
    flag=0
    data=np.diff(data)
    #plt.plot(data)
    #plt.show()
    for n in range (0,len(data)):
        if abs(data[n])>key:
            temp=list(data[n:n+150])
            if abs(temp.index(max(temp))-temp.index(min(temp)))>60 and \
               abs(temp.index(max(temp))-temp.index(min(temp)))<150 and \
               max(temp)>key and \
               min(temp)<-key:
                flag=1
                break
            else:
                continue      
    if flag==1:
        return [temp.index(max(temp))+n,temp.index(min(temp))+n,abs(temp.index(max(temp))-temp.index(min(temp)))]
    else:
        return False

def find_resolution(im,direction,whichlines,gap,start,end):
    count_list=[]
    row=len(im)
    col=len(im[0])
    if direction=="hor":
        rgb=im[int(whichlines)]
        gray=[]
        for m in range (0,len(rgb)):
            gray.append(int((0.299*rgb[m][0] + 0.587*rgb[m][1] + 0.114*rgb[m][2])*1))

    elif direction=="ver":
        rgb=im[0:row,int(whichlines):int(whichlines)+1]
        gray=[] 
        for m in range (0,len(rgb)):
            gray.append(int((0.299*rgb[m][0][0] + 0.587*rgb[m][0][1] + 0.114*rgb[m][0][2])*1))        

    clips=np.diff(gray)

    
    clips=clips[start:end]
    clips=list(clips)
    while 0 in clips:
        clips.remove(clips[clips.index(0)])
    #plt.plot(clips)
    #plt.show()
    
    for n in range (0,len(clips)-1):
        tempclips=clips[n:gap//2+n]
        count=[]
        avgclips=np.average(abs(np.array(tempclips)))
        #print(avgclips)
        for m in range (1,len(tempclips)-1):
            if tempclips[m]<-4 and \
               tempclips[m]<tempclips[m-1] and \
               tempclips[m]<tempclips[m+1]:
                count.append([tempclips,m])
        if len(count)>=9:
            count_list.append(len(count))
            break
        else:
            count_list.append(len(count))
    print(max(count_list))
    return max(count_list)


def locate(image_file,key=12):
    try:
        horleftup=0
        horleftdown=0
        horrightup=0
        horrightdown=0
        verupleft=0
        verupright=0
        verdownleft=0
        verdownright=0
        gap=0
        #image_file="small.jpg"
        im=Image.open(image_file)
        im=np.asarray(im)
        row=len(im)
        col=len(im[0])
        cenrow=len(im)//2
        cencol=len(im[0])//2

        rgb=im[int(cenrow)]
        gray=[]
        for m in range (0,len(rgb)):
            gray.append(int((0.299*rgb[m][0] + 0.587*rgb[m][1] + 0.114*rgb[m][2])*1))

        try:
            vercenleft=max(find_edge(gray[0:cencol],key)[0:2])
        except:
            vercenleft=0

        try:
            vercenright=min(find_edge(gray[int(-cencol/3):],key)[0:2])+(col+int(-cencol/3))
        except:
            vercenright=(col+int(-cencol/3))
            
        
        print("cenvh",cencol,cenrow)
        print("ver",vercenleft,vercenright)

        rgb=im[0:row,int(cencol):int(cencol)+1]
        gray=[] 
        for m in range (0,len(rgb)):
            gray.append(int((0.299*rgb[m][0][0] + 0.587*rgb[m][0][1] + 0.114*rgb[m][0][2])*1))

        horcenup=max(find_edge(gray[0:cenrow],key)[0:2])
        horcendown=min(find_edge(gray[-cenrow:],key)[0:2])+cenrow

        gap=abs(find_edge(gray[0:cenrow],key)[2])
        print("hor",horcenup,horcendown)
        print("gap",gap)

        horcen=(horcenup+horcendown)//2
        vercen=(vercenleft+vercenright)//2
        print("horcen",horcen,vercen)


        #ud=1944-1324-607+624-581//2
        #lr=2599-1869-495, 1879-1863

        ###############333Hor
        line=vercenleft+gap
        rgb=im[0:row,int(line):int(line)+1]
        gray=[]
        for m in range (0,len(rgb)):
            gray.append(int((0.299*rgb[m][0][0] + 0.587*rgb[m][0][1] + 0.114*rgb[m][0][2])*1))

        try:
            horleftup=max(find_edge(gray[horcenup-2*gap:horcenup+2*gap],key)[0:2])+horcenup-2*gap
        except:
            horleftup=horcenup-2*gap
        #print(find_edge(gray[horcendown-2*gap:horcendown+2*gap]))
        try:
            horleftdown=min(find_edge(gray[horcendown-2*gap:horcendown+2*gap],key)[0:2])+horcendown-2*gap
        except:
            horleftdown=horcendown-2*gap

        line=vercenright-gap
        rgb=im[0:row,int(line):int(line)+1]
        gray=[]
        for m in range (0,len(rgb)):
            gray.append(int((0.299*rgb[m][0][0] + 0.587*rgb[m][0][1] + 0.114*rgb[m][0][2])*1))

        try:
            horrightup=max(find_edge(gray[horcenup-2*gap:horcenup+2*gap],key)[0:2])+horcenup-2*gap
        except:
            horrightup=horcenup-2*gap

        try:
            horrightdown=min(find_edge(gray[horcendown-2*gap:horcendown+2*gap],key)[0:2])+horcendown-2*gap
        except:
            horrightdown=horcendown-2*gap

        #im[row,col]
        ################VER
        line=int(horcenup+gap)
        rgb=im[int(line)]
        gray=[]
        for m in range (0,len(rgb)):
            gray.append(int((0.299*rgb[m][0] + 0.587*rgb[m][1] + 0.114*rgb[m][2])*1))

        try:
            verupleft=max(find_edge(gray[0:cencol],key)[0:2])
        except:
            verupleft=0

        try:
            verupright=min(find_edge(gray[-cencol:],key)[0:2])+cencol
        except:
            verupright=cencol

        line=int(horcendown-gap)
        rgb=im[int(line)]
        gray=[]
        for m in range (0,len(rgb)):
            gray.append(int((0.299*rgb[m][0] + 0.587*rgb[m][1] + 0.114*rgb[m][2])*1))

        try:
            verdownleft=max(find_edge(gray[0:cencol],key)[0:2])
        except:
            verdownleft=0

        try:
            verdownright=min(find_edge(gray[-cencol:],key)[0:2])+cencol
        except:
            verdownright=cencol

        #horcen=(horleftup+horleftdown)//2
        #vercen=(verupleft+verupright)//2
        print(horcen,vercen)
        #horcen=horcen-(horrightup-horleftup)
        #vercen=vercen-(verupright-verdownright)

        #ud=1944-1324-607+(624-581)//2
        #lr=2599-1869-495, 1879-1863

        
        return [im,horcen,vercen,vercenleft,vercenright,horcenup,horcendown,horleftup,horleftdown,horrightup,horrightdown,verupleft,verupright,verdownleft,verdownright,gap]

    except:
        traceback.print_exc()
        return False,False,False,False,False,False,False,False,False,False,False,False       



#Excel control
class StringConverter(dict):
    def __contains__(self, item):
        return True
    def __getitem__(self, item):
        return str
    def get(self, default=None):
        return str


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

def update_result(res_value,file_name):
    try:
        if filecmp.cmp(os.path.join(os.getcwd(),"%s.csv"%file_name),os.path.join(os.getcwd(),"%s_backup.csv"%file_name)):
            df=pd.read_csv(os.path.join(os.getcwd(),"%s.csv"%file_name),converters=StringConverter())
            res_value_list=list(res_value.keys())
            for n in range (0,len(df)):
                if res_value["SNID"][1]==df.loc[n].SNID:
                    for m in range (0,len(res_value_list)):
                        df.loc[n,"%s"%res_value_list[m]]=res_value[res_value_list[m]][1]
                    break
            df.to_csv(os.path.join(os.getcwd(),"%s.csv"%file_name),index = False)
            shutil.copyfile(os.path.join(os.getcwd(),"%s.csv"%file_name), os.path.join(os.getcwd(),"%s_backup.csv"%file_name))
            return "UPDATE"
        else:
            return "ERROR"
    except:
        traceback.print_exc()
        return "ERROR"


#mysql server
def connect_db(database,hostname,username,password,portnum):
    try:
        db=pymysql.connect(hostname,username,password,database,port=int(portnum))
        return db
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

def delete_data(database,hostname,username,password,portnum,table,index_name,index_value):
    """table=table name"""
    try:
        db=connect_db(database,hostname,username,password,portnum)
        cursor = db.cursor()
        sqldelete="DELETE FROM %s WHERE %s='%s'"%(table,index_name,index_value)
        print(sqldelete)
        try:
            cursor.execute(sqldelete)
            db.commit()
            db.close()
            return True
        except Exception as e:
            traceback.print_exc()
            db.rollback()
            db.close()
            return e.args[1]
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

def fixnum(count,value):
    while len(value)<count:
        value="0"+str(value)
    return value

def fetch_tacsn(database,hostname,username,password,portnum,table,index_name,index_value):
    
    """table=table name"""
    try:
        db=connect_db(database,hostname,username,password,portnum)
        cursor = db.cursor()
        sqlselect="SELECT * FROM %s WHERE %s='%s'"%(table,index_name,index_value)
        print(sqlselect)
        try:
            cursor.execute(sqlselect)
            out = cursor.fetchall()[0]
            tac=out[1]
            sn=out[2]
            items=["TAC","SN"]
            values=[tac,fixnum(6,str(int(sn)+1))]
            update_list=""
            for n in range (0,len(items)):
                update_list=update_list+str(items[n])+"="+"""'%s'"""%str(values[n])+","
            sqlupdate="UPDATE %s SET %s WHERE %s='%s'"%(table,update_list[:-1],index_name,index_value)
            cursor.execute(sqlupdate)
            db.commit()
            db.close()
            return tac,sn
        except Exception as e:
            traceback.print_exc()
            db.rollback()
            db.close()
            return e.args[1]
    except Exception as e:
        traceback.print_exc()
        return e.args[1]  

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
            #print(mac_next)

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
    return mac_wrt.replace(":","")



