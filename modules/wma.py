#! /usr/bin/env python

'''
Module containing the functions necessary to interact with the wma.
Credit and less than optimal code has to be spreaded among lots of people.
'''
from __future__ import print_function
from __future__ import absolute_import
import os
try:
    import httplib
except ImportError:
    import http.client as httplib

import imp
import sys
import time
import json
# Lightweight helpers for upload to ReqMgr2
from modules.tweak_maker_lite import TweakMakerLite
from modules.config_cache_lite import ConfigCacheLite
print('Using TweakMakerLite and ConfigCacheLite!')


URL = 'https://cmsweb.cern.ch'
DBS_URL = URL + '/dbs/prod/global/DBSReader'
PHEDEX_ADDR = URL + '/phedex/datasvc/json/prod/blockreplicas?dataset=%s*'
DATABASE_NAME = 'reqmgr_config_cache'
COUCH_DB_ADDRESS = 'https://cmsweb.cern.ch/couchdb'
WMAGENT_URL = 'cmsweb.cern.ch'
DBS3_URL = "/dbs/prod/global/DBSReader/"


class ConnectionWrapper():
    """
    Wrapper class to re-use existing connection to DBS3Reader
    """
    def __init__(self):
        ##TO-DO:
        # add a parameter to pass DBS3 url, in case we want to use different address
        self.connection = None
        self.connection_attempts = 3
        self.wmagenturl = 'cmsweb.cern.ch'
        self.dbs3url = '/dbs/prod/global/DBSReader/'

    def refresh_connection(self, url):
        self.connection = init_connection(url)

    def abort(self, reason=""):
        raise Exception("Something went wrong. Aborting. " + reason)

    def api(self, method, field, value, detail=False, post=False):
        """Constructs query and returns DBS3 response
        """
        if not self.connection:
            self.refresh_connection(self.wmagenturl)

        # this way saves time for creating connection per every request
        for i in range(self.connection_attempts):
            try:
                if post:
                    params = {}
                    params[field] = value
                    res = httppost(self.connection, self.dbs3url +
                            method, params).replace("'", '"')

                else:
                    if detail:
                        res = httpget(self.connection,
                                self.dbs3url + "%s?%s=%s&detail=%s"
                                % (method, field, value, detail))

                    else:
                        res = httpget(self.connection, self.dbs3url +
                                "%s?%s=%s" % (method, field, value))
                break
            except Exception:
                # most likely connection terminated
                self.refresh_connection(self.wmagenturl)
        try:
            return json.loads(res)
        except:
            self.abort("Could not load the answer from DBS3: " + self.dbs3url
                       + "%s?%s=%s&detail=%s" % (method, field, value, detail))

def testbed(to_url):
    global COUCH_DB_ADDRESS
    global WMAGENT_URL
    global DBS3_URL
    WMAGENT_URL = to_url
    COUCH_DB_ADDRESS = 'https://%s/couchdb' % (WMAGENT_URL)
    DBS3_URL = '/dbs/int/global/DBSReader/'


def init_connection(url):
    return httplib.HTTPSConnection(url, port=443,
            cert_file=os.getenv('X509_USER_PROXY'),
            key_file=os.getenv('X509_USER_PROXY'))

def httpget(conn, query):
    conn.request("GET", query.replace('#', '%23'))
    try:
        response = conn.getresponse()
    except httplib.BadStatusLine:
        raise RuntimeError('Something is really wrong')
    if response.status != 200:
        print("Problems quering DBS3 RESTAPI with %s: %s" % (
            conn.host + query.replace('#', '%23'), response.read()))

        return None
    return response.read()

def httppost(conn, where, params):
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    conn.request("POST", where, json.dumps(params), headers)
    try:
        response = conn.getresponse()
    except httplib.BadStatusLine:
        raise RuntimeError('Something is really wrong')
    if response.status != 200:
        print("Problems quering DBS3 RESTAPI with %s: %s" % (
            params, response.read()))

        return None
    return response.read()

def __check_GT(gt):
    if not gt.endswith("::All"):
        print(("It seemslike the name of the GT '%s' has a typo in it, "
                "missing the final ::All which will crash your job. "
                "If insted you're using CondDBv2, you're fine.") % gt)

def __check_input_dataset(dataset):
    if dataset and dataset.count('/')!=3:
      raise Exception ("Malformed dataset name %s!" %dataset)

def __check_request_params(params):
    if 'GlobalTag' in params:
      __check_GT(params['GlobalTag'])
    for inputdataset in ('MCPileup','DataPileup','InputDataset'):
        if inputdataset in params:
            __check_input_dataset(params[inputdataset])

#-------------------------------------------------------------------------------

def approveRequest(url, workflow, encodeDict=False):
    params = {"RequestStatus": "assignment-approved"}
    headers = {"Content-type": "application/json",
            "Accept": "application/json"}

    conn = httplib.HTTPSConnection(url, cert_file=os.getenv('X509_USER_PROXY'),
            key_file=os.getenv('X509_USER_PROXY'))

    conn.request("PUT", "/reqmgr2/data/request/%s" % workflow, json.dumps(params), headers)
    response = conn.getresponse()
    if response.status != 200:
        print('could not approve request with following parameters:')
        for item in params.keys():
            print(item + ": " + str(params[item]))
        print('Response from http call:')
        print('Status:', response.status, 'Reason:', response.reason)
        print('Explanation:')
        data = response.read()
        print(data.decode('utf-8'))
        print("Exiting!")
        sys.exit(1)
    conn.close()
    print('Approved workflow:', workflow)
    return

#-------------------------------------------------------------------------------

def getWorkflowStatus(url, workflow):
    headers = {"Content-type": "application/json",
            "Accept": "application/json"}
    conn = httplib.HTTPSConnection(url, cert_file=os.getenv('X509_USER_PROXY'),
            key_file=os.getenv('X509_USER_PROXY'))
    conn.request("GET", "/reqmgr2/data/request/%s" % workflow, {}, headers)
    response = conn.getresponse().read()
    workflow_status = ''
    try:
        data = json.loads(response)
        workflow_status = data['result'][0][workflow]['RequestStatus']
    except Exception as e:
        print('Error parsing workflow %s' % str(e))
    conn.close()
    return workflow_status

#-------------------------------------------------------------------------------

def __loadConfig(configPath):
    """
    _loadConfig_

    Import a config.
    """
    print("Importing the config, this may take a while...", end=' ')
    sys.stdout.flush()
    cfgBaseName = os.path.basename(configPath).replace(".py", "")
    cfgDirName = os.path.dirname(configPath)
    modPath = imp.find_module(cfgBaseName, [cfgDirName])
    loadedConfig = imp.load_module(cfgBaseName, modPath[0],modPath[1], modPath[2])

    print("done.")
    return loadedConfig

#-------------------------------------------------------------------------------
# DP leave this untouched even if less than optimal!
def makeRequest(url, params, encodeDict=False):
    ##TO-DO import json somewhere else globally. for now this fix is wmcontrol submission
    __check_request_params(params)

    headers = {"Content-type": "application/json",
            "Accept": "application/json"}

    conn = httplib.HTTPSConnection(url, cert_file=os.getenv('X509_USER_PROXY'),
            key_file=os.getenv('X509_USER_PROXY'))

    ##TO-DO do we move it to top of file?
    __service_url  = "/reqmgr2/data/request"
    print("Will do POST request to:%s%s" % (url, __service_url))
    conn.request("POST", __service_url, json.dumps(params), headers)
    response = conn.getresponse()
    data = response.read()

    if response.status != 200:
        print('could not post request with following parameters:')
        print(json.dumps(params, indent=4))
        print()
        print('Response from http call:')
        print('Status:', response.status, 'Reason:', response.reason)
        print('Explanation:')
        print(data.decode('utf-8'))
        print("Exiting!")
        sys.exit(1)

    workflow = json.loads(data)['result'][0]['request']
    print('Injected workflow:', workflow)

    conn.close()
    return workflow

#-------------------------------------------------------------------------------

def tweaks_from_configuration(cfg_name):
    """
    Creates tweaks from a cms-sw configuration file.

    Args:
        cfg_name (str): Autogenerated cms-sw configuration fragment file.

    Returns:
        dict: Tweaked configuration parameters.
    """
    if not os.path.exists(cfg_name):
        raise RuntimeError("Error: Can't locate config file %s." % cfg_name)

    retries = 2
    exception_raised = None
    loadedConfig = None
    for attempt in range(retries):
        try:
            loadedConfig = __loadConfig(cfg_name)
        except Exception as e:
            print(
                "%s - Error: Unable to load configuration from %s. Retrying again..."
                % (attempt + 1, cfg_name)
            )
            exception_raised = e
            time.sleep(2)

    # Unable to load the configuration from file.
    if exception_raised and not loadedConfig:
        raise exception_raised

    tweak_maker = TweakMakerLite()
    tweaks_dict = tweak_maker.make(process=loadedConfig.process, add_parameters_list=True)
    return tweaks_dict


def tweak_file_path(cfg_name):
    """
    Gets the file name for a tweaked parameter document.
    
    Args:
        cfg_name (str): Autogenerated cms-sw configuration fragment file.
    """
    return os.path.splitext(cfg_name)[0] + ".tweaks"


def tweaks_to_file(cfg_name):
    """
    Creates tweaks from a cms-sw configuration file and stores the
    result into a JSON file.

    Args:
        cfg_name (str): Autogenerated cms-sw configuration fragment file.
    """
    path = tweak_file_path(cfg_name)
    tweaks_dict = tweaks_from_configuration(cfg_name)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(tweaks_dict, file, indent=2, ensure_ascii=False)


def from_tweaks_file(cfg_name):
    """
    Loads tweaks from JSON document.

    Args:
        cfg_name (str): Autogenerated cms-sw configuration fragment file.
    """
    path = tweak_file_path(cfg_name)
    if not os.path.isfile(cfg_name):
        raise RuntimeError(
            "Error: Unable to load tweaks from %s" % (path)
        )

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def upload_to_couch(cfg_name, section_name, user_name, group_name, test_mode=False, url=None, tweaks={}):
    if test_mode:
        return "00000000000000000"

    if not os.path.exists(cfg_name):
        raise RuntimeError("Error: Can't locate config file %s." % cfg_name)

    # create a file with the ID inside to avoid multiple injections
    oldID = cfg_name + '.couchID'

    if os.path.exists(oldID):
        f = open(oldID)
        the_id = f.readline().replace('\n','')
        f.close()
        print(cfg_name, 'already uploaded with ID', the_id, 'from', oldID)
        return the_id

    if tweaks:
        tweaks_dict = tweaks
    else:
        tweaks_dict = tweaks_from_configuration(cfg_name)

    couchdb_url = COUCH_DB_ADDRESS
    if url:
        couchdb_url = url

    couchdb_url = couchdb_url.replace('https://', '').split('/', 1)[0]
    config_cache = ConfigCacheLite(couchdb_url)
    config_cache.set_user_group(user_name, group_name)
    config_cache.add_config(cfg_name)
    config_cache.set_PSet_tweaks(tweaks_dict)
    config_cache.set_label(section_name)
    config_cache.set_description(section_name)
    config_cache.save()

    print("Added file to the config cache:")
    print("  DocID:    %s" % config_cache.document["_id"])
    print("  Revision: %s" % config_cache.document["_rev"])

    f = open(oldID,"w")
    f.write(config_cache.document["_id"])
    f.close()
    return config_cache.document["_id"]

#-------------------------------------------------------------------------------

def time_per_events(campaign):
    ### ad-hoc method until something better comes up to define the time per event in injection time
    addHoc = {
        'Summer12_DR53X' : 17.5,
        'Summer12_DR52X' :  20.00,
        'Fall11_R1' :   5.00,
        'Fall11_R2' :  10.00,
        'Fall11_R4' :   7.00,
        'UpgradeL1TDR_DR6X' : 40.00,
        'UpgradePhase2BE_2013_DR61SLHCx' : 90,
        'UpgradePhase2LB4PS_2013_DR61SLHCx' : 90,
        'UpgradePhase2LB6PS_2013_DR61SLHCx' : 90}

    if campaign in addHoc:
        return addHoc[campaign]
    else:
        return None
