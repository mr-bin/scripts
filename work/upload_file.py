#!/usr/bin/python2

import sys
sys.path[0:0] = ['/home/mr_bin/.buildout/python-eggs/requests-2.5.0-py2.7.egg',]
import json
import requests
import random
now = random.randint(1,100)
print now
create_file = 'http://127.0.0.1:45000/api/1/files/create/'
data = {'path' : '/folder_1/temp_file_%s.txt' % now}
files = {'file': ('ws.py', open('/home/mr_bin/workspace/test/ws.py', 'rb'))}
res = requests.post(create_file, data=data, headers={'Mountbit-Auth':  '7679c3b63d884ee889f6b147b2f25b69'})
print 0
create_data = json.loads(res.content)
print 1
requests.post(create_data['url'], data=create_data['headers'], files=files, allow_redirects=False)
print 2
requests.post(create_data['confirm_url'], headers={'Mountbit-Auth':  '7679c3b63d884ee889f6b147b2f25b69'})
print 3

