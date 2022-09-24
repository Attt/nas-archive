#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
    Get IPv6 address and update DNSPod AAAA record scheduledly, 
    send mails if record is updated or something went wrong. 

- input: none
- config: ./ddnspodv6.yaml
- output: ./all.log, ./error.log, ./v6.address
- requirements: true

@File     :  ddnspodv6.py
@Time     :  2022/09/24 17
@Author   :  Attt
@Version  :  1.0
@Contact  :  https://github.com/Attt
@Lincense : (c)Copyright 2022-2024, attt
@Desc     : None
'''
import requests
import schedule
import time
import yaml
import os
import colorama
import logging
import json
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from logging import handlers

# define logger 
class Logger(object):
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    } # map logging level

    def __init__(self,filename,level='info',fmt='%(asctime)s - [:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        self.logger.setLevel(self.level_relations.get(level)) # set log level
        
        fileHandler = handlers.TimedRotatingFileHandler(filename=filename, when='D', backupCount=4 ,encoding='utf-8') 
        fileHandler.setFormatter(logging.Formatter(fmt)) # set log format
        self.logger.addHandler(fileHandler) # set log handler

# init logger and error logger
_debug = Logger('all.log',level='debug')
_err = Logger('error.log', level='error')

colorama.init(autoreset=True)

# pre-define
dnspod_ddns_api = ''
dnspod_record_api = ''
dnspod_token = '12331,333333333333333333444aaa'
domain = 'abc.com.cn'
sub_domain = 'www'
ua = 'Chrome blabla version(111.222.0)'
prefix_to_check = '2409'
mail_smtp = 'smtp.xxx.com'
mail_smtp_port = 445
mail_user = 'aa'
mail_pass = 'bb'
mail_to_address = 'xxx@xxx.com'
mail_sender_is_starttls = False
v6_test_url = ['https://6.ipw.cn']

v6_address = ''

# read from config file
with open("ddnspodv6.yaml","r") as f:
    config=yaml.load(f.read(),Loader=yaml.Loader)
    dnspod_ddns_api = config["dnspod"]["ddns_api"]
    dnspod_record_api = config["dnspod"]["record_api"]
    dnspod_token = config["dnspod"]["token"]
    domain = config["domain"]
    sub_domain = config["sub_domain"]
    prefix_to_check = config['prefix_to_check']
    interval = config["interval"]
    ua = config["user_agent"]
    mail_smtp = config['mail']['smtp_server']
    mail_smtp_port = config['mail']['smtp_port']
    mail_user = config['mail']['user']
    mail_pass = config['mail']['pass']
    mail_to_address = config['mail']['to_address']
    mail_sender_is_starttls = config['mail']['is_starttls']
    v6_test_url = config['v6_test_url']
    print(f'\033[1;37;41m[**Warning**]\033[0mconfigs read from file:')
    print(f'\t - dnspod ddns api:\t\033[1;37;41m{dnspod_ddns_api}\033[0m')
    print(f'\t - dnspod record api:\t\033[1;37;41m{dnspod_record_api}\033[0m')
    print(f'\t - dnspod token:\t\033[1;37;41m{dnspod_token}\033[0m')
    print(f'\t - domain:\t\033[1;37;41m{domain}\033[0m')
    print(f'\t - sub domain:\t\033[1;37;41m{sub_domain}\033[0m')
    print(f'\t - prefix to check:\t\033[1;37;41m{prefix_to_check}\033[0m')
    print(f'\t - interval:\t\033[1;37;41m{interval}\033[0m')
    print(f'\t - user agent:\t\033[1;37;41m{ua}\033[0m')
    print(f'\t - mail smtp:\t\033[1;37;41m{mail_smtp}\033[0m')
    print(f'\t - mail smtp port:\t\033[1;37;41m{mail_smtp_port}\033[0m')
    print(f'\t - mail user:\t\033[1;37;41m{mail_user}\033[0m')
    print(f'\t - mail pass:\t\033[1;37;41m{mail_pass}\033[0m')
    print(f'\t - mail to address:\t\033[1;37;41m{mail_to_address}\033[0m')
    print(f'\t - mail sender is starttls:\t\033[1;37;41m{mail_sender_is_starttls}\033[0m')
    print(f'\t - v6 test url:\t\033[1;37;41m{v6_test_url}\033[0m')
    f.close()

def sendMail(title, content):
    '''
    :param message: str
    :param Subject: str
    :param sender_show: str
    :param recipient_show: str
    :param to_addrs: str
    :param cc_show: str
    '''
    # content
    msg = MIMEText(content, 'html', _charset="utf-8")
    # subject
    msg["Subject"] = title
    # sender
    msg["from"] = 'Attt DDNSPodV6' ## useless value
    # receiver
    msg["to"] = mail_to_address
    
    
    smtp = smtplib.SMTP(mail_smtp ,mail_smtp_port)
    # smtp.set_debuglevel(1)
    if mail_sender_is_starttls :
        smtp.starttls()
    # log in smtp server
    smtp.login(user = mail_user, password = mail_pass)
    # send mail
    smtp.sendmail(from_addr = mail_user, to_addrs=mail_to_address, msg=msg.as_string())
    smtp.quit()

# send mail if ddns api is down
def sendEmergencyMail(address, apiFailMessage):
    title = '[WARNING] V6 addresss updated but DNSPod API is down'
    content = f'New V6: </br><font style="font-weight:bold;font-size:24px;color:orange;">{address}</font></br>Fail due to: </br><font style="font-weight:bold;font-style:italic;color:red;">{apiFailMessage}</font></br>'
    sendMail(title, content)


def sendAddressChangeMail(address, before):
    title = '[INFO] V6 addresss updated successfully thru DNSPod API'
    content = f'New V6: </br><font style="font-weight:bold;font-size:24px;color:green;">{address}</font></br>Changed from: </br><font style="font-weight:bold;font-style:italic;color:orange;">{before}</font></br>'
    sendMail(title, content)

# test
# sendEmergencyMail("fe80:adc1::1", "too frequency api call")
# sendAddressChangeMail("2409:aaaa:bbb:ccc:ddd:fff:eeee:1111", "2409:aaaa:bbb:ccc::8ff0:9a1f:e4c3")

#sendEmergencyMail('fe80::1', "it's just a final test")

# def mockGetWanV6():
#     return 'fe80::1'

def getWanV6():
    for test_url in v6_test_url:
        x = requests.get(test_url)
        newV6_address = x.text
        if newV6_address.startswith(prefix_to_check):
            return newV6_address
    sendEmergencyMail('unknown', 'all v6 test url is false')
    # newV6_address = mockGetWanV6()
    return newV6_address

def getLatestAddress():
    if not os.path.exists('v6.address'):
        open('v6.address', 'w').close()
        return
    with open("v6.address",mode='r') as dat:
        global v6_address
        v6_address = ''
        for line in dat.readlines():
            line = line.strip()
            if line.__len__ != 0:
                v6_address = line
                print(f'latest address read from file is \033[7;30;47m{v6_address}\033[0m\n')
                _debug.logger.info(f'latest address read from file is {v6_address}')
        dat.close()

getLatestAddress() # init v6_address from file

def persistAddress(address):
    if address.__len__ != 0:
        with open("v6.address",mode='w') as dat:
            dat.writelines(address + '\n')
            dat.close()

# job function
def updateDNSPod():
    try:
        global v6_address
        ## get wan v6 thru test url
        newV6_address = getWanV6()

        ## if v6 addresss is legal (according to prefix_to_check in config file)
        if not newV6_address.startswith(prefix_to_check):
            print(f'xxxxxx \t wan v6 address is ILLEGAL!!!: \033[1;37;41m{newV6_address}\033[0m\n')
            print('\033[1;37;41mskipped due to address illegal\033[0m\n')
            _debug.logger.info(f'xxxxxx \t wan v6 address is ILLEGAL!!!: {newV6_address}')
            _debug.logger.info('skipped due to address illegal')
            return
        else:
            print(f'>>>>>> \t wan v6 address is: \033[7;30;47m{newV6_address}\033[0m\n')
            _debug.logger.info(f'>>>>>> \t wan v6 address is: {newV6_address}')


        ## nothing changed
        if newV6_address == v6_address:
            print('------ \t \033[1;37;41mskipped due to address not changed\033[0m\n')
            _debug.logger.info('------ \t skipped due to address not changed')
        else:
            ## update dns AAAA record
            ## fetch record list api first to get record_id and record_line_id and present AAAA value
            request = requests.Session()

            payload = {'login_token':dnspod_token, 'domain':domain, 'sub_domain': sub_domain}
            # headers = {'User-Agent': ua} it's dnspod bug that use U-A could get 403 Forbidden response
            result = request.post(dnspod_record_api, data = payload)
            resultObj = json.loads(result.text)

            ## check if api response is OK
            if resultObj['status']['code'] != '1':
                message = resultObj['status']['message']

                ## send emergency mail
                sendEmergencyMail(newV6_address, message)
                print(f'xxxxxx \t failed to request record api!!!: \033[1;37;41m{message}\033[0m\n')
                print(f'\033[1;37;41mskipped due to record request failed {message}\033[0m\n')
                _debug.logger.info(f'xxxxxx \t failed to request record api!!!: {message}')
                _debug.logger.info(f'skipped due to record request failed {message}')
                return

            ## get record id and record_line_id and value
            record_id = '-1'
            record_line_id = '0'
            dns_value = ''
            for rec in resultObj['records']:
                if rec['name'] == sub_domain:
                    record_id = rec['id']
                    record_line_id = rec['line_id']
                    dns_value = rec['value']
                    break

            ## check if dns record value is not changed since last update
            if dns_value == newV6_address:
                print(f'<<<<<< \t dns value is already set to \033[1;37;41m{dns_value}\033[0m\n')
                print('\033[1;37;41mskipped due to dns value is already set\033[0m\n')
                _debug.logger.info(f'<<<<<< \t dns value is already set to {dns_value}')
                _debug.logger.info('skipped due to dns value is already set')
                ## persist the latest v6 address
                persistAddress(dns_value)
                ## update local var
                v6_address = dns_value
                return
            
            ## check record_id is correctly fetched
            if record_id == '-1':
                ## send emergency mail
                sendEmergencyMail(newV6_address, 'can not parse record_id from ddns api body!!')
                print(f'xxxxxx \t record id is is ILLEGAL!!!: \033[1;37;41m{record_id}\033[0m\n')
                print('\033[1;37;41mskipped due to record id illegal\033[0m\n')
                _debug.logger.info(f'xxxxxx \t record id is is ILLEGAL!!!: {record_id}')
                _debug.logger.info('skipped due to record id illegal')
                return

            print(f'>>>>>> \t dns record id is {record_id} and record line id is {record_line_id}\n')
            _debug.logger.info(f'>>>>>> \t dns record id is {record_id} and record line id is {record_line_id}')

            ## now to update dns record value
            payload = {'login_token':dnspod_token, 'format':'json', 'domain':domain, 'sub_domain':sub_domain, 'record_id': record_id,'record_line_id':record_line_id, 'value': newV6_address}
            result = request.post(dnspod_ddns_api, data = payload)
            resultObj = json.loads(result.text)

            ## check if api response is OK
            if resultObj['status']['code'] != '1':
                message = resultObj['status']['message']
                ## send emergency mail
                sendEmergencyMail(newV6_address, message)
                print(f'xxxxxx \t failed to request ddns api!!!: \033[1;37;41m{message}\033[0m\n')
                print(f'\033[1;37;41mskipped due to ddns request failed {message}\033[0m\n')
                _debug.logger.info(f'xxxxxx \t failed to request ddns api!!!: {message}')
                _debug.logger.info(f'skipped due to ddns request failed {message}')
                return
           
            print(f'>>>>>> \t dns record updated with \033[7;30;47m{newV6_address}\033[0m\n')
            _debug.logger.info(f'>>>>>> \t dns record updated with {newV6_address}')

            ## send address changed email
            sendAddressChangeMail(newV6_address, v6_address)

            v6_address = newV6_address

            ## persist the latest v6 address
            persistAddress(v6_address)
        
    except Exception as e:
        print(e)
        _err.logger.error(f'\033[1;37;41m[error occurred due to {e}\033[0m')


schedule.every(interval).minutes.do(updateDNSPod) # run scheduled job every ${interval} mins
# schedule.every(interval).seconds.do(updateDNSPod) # too frequency only for test

while True:
    schedule.run_pending()   # run all jobs
    time.sleep(1)