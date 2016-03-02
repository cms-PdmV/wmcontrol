#! /usr/bin/env python

'''
Module containing the functions necessary to interact with the wma.
Credit and less than optimal code has to be spreaded among lots of people.
'''
import os
import urllib
import httplib
import imp
import sys
import time
import json

try:
    from PSetTweaks.WMTweak import makeTweak
    from WMCore.Cache.WMConfigCache import ConfigCache
except:
    print "Probably no WMClient was set up. Trying to proceed anyway..."

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
        ##TO-DO move back to prod after reqmgr2 migration
        #self.wmagenturl = 'cmsweb.cern.ch'
        #self.dbs3url = '/dbs/prod/global/DBSReader/'
        self.wmagenturl = 'cmsweb-testbed.cern.ch'
        self.dbs3url = '/dbs/int/global/DBSReader/'

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
        print "Problems quering DBS3 RESTAPI with %s: %s" % (
            conn.host + query.replace('#', '%23'), response.read())

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
        print "Problems quering DBS3 RESTAPI with %s: %s" % (
            params, response.read())

        return None
    return response.read()

def __check_GT(gt):
    if not gt.endswith("::All"):
        print ("It seemslike the name of the GT '%s' has a typo in it, "
                "missing the final ::All which will crash your job. "
                "If insted you're using CondDBv2, you're fine.") % gt

def __check_input_dataset(dataset):
    if dataset and dataset.count('/')!=3:
      raise Exception ("Malformed dataset name %s!" %dataset)

def __check_request_params(params):
    if params.has_key('GlobalTag'):
      __check_GT(params['GlobalTag'])
    for inputdataset in ('MCPileup','DataPileup','InputDataset'):
        if params.has_key(inputdataset):
            __check_input_dataset(params[inputdataset])

#-------------------------------------------------------------------------------

def approveRequest(url, workflow, encodeDict=False):
    import json
    params = {"RequestStatus": "assignment-approved"}
    headers = {"Content-type": "application/json",
            "Accept": "application/json"}

    conn = httplib.HTTPSConnection(url, cert_file=os.getenv('X509_USER_PROXY'),
            key_file=os.getenv('X509_USER_PROXY'))

    conn.request("PUT", "/reqmgr2/data/request/%s" % workflow, json.dumps(params), headers)
    response = conn.getresponse()
    if response.status != 200:
        print 'could not approve request with following parameters:'
        for item in params.keys():
            print item + ": " + str(params[item])
        print 'Response from http call:'
        print 'Status:', response.status, 'Reason:', response.reason
        print 'Explanation:'
        data = response.read()
        print data
        print "Exiting!"
        sys.exit(1)
    conn.close()
    print 'Approved workflow:', workflow
    return

#-------------------------------------------------------------------------------

def __loadConfig(configPath):
    """
    _loadConfig_

    Import a config.
    """
    print "Importing the config, this may take a while...",
    sys.stdout.flush()
    cfgBaseName = os.path.basename(configPath).replace(".py", "")
    cfgDirName = os.path.dirname(configPath)
    modPath = imp.find_module(cfgBaseName, [cfgDirName])
    loadedConfig = imp.load_module(cfgBaseName, modPath[0],modPath[1], modPath[2])

    print "done."
    return loadedConfig

#-------------------------------------------------------------------------------
# DP leave this untouched even if less than optimal!
def makeRequest(url, params, encodeDict=False):
    ##TO-DO import json somewhere else globally. for now this fix is wmcontrol submission
    import json
    __check_request_params(params)

    headers = {"Content-type": "application/json",
            "Accept": "application/json"}

    conn  =  httplib.HTTPSConnection(url, cert_file=os.getenv('X509_USER_PROXY'),
            key_file=os.getenv('X509_USER_PROXY'))

    ##TO-DO do we move it to top of file?
    __service_url  = "/reqmgr2/data/request"
    print "Will do POST request to:%s%s" % (url, __service_url)
    conn.request("POST", __service_url, json.dumps(params), headers)
    response = conn.getresponse()
    data = response.read()

    if response.status != 200:
        print 'could not post request with following parameters:'
        json.dumps(params, indent=4)
        print
        print 'Response from http call:'
        print 'Status:', response.status, 'Reason:', response.reason
        print 'Explanation:'
        print data
        print "Exiting!"
        sys.exit(1)

    workflow = json.loads(data)['result'][0]['request']
    print 'Injected workflow:', workflow
    conn.close()
    return workflow

#-------------------------------------------------------------------------------

def upload_to_couch(cfg_name, section_name, user_name, group_name, test_mode=False, url=None):
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
        print cfg_name, 'already uploaded with ID', the_id, 'from', oldID
        return the_id

    try:
        loadedConfig = __loadConfig(cfg_name)
    except:
        #just try again !!
        time.sleep(2)
        loadedConfig = __loadConfig(cfg_name)

    where = COUCH_DB_ADDRESS
    if url:
        where = url

    configCache = ConfigCache(where, DATABASE_NAME)
    configCache.createUserGroup(group_name, user_name)
    configCache.addConfig(cfg_name)
    configCache.setPSetTweaks(makeTweak(loadedConfig.process).jsondictionary())
    configCache.setLabel(section_name)
    configCache.setDescription(section_name)
    configCache.save()

    print "Added file to the config cache:"
    print "  DocID:    %s" % configCache.document["_id"]
    print "  Revision: %s" % configCache.document["_rev"]

    f = open(oldID,"w")
    f.write(configCache.document["_id"])
    f.close()
    return configCache.document["_id"]

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
