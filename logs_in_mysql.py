#!/usr/bin/python
# -*- coding: utf-8
import re
import string
import MySQLdb
import time
from datetime import datetime
from itertools import ifilter
from email.message import Message
from email.header import Header
from email.header import decode_header
import sys

sys.setrecursionlimit(10000)
blacklist = ['username@example.com']

def unpack_line(line):
        result = re.match(ur'(\w\w\w\s+\d+\s\d\d:\d\d:\d\d)\s.+\: ([\w\d]{10})\:.+header ([^\>]*).*\sfrom=<([^\>]*)>.*\sto=<([^\>]+)>',line)
        date = result.group(1)
	msgid = result.group(2)
        subj = result.group(3)
        mfrom = result.group(4)
        mto = result.group(5)
        year = datetime.strftime(datetime.now(), "%Y")
        date = year+" " + date
        date = time.strptime(date,"%Y %b %d %H:%M:%S")
        date = time.strftime("%Y-%m-%d %H:%M:%S", date)
	if mfrom not in blacklist:
                return date, msgid, subj, mfrom, mto

def split_header(fullline):
	result = re.sub(ur'\?=.+?=\?','?=\n=?',fullline)
	result = result.split("\n")
	header = Header()
	for line in result:
		header.append(line)
	default_charset = 'ASCII'
	dh = decode_header(header)
	try: 
	    line_decoded = ''.join([ unicode(t[0], t[1] or default_charset) for t in dh ]);
	    return line_decoded
	except BaseException:
		return fullline
	
db = MySQLdb.connect(host="localhost", user="mailman", passwd="password", db="databases", charset='utf8')
cursor = db.cursor()

f = open('/var/log/mail.log','r')
for line in f:
        if 'warning: header Subject:' in line:
                varible = unpack_line(line)
                if varible != (None):
                        date, msgid, subj, mfrom, mto = unpack_line(line)
			sub = re.match(r'Subject: (.+) from ',subj)
			if sub != (None):
				v = split_header(sub.group(1))
				v_filtered = re.sub(ur'[^А-Яа-яёЁ\x00-\x7f]','', v) 
				sql = "INSERT INTO user_mail(date, msgid, subj, mfrom, mto) VALUE (%s, %s, %s, %s, %s)"
				print msgid
				cursor.execute(sql,(date, msgid, v_filtered, mfrom, mto))
db.commit()
db.close()
f.close()
