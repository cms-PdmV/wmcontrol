#!/usr/bin/env python

# Original script of Jean-Roch Vlimant, adapted only for the couch password
# Before starting, don't forget the tunneling:
# https://twiki.cern.ch/twiki/bin/view/CMS/WMAgentMakeRequestTunneling

import os
import sys

#-------------------------------------------------------------------------------
# Check if it is the case to start

if not (os.environ.has_key('WMCONTROL_USER') and os.environ.has_key('WMCONTROL_GROUP')):
  print "The environmental variables WMCONTROL_USER or WMCONTROL_GROUP do not seem to be set. Please check."
  sys.exit(1)

if not os.environ.has_key('CMSSW_VERSION'):
  print "The CMSSW environment does not seem to be set. Please check."
  sys.exit(1)

#-------------------------------------------------------------------------------

import httplib
import urllib

import copy
import hashlib
import wma
import pprint

DUMPED_REQUESTS_SCHELETON="requests_for_%s_cache"

g_dry_run=False

requestDefault={
    "CMSSWVersion": os.environ['CMSSW_VERSION'],
    "ScramArch": os.environ['SCRAM_ARCH'],
    "RequestPriority": 100000,
    "InputDataset": None,    
    "RunWhitelist": [],
    "RunBlacklist": [],
    "BlockWhitelist": [],
    "BlockBlacklist": [],    
    "DbsUrl": wma.DBS_URL,
    "GlobalTag": None,
    "inputMode": "couchDB",    
    "ProcConfigCacheID": None,
    "RequestString": None,    
    "RequestType": "ReReco",
    "Requestor": os.environ['WMCONTROL_USER'],
    "Group": os.environ['WMCONTROL_GROUP']
    }


#-------------------------------------------------------------------------------

def addSkimToRequest(params,cfg):
    nextIndex=1
    while 'SkimName%d'%(nextIndex,) in params.keys():
        nextIndex+=1
    params['SkimName%d'%(nextIndex,)] = params["RequestString"]+'Skim'
    params['SkimInput%d'%(nextIndex,)] = 'RECOoutput'
    cfgid=wma.upload_to_couch(cfg,params["RequestString"]+'Skim',params["RequestString"]+'Skim',g_dry_run)
    if cfgid==None:
        print "no id for",cfg
        sys.exit()
    params['Skim%dConfigCacheID'%(nextIndex,)] = cfgid
    params["nskims"] = nextIndex
    params['NR_skim']=cfg

#-------------------------------------------------------------------------------

def getReproCfg(PD):

  cosm_name='cosmics'
  pp_name='pp'

  rereco_pp = 'rereco_%s_pp.py' %PD
  if os.path.exists(rereco_pp):
    return (pp_name,rereco_pp)
   
  rereco_cosmics = 'rereco_%s_cosmics.py' %PD
  if os.path.exists(rereco_cosmics):
    return (cosm_name,rereco_cosmics)
   
  if cosm_name in PD.lower():
    return (cosm_name,'rereco_cosmics.py')
  else:
    return (pp_name,'rereco_pp.py')
   
  return None
    
#-------------------------------------------------------------------------------

def getSkimCfg(PD):

  skim_cfg_filename='skim_%s.py'%PD
  if os.path.exists(skim_cfg_filename):
    return skim_cfg_filename
  return None
    
#-------------------------------------------------------------------------------

def prepareRequest(rawdataset,options):
    requests=[]
    for dataset in rawdataset:
        PD=dataset.split('/')[1]

        dsparameters=copy.copy(requestDefault)
        dsparameters["InputDataset"] = dataset
        dsparameters["RequestString"]+=PD
        if options.lastRun>0:
            if options.firstRun>0:
                dsparameters["RunWhitelist"]=runlistfromdbs('dataset = %s and run.number<=%s and run.number>=%s'%(dataset,options.lastRun,options.firstRun))
            else:
                dsparameters["RunWhitelist"]=runlistfromdbs('dataset = %s and run.number<=%s'%(dataset,options.lastRun))
            
        #find the reprocessing configuration
        scenario,reprocfg=getReproCfg(PD)
        cfgid=wma.upload_to_couch(reprocfg,dsparameters["RequestString"],dsparameters["RequestString"],g_dry_run)
        if cfgid:
            dsparameters["ProcConfigCacheID"]=cfgid
            dsparameters["Scenario"]=scenario
        else:
            raise Exception("no id for"+PD+" "+reprocfg)
        dsparameters['NR_cfg']=reprocfg
        #find the skimming configuration
        skim=getSkimCfg(PD)
        if skim:
            addSkimToRequest(dsparameters,skim)
        
        requests.append(dsparameters)
    return requests

#-------------------------------------------------------------------------------

def onePar(request,par):
    if par in request:
        print par,request[par]
        return
    for k in request:
        if par in k:
            print k,":",request[k]

#-------------------------------------------------------------------------------

def cat_file(filename):
  f=open(filename,"r")
  print f.read()
  f.close()

#-------------------------------------------------------------------------------

def fullTwikiPrint(requests):
    twikifilename='fullTwiki.txt'
    f=open(twikifilename,'w')
    f.write('| %40s | %30s | %20s | %30s | %20s | \n'%('*Dataset*',
                                                       '*Configuration*',
                                                       '*Couch ID*',
                                                       '*Skimming*',
                                                       '*Couch ID*'))

    for request in requests:
        if 'NR_skim' in request:
            f.write('| %40s | %30s | %20s | %30s | %20s | \n'%(request['InputDataset'],
                                                               request['NR_cfg'],
                                                               request['ProcConfigCacheID'],
                                                               request['NR_skim'],
                                                               request['Skim1ConfigCacheID']
                                                               ))
        else:
            f.write('| %40s | %30s | %20s | %30s | %20s | \n'%(request['InputDataset'],
                                                               request['NR_cfg'],
                                                               request['ProcConfigCacheID'],
                                                               '%NA%',
                                                               '%NA%'))
    f.close()
    
    cat_file(twikifilename)

#-------------------------------------------------------------------------------
    
def twikiPrint(requests):
    twikifilename='twiki.txt'
    f=open(twikifilename,'w')
    f.write('| %40s | %30s | %30s | \n'%('*Dataset*',
                                         '*Configuration*',
                                         '*Skimming*'))
    for request in requests:
        if 'NR_skim' in request:
            f.write('| %40s | %30s | %30s | \n'%(request['InputDataset'],
                                                 request['NR_cfg'],
                                                 request['NR_skim']))
        else:
            f.write('| %40s | %30s | %30s | \n'%(request['InputDataset'],
                                                 request['NR_cfg'],
                                                 '%NA%'))
    f.close()
    cat_file(twikifilename)

#-------------------------------------------------------------------------------
    
def prettyPrint(request):
    onePar(request,'InputDataset')
    if len(request["RunWhitelist"]):
        print request["RunWhitelist"]
    onePar(request,'RequestString')
    onePar(request,'Scenario')
    onePar(request,'SkimName')
    onePar(request,'ConfigCacheID')

#-------------------------------------------------------------------------------

def prettyPrintRequest(requests):
    for request in requests:
        print 
        prettyPrint(request)
        #print request
        print

#-------------------------------------------------------------------------------

def printRequest(requests):
    for request in requests:
        print "------------------ SHOWING ----------------------"
        print request
        print

#-------------------------------------------------------------------------------

def make_requests(requests):
    print 'Making the requests'
    global dry_run
    for request in requests:
        print " ----------------- SENDING ----------------------"
        prettyPrint(request)
        trimmedRequest=copy.copy(request)
        for k in trimmedRequest.keys():
            if k.startswith('NR_'):
                trimmedRequest.pop(k)
        if not dry_run:
                workflow = wma.makeRequest(wma.WMAGENT_URL,trimmedRequest)
                wma.approveRequest(wma.WMAGENT_URL,workflow)

#-------------------------------------------------------------------------------

def makerawdatsetfromdbs(query):
    rawdataset=[]
    dbs=os.popen('dbs search --noheader --query "find dataset where %s"'%(query,))
    for line in dbs:
        dataset=line.split()[0]
        rawdataset.append(dataset)
    return rawdataset

#-------------------------------------------------------------------------------

def runlistfromdbs(query):
    runlist=[]
    print "getting run list from dbs for the query:",query

    queryhash=hashlib.sha224(query).hexdigest()
    runlist="runList_%s.list"%(queryhash,)
    try:
        dbs=open(runlist,'r')
        print runlist,"opened for reading run list for query:",query
    except:
        print "query never done doing it"
        dbs=os.popen('dbs search --noheader --query "find run.number where %s"'%(query,))
        store=open(runlist,'w')
        print runlist,"opened for writing run list for query:",query
        store.write('QUERY: '+query+'\n')
        for line in dbs: store.write(line)
        store.close()
        dbs=open(runlist,'r')
        
    for line in dbs:
        if 'QUERY' in line:
            querystore=(line[7:]).replace('\n','')
            if query!=querystore:
                print "Problem:",
                print query,"---"
                print "different than"
                print querystore,"---"
                sys.exit()
            continue
        runnumber=int(line.split()[0])
        runlist.append(runnumber)
    return runlist

#-------------------------------------------------------------------------------

def dump_requests(reprocfg_filename, requests):
  ofilename=DUMPED_REQUESTS_SCHELETON %reprocfg_filename
  ofile=file(ofilename,"w")
  pprint.pprint(requests,ofile)
  ofile.close()
  print "Requests dumped in %s" %ofilename

#-------------------------------------------------------------------------------

def read_requests(reprocfg_filename):
  ifilename=DUMPED_REQUESTS_SCHELETON %reprocfg_filename
  ifile=file(ifilename,"r")
  requests = eval (ifile.read())
  pprint.pprint(requests)
  ifile.close()
  print "Requests read from %s" %ifilename
  return requests

#-------------------------------------------------------------------------------

def print_and_exec(command):
  print "Executing %s" %command
  os.system(command)
     
#-------------------------------------------------------------------------------
# FIXME: multiprocess for speedup
def prepare_configs(repromatrix_ver,skimmingMatrix_ver,globaltag):
    
    cmssw_base_src="%s/src" %os.environ["CMSSW_BASE"]
    
    curdir=os.getcwd()
    os.chdir(cmssw_base_src)
    print_and_exec('cvs co -r %s Configuration/GlobalRuns/test/reProcessingMatrix.py\n'%repromatrix_ver )
    print_and_exec('cvs co -r %s Configuration/Skimming/test/skimmingMatrix.py\n' %skimmingMatrix_ver)
    print_and_exec('scram b python\n')
    os.chdir(curdir)
    print_and_exec('python %s/Configuration/Skimming/test/skimmingMatrix.py --GT %s\n' %(cmssw_base_src,globaltag))
    print_and_exec('python %s/Configuration/GlobalRuns/test/reProcessingMatrix.py --GT %s' %(cmssw_base_src,globaltag) )

#-------------------------------------------------------------------------------

def check_rawdataset(rawdataset):
  for dataset in rawdataset:
    if dataset.count('/')!=3:
      raise Exception ("Malformed dataset name %s!" %dataset)
    if not dataset.endswith("RAW"):
      raise Exception ("Dataset %s is not RAW!" %dataset)

#-------------------------------------------------------------------------------

def request(rawdataset,options):
  global dry_run
  dry_run=options.test

  if options.upload:
    print 'Ready for uploading configs to couchDB'

    check_rawdataset(rawdataset)

    requests=prepareRequest(rawdataset,options)    
    #pprint.pprint(requests)

    printRequest(requests)
    twikiPrint(requests)
    fullTwikiPrint(requests)

    # dump requests in an ascii file
    dump_requests(options.reprocfg,requests)

  if options.request:    
    requests = read_requests(options.reprocfg)
    make_requests(requests)
        
#-------------------------------------------------------------------------------
