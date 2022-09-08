#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
    Watch qBittorrent bt tasks using qbittorrent-api, 
    move all task files to other places defined in config file if bt task seeded up.

- input: none
- config: ./move_files_after_qb_seeded_up.yaml
- output: ./all.log, ./error.log
- requirements:
    - pip install pyyaml, schedule, qbittorrent-api, colorama

@File     :  move_files_after_qb_seeded_up.py
@Time     :  2022/09/08 22
@Author   :  Attt
@Version  :  1.0
@Contact  :  https://github.com/Attt
@Lincense : (c)Copyright 2022-2024, attt
@Desc     : None
'''
import schedule
import time
import qbittorrentapi
import shutil
import yaml
import os
import colorama
import logging
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

    def __init__(self,filename,level='info',fmt='%(asctime)s - %(pathname)s [:%(lineno)d] - %(levelname)s: %(message)s'):
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
host='localhost'
port=8080
username='admin'
password='adminadmin'
target_path="C:\\Users\\Administrator\\Downloads\\TargetDir"
interval=30

# read from config file
with open("move_files_after_qb_seeded_up.yaml","r") as f:
    config=yaml.load(f.read(),Loader=yaml.Loader)
    host = config["client"]["host"]
    port = config["client"]["port"]
    username = config["client"]["user"]
    password = config["client"]["passwd"]
    target_path = config["qb"]["target_path"]
    interval = config["interval"]
    print(f'\033[1;37;41m[**Warning**]\033[0mconfigs read from file:')
    print(f'\t - host:\t\033[1;37;41m{host}\033[0m')
    print(f'\t - port:\t\033[1;37;41m{port}\033[0m')
    print(f'\t - username:\t\033[1;37;41m{username}\033[0m')
    print(f'\t - password:\t\033[1;37;41m{password}\033[0m')
    print(f'\t - target path:\t\033[1;37;41m{target_path}\033[0m')
    print(f'\t - interval:\t\033[1;37;41m{interval}\033[0m')

print('instantiate qb client')
# instantiate a Client using the appropriate WebUI configuration
qbt_client = qbittorrentapi.Client(
    host=host,
    port=port,
    username=username,
    password=password,
)

def connectToQbClient():
    # the Client will automatically acquire/maintain a logged-in state
    # in line with any request. therefore, this is not strictly necessary;
    # however, you may want to test the provided login credentials.
    try:
        print('auth qb client')
        qbt_client.auth_log_in()
    except qbittorrentapi.LoginFailed as e:
        print(e)

def printQbClientInfo():
     # display qBittorrent info
    print(f'\tqBittorrent: {qbt_client.app.version}')
    print(f'\tqBittorrent Web API: {qbt_client.app.web_api_version}')
    print()
    for k,v in qbt_client.app.build_info.items(): print(f'\t >>>> {k}: {v}')

## connect and print client info
connectToQbClient()
printQbClientInfo()

# job function
def moveSeededFiles():
    try:
        connectToQbClient()

        # retrieve and show all torrents
        for torrent in qbt_client.torrents_info():
            _debug.logger.info(f'{torrent.hash[-6:]} info: \n\t |- name {torrent.name}\n\t |- state {torrent.state}\n')
            print(f'\033[7;30;47m{torrent.hash[-6:]}\033[0m info: \n\t |- \033[1;33;40m name {torrent.name}\033[0m\n\t |- \033[1;33;40m state {torrent.state}\033[0m\n')
            if torrent.state == 'pausedUP' :
                ## path
                _from = os.path.join(torrent.save_path, torrent.name)
                _to = os.path.join(target_path, torrent.hash[-6:] + '_' + torrent.name)

                _debug.logger.info(f'move tor {torrent.hash} files \n\t >- from {_from}\n\t >- to {_to}')
                print(f'move tor \033[7;30;47m{torrent.hash}\033[0m files \n\t >- from \033[1;32;40m {_from}\033[0m\n\t >- to \033[1;32;40m {_to}\033[0m\n\n')
                
                # copy first then delete to keep the original files safe
                if os.path.isdir(_from):
                    shutil.copytree(_from, _to)
                else:
                    shutil.copy2(_from, _to)
                
                torrent.delete(True) # delete torrent and files
                # shutil.rmtree(torrent.save_path) # call qb client delete api instead
    except Exception as e:
        print(e)
        _err.logger.error(f'\033[1;37;41m[error occurred due to {e}\033[0m')


schedule.every(interval).minutes.do(moveSeededFiles) # run scheduled job every ${interval} mins

while True:
    schedule.run_pending()   # run all jobs
    time.sleep(1)
