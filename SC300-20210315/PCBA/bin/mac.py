import pymysql
import traceback

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


hostname="172.20.3.177"
username="nscrd"
password="DNwwa8H"
portnum=3306
database="tcptestdata"
table="nsc_server"
record_server_tb="ELAN_SC300"
sn_num="EL01491X189210306666"

print(fetch_data(database,hostname,username,password,portnum,record_server_tb,"SNID",sn_num,target="ethmac"))

#mac_num=elan_get_mac_addr(hostname,username,password,portnum,database,table)


