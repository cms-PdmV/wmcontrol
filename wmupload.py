#! /usr/bin/env python
from __future__ import print_function
import optparse
import os
from modules import wma

def prepare_parser():
    parser = optparse.OptionParser()
    parser.add_option('-u', '--user', help='Username', dest='user',
                      default=os.environ['WMCONTROL_USER'] if 'WMCONTROL_USER' in os.environ else '')
    parser.add_option('-g', '--group', help='User group', dest='group',
                      default=os.environ['WMCONTROL_GROUP'] if 'WMCONTROL_GROUP' in os.environ else '')
    parser.add_option('-l', '--label', help='Label and description of config', dest='label',
                      default='Uploaded through wmupload')
    parser.add_option('--wmtest', help='To inject requests to the cmsweb test bed', action='store_true' ,
                      dest='wmtest', default=False)
    parser.add_option('--wmtesturl', help='To inject to a specific testbed', dest='wmtesturl',
                      default='cmsweb-testbed.cern.ch')
    parser.add_option('--create-tweak',
                      help='Instead of performing the submission directly, tweak the parameters and just save them as JSON',
                      dest='create_tweak',
                      default=False,
                      action='store_true')
    parser.add_option('--from-tweak',
                      help='Submit the configuration to the ReqMgr2 cache loading tweaked parameters from a JSON file, instead of loading the module',
                      dest='from_tweak',
                      default=False,
                      action='store_true')
    return parser

def main():
    parser = prepare_parser()
    options, args = parser.parse_args()

    if options.create_tweak and options.from_tweak:
        raise RuntimeError('--create-tweak and --from-tweak are mutually exclusive options. Select only one of them')
    if options.wmtest:
        print("Setting to injection in cmswebtest : ", options.wmtesturl)
        wma.testbed(options.wmtesturl)

    for cfg_name in args:
        if options.create_tweak:
            wma.tweaks_to_file(cfg_name)
        else:
            tweaks = wma.from_tweaks_file(cfg_name) if options.from_tweak else {}
            wma.upload_to_couch(cfg_name, options.label, options.user, options.group, tweaks=tweaks)

if __name__ == "__main__":
    main()
