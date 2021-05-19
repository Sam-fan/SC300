from PyQt5 import QtCore, QtGui, QtWidgets
import finished_ui
from finished_func import *
from comfunc import *
import sys
import _thread
import traceback
from zebra import zebra
import threading

#class pcba_ate(pcba_ui.Ui_Form):
#    def __init__(self,Form):
#        super().setupUi(Form)


class mbox(QtWidgets.QWidget, finished_ui.Ui_Form):
    def __init__(self,parent=None):
        super(mbox, self).__init__(parent)
        self.setupUi(self)
        
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.operate)
        self.timer.start(1000)

        self.btn_conf.clicked.connect(self.conf_btn_clicked)
        self.btn_cri.clicked.connect(self.cri_btn_clicked)
        
        self.btn_getip.clicked.connect(self.getip_clicked)
        self.btn_ir.clicked.connect(self.ir_clicked)
        self.btn_rs485.clicked.connect(self.rs485_clicked)
        self.btn_sense.clicked.connect(self.sense_clicked)
        self.btn_rs232.clicked.connect(self.rs232_clicked)
        self.btn_relay.clicked.connect(self.relay_clicked)
        self.btn_audio.clicked.connect(self.audio_clicked)
        self.btn_usb2.clicked.connect(self.usb_clicked)
        self.btn_usb3.clicked.connect(self.usb3_clicked)
        self.btn_iperfwifi.clicked.connect(self.iperfwifi_clicked)
        self.btn_uic.clicked.connect(self.uic_clicked)
        
        self.btn_auto.clicked.connect(self.auto_clicked)
        self.btn_submit.clicked.connect(self.submit_clicked)
        self.btn_reset.clicked.connect(self.reset_clicked)

        
        self.btn_list=[self.btn_getip,
                       self.btn_ir,
                       self.btn_rs485,
                       self.btn_sense,
                       self.btn_rs232,
                       self.btn_relay,
                       self.btn_audio,
                       self.btn_usb2,
                       self.btn_usb3,
                       self.btn_iperfwifi,
                       self.btn_uic,
                       self.btn_auto,
                       ]
        
        self.res_list=[self.res_ir1,
                       self.edit_snscan,
                       self.edit_getip,
                       self.res_ir2,
                       self.res_ir3,
                       self.res_ir4,
                       self.res_ir5,
                       self.res_ir6,
                       self.res_ir7,
                       self.res_ir8,
                       self.res_ir9,
                       self.res_ir10,
                       self.res_ir11,
                       self.res_ir12,
                       self.res_rs485,
                       self.res_sense1,
                       self.res_sense2,
                       self.res_sense3,
                       self.res_sense4,
                       self.res_rs23215,
                       self.res_rs23226,
                       self.res_rs23237,
                       self.res_rs23248,
                       self.res_relay,
                       self.res_thd,
                       self.res_amp,
                       self.res_usb2,
                       self.res_usb3,
                       self.res_iperfwifi,
                       self.res_led,
                       self.res_hdmi,
                       self.res_rstbtn,
                       self.res_powbtn,
                       self.res_bspver,
                       self.res_irver,
                       self.res_sensever,
                       self.res_ethmac,
                       self.res_wifimac
                       ]
                       

        self.label_list=[self.lab_ir1,
                       self.lab_scansn,
                       self.lab_ir2,
                       self.lab_ir3,
                       self.lab_ir4,
                       self.lab_ir5,
                       self.lab_ir6,
                       self.lab_ir7,
                       self.lab_ir8,
                       self.lab_ir9,
                       self.lab_ir10,
                       self.lab_ir11,
                       self.lab_ir12,
                       self.lab_sense1,
                       self.lab_sense2,
                       self.lab_sense3,
                       self.lab_sense4,
                       self.lab_rs23215,
                       self.lab_rs23226,
                       self.lab_rs23237,
                       self.lab_rs23248,
                       self.lab_thd,
                       self.lab_amp,
                       self.lab_led,
                       self.lab_hdmi,
                       self.lab_rstbtn,
                       self.lab_powbtn,
                       self.lab_bspver,
                       self.lab_irver,
                       self.lab_sensever,
                       self.lab_ethmac,
                       self.lab_wifimac
                       ]


        self.btn_submit.setEnabled(False)


    def conf_btn_clicked(self):
        os.system("xdg-open finished.conf")

    def cri_btn_clicked(self):
        os.system("xdg-open finished.cri")

    def showMsg(self,message_type,title,issue):
        if message_type=="question":
            a=QtWidgets.QMessageBox.question(self, title, issue, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            return a==QtWidgets.QMessageBox.Yes
        if message_type=="warning":
            a=QtWidgets.QMessageBox.warning(self,title, issue,QtWidgets.QMessageBox.Ok)
        if message_type=="infomation":
            a=QtWidgets.QMessageBox.warning(self,title, issue,QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            return a==QtWidgets.QMessageBox.Yes

    def active_onebtn(self,target_btn):
        try:
            for n in range (0,len(self.btn_list)):
                self.btn_list[n].setEnabled(False)
            target_btn.setStyleSheet("color:yellow")
        except:
            traceback.print_exc()
            
    def enable_allbtn(self):
        for n in range (0,len(self.btn_list)):
            self.btn_list[n].setEnabled(True)

    def reset_allbtn(self):
        res_value={}
        for n in range (0,len(self.btn_list)):
            self.btn_list[n].setEnabled(True)
            self.btn_list[n].setStyleSheet("color:")
        for n in range (0,len(self.res_list)):
            self.res_list[n].setText("NA")
        for n in range (0,len(self.label_list)):
            self.label_list[n].setStyleSheet("color:")
        self.btn_submit.setEnabled(False)
        self.btn_submit.setStyleSheet("color:")
        self.btn_auto.setStyleSheet("color:")
        self.btn_auto.setText("AUTO")

    def getip_clicked(self):
        try:
            self.active_onebtn(self.btn_getip)
            _thread.start_new_thread(getstaip,(ssh_user,ssh_passwd,ssh_portnum,ser_switch,ssid,psd,resq,))
        except:
            traceback.print_exc()
            self.enable_allbtn()
            
    def ir_clicked(self):
        try:
            ip=self.edit_getip.text()
            self.active_onebtn(self.btn_ir)
            _thread.start_new_thread(ir_test,(ssh_shell,ser_ir,resq))
        except:
            traceback.print_exc()
            self.enable_allbtn()
            
    def rs485_clicked(self):
        try:
            self.active_onebtn(self.btn_rs485)
            _thread.start_new_thread(rs485_test,(ssh_shell,resq))
        except:
            traceback.print_exc()
            self.enable_allbtn()
            
    def sense_clicked(self):
        try:
            self.active_onebtn(self.btn_sense)
            _thread.start_new_thread(sense_test,(ssh_shell,ser_switch,sensevol_range,resq))
        except:
            traceback.print_exc()
            self.enable_allbtn()
            
    def rs232_clicked(self):
        try:
            self.active_onebtn(self.btn_rs232)
            _thread.start_new_thread(rs232_test,(ssh_shell,resq))
        except:
            traceback.print_exc()
            self.enable_allbtn()

    def relay_clicked(self):
        try:
            self.active_onebtn(self.btn_relay)
            _thread.start_new_thread(relay_test,(ssh_shell,relayvol_range,resq))
        except:
            traceback.print_exc()
            self.enable_allbtn()
            
    def audio_clicked(self):
        try:
            self.active_onebtn(self.btn_audio)
            _thread.start_new_thread(audio_test,(ssh_shell,recordinput,resq))
        except:
            traceback.print_exc()
            self.enable_allbtn()
            
    def usb_clicked(self):
        try:
            self.active_onebtn(self.btn_usb2)
            _thread.start_new_thread(usb2_test,(ssh_shell,resq))
        except:
            traceback.print_exc()
            self.enable_allbtn()

    def usb3_clicked(self):
        try:
            self.active_onebtn(self.btn_usb3)
            _thread.start_new_thread(usb3_test,(ssh_shell,resq))
        except:
            traceback.print_exc()
            self.enable_allbtn()

            
    def iperfwifi_clicked(self):
        try:
            self.active_onebtn(self.btn_iperfwifi)
            #_thread.start_new_thread(iperfeth,(ssh_shell,resq,))
            _thread.start_new_thread(iperfwifi,(ssh_shell,ssid,psd,resq,))
        except:
            traceback.print_exc()
            self.enable_allbtn()

    def uic_clicked(self):
        try:
            self.active_onebtn(self.btn_uic)
            _thread.start_new_thread(uic,(resq,))
        except:
            traceback.print_exc()
            self.enable_allbtn()
    
    def auto_clicked(self):
        global res_value,ser_ir     
        try:
            self.reset_allbtn()
            self.btn_auto.setStyleSheet("color:yellow")
            self.btn_auto.setText("RUNNING")
            res_value={}
            self.active_onebtn(self.btn_auto)
            _thread.start_new_thread(auto,(ssh_user,ssh_passwd,ssh_portnum,resq,res_value,ser_ir,ser_switch,sensevol_range,relayvol_range,recordinput,ssid,psd,hostname,username,password,portnum,database,table))                            
        except:
            self.enable_allbtn()
            traceback.print_exc()
            self.btn_auto.setStyleSheet("color:red")
            with open('log.txt', 'a') as f:
                f.write(traceback.format_exc())






    def submit_clicked(self):
        try:
            #res_value["time"]=["P",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))]
            index_name="SNID"
            index_value=res_value["SNID"][1]
            items=list(res_value.keys())
            values=[]
            for n in range (0,len(res_value)):
                values.append(res_value[items[n]][1])

            checkexit=fetch_data(record_server_db,record_server_name,record_server_usr,record_server_psd,record_server_pn,record_server_tb,index_name,index_value,target="")
            print(checkexit)
            if len(checkexit)==0:
                insert_data(record_server_db,record_server_name,record_server_usr,record_server_psd,record_server_pn,record_server_tb,[index_name],[index_value])

            out=save_result(res_value,"sc300_fg")
            if out=="ADD":
                if update_data(record_server_db,record_server_name,record_server_usr,record_server_psd,record_server_pn,record_server_tb,index_name,index_value,items,values)==True:
                    self.btn_submit.setStyleSheet("color:green")
                    answer=self.showMsg("warning","Done","Test Done!")
                else:
                     answer=self.showMsg("warning","submit","Fail to submit to the server, please check connection or productsn not in database")
            elif out=="DUP":
                self.btn_submit.setStyleSheet("color:yellow")
                answer=self.showMsg("question","sumit","Dupilcation of sn!, are you sure you want to update the current data?")
                if answer==True:
                    out=update_result(res_value,"sc300_fg")
                    if "UPDATE" in out:
                        if update_data(record_server_db,record_server_name,record_server_usr,record_server_psd,record_server_pn,record_server_tb,index_name,index_value,items,values)==True:
                            self.btn_submit.setStyleSheet("color:green")
                            answer=self.showMsg("warning","Done","Test Done!")
                        else:
                            answer=self.showMsg("warning","submit","Fail to submit to the server, please check connection or productsn not in database")                            
                    else:
                        answer=self.showMsg("warning","submit","Not able to submit data, please check if the excel is open!")
                else:
                    answer=self.showMsg("warning","submit","Not able to submit data, please check if the excel is open!")
            elif out=="WARN":
                self.btn_submit.setStyleSheet("color:red")
                answer=self.showMsg("warning","sumit","backup data different with record, please save the backup back to avoid data lost!")
            elif out=="ERROR":
                self.btn_submit.setStyleSheet("color:red")
                answer=self.showMsg("warning","sumit","Not able to submit data, please check if the excel is open!")
            else:
                self.btn_submit.setStyleSheet("color:red")
                answer=self.showMsg("warning","sumit","Not able to submit data, please check if the excel is open!")
        except:
            traceback.print_exc()
            with open('log.txt', 'a') as f:
                f.write(traceback.format_exc())


    def reset_clicked(self):
        try:            
            res_value={}
            self.reset_allbtn()
            self.btn_submit.setStyleSheet("color:")
            self.btn_auto.setText("AUTO")
            self.btn_submit.setEnabled(False)
        except:
            traceback.print_exc()
            
    def operate(self):
        global res_value

        if not resq.empty():
            getresq=resq.get()
            print("************",getresq,res_value,len(res_value))
            
            if getresq[0]=="auto":
                try:
                    #print("debug:",getresq[1])
                    if getresq[1]==True:
                        self.btn_auto.setText("DONE")
                        self.btn_auto.setStyleSheet("color:blue")
                        self.enable_allbtn()
                    elif getresq[1]=="ING":
                        self.btn_auto.setText("RUNNING")
                        self.btn_auto.setStyleSheet("color:yellow")
                        self.active_onebtn(self.btn_auto)
                    else:
                        self.btn_auto.setText("FAIL")
                        self.btn_auto.setStyleSheet("color:red")
                        self.enable_allbtn()
                except:
                    traceback.print_exc()
                    
            if len(res_value)==17:
                pcount=0
                res_value_values=list(res_value.values())
                for n in range (0,len(res_value_values)):
                    if res_value_values[n][0]=="P":
                        pcount=pcount+1
                if pcount==17:
                    self.btn_submit.setEnabled(True)
    

            if getresq[0]=="getip":
                global ip,ssh_shell
                try:
                    if getresq[1]==True:
                        ip=getresq[2]
                        ssh_shell=getresq[3]
                        sn=getresq[4]
                        ethmac=getresq[5]
                        wifimac=getresq[6]
                        bspver=getresq[7]
                        irver=getresq[8]
                        sensever=getresq[9]
                        if len(sn)==20:
                            self.lab_scansn.setStyleSheet("color:green")
                            res_value["SNID"] = ["P",sn]
                            self.edit_snscan.setText(sn)
                        else:
                            self.lab_scansn.setStyleSheet("color:red")
                            res_value["SNID"] = ["F",""]
                        self.lab_ethmac.setStyleSheet("color:green")
                        self.res_ethmac.setText(ethmac)
                        self.lab_wifimac.setStyleSheet("color:green")
                        self.res_wifimac.setText(wifimac)
                        self.lab_bspver.setStyleSheet("color:green")
                        self.res_bspver.setText(bspver)
                        self.lab_irver.setStyleSheet("color:green")
                        self.res_irver.setText(irver)
                        self.lab_sensever.setStyleSheet("color:green")
                        self.res_sensever.setText(sensever)
                        res_value["bspver"]=["P",str(bspver)]
                        res_value["irver"]=["P",str(irver)]
                        res_value["sensever"]=["P",str(sensever)]
                        
                        self.btn_getip.setStyleSheet("color:green")
                        self.edit_getip.setText(getresq[2])
                        
                    else:
                        '''
                        self.lab_bspver.setStyleSheet("color:red")
                        self.res_bspver.setText(str(bspver))
                        self.lab_irver.setStyleSheet("color:red")
                        self.res_irver.setText(str(irver))
                        self.lab_sensever.setStyleSheet("color:red")
                        self.res_sensever.setText(str(sensever))
                        res_value["bspver"]=["F",str(bspver)]
                        res_value["irver"]=["F",str(irver)]
                        res_value["sensever"]=["F",str(sensever)]
                        res_value["SNID"] = ["F",""]
                        #res_value["getip"]=["F","F"]
                        '''
                        self.btn_getip.setStyleSheet("color:red")
                    self.enable_allbtn()
                except:
                    self.enable_allbtn()
                    #self.res_bspver.setText(str(bspver))
                    #self.res_irver.setText(str(irver))
                    #self.res_sensever.setText(str(sensever))
                    res_value["bspver"]=["F",str(bspver)]
                    res_value["irver"]=["F",str(irver)]
                    res_value["sensever"]=["F",str(sensever)]
                    res_value["getip"]=["F",""]
                    res_value["SNID"] = ["F",""]
                    self.btn_getip.setStyleSheet("color:red")
                    traceback.print_exc()
                    with open('log.txt', 'a') as f:
                        f.write(traceback.format_exc())

                        
            if getresq[0]=="ir":
                try:
                    ir_list=[self.lab_ir1,
                             self.lab_ir2,
                             self.lab_ir3,
                             self.lab_ir4,
                             self.lab_ir5,
                             self.lab_ir6,
                             self.lab_ir7,
                             self.lab_ir8,
                             self.lab_ir9,
                             self.lab_ir10,
                             self.lab_ir11,
                             self.lab_ir12]
                    if getresq[1]==True:
                        res_value["ir"]=["P","P"]
                        self.btn_ir.setStyleSheet("color:green")
                        for n in range (0,len(ir_list)):
                            ir_list[n].setStyleSheet("color:green")
                    else:
                        res_value["ir"]=["F","F"]
                        self.btn_ir.setStyleSheet("color:red")
                        for n in range (0,len(ir_list)):
                            if getresq[2][n]==True:
                                ir_list[n].setStyleSheet("color:green")
                            else:
                                ir_list[n].setStyleSheet("color:red")
                    self.enable_allbtn()
                except:
                    self.enable_allbtn()
                    res_value["ir"]=["F",""]
                    self.btn_ir.setStyleSheet("color:red")
                    traceback.print_exc()


            if getresq[0]=="rs485":
                try:
                    if getresq[1]==True:
                        res_value["rs485"]=["P","P"]
                        self.btn_rs485.setStyleSheet("color:green")
                    else:
                        res_value["rs485"]=["F","F"]
                        self.btn_rs485.setStyleSheet("color:red")
                    self.enable_allbtn()
                except:
                    self.enable_allbtn()
                    res_value["rs485"]=["F",""]
                    self.btn_rs485.setStyleSheet("color:red")
                    self.res_rs485.setStyleSheet("color:red")
                    traceback.print_exc()
                    with open('log.txt', 'a') as f:
                        f.write(traceback.format_exc())

            if getresq[0]=="sense":
                try:
                    if getresq[1]==True:
                        res_value["sense"]=["P","P"]
                        self.btn_sense.setStyleSheet("color:green")
                        self.lab_sense1.setStyleSheet("color:green")
                        self.lab_sense2.setStyleSheet("color:green")
                        self.lab_sense3.setStyleSheet("color:green")
                        self.lab_sense4.setStyleSheet("color:green")                                              
                    else:
                        res_value["sense"]=["F","F"]
                        self.btn_sense.setStyleSheet("color:red")
                        self.lab_sense1.setStyleSheet("color:red")
                        self.lab_sense2.setStyleSheet("color:red")
                        self.lab_sense3.setStyleSheet("color:red")
                        self.lab_sense4.setStyleSheet("color:red") 
                    self.enable_allbtn()
                except:
                    traceback.print_exc()
                    self.enable_allbtn()
                    self.btn_sense.setStyleSheet("color:red")
                    res_value["sense"]=["F"," "]
                    with open('log.txt', 'a') as f:
                        f.write(traceback.format_exc())

            if getresq[0]=="rs232":
                try:
                    rs232_list=[self.lab_rs23215,
                             self.lab_rs23226,
                             self.lab_rs23237,
                             self.lab_rs23248]
                    if getresq[1]==True:
                        res_value["rs232"]=["P","P"]
                        self.btn_rs232.setStyleSheet("color:green")
                        for n in range (0,len(rs232_list)):
                            rs232_list[n].setStyleSheet("color:green")
                    else:
                        res_value["rs232"]=["F","F"]
                        self.btn_rs232.setStyleSheet("color:red")
                        for n in range (0,len(rs232_list)):
                            if getresq[2][n]==True:
                                rs232_list[n].setStyleSheet("color:green")
                            else:
                                rs232_list[n].setStyleSheet("color:red")
                    self.enable_allbtn()
                except:
                    self.enable_allbtn()
                    res_value["rs232"]=["F",""]
                    self.btn_rs232.setStyleSheet("color:red")
                    traceback.print_exc()

            if getresq[0]=="relay":
                try:
                    print(getresq[1])
                    if getresq[1]==True:
                        res_value["relay"]=["P","P"]
                        self.btn_relay.setStyleSheet("color:green")
                    else:
                        res_value["relay"]=["F","F"]
                        self.btn_relay.setStyleSheet("color:red")
                    self.enable_allbtn()
                except:
                    self.enable_allbtn()
                    res_value["relay"]=["F",""]
                    self.btn_relay.setStyleSheet("color:red")
                    traceback.print_exc()
                    with open('log.txt', 'a') as f:
                        f.write(traceback.format_exc())

            if getresq[0]=="audio":
                try:
                    if getresq[1]!=False and compare(getresq[1],spkthd_range) and  compare(getresq[2],spkamp_range):
                        res_value["audio"]=["P",str(getresq[1])]
                        self.btn_audio.setStyleSheet("color:green")
                        self.lab_thd.setStyleSheet("color:green")
                        self.lab_amp.setStyleSheet("color:green")
                    else:
                        res_value["audio"]=["F","F"]
                        self.btn_audio.setStyleSheet("color:red")
                        self.lab_thd.setStyleSheet("color:red")
                        self.lab_amp.setStyleSheet("color:red")
                    self.res_thd.setText(str(getresq[1]))
                    self.res_amp.setText(str(getresq[2]))
                    self.enable_allbtn()
                except:
                    self.enable_allbtn()
                    res_value["audio"]=["F",""]
                    self.btn_spkthd.setStyleSheet("color:red")
                    traceback.print_exc()
                    with open('log.txt', 'a') as f:
                        f.write(traceback.format_exc())

            
            if getresq[0]=="usb2.0":
                try:
                    if getresq[1]==True:
                        res_value["usb2.0"]=["P","P"]
                        self.btn_usb2.setStyleSheet("color:green")
                    else:
                        res_value["usb2.0"]=["F","F"]
                        self.btn_usb2.setStyleSheet("color:red")
                    self.enable_allbtn()
                except:
                    self.enable_allbtn()
                    res_value["usb2.0"]=["F",""]
                    self.btn_usb2.setStyleSheet("color:red")
                    traceback.print_exc()
                    with open('log.txt', 'a') as f:
                        f.write(traceback.format_exc())

            if getresq[0]=="usb3.0":
                try:
                    if getresq[1]==True:
                        res_value["usb3.0"]=["P","P"]
                        self.btn_usb3.setStyleSheet("color:green")
                    else:
                        res_value["usb3.0"]=["F","F"]
                        self.btn_usb3.setStyleSheet("color:red")
                    self.enable_allbtn()
                except:
                    self.enable_allbtn()
                    res_value["usb3.0"]=["F",""]
                    self.btn_usb3.setStyleSheet("color:red")
                    traceback.print_exc()
                    with open('log.txt', 'a') as f:
                        f.write(traceback.format_exc())

            if getresq[0]=="iperfwifi":
                try:
                    if getresq[1]==True and compare(getresq[2],iperfwifi_range):
                        res_value["iperfwifi"]=["P",str(getresq[2])]
                        self.btn_iperfwifi.setStyleSheet("color:green")
                    else:
                        res_value["iperfwifi"]=["F","F"]
                        self.btn_iperfwifi.setStyleSheet("color:red")
                    self.res_iperfwifi.setText(str(getresq[2]))
                    self.enable_allbtn()
                except:
                    self.enable_allbtn()
                    res_value["iperfwifi"]=["F",""]
                    self.btn_iperfwifi.setStyleSheet("color:red")
                    traceback.print_exc()
                    with open('log.txt', 'a') as f:
                        f.write(traceback.format_exc())

            if getresq[0]=="uic":
                n=0
                try:
                    ssh_cmd(ssh_shell,"/etc/led.sh red",True)
                    time.sleep(0.5)
                    ssh_cmd(ssh_shell,"/etc/led.sh blue",True)
                    time.sleep(0.5)
                    ssh_cmd(ssh_shell,"/etc/led.sh amber",True)
                    time.sleep(0.5)
                    ssh_cmd(ssh_shell,"/etc/led.sh off",True)
                    LED=self.showMsg("question","LED","Is LED display 3 color?")
                    if LED:
                        res_value["LED"]=["P","P"]
                        self.lab_led.setStyleSheet("color:green")
                        n+=1
                    else:
                        res_value["LED"]=["F","F"]
                        self.lab_led.setStyleSheet("color:red")
                        
                    HDMI=self.showMsg("question","HDMI","Is HDMI display ELAN normally?")
                    if HDMI:
                        res_value["HDMI"]=["P","P"]
                        self.lab_hdmi.setStyleSheet("color:green")
                        n+=1
                    else:
                        res_value["HDMI"]=["F","F"]
                        self.lab_hdmi.setStyleSheet("color:red")
                        
                    RSTBTN=self.showMsg("question","Reset button","Please hold reset button for 3 seconds, and then to see if the LED blink? ")
                    if RSTBTN:
                        print("Reset button test pass")
                        res_value["reset"]=["P","P"]
                        self.lab_rstbtn.setStyleSheet("color:green")
                        n+=1
                    else:
                        print("Reset button test fail")
                        res_value["reset"]=["F","F"]
                        self.lab_rstbtn.setStyleSheet("color:red")

                    POWBTN=self.showMsg("question","Power button","Please hold power button until the LED power off! does the led power off? ")  
                    if POWBTN:     
                        print("Power button test pass")
                        res_value["power"]=["P","P"]
                        self.lab_powbtn.setStyleSheet("color:green")
                        n+=1
                    else:
                        print("Power button test fail")
                        res_value["power"]=["F","F"]
                        self.lab_powbtn.setStyleSheet("color:red")
                        
                    if n==4:
                        #res_value["uic"]=["P","P"]
                        self.btn_uic.setStyleSheet("color:green")
                        self.enable_allbtn()
                        self.btn_submit.setEnabled(True)
                    else:
                        #res_value["uic"]=["F","F"]
                        self.btn_uic.setStyleSheet("color:red")
                        self.enable_allbtn()

                    print(res_value)
                    resq.put(["auto",True])
                except:
                    self.enable_allbtn()
                    traceback.print_exc()
                    #res_value["uic"]=["F","F"]
                    self.btn_uic.setStyleSheet("color:red")
            
                
                        
def sn_template(_sn):
    zebra_template="""
^XA
^MMT
^PW850
^LL0307
^LS0
^BY3,3,149^FT128,171^BCN,,N,N
^FD>:%s>5%s>6%s>5%s^FS
^FT189,216^A0N,45,45^FH\^FD%s^FS
^PQ1,0,1,Y^XZ
"""%(_sn[0:3],_sn[3:7],_sn[7:8],_sn[8:],_sn)
    return zebra_template

def wifimac_template(_wifimac):
    _wifimac_temp=_wifimac.replace("-","")
    zebra_template="""
^XA
^MMT
^PW850
^LL0307
^LS0
^BY3,3,149^FT171,175^BCN,,N,N
^FD>:%s>5%s>6%s^FS
^FT171,219^A0N,44,36^FH\^FD%s WIFI^FS
^PQ1,0,1,Y^XZ
"""%(_wifimac_temp[0:1],_wifimac_temp[1:5],_wifimac_temp[5:],_wifimac)
    return zebra_template

def ethmac_template(_ethmac):
    _ethmac_temp=_ethmac.replace("-","")
    zebra_template="""
^XA
^MMT
^PW850
^LL0307
^LS0
^BY3,3,149^FT171,175^BCN,,N,N
^FD>:%s>5%s>6%s^FS
^FT170,220^A0N,45,45^FH\^FD%s^FS
^PQ1,0,1,Y^XZ
"""%(_ethmac_temp[0:1],_ethmac_temp[1:5],_ethmac_temp[5:],_ethmac)
    return zebra_template  



global res_value
#LOAD CONFIGURATION
config_path="finished.conf"
resq=queue.Queue()                       
res_value={}

serial_number_BBPPPPP=read_config(config_path,"serial_number_BBPPPPP")
serial_number_RR=read_config(config_path,"serial_number_RR")
serial_number_MM=read_config(config_path,"serial_number_MM")

_ir_port=read_config(config_path,"ir_port")
_switch_port=read_config(config_path,"switch_port")
ir_port,switch_port=find_port(_ir_port,_switch_port)

ser_ir=serial.Serial(ir_port,9600,timeout=0.1)
ser_switch=serial.Serial(switch_port,9600,timeout=0.1)
time.sleep(0.5)
switchto(ser_switch,status=0)
#ser_switch.write(b"\x8f")
ssh_user=read_config(config_path,"ssh_user")
ssh_passwd=read_config(config_path,"ssh_passwd")
ssh_portnum=read_config(config_path,"ssh_portnum")

ssid=read_config(config_path,"ssid5")
psd=read_config(config_path,"psw5")
channel=read_config(config_path,"channel5")

hostname=read_config(config_path,"hostname")
username=read_config(config_path,"username")
password=read_config(config_path,"password")
database=read_config(config_path,"database")
portnum=read_config(config_path,"portnum")
table=read_config(config_path,"table")

record_server_name=read_config(config_path,"record_server_name")
record_server_usr=read_config(config_path,"record_server_usr")
record_server_psd=read_config(config_path,"record_server_psd")
record_server_db=read_config(config_path,"record_server_db")
record_server_pn=read_config(config_path,"record_server_pn")
record_server_tb=read_config(config_path,"record_server_tb")

target_freq=read_config(config_path,"target_freq")
recordinput=read_config(config_path,"recordinput")

#LOAD CRITERIA
criteria_path="finished.cri"
freqwifi_range=read_cri(criteria_path,"freqwifi_range")
iperfwifi_range=read_cri(criteria_path,"iperfwifi_range")
relayvol_range=read_cri(criteria_path,"relayvol_range")
sensevol_range=read_cri(criteria_path,"sensevol_range")
spkthd_range=read_cri(criteria_path,"spkthd_range")
spkamp_range=read_cri(criteria_path,"spkamp_range")
bspversion=read_config(config_path,"bspversion")

z=zebra()
zlist=os.popen("lpinfo -v").read().split()
for n in range (0,len(zlist)):
    if "Zebra" in zlist[n]:
        os.system("lpadmin -p godex -v %s -m raw -o usb-unidir-default=true"%zlist[n])
        break

        
z.setqueue("godex")

'''
sn="2020070313320001"
imei1="01578-"
imei2="5000000017"
ltetype="A"
z.output(label_template(sn,imei1,imei2,ltetype))
'''

if __name__=='__main__':
    os.system("chmod +x *")
    gen_5gconf(ssid,ssid,psd,channel)
    os.system("systemctl stop hostapd;cp %s /etc/hostapd/hostapd.conf;systemctl start hostapd "%ssid)
    #sys.path.append(resource_path(os.getcwd()))
    app = QtWidgets.QApplication(sys.argv)
    myWin=mbox ()
    myWin.show()
    sys.exit(app.exec_())

