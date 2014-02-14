#! /usr/bin/env python
import urllib
import httplib
import sys
import os
import optparse
import time

def changePriorityWorkflow(url, workflow, priority, cert, key, retry):
    params = {workflow + ":status": "", workflow + ":priority": str(priority)}
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    for i in range(retry):
    	stats, data = send_message(url, cert, key, params, headers)
    	if stats==200:
	    break
        else:
            data = "Unable to change priority of workflow {0}, status code: {1}".format(workflow, stats)
   	time.sleep(1)
    print data

def send_message(url, cert, key, params, headers):
    conn = httplib.HTTPSConnection(url, cert_file=cert, key_file=key)
    encodedParams = urllib.urlencode(params)
    conn.request("PUT", "/reqmgr/view/doAdmin", encodedParams, headers)
    response = conn.getresponse()
    status, data = response.status, response.read()
    conn.close()
    return status, data

def prepare_parser():
    parser = optparse.OptionParser()
    parser.add_option('-u', '--url', help='Base url to send request to', dest='url',
                      default='cmsweb.cern.ch')
    parser.add_option('-c', '--cert', help='Cert file location', dest='cert',
                      default=os.getenv('X509_USER_PROXY'))
    parser.add_option('-k', '--key', help='Key file location', dest='key',
                      default=os.getenv('X509_USER_PROXY'))
    parser.add_option('-r', '--retry', help='Number of retries', dest='retry', default=2)
    return parser


def main():
    parser = prepare_parser()
    options, args = parser.parse_args()
    if len(args) < 2:
        print "usage: wmpriority.py <workflowname> <priority> [options]"
        sys.exit(1)
    workflow = args[0]
    priority = args[1]
    changePriorityWorkflow( options.url, workflow, priority, options.cert, options.key, options.retry)
    sys.exit(0)

if __name__ == "__main__":
    main()
