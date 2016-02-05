#! /usr/bin/env python
import optparse
import os
from modules import wma

def prepare_parser():
    parser = optparse.OptionParser()
    parser.add_option('-u', '--user', help='Username', dest='user',
                      default=os.environ['WMCONTROL_USER'] if os.environ.has_key('WMCONTROL_USER') else '')
    parser.add_option('-g', '--group', help='User group', dest='group',
                      default=os.environ['WMCONTROL_GROUP'] if os.environ.has_key('WMCONTROL_GROUP') else '')
    parser.add_option('-l', '--label', help='Label and description of config', dest='label',
                      default='Uploaded through wmupload')
    parser.add_option('--wmtest', help='To inject requests to the cmsweb test bed', action='store_true' ,
                      dest='wmtest', default=False)
    parser.add_option('--wmtesturl', help='To inject to a specific testbed', dest='wmtesturl',
                      default='cmsweb-testbed.cern.ch')
    return parser

def main():
    parser = prepare_parser()
    options, args = parser.parse_args()
    if options.wmtest:
        print "Setting to injection in cmswebtest : ", options.wmtesturl
        wma.testbed(options.wmtesturl)
    for cfg_name in args:
        wma.upload_to_couch(cfg_name, options.label, options.user, options.group)

if __name__ == "__main__":
    main()
