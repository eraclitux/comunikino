# -*- coding: utf-8 -*-
"""
	Mailuino AKA Comunikino<--->PC bridge, Windows version
	Version: 0.1
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


############ Settings ######################
trustedsender = "CHANGE ME"      # to avoid abuse, this is the only address allowed to communicate with Comunikino
receiver      = "CHANGE ME"      # mailbox to send Comunikino's answers
user          = "CHANGE ME"      # Comunikino's email address here (Gmail highly recommended!)
passwd        = "CHANGE ME"      # your Password here
smtpServer    = "smtp.gmail.com" # smtp server
smtpPort      = 587              # smtp port
popServer     = "pop.gmail.com"  # pop server
usbport       = "COM3"           # Arduino's COM port
popchecktime  = 5                # seconds between each mailbox check
timebetwsubj  = 15               # seconds before sending next subject to Arduino
########################################

def connectToMail():
	""" Mail Account Setup """
	connection = poplib.POP3_SSL(popServer)
	connection.user(user)
	connection.pass_(passwd)			
	return connection

def sendMail(Subj,Body):
        msg = MIMEText(Body)
        msg['Subject'] = Subj
        msg['From'] = "Comunikino <"+user+">"
        msg['To'] = receiver
        try:
                smtpObj = smtplib.SMTP(smtpServer, smtpPort)	
                smtpObj.set_debuglevel(False)
                smtpObj.ehlo()
                smtpObj.starttls()
                smtpObj.ehlo()
                smtpObj.login(user,passwd) 
                smtpObj.sendmail(user, receiver, msg.as_string())        
                print "<-- [Success "+ time.strftime("%H:%M:%S", time.localtime()) +"] sent "+Subj+" "+Body
                smtpObj.quit()
        except smtplib.SMTPException:
                print "<-- [Error]: unable to send "+Subj

def retrieveSubject(mailobj, i):
	"""Retrive object of last received mail"""
	stringa = ''
	msg=mailobj.retr(i)			#this is a tuple
	message=msg[1] 				#this is an array :-P
	for part in message:
		stringa += part + "\n"
	messaggio = email.message_from_string(stringa)
	return messaggio['Subject']		# or messaggio['From'] etc etc

def retrieveSender(mailobj, i):
	"""Retrive Sender of last received mail"""
	stringa = ''
	msg=mailobj.retr(i)	
	message=msg[1] 		
	for part in message:
		stringa += part + "\n"
	messaggio = email.message_from_string(stringa) 
	#print messaggio['From'] #debugg
	sender =   messaggio['From'].partition('<')
	sender = sender[2].rstrip('>')
	#print sender #debugg
	return sender

def newMails(mailobj):
	"""Return number of unreded mails"""
	if (mailobj.stat()[0] != 0): 
		return mailobj.stat()[0] 
	return 0

def fetchMailssubjects(mailobj):
	"""Return an array with mails' subjects """
	subjects=[""]
	nummails= newMails(mailobj)
	if (nummails > 0):
		for i in range(1,nummails+1):
			if (retrieveSender(mailobj,i) == trustedsender): 
				subjects.append( retrieveSubject(mailobj,i) )
				#print retrieveSender(mailobj,i)#debugg
	subjects.pop(0)			#remove "" 
	return subjects

def sendSubjToArduino(subjects,serial):
	"""Send subjects to arduino"""
	#We could have troubles here, only the last subject will be printed on Comunikino's screen at the end
	for sub in subjects:
		print "--> [Received "+time.strftime("%H:%M:%S", time.localtime())+"]: " + sub
		serial.write(sub + "#")			# the '#' char is used between subjects
		time.sleep(timebetwsubj)		#eih! let Arduino breathe!

def manageAnswfromArduino():
	""""""
	answ=usbconn.readline()
	if (answ=="Y\n"):
		sendMail("[Comunikino's Answer]","Yes")
		usbconn.flushInput()
		return
	elif (answ=="N\n"):
		sendMail("[Comunikino's Answer]","No")
		usbconn.flushInput()
		return
	elif (answ=="B\n"):
		sendMail("[Comunikino's Answer]","HeartBeat")
		usbconn.flushInput()
		return

def mainloop():
	while True:
		try:
			popconnection = connectToMail()
			sendSubjToArduino(fetchMailssubjects(popconnection),usbconn)
			manageAnswfromArduino()
			popconnection.quit()                   #Close connection with pop server
			time.sleep(popchecktime)
		except KeyboardInterrupt:
			usbconn.close()
			exit()
		
############### Initialization ###################################		
usb_error_message="\
################ !!!          Usb Error       !!! ################\n\
## 	              Is Arduino plugged in?                    ##\n\
##################################################################"
try:
	usbconn = serial.Serial(usbport, timeout=1) # Create a connection with Arduino board
	time.sleep(3)
except serial.SerialException:
	raw_input(usb_error_message)
	exit()                                      # Close mailuino if Arduino is not connected
sendMail("[Comunikino is on line!]","Heartbeat.")   # When mailuino is started give a lifesign

if __name__ == '__main__':
	mainloop()
