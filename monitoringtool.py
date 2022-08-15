#attention: please adjust the smtpdata.py and hostlistfile before executing

from logging.handlers import TimedRotatingFileHandler
import os
import time
import smtplib
import smtpdata


def mailservice():
    user = smtpdata.usr		                                                                    #username saved in smtpdata.py
    pwd = smtpdata.pwd		                                                                    #password saved in smtpdata.py
    mail_text = f"{ip} is {status}!"
    subject = "Alert from Python-Ping-Monitoring"

    mailfrom = smtpdata.mailadr                                                                 #mailaddress saved in smtpdata.py
    mailto = smtpdata.toadr                                                                     #recipient mailaddress saved in smtpdata.py
    mailcontent = "From:%s\nTo:%s\nSubject:%s\n\n%s" % (mailfrom, mailto, subject, mail_text)

    server = smtplib.SMTP(smtpdata.smtpserver,smtpdata.smtpport)                                #smtp server and port saved in smtpdata.py
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(user, pwd)
    server.sendmail(mailfrom, mailto, mailcontent)
    server.quit()


def pingscript():
    global received
    global status
    received = os.system(f"ping -c 4 {ip} > /dev/null")
    if received == 0:
        #print(f"{ip} is up!")
        status = "up"
    else:
        #print(f"{ip} is down!")
        status = "down"


def readcache():                                #scan for ip in cachefile
    with open("cache") as file:
        global incache
        global timecache
        if ip in file.read():
            incache = True
        else:
            incache = False
    file.close()


def writecache():                               #write ip to cachefile
    file = open("cache", "a")
    print(file.write(f"\n{ip}"))
    file.close()


def clearcache():                               #clean ip from cachefile
    with open("cache", "r") as file:
        lines = file.readlines()
    with open("cache", "w") as file:
        for line in lines:
            if line.strip("\n") != ip:
                file.write(line)


def preparelist():                              #delete empty line from cachefile and hostlistfile
    lists = ["hostlist", "cache"]
    for list in lists:
        output = ""
        with open(list) as file:
            for line in file:
                if not line.isspace():
                    output+=line
        file= open(list,"w")
        file.write(output)


def readhostlist():
    global hostlist
    with open("hostlist") as file:
        hostlist = file.read()
        hostlist = hostlist.splitlines()

readhostlist()
print(f"start scanning hosts: {hostlist}\n")


tup = 1200                                      #timer for host status up
tdown = 120                                     #timer for host status down

timer = tup

while(True):
    readhostlist()
    for ip in hostlist:
        preparelist()
        pingscript()
        if(received != 0):
            readcache()
            print(f"\n{ip} is down!")
            if(incache == False):
                writecache()
                mailservice()
                time.sleep(1)
                print("sent email!")
                timer = tdown

        elif(received == 0):
            readcache()
            if(incache == True):
                clearcache()
                print(f"\n{ip} is up!\nsent email!")
                mailservice()
                time.sleep(1)
                timer = tup
                for ip in hostlist:
                    readcache()
                    if(incache == True):
                        timer = tdown
    time.sleep(timer)