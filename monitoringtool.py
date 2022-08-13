import time
import smtplib
import smtpdata
from ping3 import ping


def mailservice():
    user = smtpdata.usr		                    #username saved in smtpdata.py
    pwd = smtpdata.pwd		                    #password saved in smtpdata.py
    mail_text = f"{ip} is {status}!"
    subject = "Alert from Python-Ping-Monitoring"

    MAIL_FROM = smtpdata.mailadr                #mailaddress saved in smtpdata.py
    RCPT_TO = smtpdata.toadr                    #recipient mailaddress saved in smtpdata.py
    DATA = "From:%s\nTo:%s\nSubject:%s\n\n%s" % (MAIL_FROM, RCPT_TO, subject, mail_text)
    
    server = smtplib.SMTP(smtpdata.smtpserver,smtpdata.smtpport)    #smtp server and port saved in smtpdata.py
    server.starttls()
    server.login(user, pwd)
    server.sendmail(MAIL_FROM, RCPT_TO,DATA)
    server.quit()


def pingscript():
    global response
    global status
    response = ping(ip)
    if response == False:
        #print(f"{ip} is down!")
        status = "down"
    else:
        #print(f"{ip} is up!")
        status = "up"


def readcache():                                #scan for ip in cachefile
    with open("cache") as f:
        global incache
        if ip in f.read():
            incache = True
        else:
            incache = False
    file.close()


def writecache():                               #write ip to cachefile
    file = open("cache", "a")
    print(file.write(f"\n{ip}"))
    file.close()
 
    
def clearcache():                               #clean ip from cachefile
    with open("cache", "r") as f:
        lines = f.readlines()
    with open("cache", "w") as f:
        for line in lines:
            if line.strip("\n") != ip:
                f.write(line)


with open("hostlist") as file:        
    hostlist = file.read()
    hostlist = hostlist.splitlines()

print(f"start scanning hosts: {hostlist}\n")


timer = 3600                                    

while(True):
    for ip in hostlist:
        pingscript()
        time.sleep(1)
        if(response == False):
            readcache()
            print(f"\n{ip} is down!")
            if(incache == False):
                writecache()                            
                mailservice()
                print(f"\n{ip} is down!\nsent email!\n")
                timer = 300
        
        elif(response != False):
            readcache()
            if(incache == True):
                clearcache()  
                print(f"\n{ip} is up!\nsent email!\n")                          
                mailservice()
                timer = 3600
    time.sleep(timer)