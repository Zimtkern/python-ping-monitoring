# attention: please adjust the smtpdata.py and hostlistfile before executing

from logging.handlers import TimedRotatingFileHandler
import os
import time
import smtplib
import smtpdata


def mailservice(ip, hostname, status):
    user = smtpdata.usr          # username saved in smtpdata.py
    pwd = smtpdata.pwd           # password saved in smtpdata.py
    hostname = hostname if hostname else "Unknown Host"
    mail_text = f"{hostname} ({ip}) is {status}!"
    subject = "Alert from Python-Ping-Monitoring"

    mailfrom = smtpdata.mailadr  # mailaddress saved in smtpdata.py
    mailto = smtpdata.toadr      # recipient mailaddress saved in smtpdata.py
    mailcontent = f"From: {mailfrom}\nTo: {mailto}\nSubject: {subject}\n\n{mail_text}"

    try:
        server = smtplib.SMTP(smtpdata.smtpserver, smtpdata.smtpport)  # smtp server and port saved in smtpdata.py
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(user, pwd)
        server.sendmail(mailfrom, mailto, mailcontent)
        server.quit()
        print(f"Email sent successfully: {mail_text}")
    except Exception as e:
        print(f"Failed to send email: {e}")


def pingscript(ip):
    received = os.system(f"ping -c 4 {ip} > /dev/null")
    if received == 0:
        status = "up"
    else:
        status = "down"
    return received, status


def readcache(ip):                                # scan for ip in cachefile
    with open("cache") as file:
        incache = ip in file.read()
    return incache


def writecache(ip):                               # write ip to cachefile
    with open("cache", "a") as file:
        file.write(f"\n{ip}")


def clearcache(ip):                               # clean ip from cachefile
    with open("cache", "r") as file:
        lines = file.readlines()
    with open("cache", "w") as file:
        for line in lines:
            if line.strip("\n") != ip:
                file.write(line)


def preparelist():                                # delete empty line from cachefile and hostlistfile
    lists = ["hostlist", "cache"]
    for list in lists:
        output = ""
        with open(list) as file:
            for line in file:
                if not line.isspace():
                    output += line
        with open(list, "w") as file:
            file.write(output)


def readhostlist():
    hostlist = []
    with open("hostlist") as file:
        for line in file:
            parts = line.split()
            if len(parts) > 0:
                ip = parts[0]
                hostname = parts[1] if len(parts) > 1 else None
                hostlist.append((ip, hostname))
    return hostlist


hostlist = readhostlist()
print(f"start scanning hosts: {hostlist}\n")

tup = 1200   # timer for host status up
tdown = 120  # timer for host status down

timer = tup

while True:
    hostlist = readhostlist()
    for ip, hostname in hostlist:
        preparelist()
        received, status = pingscript(ip)
        if received != 0:
            incache = readcache(ip)
            print(f"\n{ip} ({hostname if hostname else 'Unknown Host'}) is down!")
            if not incache:
                writecache(ip)
                mailservice(ip, hostname, status)
                time.sleep(1)
                print("sent email!")
                timer = tdown

        elif received == 0:
            incache = readcache(ip)
            if incache:
                clearcache(ip)
                print(f"\n{ip} ({hostname if hostname else 'Unknown Host'}) is up!\nsent email!")
                mailservice(ip, hostname, status)
                time.sleep(1)
                timer = tup
                for ip, hostname in hostlist:
                    incache = readcache(ip)
                    if incache:
                        timer = tdown
    time.sleep(timer)
