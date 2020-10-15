import sys, pdb, os, base64, time, datetime, locale, traceback, curses
import urllib.request, urllib.parse, urllib.error, configparser
from threading import Thread
from os.path import basename
from huawei_lte_api.Client import Client
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
from huawei_lte_api.Connection import Connection
import pymysql

#initialize database
host = "localhost"
user = "root"
password = ""
db = "huawei-router"
routerPassword = '123456789'

#get device information
def DeviceInfo(_devicename, _serial_number, _imei, _imsi, _hardver, _softver, _macaddr1, _uptime, _kode_toko):
	device_name = _devicename
	serial_number = _serial_number
	imei = _imei
	imsi = _imsi
	hardver = _hardver
	softver = _softver
	macaddr1 = _macaddr1
	uptime = _uptime
	kode_toko = _kode_toko #assign to place, you can delete this
  
  #create database object
	con = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
	cur = con.cursor()

  #get serial number of huawei router
	cur.execute("SELECT * FROM DeviceInfo WHERE serial_number =%s", (serial_number))

	result = cur.fetchone()

  #if device found then update device information
	if result:
		print("Device existed")
		cur.execute("UPDATE DeviceInfo SET soft_version = %s, mac_addr = %s, uptime = %s, kodeToko = %s WHERE serial_number = %s", (softver, macaddr1, uptime, kode_toko, serial_number))
		con.commit()
	else:
    #if not then add as new device
		cur.execute("INSERT INTO DeviceInfo(device_name, serial_number, imei, imsi, hard_version, soft_version, mac_addr, uptime, kodeToko) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (device_name, serial_number, imei, imsi, hardver, softver, macaddr1, uptime, kode_toko))
		con.commit()

#get signal information
def SignalInfo(_wan_ip, _wan_dns, _support_mode, _work_mode, _rsrp, _rsrq, _sinr, _plmn, _cell_id, _serial_number):
	wan_ip = _wan_ip
	wan_dns = _wan_dns
	support_mode = _support_mode
	work_mode = _work_mode
	rsrp = _rsrp
	rsrq = _rsrq
	sinr = _sinr
	plmn = _plmn
	cell_id = _cell_id
	serial_number = _serial_number
	lastupdate = datetime.datetime.now()

	con = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
	cur = con.cursor()

	cur.execute("SELECT * FROM DeviceInfo WHERE serial_number =%s", (serial_number))

	result = cur.fetchone()
  
  #if device found then insert signal information
	if result:
		cur.execute("INSERT INTO SignalInfo(wan_ip, wan_dns, support_mode, work_mode, rsrp, rsrq, sinr, plmn, cell_id, serial_number, lastUpdate) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (wan_ip, wan_dns, support_mode, work_mode, rsrp, rsrq, sinr, plmn, cell_id, serial_number, lastupdate))
		con.commit()
	else:
		print("Device not found")

#add statistic about data usage
def NetStatistic(_download_rate, _upload_rate, _total_download, _total_upload, _data_usage, _serial_number):
	download_rate = _download_rate
	upload_rate = _upload_rate
	totaldownload = _total_download
	totalupload = _total_upload
	datausage = _data_usage
	serial_number = _serial_number
	lastupdate = datetime.datetime.now()

	con = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
	cur = con.cursor()

	cur.execute("SELECT * FROM DeviceInfo WHERE serial_number =%s", (serial_number))

	result = cur.fetchone()

	if result:
		cur.execute("INSERT INTO NetStatistic(download_rate, upload_rate, download_stat, upload_stat, data_usage, serial_number, lastUpdate) VALUES(%s, %s, %s, %s, %s, %s, %s)", (download_rate, upload_rate, totaldownload, totalupload, datausage, serial_number, lastupdate))
		con.commit()
	else:
		print("Device not found")

#main function
def main():
	#read CONFIG.INI file then use it as parameter
	config = configparser.ConfigParser()
	config.read('CONFIG.INI')
	kodeToko = config.get('toko', 'kode_toko')
	routerIP = config.get('router', 'router_ip')

	locale.setlocale(locale.LC_ALL, 'en_ID.utf8')

	# Service
	bandIn = "stat"
	if bandIn == "stat" :
		band = -1 # Monitoring only, no band set
	elif bandIn == "manual" :
		band = -2 
		lteband = "80000" # Manual choice
	else :
		bandTab = (bandIn.replace("+", " ")).split()
		band = 0
		for bandt in bandTab :
			if bandt == "700" :
				exp = int(bandsList[11][0].replace('b', ''))
			elif bandt == "800" :
				exp = int(bandsList[9][0].replace('b', '')) 
			elif bandt == "900" :
				exp = int(bandsList[7][0].replace('b', '')) 
			elif bandt == "1800" :
				exp = int(bandsList[2][0].replace('b', '')) 
			elif bandt == "2100" :
				exp = int(bandsList[0][0].replace('b', ''))
			elif bandt == "2300" :
				exp = int(bandsList[14][0].replace('b', ''))
			elif bandt == "2600" :
				exp = int(bandsList[6][0].replace('b', '')) 
			else :
				rep = "KO"
				print("Unknown frequency")
				print("Usage : " + basename(sys.argv[0]) + " " + usage)
				exit()	
			band = band + 2**(exp-1)
		lteband =str(hex(band)).replace("0x", "")
	
	try :
		connection = AuthorizedConnection('http://admin:'+routerPassword+'@'+routerIP+'/')
		client = Client(connection) # This just simplifies access to separate API groups, you can use device = Device(connection) if you want
		networkband = "3FFFFFFF"
		networkmode = "03"
		if band != -1 :
			client.net.set_net_mode(lteband, networkband, networkmode) 

		last_update = time.strftime('%d %B %Y - %H:%M:%S',time.localtime())

		devinfo = client.device.information()
		device_name = devinfo["DeviceName"]
		serial_number = devinfo["SerialNumber"]
		imei = devinfo["Imei"]
		imsi = devinfo["Imsi"]
		hardver = devinfo["HardwareVersion"]
		softver = devinfo["SoftwareVersion"]
		macaddr1 = devinfo["MacAddress1"]
		uptime = devinfo["uptime"]
		kode_toko = kodeToko
		DeviceInfo(_devicename = device_name, _serial_number = serial_number, _imei = imei, _imsi = imsi, _hardver = hardver, _softver = softver, _macaddr1 = macaddr1, _uptime = uptime, _kode_toko = kode_toko)

		sig = client.device.signal()
		wan_ip = devinfo["WanIPAddress"]
		wan_dns = devinfo["wan_dns_address"]
		support_mode = devinfo["supportmode"]
		work_mode = devinfo["workmode"]
		rsrp = sig["rsrp"]
		rsrq = sig['rsrq']
		sinr = sig['sinr']
		plmn = sig['plmn']
		cell_id = sig['cell_id']
		SignalInfo(_wan_ip = wan_ip, _wan_dns = wan_dns, _support_mode = support_mode, _work_mode = work_mode, _rsrp = rsrp, _rsrq = rsrq, _sinr = sinr, _plmn = plmn, _cell_id = cell_id, _serial_number = serial_number)
		
		traff = client.monitoring.traffic_statistics()
		downloadrate_ = str(int(traff["CurrentDownloadRate"])/(1024*1024))
		totaldownload_ = str(int(traff["TotalDownload"])/(1024*1024))
		uploadrate_ = str(int(traff["CurrentUploadRate"])/(1024*1024))
		totalupload_ = str(int(traff["TotalUpload"])/(1024*1024))
		datausage_ = str((int(traff["TotalDownload"])+int(traff["TotalUpload"]))/(1024*1024))

		NetStatistic(_download_rate = downloadrate_, _upload_rate = uploadrate_, _total_download = totaldownload_, _total_upload = totalupload_, _data_usage = datausage_, _serial_number = serial_number)

	except Exception as e :
		print("Connection error - " + str(e))
		exit()

main()
