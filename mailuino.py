#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
	Mailuino AKA Comunikino<--->PC bridge
	Version: 0.2
	Copyright(c) 2011 Andrea Masi - www.eraclitux.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import serial, poplib, email, smtplib, time
from email.mime.text import MIMEText

############ Settings #################
#To avoid abuse, this is the only address allowed to communicate with Comunikino
TRUSTED_SENDER = "CHANGE ME"
#mailbox to send Comunikino's answers to
RECEIVER = "CHANGE ME"
#Comunikino's email address here (Gmail recommended)
USER = "CHANGE ME"      
#mailbox Password here
PASSWD	= "CHANGE ME"      
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
POP_SERVER = "pop.gmail.com"
#Arduino's port. Something like "COM3" for windows or "/dev/ttyUSB0" for linux
USB_PORT = "/dev/ttyUSB0"
#seconds between each mailbox check
POP_CHECK_INTERVALL = 60 
#seconds before sending next subject to Arduino
TIME_BETWEEN_SUBJ = 5
########################################

def connect_to_pop():
	""" Mail Account Setup """
	connection = poplib.POP3_SSL(POP_SERVER)
	connection.user(USER)
	connection.pass_(PASSWD)			
	return connection

def send_mail(subj, body):
	msg = MIMEText(body)
	msg['subject'] = subj
	msg['From'] = "Comunikino <"+USER+">"
	msg['To'] = RECEIVER
	try:
		smtpobj = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)	
		smtpobj.set_debuglevel(False)
		smtpobj.ehlo()
		smtpobj.starttls()
		smtpobj.ehlo()
		smtpobj.login(USER, PASSWD) 
		smtpobj.sendmail(USER, RECEIVER, msg.as_string())	
		print "<-- [Success "+time.strftime("%H:%M:%S", time.localtime())+"] sent "+subj+" "+body
		smtpobj.quit()
	except smtplib.SMTPException:
		print "<-- [Error]: unable to send "+subj

def retrieve_subject(mailobj, i):
	"""Retrive object of last received mail"""
	stringa = ''
	#this is a tuple
	msg = mailobj.retr(i)
 	#this is an array :-P
	message = msg[1]
	for part in message:
		stringa += part + "\n"
	messaggio = email.message_from_string(stringa)
	#or messaggio['From'] etc etc
	return messaggio['Subject']

def retrieve_sender(mailobj, i):
	"""Retrive Sender of last received mail"""
	stringa = ''
	msg = mailobj.retr(i)	
	message = msg[1] 		
	for part in message:
		stringa += part + "\n"
	messaggio = email.message_from_string(stringa) 
	#print messaggio['From'] #debugg
	sender = messaggio['From'].partition('<')
	sender = sender[2].rstrip('>')
	#debugg
	#print sender 
	return sender

def new_mails(mailobj):
	"""Return number of unreded mails"""
	if (mailobj.stat()[0] != 0): 
		return mailobj.stat()[0] 
	return 0

def fetch_mail_subjects(mailobj):
	"""Return an array with mails' subjects """
	subjects = [""]
	nummails = new_mails(mailobj)
	if (nummails > 0):
		for i in range(1, nummails+1):
			if (retrieve_sender(mailobj, i) == TRUSTED_SENDER): 
				subjects.append( retrieve_subject(mailobj, i) )
				#print retrieve_sender(mailobj,i)#debugg
	#remove "" 
	subjects.pop(0)
	return subjects

def send_subj_to_arduino(subjects, conn):
	"""Send subjects to arduino"""
	#We could have troubles here, only the last subject will be printed on Comunikino's screen at the end
	for sub in subjects:
		print "--> [Received "+time.strftime("%H:%M:%S", time.localtime())+"]: "+sub
		# '#' char is used between subjects
		conn.write(sub + "#")
		#eih! let Arduino breathe!
		time.sleep(TIME_BETWEEN_SUBJ)

def manage_arduino_answ():
	answ = usbconn.readline()
	if (answ=="Y\n"):
		send_mail("[Comunikino's Answer]", "Yes")
		usbconn.flushInput()
		return
	elif (answ=="N\n"):
		send_mail("[Comunikino's Answer]", "No")
		usbconn.flushInput()
		return
	elif (answ=="B\n"):
		send_mail("[Comunikino's Answer]", "HeartBeat")
		usbconn.flushInput()
		return

def mainloop():
	while True:
		try:
			popconnection = connect_to_pop()
			send_subj_to_arduino(fetch_mail_subjects(popconnection), usbconn)
			manage_arduino_answ()
			popconnection.quit()
			time.sleep(POP_CHECK_INTERVALL)
		except KeyboardInterrupt:
			usbconn.close()
			exit()
		
############### Initialization ############################		
USB_ERROR_MESSAGE = "\
################ !!!	  Usb Error       !!! ################\n\
## 		      Is Arduino plugged in?		    ##\n\
##############################################################"
try:
	#Create a connection with Arduino board
	usbconn = serial.Serial(USB_PORT, timeout=1)
	time.sleep(3)
except serial.SerialException:
	#Close mailuino if Arduino is not connected
	raw_input(USB_ERROR_MESSAGE)
	exit()
#When mailuino is started give a heartbeat
send_mail("[Comunikino is on line!]", "Heartbeat.")

if __name__ == '__main__':
	mainloop()
