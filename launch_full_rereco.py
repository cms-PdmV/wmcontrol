#! /usr/bin/env python

from __future__ import print_function
import sys
import os
import optparse
import pprint

try:
    from ConfigParser import SafeConfigParser
except ImportError:
    from configparser import SafeConfigParser

sys.path.append(os.path.join(sys.path[0], 'modules'))
from full_rereco import *

#-------------------------------------------------------------------------------

def build_parser():
    #global request_upload

    usage = "Run with\n"
    usage += "%prog --reprocfg myinicfg.ini --prepare_configs\n"
    usage += "%prog --reprocfg myinicfg.ini --upload\n"
    usage += "%prog --reprocfg myinicfg.ini --request\n"
    parser = optparse.OptionParser(usage)
    parser.add_option("--upload",default=False,action='store_true',
                    help="use this option to upload the configurations to couchDB")
    parser.add_option("--request",default=False,action='store_true',
                    help="use this option to actually send the request to the request-manager web interface")
    parser.add_option("--lastRun",default=-1)
    parser.add_option("--firstRun",default=-1)

    # new options
    parser.add_option("--reprocfg",default=None,
                    help="Specify the reprocessing configfile")
    parser.add_option("--prepare_configs",default=False,action='store_true',
                    help="Prepare all the configurations")
    parser.add_option("--test",default=False,action='store_true',
                    help="Do a dry run")

    options, args = parser.parse_args()
    return options, args

#-------------------------------------------------------------------------------

def commasep2list(string):
    list_str = string.replace("\n", " ")
    list_str = list_str.replace(" ", "")
    #print list_str
    the_list = list_str.split(",")
    return the_list

#-------------------------------------------------------------------------------

def get_params(cfgfilename):

    if cfgfilename == None:
        print("No configfile selected!")
        sys.exit(1)

    if not os.path.exists(cfgfilename):
        print("Configfile %s does not exist: please select an existing one!" % (
                cfgfilename))

        sys.exit(1)

    parser = SafeConfigParser()
    parser.read(cfgfilename)


    section = "reprocessing"

    try:
        globaltag = requestDefault["GlobalTag"] = parser.get(section, 'globaltag')
    except:
        raise Exception ("Globaltag (parameter 'globaltag') not set in config file")

    try:
        requestDefault["RequestString"] = parser.get(section, 'requeststring')
    except:
        raise Exception ("No Request string (parameter 'requeststring') set in the configfile")

    try:
        rawdataset_str = parser.get(section, 'datasets')
    except:
        raise Exception ("No RAW datasets (parameter 'datasets') set in the configfile")

    rawdataset=commasep2list(rawdataset_str)

    try:
      repromatrix_ver = parser.get(section, 'reproMatrix_ver')
    except:
      repromatrix_ver = os.environ["CMSSW_VERSION"]

    try:
        skimmingMatrix_ver = parser.get(section, 'skimmingMatrix_ver')
    except:
        skimmingMatrix_ver = os.environ["CMSSW_VERSION"]

    try:
        runwhitelist_str = parser.get(section, 'run_whitelist')
        runwhitelist = commasep2list(runwhitelist_str)
    except:
        runwhitelist = []

    requestDefault['RunWhitelist'] = map(int, runwhitelist)

    return {'rawdataset':rawdataset,
            'repromatrix_ver':repromatrix_ver,
            'skimmingMatrix_ver':skimmingMatrix_ver,
            'runwhitelist':runwhitelist,
            'globaltag':globaltag}

#-------------------------------------------------------------------------------

if __name__ == "__main__":
    options, args = build_parser()
    params_dict = get_params(options.reprocfg)

    print("The parameters are: ")
    pprint.pprint(params_dict)

    if options.prepare_configs:
        prepare_configs(params_dict['repromatrix_ver'],
                params_dict['skimmingMatrix_ver'], params_dict['globaltag'])

    request(params_dict['rawdataset'],options)
