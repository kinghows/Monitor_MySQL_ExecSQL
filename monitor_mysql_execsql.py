#!/usr/local/bin/python
# coding: utf-8

# Monitor MySQL SQL V1.0.0
# Monitor MySQL SQL execute
# Copyright (C) 2019-2019 Kinghow - Kinghow@hotmail.com
# Git repository available at https://github.com/kinghows/MySQL_Watcher

import MySQLdb
import configparser
import getopt
import sys
import re
import time
import os
import subprocess
from warnings import filterwarnings

filterwarnings('ignore', category = MySQLdb.Warning)

filter_str = ''
logpath = os.getcwd() + '/mysql.log'

def monitor():
    command = 'tail -f ' + logpath
    popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    try:
        while True:
            line = popen.stdout.readline().strip()
            encodeStr = bytes.decode(line)
            pattern = re.findall(r'Query\s*(.*)', encodeStr, re.S)
            if len(pattern) != 0:
                selectStr = pattern[0]
                STR1 = re.findall(r'SET\s*(.*)', selectStr, re.S)
                STR2 = re.findall(r'SHOW\s*(.*)', selectStr, re.S)
                STR3 = re.findall(r'COMMIT\s*(.*)', selectStr, re.S)
                STR4 = re.findall(r'EXPLAIN\s*(.*)', selectStr, re.S)
                STR5 = re.findall(r'\b' + 'information_schema' + r'\w*', selectStr, re.S)
                STR6 = re.findall(r'show\s*(.*)', selectStr, re.S)
                if len(STR1)+len(STR2)+len(STR3)+len(STR4)+len(STR5)+len(STR6) == 0:
                    if filter_str != "":
                        reg = re.findall(r'\w*' + filter_str + r'\w*', encodeStr, re.S)
                        if len(reg) != 0:
                            joinTime = time.strftime("%H:%M:%S", time.localtime()) + '    '
                            print(joinTime + '   ' + selectStr)
                    else:
                        joinTime = time.strftime("%H:%M:%S", time.localtime()) + '    '
                        print(joinTime + '   ' + selectStr)

    except KeyboardInterrupt:
        os.remove(logpath)
		
def f_set_log(dbinfo):
    try:
        conn = MySQLdb.connect(host=dbinfo[0],user=dbinfo[1],passwd=dbinfo[2],db=dbinfo[3],port=int(dbinfo[4]))
        cur = conn.cursor()
        cur.execute('set global general_log = on')
        conn.commit()
        currentPath = 'set global log_output = \'file\''
        cur.execute(currentPath)
        conn.commit()
        cur.execute('set global general_log_file=' + '\'' + logpath + '\'')
        conn.commit()
        conn.close()		
    except MySQLdb.Error as e:
        print("Error %d: %s" % (e.args[0], e.args[1]))
        sys.exit(1)

if __name__ == '__main__':
    dbinfo=["127.0.0.1","root","root","mysql",3306] #host,user,passwd,db,port
    config_file="dbset.ini"
    option = []
	
    opts, args = getopt.getopt(sys.argv[1:], "p:")
    for o,v in opts:
        if o == "-p":
            config_file = v

    config = configparser.ConfigParser()
    config.read(config_file)
    dbinfo[0] = config.get("database","host")
    dbinfo[1] = config.get("database","user")
    dbinfo[2] = config.get("database","passwd")
    dbinfo[3] = config.get("database","db")
    dbinfo[4] = config.get("database", "port")

    f_set_log(dbinfo)
    filter_str = config.get("option","filter_str")
    time.sleep(2)
    monitor()
