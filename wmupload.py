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
    return parser

def main():
    parser = prepare_parser()
    options, args = parser.parse_args()
    for cfg_name in args:
        wma.upload_to_couch(cfg_name, options.label, options.user, options.group)

if __name__ == "__main__":
    main()