#!/usr/bin/env python

import json
import argparse
import requests
import sys
import time
import datetime

parser = argparse.ArgumentParser(description='Script checks analytics of lst day')
parser.add_argument('-s', '--sheme', help='sheme', required=True)
parser.add_argument('-a', '--host', help='host', required=True)
parser.add_argument('-t', '--token', help='host', required=True)
parser.add_argument('-r', '--regions', nargs='+', help='host', required=True)
args = parser.parse_args()

headers = { 'User-Agent' : 'OpsView analytics checker',
                        'Mountbit-Auth': args.token }

necessary_metrics = [
                     '<platform>.<region>.account.active.<period>.storage.files.average.day',
                     '<platform>.<region>.account.storage.files.average.day',
                     '<platform>.<region>.account.active.<period>.storage.used.average.day',
                     '<platform>.<region>.account.storage.used.average.day',
                     '<platform>.<region>.<device>.accounts.count.sum.day',
                     '<platform>.<region>.account.active.<period>.count.last.day',
                     '<platform>.<region>.cloudike.api.requests.user.average.day',
                     '<platform>.<region>.filetype.<data_type>.size.last.day',
                     '<platform>.<region>.filetype.<data_type>.count.last.day',
                     '<platform>.<region>.account.storage.segmentation.<storage_segment>.count.day',
                     '<platform>.<region>.account.count.last.day',
                     '<platform>.<region>.<device>.files.added.count.sum.day',
                     '<platform>.<region>.<device>.filesops.deleted.count.sum.day',
                     '<platform>.<region>.account.deleted.sum.day',
                     '<platform>.<region>.account.registered.sum.day',
                     '<platform>.<region>.storage.files.total.last.day',
                     '<platform>.<region>.storage.size.used.last.day',
                     '<platform>.<region>.account.traffic.<direction>.count.last.day',
                     '<platform>.<region>.account.traffic.<direction>.average.<period>.last.day',
                     ]

necessary_regions = ['all', 'uf', 'cf', 'dvf', 'kf', 'stf', 'sf', 'szf', 'pf']

def get_metric_names():
    create_folder = '/api/1/analytics/get_metrics/'
    r = requests.post('%s://%s%s' % (args.sheme, args.host, create_folder), headers=headers)
    return json.loads(r.content)

def get_metric_data(metric, date_from, date_to):
    create_folder = '/api/1/analytics/get_data/'
    data = {'metric': metric,
                    'date_from': int(time.mktime(date_from.timetuple())),
                    'date_to': int(time.mktime(date_to.timetuple()))
                    }

    r = requests.post('%s://%s%s' % (args.sheme, args.host, create_folder), data=data, headers=headers)
    metric_data = json.loads(r.content)
    return metric_data


def main():
    date_to = datetime.datetime.utcnow()
    date_to = date_to.replace(hour=0, minute=0, second=0, microsecond=0)
    date_from = date_to - datetime.timedelta(days=10)
    
    stat = {'checked_metrics': 0,
                  'ignored_metrics' : 0,
                  'succeeded_metrics' : 0,
                  'failed_metrics': 0}
    failed_metrics = []

    try:
        for metric_name, params in get_metric_names().iteritems():
            template_name = params.get('template_name', '')
            if (template_name in necessary_metrics) and (metric_name.split('.')[1] in args.regions):
                metric_data = get_metric_data(metric_name, date_from, date_to)
                if metric_data:
                    metric_data = sorted(metric_data, key=lambda k: k['time'], reverse=True)
                    metric_time = datetime.datetime.fromtimestamp(metric_data[0]['time'])
                    metric_time = metric_time.replace(hour=0, minute=0, second=0, microsecond=0)
                    if metric_time == date_to - datetime.timedelta(days=1):
                        stat['succeeded_metrics'] += 1
                    else:
                        stat['failed_metrics'] += 1
                        failed_metrics.append({'metric_name': metric_name, 'last_calculated_time': metric_time})
                    stat['checked_metrics'] += 1
            else:
                stat['ignored_metrics'] += 1
    except Exception as e:
        print "CRITICAL: %s" % e
        sys.exit(2)

    return stat, failed_metrics

if __name__ == '__main__':
    stat, failed_metrics = main()
    if stat['succeeded_metrics'] == stat['checked_metrics'] and not failed_metrics:
        print "OK: All good"
        sys.exit(0)
    else:
        print stat, failed_metrics
        sys.exit(2)
