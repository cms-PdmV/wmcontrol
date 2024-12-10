#!/usr/bin/env python3
from __future__ import print_function
try:
    import httplib
except ImportError:
    import http.client as httplib

import sys
import os
import optparse
import time
import json


def change_priority(url, workflow, priority, cert, key, retry):
    data = {'RequestPriority': priority}
    headers = {'Content-type': 'application/json',
               'Accept': 'application/json'}

    for _ in range(retry):
        conn = httplib.HTTPSConnection(url, cert_file=cert, key_file=key)
        conn.request('PUT', '/reqmgr2/data/request/%s' % workflow, json.dumps(data), headers)
        response = conn.getresponse()
        status, res = response.status, response.read()
        conn.close()
        if status == 200:
            return json.loads(res).get('result', [])[0].get(workflow, '').lower() == 'ok'

        print('Status: %s, response: %s' % (status, res))
        time.sleep(1)

    return False


def main():
    parser = optparse.OptionParser()
    parser.add_option('-u', '--url',
                      help='Base url to send request to',
                      dest='url',
                      default='cmsweb.cern.ch')
    parser.add_option('-c', '--cert',
                      help='Cert file location',
                      dest='cert',
                      default=os.getenv('X509_USER_PROXY'))
    parser.add_option('-k', '--key',
                      help='Key file location',
                      dest='key',
                      default=os.getenv('X509_USER_PROXY'))
    parser.add_option('-r', '--retry',
                      help='Number of retries',
                      dest='retry',
                      default=1)
    options, args = parser.parse_args()
    if len(args) < 2:
        print('usage: wmpriority.py <workflowname> <priority> [options]')
        sys.exit(1)

    workflow = args[0]
    priority = int(args[1])
    res = change_priority(options.url, workflow, priority, options.cert, options.key, options.retry)
    print('%s: %s' % (workflow, res))

if __name__ == "__main__":
    main()
