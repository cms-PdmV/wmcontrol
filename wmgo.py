#! /usr/bin/env python
import urllib
import httplib
import sys
import os
import optparse
import time
import random
from modules import wma
import json

def get_status(workflow, url, cert, key):
    conn = httplib.HTTPSConnection(url, cert_file=cert, key_file=key)
    conn.request("GET", "/reqmgr/reqMgr/request?requestName="+workflow, )#headers)
    response = conn.getresponse()
    status, data = response.status, response.read()
    conn.close()
    return status, data

def prepare_parser():
    parser = optparse.OptionParser()
    parser.add_option('-u', '--url', help='Base url to send request to', dest='url',
                      default=wma.WMAGENT_URL)#'cmsweb.cern.ch')
    parser.add_option('-c', '--cert', help='Cert file location', dest='cert',
                      default=os.getenv('X509_USER_PROXY'))
    parser.add_option('-k', '--key', help='Key file location', dest='key',
                      default=os.getenv('X509_USER_PROXY'))
    parser.add_option('-r', '--retry', help='Number of retries', dest='retry', default=2)
    return parser

def main():
    parser = prepare_parser()
    options, args = parser.parse_args()
    if len(args) < 1:
        print "usage: wmgo.py workflow1 workflow2 [options]"
        sys.exit(1)
    workflows = args

    for wf in workflows:
        hstatus, data = get_status( wf, options.url, options.cert, options.key )
        try:
            status = json.loads(data)['RequestStatus']
        except:
            print "cannot get status for",wf
            sys.exit(-1)

        if status != 'new':
            print "Status of",wf,"is",status,"NOT in new"
            continue
        timeout=options.retry
        ok=False
        while timeout>0:
            print "Trying",wf
            ## should check whether the request is already in status assignment-approved
            try:
                wma.approveRequest(option.url, wf)
                ok=True
            except:
                time.sleep( 0.05 )
                print timeout,"remaining tries"
            timeout-=1

        if not ok:
            sys.exit(-1)
            
    sys.exit(0)

if __name__ == "__main__":
    main()
