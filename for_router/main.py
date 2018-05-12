# -*- coding: utf-8 -*- 
#main script

import os
import poplib
import email
import string
import sys
import re
import cgi
import quopri
import time
import datetime
from datetime import date
from storm.locals import *

'''
sqlite tables
'''
class Cost(object):
    def __init__(self, store):
        try:
            store.execute("CREATE TABLE cost "
                          "(id INTEGER PRIMARY KEY, spend_date VARCHAR, added_date VARCHAR, value INTEGER, type VARCHAR)")
        except:
            pass
    
    __storm_table__ = "cost"
    id = Int(primary=True)    
    spend_date = DateTime()
    added_date = DateTime()    
    value = Int()
    type = Unicode()
    
class Product(object):
    def __init__(self, store):
        try:
            store.execute("CREATE TABLE product "
                          "(id INTEGER PRIMARY KEY, name VARCHAR UNIQUE)")
        except:
            pass
    
    __storm_table__ = "product"
    id = Int(primary=True)
    name = Unicode()

'''
parser vNote files from email
'''
class vNoteParser():
    def __init__(self, messages, save_path):
        self.line_pattern = re.compile('([A-Z-]+);?([^:]*):(.*)') # e.g. BODY;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:some note
        self.original_messages = messages
        self.parsed_messages = []
        self.save_path = save_path
    
    def parse_file(self, attachment):
        values = {}
        metadata = {}
        prevline = None
        for line in attachment:
            # merge quoted-printable soft newlines e.g.
            # BEGIN:VCARD
            # BODY;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:=12=34=
            # =56
            # END:VCARD
            if line == '':
                continue
            
            if prevline:
                line = prevline + line
            prevline = None
    
            # parse vcard properties
            parts = self.line_pattern.findall(line.strip())
            if len(parts) == 0:
                print ("unable to parse line: " + line)
                return None,None
            else:
                parts = parts[0]
            key = parts[0]
            if len(parts) == 2:
                values[key] = parts[1]
            elif len(parts) == 3:
                values[key] = parts[2]
                propdict = metadata.setdefault(key, {})
                for prop in parts[1].split(';'):
                    if len(prop) > 0:
                        k, v = prop.split('=')
                        propdict[k] = v
    
                if propdict.get('ENCODING') == 'QUOTED-PRINTABLE' and values[key].endswith('='):
                    prevline = line.rstrip()[:-1] # reparse
    
            else:
                print ("unable to parse line: " + line)
                return None,None
    
        return values, metadata
    
    def process_file(self, attachment):
        values, metadata = self.parse_file(attachment)
    
        # TODO: more integrity checking of the file
        if values is None:
            return None, None
        elif values['BEGIN'] != 'VNOTE' or values['END'] != 'VNOTE' or values['VERSION'] != '1.1':
            return None, "is not a valid vNote 1.1 file"
        else:
            body = values['BODY']
            if metadata['BODY'].get('ENCODING') == 'QUOTED-PRINTABLE':
    
                # add end-of-line
                if len(body) > 0 and body[-1] != '\n':
                    body += '\r\n'
    
                # decode quoted-printable
                if sys.hexversion >= 0x030000F0:
                    body = body.encode('utf8')
                body = quopri.decodestring(body, header=False)
    
            return body, None
    
    def parse(self):    
        errors = False
    
        for message in self.original_messages:
            for attachment in message['attachment']:    
                body, error = self.process_file(attachment['content'])
                if body is None:
                    errors = True
                    if error is None:
                        sys.stdout.write("error\n")
                    else:
                        sys.stdout.write(error + "\n")
                else:
                    self.parsed_messages.append(body)
                    
        self.parsed_messages = string.join(self.parsed_messages, "").split("\n")
        del(self.parsed_messages[len(self.parsed_messages)-1])
    
    def save(self):                   
        fp = open(os.path.join(self.save_path, 'parsed.txt'), 'wb')
        fp.write(string.join(self.parsed_messages, "\n"))
        fp.close()  

'''
download all messages from email box and get attached vnt files
'''
class vNoteDownloader():
    def __init__(self, mail_server, user, password, save_path):
        self.messages = []
        self.mail_server = mail_server
        self.user = user
        self.password = password
        self.save_path = save_path

    def check_mail(self):
        M = poplib.POP3(self.mail_server)
        M.user(self.user)
        M.pass_(self.password)
        
        numMessages = len(M.list()[1])
        
        for i in range(numMessages):
            msg = M.retr(i+1)
            str = string.join(msg[1], "\n")
            mail = email.message_from_string(str)
            
            one_message = {
                            'from': mail["From"],
                            'subject': mail["Subject"],
                            'date': mail["Date"],  
                            'attachment': [],     
                           }
            
            if mail.is_multipart():
                one_message['payload'] = mail.get_payload(0).get_payload()
            else:
                one_message['payload'] = mail.get_payload()           
                
            for part in mail.walk():
                one_message['content_type'] = part.get_content_type()
                            
                if part.get_content_maintype() == 'multipart' and part.get('Content-Disposition') is None:
                    continue
                
                filename = part.get_filename()
                if filename:
                    one_message['attachment'].append({'name': filename,
                                                      'content': part.get_payload(decode=1).split('\r\n'),})
            
            self.messages.append(one_message)                                 
        M.quit()
        
        return self.messages
    
    def save(self):
        for message in self.messages:
            for attachment in message['attachment']:            
                fp = open(os.path.join(self.save_path, attachment['name']), 'wb')
                fp.write(string.join(attachment['content'], "\r\n"))
                fp.close()         

class costManager():
    month_dict = {
             u'янв': 1,
             u'фев': 2,
             u'мар': 3,
             u'апр': 4,
             u'май': 5,
             u'июнь': 6,
             u'июль': 7,
             u'авг': 8,
             u'сен': 9,
             u'окт': 10,
             u'ноя': 11,
             u'дек': 12,
             }
    
    def __init__(self, db, cost_list):
        self.cost_list = cost_list
        self.cost_list_by_fields = []
        database = create_database("sqlite:"+db)
        self.store = Store(database)    
    
    def costs_by_fields(self):
        today = date.today()
        
        for one_cost in self.cost_list:
            month = int(self.month_dict[one_cost.split(' ')[1].decode('utf-8')])  
            day = int(one_cost.split(' ')[0])
            splited_cost = {
                            'date': datetime.datetime(today.year, month, day),
                            'type': one_cost.split(' ')[2],
                            'value': one_cost.split(' ')[3],
                            'products': one_cost.split(' ')[4:]
                            }
            
            self.cost_list_by_fields.append(splited_cost)

    def saveCosts(self):
        for one_cost in self.cost_list_by_fields:
            cost = Cost(self.store)
            cost.spend_date = one_cost['date']
            cost.added_date = datetime.datetime.now()
            cost.value = int(one_cost['value'])
            cost.type = one_cost['type'].decode('utf-8')
            for one_product in one_cost['products']:
                product = Product(self.store)
                product.name = one_product.decode('utf-8')
                self.store.add(product)
            self.store.add(cost)
        
        self.store.flush()
        self.store.commit()
        
vnt_loader = vNoteDownloader('pop.mail.ru', 'XXX', 'XXX', '/home/XXX')
vnt_loader.check_mail()
#vnt_loader.save()

vnt_parser = vNoteParser(vnt_loader.messages, '/home/XXX')
vnt_parser.parse()
vnt_parser.save()

cost = costManager('/home/XXX/workspace/scripts/for_router/home_accounting/db/accounting.sqlite', vnt_parser.parsed_messages)
cost.costs_by_fields()
cost.saveCosts()

print datetime.datetime.now()

fs = cgi.FieldStorage()

for key in fs.keys():
    print "%s = %s" % (key, fs[key].value)
