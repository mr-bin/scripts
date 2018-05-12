#!/usr/bin/env python

import json
import argparse
import websocket
import requests
import sys
import time


parser = argparse.ArgumentParser(description='Script creates and deletes test folder, than it checks websockets content')
parser.add_argument('-s', '--sheme', help='sheme', required=True)
parser.add_argument('-a', '--host', help='host', required=True)
parser.add_argument('-t', '--token', nargs='+', help='host', required=True)
args = parser.parse_args()


def create_file(now, headers):
    create_file = '/api/1/files/create/'
    data = {'path' : '/OpsView_websockets_checker_%s/temp_file_%s.txt' % (now, now)}
    files = {'file': (__file__, open(__file__, 'rb'))}

    create_data = json.loads(requests.post('%s://%s%s' % (args.sheme, args.host, create_file), data=data, headers=headers).content)
    requests.post(create_data['url'], data=create_data['headers'], files=files, allow_redirects=False)
    requests.post(create_data['confirm_url'], headers=headers)


def delete_folder(now, headers):
    remove_folder = '/api/1/fileops/delete/'
    data = {'path' : '/OpsView_websockets_checker_%s' % now, 'without_trash': True}

    requests.post('%s://%s%s' % (args.sheme, args.host, remove_folder), data=data, headers=headers)

def check_api_events(now, headers):
    events = '/api/1/events/'
    events = json.loads(requests.post('%s://%s%s' % (args.sheme, args.host, events), data={'limit' : 3}, headers=headers).content)

    event_types = [one['type'] for one in events]
    if event_types != ['folder_deleted', 'file_created', 'folder_created']:
        raise Exception('api events did not match. %s' % [(one['type'], one['timestamp']) for one in events])
    return events[2]['timestamp'] - 5000

def check_ws_events(ts, now, headers, token):
    ws = websocket.create_connection("ws://%s/subscribe/?token=%s&timestamp=%s" % (args.host, token, ts))
    events = json.loads(ws.recv())
    events = json.loads(ws.recv())

    event_types = [events[-1]['type'], events[-2]['type'], events[-3]['type']]
    if event_types != ['folder_deleted', 'file_created', 'folder_created']:
        raise Exception('ws events did not match. %s' % [(one['type'], one['timestamp']) for one in events])
    ws.close()


def main():
    some_thing_went_wrong = False
    for token in args.token:
        headers = { 'User-Agent' : 'OpsView websockets checker',
                                'Mountbit-Auth':  token}

        try:
            now = time.time()
            print 'start for token %s, at %s' % (token, now)
            create_file(now, headers)
            delete_folder(now, headers)
            ts = check_api_events(now, headers)
            check_ws_events(ts, now, headers, token)
            print 'end for token %s, duration %s' % (token, time.time() - now)
        except Exception as e:
            print "CRITICAL: exception description: %s" % e
            some_thing_went_wrong = True

    if some_thing_went_wrong:
        sys.exit(2)

if __name__ == '__main__':
    main()

    print "OK: All good"
    sys.exit(0)
