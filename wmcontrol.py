#! /usr/bin/env python

################################################################################
#                                                                              #
# WMAControl: the swiss army knife for central requests submissions.           #
# Several pieces were imported from the WMAgent infrastructure.                #
# The name is clearly inspired to GridControl.                                 #
#                                                                              #
# Danilo Piparo, CERN                                                          #
#                                                                              #
################################################################################

import os
import urllib
import sys
import subprocess
import time
import random
import optparse
import json
import pprint
import ConfigParser
import traceback
import re
import time
import copy 

sys.path.append(os.path.join(sys.path[0], 'modules'))
from modules import helper
from modules import wma # here u have all the components to interact with the wma

#-------------------------------------------------------------------------------


dbs_url_g = wma.DBS_URL

test_mode = False # Put True not to upload the requests

max_step=9
## you find me the right lib, I take it !!!
step_words=['Zero','One','Two','Three', 'Four','Five','Six','Seven','Eight','Nine']
if max_step > len(step_words)-1:
    raise Exception ("Not enough word for all steps")


default_parameters = {
'dbsurl':dbs_url_g,
'priority':181983,
'request_type':'ReReco',
'scramarch':'slc5_amd64_gcc462',
'includeparents': 'False'
  }
for i in range(max_step):
    default_parameters['keep_step%d'%(i+1)]=False


if os.getenv('SCRAM_ARCH'):
    default_parameters['scramarch']=os.getenv('SCRAM_ARCH')

#-------------------------------------------------------------------------------
class ExtendedOption (optparse.Option):
  ACTIONS = optparse.Option.ACTIONS + ("extend",)
  STORE_ACTIONS = optparse.Option.STORE_ACTIONS + ("extend",)
  TYPED_ACTIONS = optparse.Option.TYPED_ACTIONS + ("extend",)
  ALWAYS_TYPED_ACTIONS = optparse.Option.ALWAYS_TYPED_ACTIONS + ("extend",)

  def take_action(self, action, dest, opt, value, values, parser):
    if action == "extend":
      lvalue = value.split(",")
      values.ensure_value(dest, []).extend(lvalue)
    else:
      optparse.Option.take_action(self, action, dest, opt, value, values, parser)

#-------------------------------------------------------------------------------

class Configuration:
    '''
    A class that offers a common interface to get parameters out of a
    optionParser (command line) or a ConfigParser (ini cfg).
    The key is to build a ConfigParser object with a single section out
    of the option parser.
    '''

    default_section= '__OptionParser__'
    def __init__ (self, parser):
        # assume you have a .conf input file, first...
        # see : https://docs.python.org/2/library/configparser.html
        self.configparser=ConfigParser.SafeConfigParser()

        try:
            options,args = parser.parse_args()
        except SystemExit:
            print "Error in parsing options"
            sys.stderr.write("[wmcontrol exception] Error in parsing options")
            sys.exit(-1)

        global test_mode
        test_mode = test_mode or options.test

        if options.wmtest:
            print "Setting to injection in cmswebtest : ", options.wmtesturl
            wma.testbed(options.wmtesturl)

        if options.req_file != '' and options.req_file !=None:
            cfg_filename=options.req_file
            print "We have a configfile: %s." %cfg_filename
            self.configparser.read(cfg_filename)
        else: # ... otherwise, we have to convert the command line option parser to a .conf, and populate self.configparser
            print "We have a commandline."
            self.__fill_configparser(options)



    def __fill_configparser(self,options):
        '''
        Convert the option parser (from command line) into a configparser (as if it was .conf file).
        '''
        # loop on all option parser parameters and fille the cp
        self.configparser.add_section(self.__class__.default_section)
        for param,param_value in options.__dict__.items():
          if param_value == None:
            param_value = "__NOT-DEFINED__"
          #print "Setting params in cfg: %s with default %s" %(param,param_value)
          ### HOLLY SHIT THE SYSTEMATIC RECASTING TO STR
          self.configparser.set(self.__class__.default_section, param, str(param_value))
        #with open('example.cfg', 'wb') as configfile:
            #self.ConfigParser.write(configfile)

    def get_param(self,name,default=None,section=default_section,verbose=False):
        '''
        I am astonished that such function does not exist in Python!!
        '''
        ret_val=None
        if verbose:
          print "I am looking for section %s and option %s, the default is #%s#" %(name, section, default)
        if self.configparser.has_section(section):
          if self.configparser.has_option(section,name):
            #print "Getting %s %s" %(section,name)
            ret_val = self.configparser.get(section,name)
            # We had a cfg file and the default was not given
            if ret_val == "__NOT-DEFINED__":
              if verbose:
                print "I was reading parameter %s and I put the default %s" %(name, default)
              ret_val = default
            # we have both: read and return!
            else:
              pass
          else:
            # We don't have the option, try to return the default
            if default!=None:
              # Case 1, we have the default
              ret_val = default
            else:
              # Case 2, we do not have the default, exception
              raise Exception ("Parameter %s cannot be found in section %s and no default is given." %(name,section))
        else:
          # No section found, just rais e an exception
          raise Exception ("No section %s found in configuration." %section)

        if verbose:
          print "I am returning the value #%s#" %(ret_val)
        return ret_val

def get_runs(dset_name,minrun=-1,maxrun=-1):
    '''
    Get the runs from the DBS via the DBS interface
    '''
    print "Looking for runs in DBS for %s" %dset_name
    minrun=int(minrun)
    maxrun=int(maxrun)

    # check if cmssw is set up for the dbs command
    if not os.environ.has_key("CMSSW_BASE"):
        raise Exception("No CMSSW environment set. You need it to query dbs.")

    return_data = json.loads(wma.generic_get(wma.WMAGENT_URL, wma.DBS3_URL+"runs?dataset=%s" %(dset_name)))
    run_list = return_data[0]["run_num"]
    if minrun >= 0:
        run_list = filter(lambda n: n >= minrun,run_list)
    if maxrun >= 0:
        run_list = filter(lambda n: n <= maxrun,run_list)

    return sorted(run_list)

#-------------------------------------------------------------------------------

def custodial(datasetpath):
# not clear if this custodial method is actually used anywhere; otherwise clean it up ?

   if test_mode:
     return "custodialSite1"

   allSites = 1

#   datasetpath = None
#   lfn = None
#    allSites = 0
#   try:
#       opts, args = getopt.getopt(sys.argv[1:], "", ["lfn=","dataset=","allSites"])
#   except getopt.GetoptError:
#       print 'Please specify dataset with --dataset'
#       print 'Specify --allSites to show all site location, otherwise show only T1 sites'
#       sys.exit(2)

   # check command line parameter
#   for opt, arg in opts :
#       if opt == "--dataset" :
#           datasetpath = arg
#       if opt == "--lfn" :
#           lfn = arg
#       if opt == "--allSites" :
#           allSites = 1

#   if datasetpath == None and lfn == None:
#       print 'Please specify dataset with --dataset'
#       sys.exit(2)


   custodial = {}
   non_custodial = {}

#   if lfn == None :
   url=wma.PHEDEX_ADDR %datasetpath
   try:
       result = json.load(urllib.urlopen(url))
   except:
       print 'Problems with url',url
   try:
           for block in result['phedex']['block']:
               name = block['name']
               for replica in block['replica']:
                   files = replica['files']
                   site = str(replica['node'])
                   is_custodial = replica['custodial']
                   if allSites == 1 or ( site[0:2] == 'T1' or site[0:2] == 'T0') :
                       if is_custodial == 'y' :
                           if site not in custodial.keys() :
                               custodial[site] = int(files)
                           else :
                               custodial[site] += int(files)
                       else :
                           if site not in non_custodial.keys() :
                               non_custodial[site] = int(files)
                           else :
                               non_custodial[site] += int(files)
   except:
           print 'Problems with dataset:',datasetpath

   custodial_sites = custodial.keys()
   non_custodial_sites = non_custodial.keys()

   custodial_sites.sort()
   non_custodial_sites.sort()

   if len(custodial_sites) == 0 :
       custodial['NONE'] = 0
   if len(non_custodial_sites) == 0 :
       non_custodial['NONE'] = 0
   if len(custodial_sites) == 1 and custodial_sites[0].count('T0') > 0 :
       custodial['NONE'] = 0
   if len(non_custodial_sites) == 1 and non_custodial_sites[0].count('T0') > 0 :
       non_custodial['NONE'] = 0

   sites = ''
   custsites = ''
   for site in non_custodial_sites :
       if site not in custodial_sites :
           sites = sites + site + '(' + str(non_custodial[site]) + '),'
   if sites[-1:] == ',' :
       sites = sites[:-1]
   for custsite in custodial_sites :
#       custsites = custsites + custsite + '(' + str(custodial[custsite]) + '),'
       custsites = custsites + custsite
   if custsites[-1:] == ',' :
       custsites = custsites[:-1]

#   if lfn == None :
   print 'dataset:',datasetpath,'custodial:',custsites,'non-custodial:',sites
#   else :
#   print 'lfn:',lfn,'custodial:',custsites,'non-custodial:',sites

   return custsites

#-------------------------------------------------------------------------------

def random_sleep(min_sleep=1,sigma=1):
    """
    Sleep for a random time in order not to choke the server submitting too many
    requests in a small time interval
    """
    rnd=abs(random.gauss(0,sigma))
    sleep_time=min_sleep+rnd
    #print "Sleeping %s seconds" %sleep_time
    time.sleep(sleep_time)

#-------------------------------------------------------------------------------

def get_dset_nick(dataset):
    """
    Create a nickname out of a dataset name. Some heuristic tricks are used to
    make the nicks shorter.
    """
    #print dataset
    nick=dataset
    if "/" in dataset:
      c1,c2,c3=dataset[1:].split('/')
      nick="%s_%s_%s" %(c1,c2,c3)
      nick=nick.replace("Electron","El")
      nick=nick.replace("Single","Sing")
      nick=nick.replace("Double","Dbl")

    return nick

#-------------------------------------------------------------------------------

def get_dataset_runs_dict(section,cfg):
      '''
      If present, eval it, if not just use the plain dataset name input and [] !
      '''
      dataset_runs_dict={}
      run_list = []
      try:
        dataset_runs_dict = eval(cfg.get_param('dset_run_dict','',section))
        for key in dataset_runs_dict.keys():
            if isinstance(dataset_runs_dict[key], str):
                if os.path.exists(dataset_runs_dict[key]):
                    try:
                        json_file = open(dataset_runs_dict[key])
                        json_info = json.load(json_file)
                        json_file.close()
                    except ValueError:
                        print "Error in JSON file: ", dataset_runs_dict[key], " Exiting..."
                        print traceback.format_exc()
                        #sys.exit()
                        return False
                    for run_number in json_info:
                        run_list.append(int(run_number))
                    run_list.sort()
                    dataset_runs_dict[key] = run_list
                    run_list = []
                else:
                    print "JSON file doesn't exists. ", os.path.join(os.getcwd(), dataset_runs_dict[key]), " Exiting..." 
                    #sys.exit()
		    return False
      except:
        dataset_runs_dict[cfg.get_param('input_name','',section)]=[]

      return  dataset_runs_dict

#-------------------------------------------------------------------------------

def make_request_string(params,service_params,request):
    request_type = service_params['request_type']
    identifier=''
    dataset=params['InputDataset']
    # Make a string a la prep if needed: #old version
#    if request == Configuration.default_section:
#        # Request ID string
#        joinString = ""
#        if custodial(params['InputDataset']):
#            joinString = "_v"
#        identifier = "%s_%s%s%s" %(params['PrepID'],
#                                   custodial(dataset),
#                                   joinString,
#                                   service_params['version'])
#
#    elif service_params['req_name'] != '' :
#      identifier=service_params['req_name']
    if request == Configuration.default_section:
        # Request ID string
        if 'PrepID' in params:
            pid=params['PrepID']
        else:
            pid=service_params['pid']

        joinString = ""
        if request_type in ['MonteCarloFromGEN', 'MonteCarlo', 'LHEStepZero', 'TaskChain']:
          joinString = "_v"
          identifier = "%s_%s%s%s_%s" %(pid,
                                   service_params['batch'],
                                   joinString,
                                   service_params['version'],
                                   service_params['process_string'])

        else:
          #if custodial(params['InputDataset']):
          #  custname = custodial(dataset)
          #else:
          #  custname = "No_custT1"
          joinString = "_v"
          identifier = "%s_%s%s%s_%s" %(pid,
                                   service_params['batch'],
                                   joinString,
                                   service_params['version'],
                                   service_params['process_string'])

    elif service_params['req_name'] != '':
        identifier=service_params['req_name']
    else:
        dset_nick = get_dset_nick(dataset)
        cmssw_version=params["CMSSWVersion"]
        cmssw_version=cmssw_version.replace("CMSSW","")
        cmssw_version=cmssw_version.replace("_","")
        cmssw_version=cmssw_version.replace("patch","p")

        identifier = "%s_%s_%s" %(service_params["section"],cmssw_version,dset_nick)
        if len(identifier)>20:
            identifier="%s_%s"%(service_params["section"],cmssw_version)

    return identifier

#-------------------------------------------------------------------------------

def loop_and_submit(cfg):
  '''
  Loop on all the sections of the configparser, build and submit the request.
  This is the orchestra director function.
  '''
  pp = pprint.PrettyPrinter(indent=4)

  for section in cfg.configparser.sections():
    # Warning muted
    #print '\n---> Processing request "%s"' %section
    # build the dictionary for the request
    params,service_params = build_params_dict(section,cfg)
    dataset_runs_dict = get_dataset_runs_dict (section,cfg)
    if not dataset_runs_dict:
        sys.stderr.write("[wmcontrol exception] No dataset_runs_dict provided")
        sys.exit(-1)

    # Submit request!
    for dataset in sorted(dataset_runs_dict.keys()):
      params['InputDataset']=dataset
      runs=[]
      new_blocks=[]
      for item in dataset_runs_dict[dataset]:
          if isinstance(item,str) and '#' in item:
              if item.startswith('#'):
                new_blocks.append(dataset+item)
              else:
                new_blocks.append(item)
          else:
            runs.append(item)
      params['RunWhitelist']=runs

      if params.has_key("BlockWhitelist"):
          if params['BlockWhitelist']==[]:
              params['BlockWhitelist']=new_blocks
          if params['BlockWhitelist']!=[] and new_blocks!=[]:
              print "WARNING: a different set of blocks was made available in the input dataset and in the blocks option."
              print "Keeping the blocks option (%s) instead of (%s)" % (str(sorted(new_blocks)), str(sorted(params['BlockWhitelist'])))
              params['BlockWhitelist']=new_blocks

      elif service_params['lumi_list'] != '':
          params['LumiList'] = service_params['lumi_list']

      params['RequestString']= make_request_string(params,service_params,section)

      if service_params['request_type'] in ['MonteCarlo','LHEStepZero']:
          params.pop('InputDataset')
          params.pop('RunWhitelist')
      elif service_params['request_type'] == 'TaskChain':
          ##if we have a global defined input_DS we set it as Task1 input
          if params['InputDataset']:
              params['Task1']['InputDataset'] = params['InputDataset']

          ##if we have a taskChain and its First task has inputDS, we do splitting algo
          ##TO-DO: move to separate method so we would not need to duplicate code
          if 'InputDataset' in params['Task1']:
              if params['Task1']['InputDataset'] != '' and params['Task1']['RequestNumEvents']:
                  if test_mode:
                      t = time.time()
                  espl = helper.SubsetByLumi(params['Task1']['InputDataset'],
                                             float(service_params['margin']))

                  if 'FilterEfficiency' in params['Task1']:
                      __events = float(params['Task1']['RequestNumEvents']) / float(
                              params['Task1']['FilterEfficiency'])
                  else:
                      __events = float(params['Task1']['RequestNumEvents'])

                  split, details = espl.run(int(__events),
                                            service_params['brute_force'],
                                            service_params['force_lumis'])

                  if split == 'blocks':
                      params['Task1']['BlockWhitelist'] = details
                  elif split == 'lumis':
                      params['Task1']['LumiList'] = details
                  elif split == 'dataset':
                      print "no white listing"
                  if test_mode:
                      print "Finished in", int((time.time()-t)*1000), "\bms"

          if params['RunWhitelist']:
              params['Task1']['RunWhitelist'] = params['RunWhitelist']

          if 'RunWhitelist' in params: #if params has key we remove it
              params.pop('RunWhitelist') #because it was set as Task parameter
          if 'InputDataset' in params:
              params.pop('InputDataset')
      elif ('RequestNumEvents' in params and 'LumiList' not in params and
            ('RunWhitelist' not in params or params['RunWhitelist']==[])):

          if 'FilterEfficiency' in params:
              events = float(params['RequestNumEvents'] / float(params['FilterEfficiency']))
          else:
              events = float(params['RequestNumEvents'])

          if events:
              if test_mode:
                  t = time.time()
              espl = helper.SubsetByLumi(params['InputDataset'],
                                         float(service_params['margin']))
              split, details = espl.run(int(events),
                                        service_params['brute_force'],
                                        service_params['force_lumis'])
              # https://github.com/dmwm/DBS/issues/280
              # https://github.com/dmwm/DBS/issues/428
              if split == 'blocks':
                  params['BlockWhitelist'] = details
              elif split == 'lumis':
                  params['LumiList'] = details
              elif split == 'dataset':
                  print "no white listing"

                  pass
              if test_mode:
                  print "Finished in", int((time.time()-t)*1000), "\bms"

      # just print the parameters of the request you would have injected
      if test_mode:
          pp.pprint(params)
      else: # do it for real!
          try:
              workflow = wma.makeRequest(wma.WMAGENT_URL,params,encodeDict=(service_params['request_type']=='TaskChain'))
          except:
              random_sleep()
              #just try a second time
              workflow = wma.makeRequest(wma.WMAGENT_URL,params,encodeDict=(service_params['request_type']=='TaskChain'))

          try:
              wma.approveRequest(wma.WMAGENT_URL,workflow)
          except:
              random_sleep()
              #just try a second time
              wma.approveRequest(wma.WMAGENT_URL,workflow)
          random_sleep()

#-------------------------------------------------------------------------------

def make_cfg_docid_dict(filename):
  '''
  opens the file if there and reads its parameters
  Skip lines beginning with #
  returns a dictionary with the cfgnames as keys and the docids as values
  Example config:
   config_0_1_cfg.py 8216d7bbd56664bc2a5853fb4f0aa36e
   config_0_2_cfg.py 8216d7bb57e664bc2a5853fb4a0aeb28
   config_0_3_cfg.py 8216d7bbd5bc64bc2a5853fb4f0aed61
  '''
  if filename =='':
    return {}

  print "Building a cfg-docID dictionary.."

  cfg_db_file=None
  try:
    cfg_db_file=open(filename,'r')
  except:
    raise Exception ('Problems in opening %s: does it exist? is it corrupted? do you have the right permissions?' %filename)
  # at this point we have the file, let's interpret it!
  cfg_docid_dict={}
  for line in cfg_db_file:
    # remove a trailing comment if there and skip the lines
    line = line[:line.find('#')]
    line = line.strip()
    if line == '' or line[0]=='#':
      continue # this is a comment line
    # small sanity check, one could add regexp
    if line.count(' ') > 1:
      raise Exception('Could not interpret line %s. Too many spaces.' %line)
    # split the line
    cfg_name,docid = line.split(' ')
    if test_mode:
      print "Name, DocID in file %s: %s %s"%(filename, cfg_name,docid)
    cfg_docid_dict[cfg_name] = docid
  cfg_db_file.close()
  return cfg_docid_dict

#-------------------------------------------------------------------------------

def get_user_group(cfg,section):
  # try to use the environment variables if nothing provided
  user_env_name ='WMCONTROL_USER'
  group_env_name='WMCONTROL_GROUP'
  user_default =''
  group_default=''
  if os.environ.has_key(user_env_name):
    user_default=os.environ[user_env_name]
  if os.environ.has_key(group_env_name):
    group_default=os.environ[group_env_name]
  #print os.environ.has_key(user_env_name)
  #print "*", user_default, "*", group_default
  user = cfg.get_param('user',user_default,section)
  group = cfg.get_param('group',group_default,section)

  #print "*", user, "*", group

  return user, group

#-------------------------------------------------------------------------------

def build_params_dict(section,cfg):
  global couch_pass
  '''
  Build the parameters dictionary for the request. Assumes the presence of an input .conf file or commandline.
  For the moment the defaults of the parameters are stored here.
  Put a dictionary on top?
  '''

  #wm testing
  wmtest = cfg.get_param('wmtest', False, section)

  url_dict = cfg.get_param('url_dict',"",section)


  # fetch some important parameters
  #this trick is to make the uniformation smoother and be able to read old cfgfiles
  # elaborate the file containing the name docid pairs
  cfg_db_file = cfg.get_param('cfg_db_file','',section)
  #print cfg_db_file
  cfg_docid_dict = make_cfg_docid_dict(cfg_db_file)

  release = cfg.get_param('release','',section)
  globaltag = cfg.get_param('globaltag','',section)
  pileup_dataset = cfg.get_param('pu_dataset','',section)
  primary_dataset = cfg.get_param('primary_dataset','',section)

  filter_eff = cfg.get_param('filter_eff','',section)
  if not filter_eff:
      filter_eff = 1.0

  number_events = int(cfg.get_param('number_events',0,section))
  #number_events = cfg.get_param('number_events',0,section)
  version = cfg.get_param('version',1,section)
  
  ##new values for renewed Request Agent
  time_event = float(cfg.get_param('time_event',20,section))
  size_memory = int(float(cfg.get_param('size_memory',2300,section)))
  size_event = int(float(cfg.get_param('size_event',2000,section)))
  if size_event <0:
      size_event = 2000

  # parameters with fallback
  scramarch = cfg.get_param('scramarch',default_parameters['scramarch'],section)
  #group = cfg.get_param('group',default_parameters['group'],section)
  #requestor = cfg.get_param('requestor',default_parameters['requestor'],section)
  identifier = cfg.get_param('identifier','',section)
  dbsurl = cfg.get_param('dbsurl',default_parameters['dbsurl'],section)

  includeparents=cfg.get_param('includeparents',default_parameters['includeparents'],section)

  req_name=cfg.get_param('req_name','',section)
  process_string = cfg.get_param('process_string','',section)
  processing_string = cfg.get_param('processing_string','',section)
  batch = cfg.get_param('batch','',section)
  open_running_timeout = int(float(cfg.get_param('open_running_timeout','43200',section))) # 12h is legacy

  # for the user and group
  user,group = get_user_group(cfg,section)

  # for the skims
  skim_cfg = cfg.get_param('skim_cfg','',section)
  skim_docid = cfg.get_param('skim_docID','',section)
  skim_name = cfg.get_param('skim_name','',section)
  skim_input = cfg.get_param('skim_input','RECOoutput',section)

  if not skim_docid and skim_cfg:
      if cfg_docid_dict.has_key(skim_cfg):
          skim_docid=cfg_docid_dict[skim_cfg]
      else:
          skim_docid=wma.upload_to_couch(skim_cfg, section, user, group,test_mode)

  # priority
  priority = cfg.get_param('priority',default_parameters['priority'],section)

  #blocks
  blocks = cfg.get_param('blocks', [], section)

  # Now the service ones
  # Service

  harvest_cfg = cfg.get_param('harvest_cfg','',section)
  harvest_docID = cfg.get_param('harvest_docID','',section)

  stepN_output=[]
  keep_stepN=[]
  stepN_cfg=[]
  stepN_docID=[]  
  for i in range(max_step):
      s=i+1 
      stepN_output.append(cfg.get_param('step%d_output'%s,'',section))
      keep_stepN.append(cfg.get_param('keep_step%d'%s,default_parameters['keep_step%d'%s],section))
      if i==0:
          cfg_path = cfg.get_param('cfg_path','',section)
          stepN_cfg.append(cfg.get_param('step%d_cfg'%s,cfg_path,section)) # defaults it to cfg_path if not specified
          doc_id = cfg.get_param('doc_id','',section)
          stepN_docID.append(cfg.get_param('step%d_docID'%s,doc_id,section)) # defaults itto doc_id if not specified
      else:
          stepN_cfg.append(cfg.get_param('step%d_cfg'%s,'',section))
          stepN_docID.append(cfg.get_param('step%d_docID'%s,'',section))

  transient_output = cfg.get_param('transient_output',[],section)

  request_type = cfg.get_param('request_type',default_parameters['request_type'],section)
  request_id = cfg.get_param('request_id','',section)
  events_per_job = cfg.get_param('events_per_job','',section)
  events_per_lumi = int(float(cfg.get_param('events_per_lumi',100,section))) # 100 is legacy
  force_lumis = cfg.get_param('force_lumis', False, section)
  brute_force = cfg.get_param('brute_force', False, section)
  margin = cfg.get_param('margin', 0.05, section)
  lumi_list = cfg.get_param('lumi_list', '', section)

  # Upload to couch if needed or check in the cfg dict if there
  for step in range(max_step):
    step_cfg_name= stepN_cfg[step]
    step_docid = stepN_docID[step]
    #print step_cfg_name, step_docid

    if step_cfg_name!='' and step_docid=='' :
      #print step_cfg_name, step_docid
      # try to see if it is in the cfg name dict
      if cfg_docid_dict.has_key(step_cfg_name):
        print "Using the one in the cfg-docid dictionary." 
        stepN_docID[step] = cfg_docid_dict[step_cfg_name]
      else:
        print "No DocId found for section %s. Uploading the cfg to the couch." %section
        stepN_docID[step] = wma.upload_to_couch(step_cfg_name, section, user, group,test_mode)

  if harvest_docID=='' and harvest_cfg!='':
      harvest_docID= wma.upload_to_couch(harvest_cfg , section, user, group,test_mode)
      
  ## check if the request is valid
  #there could be more checks here !!!
  if stepN_docID[0]=='' and url_dict=="":
    print "Invalid request, no docID configuration specified."
    print stepN_docID
    print stepN_cfg
    sys.stderr.write("[wmcontrol exception] Invalid request, no docID configuration specified.")
    sys.exit(-1)

  # Extract Campaign from PREP-ID if necessary
  campaign = cfg.get_param('campaign','',section)
  if campaign =="" and request_id=="":
    print "Campaign and request-id are not set. Provide at least the Campaign."
  elif campaign =="" and request_id!="":
    campaign = re.match(".*-(.*)-.*",request_id).group(1)
  elif campaign !="" and request_id!="":
    print "Campaign and request-id are set. Using %s as campaign." %campaign

  time_per_campaign=wma.time_per_events(campaign)
  if time_per_campaign:
      time_event=time_per_campaign

  service_params={"section": section,
                  "version": version,
                  "request_type": request_type,

                  'cfg_docid_dict' : cfg_docid_dict,
                  'req_name': req_name,
                  "batch": batch,
                  "process_string": process_string,
                  'force_lumis': force_lumis,
                  'brute_force': brute_force,
                  'lumi_list': lumi_list,
                  'margin': margin
                  }
  
  for i in range(max_step):
      s=i+1
      ## not sure that this is necessary actually to put in the service params
      service_params.update({ 'step%d_cfg'%s : stepN_cfg[i],
                              'step%d_docID'%s : stepN_docID[i],
                              'keep_step%d'%s : keep_stepN[i],
                              'step%d_output'%s : stepN_output[i]
                              })

  # According to the rerquest type, cook a request!
  params={"CMSSWVersion": release,
          "ScramArch": scramarch,
          "RequestPriority": priority,
          "RunWhitelist": ['Will Be replaced'],
          "InputDataset": 'Will Be replaced',
          "RunBlacklist": [],
          "BlockWhitelist": blocks,
          "BlockBlacklist": [],
          "DbsUrl": dbsurl,
          "RequestType": request_type,
          "GlobalTag": globaltag,
          "inputMode": "couchDB",
          "RequestString": "Will Be dynamically created",
          "Group": group,
          "Requestor": user,
          "Campaign": campaign,
          "Memory": size_memory,
          "SizePerEvent": size_event,
          "TimePerEvent": time_event,
          "OpenRunningTimeout" : open_running_timeout,
          #"ConfigCacheUrl": wma.COUCH_DB_ADDRESS,
          #"EnableHarvesting" : False
          "ProcessingString": processing_string
          }


  if wmtest:
      params["ConfigCacheUrl"] = wma.COUCH_DB_ADDRESS
      params["DbsUrl"] = "https://" + wma.WMAGENT_URL + wma.DBS3_URL

  if url_dict != "":
      #print "This is the url",url_dict,"to get the dict from"
      params = json.loads(os.popen('curl -s --insecure %s'%(url_dict)).read())
      #print params
      service_params["request_type"] = params["RequestType"]
      service_params["version"] = params["ProcessingVersion"]
      service_params["process_string"] = "T"
      service_params["pid"] = params["RequestString"]
      params["DbsUrl"] = "https://"+wma.WMAGENT_URL+wma.DBS3_URL
      params["CouchURL"] = wma.COUCH_DB_ADDRESS
      params["ConfigCacheURL"] = wma.COUCH_DB_ADDRESS
  elif request_type == "ReReco":
    if number_events:
        if blocks:
            ## cannot perform automatic block selection
            print "\n\n\n WARNING number_events is not functionnal because you specified blocks in input\n\n\n"
        else:
            print "\n\n\n WARNING automated block selection performed \n\n\n"
            params.update({"RequestNumEvents" : number_events})

    params.update({"ConfigCacheID": stepN_docID[0],
                   "Scenario": "pp",
                   "IncludeParents" : includeparents,
                   "PrepID": request_id,
                   "TransientOutputModules":transient_output})


    if skim_docid != '':
      print "This is a skim"
      params.update({"SkimName1" : skim_name,
                      "SkimInput1" : skim_input,
                      "Skim1ConfigCacheID" : skim_docid,
                      "nskims" : 1})


  elif request_type == 'MonteCarlo':


      params.update({"RequestString": identifier,
                     "FirstEvent": 1,
                     "FirstLumi": 1,
                     "TimePerEvent": time_event,
                     "FilterEfficiency": filter_eff,
                     "LheInputFiles" : cfg.get_param('lhe_input',False,section),
                     "RequestNumEvents": number_events,
                     "ConfigCacheID": stepN_docID[0],
                     "PrimaryDataset": primary_dataset,
                     "PrepID": request_id,
                     }
                    )

      events_per_lumi = int(float( events_per_lumi ) / float(filter_eff))
      params.update({"EventsPerLumi" : events_per_lumi,})

      if wmtest:
          params.pop("EventsPerLumi")

      if params["LheInputFiles"]=='True' or params["LheInputFiles"]==True:
          #max out to 500K for "lhe step zero"
          print "Setting events per job here !!!!",type(params["LheInputFiles"]),params["LheInputFiles"]
          events_per_job=500000
          if wmtest:
              events_per_job=15000

      if events_per_job and int(events_per_job):
          params.update({
              "EventsPerJob" : int(events_per_job)
              })

      if pileup_dataset:
          params.update({"MCPileup": pileup_dataset})

      params.pop('BlockBlacklist')
      params.pop('BlockWhitelist')
      params.pop('InputDataset')
      params.pop('RunBlacklist')

  elif request_type == 'MonteCarloFromGEN':
    params.update({"TimePerEvent": time_event,
                "FilterEfficiency": filter_eff,
                "ConfigCacheID": stepN_docID[0],
                "PrepID": request_id,
                "TotalTime": 28800 })

    if primary_dataset:
        params.update({"PrimaryDataset": primary_dataset})

    if pileup_dataset:
      params.update({"MCPileup": pileup_dataset})

    if int(number_events):
        params.update({"RequestNumEvents": number_events})

  elif request_type == 'LHEStepZero':
      params.update({"RequestString": identifier,
                     "TimePerEvent": time_event,
                     "FirstEvent": 1,
                     "FirstLumi": 1,
                     "LheInputFiles" : cfg.get_param('lhe_input',False,section),
                     "Memory": 2300,
                     "SizePerEvent": size_event,
                     "ConfigCacheID": stepN_docID[0],
                     "RequestNumEvents": number_events,
                     "PrimaryDataset": primary_dataset,
                     "PrepID": request_id,
                     "TotalTime": 28800 ,
                     "EventsPerLumi":300,
                     "ProdJobSplitAlgo" : "EventBased",
                     "ProdJobSplitArgs" : {"events_per_job": int(events_per_job),"events_per_lumi": int(events_per_lumi)}
                    })

      params.pop('BlockBlacklist')
      params.pop('BlockWhitelist')
      params.pop('InputDataset')
      params.pop('RunBlacklist')
      params.pop('RunWhitelist')

  elif request_type == 'ReDigi':
    if number_events:
        if blocks:
            ## cannot perform automatic block selection
            print "\n\n\n WARNING number_events is not functionnal because you specified blocks in input\n\n\n"
        else:
            print "\n\n\n WARNING automated block selection performed \n\n\n"
            params.update({"RequestNumEvents" : number_events})

    params.update({"RequestString": identifier,
                   "MCPileup": pileup_dataset,
                   #"Scenario": "pp",
                   "PrepID": request_id})

    if primary_dataset:
        params.update({"PrimaryDataset": primary_dataset})

    last=0
    for i in range(max_step):
        sname=step_words[s+1]
        if stepN_docID[i]:
            params.update({"Step%sConfigCacheID"%sname : stepN_docID[i],
                           "KeepStep%sOutput"%sname : keep_StepN[i],
                           "Step%sOutputModuleName"%sname : stepN_output[i]
                           })
            last=i
        else:
            ## there is no more valid docID
            break

    if not keep_StepN[last]:
        print "Request not keeping its last output"
        raise Exception("The request step %s output is not kept"% step_word[last])

  elif request_type == 'TaskChain':

      params.pop('RunBlacklist')
      params.pop('BlockWhitelist')
      params.pop('BlockBlacklist')

      params['TaskChain']=0
      task_index=0
      while stepN_docID[task_index]:
          task_number = task_index+1
          task_dict =  {'SplittingAlgorithm': 'LumiBased',
                        'SplittingArguments': {'lumis_per_job': int(cfg.get_param('step%d_lumisperjob'%task_number,4,section))},
                        'TaskName':'Task%d'%task_number,
                        'GlobalTag' : cfg.get_param('step%d_globaltag'%task_number,globaltag,section),
                        'CMSSWVersion' : cfg.get_param('step%d_release'%task_number,release,section),
                        'ConfigCacheID' : stepN_docID[task_index],
                        'ProcessingVersion' : version
                        }
          
          if task_index:
              task_dict['InputFromOutputModule'] = stepN_output[task_index]
              task_dict['InputTask'] = cfg.get_param('step%d_input'%task_number,'Task%d'%task_index,section)
                        

          task_dict.update({'ProcessingString' : cfg.get_param('step%s_processstring'%task_number,task_dict['GlobalTag'],section),
                            'AcquisitionEra' : cfg.get_param('step%s_era'%task_number,task_dict['CMSSWVersion'],section),
                           
                           })
          params['Task%d'%task_number] = copy.deepcopy( task_dict )
          params['TaskChain']+=1
          task_index+=1
                        
          

      #from pprint import pformat
      #print "\n current dictionnary \n",pformat(params),'\n\n'

      ###raise Exception('Unknown request type, aborting')

  elif request_type == "DQMHarvest":
     params.update({
                     "ConfigCacheUrl": "https://cmsweb.cern.ch/couchdb",
                     "DQMHarvestUnit": "byRun",
                     "Scenario": "pp",
                     "PrepID": request_id,
                     "TransientOutputModules":transient_output,
                     "DQMUploadUrl" : "https://cmsweb.cern.ch/dqm/offline",
                     "DQMConfigCacheID" : harvest_docID})
     del (params["OpenRunningTimeout"])

  else:
      print "Request type chose: "+str(request_type)
      raise Exception('Unknown request type, aborting')

  if harvest_docID and request_type!="DQMHarvest":
      ##setup automatic harvesting
      params.update({"EnableHarvesting" : 1,
                     "DQMUploadUrl" : "https://cmsweb.cern.ch/dqm/offline",
                     "DQMConfigCacheID" : harvest_docID})


  ## pop any empty parameters
  for (param,value) in params.items():
      if value in ["",[]]:
          params.pop(param)

  return params,service_params

#-------------------------------------------------------------------------------

def build_parser():
  '''
  No defaults given here,but set them in build_params_dict .
  '''
  # Example cfg
  example_cfg = "\n[MyDescriptionOfTheRequest]\n"
  example_cfg+= "dset_run_dict = {\"/DoubleElectron/Run2011B-v1/RAW\" : get_runs('/MinimumBias/Run2011B-v1/RAW',maxrun=177718)}\n"
  example_cfg+= "docID = 8216d7bbd56664bc2a5853fb4f02d0f9\n"
  example_cfg+= "release = CMSSW_4_2_8_patch3\n"
  example_cfg+= "globaltag = GR_R_42_V20::All\n"
  example_cfg+= "\n[MyDescriptionOfTheRequest2]\n"
  example_cfg+= "# The second request!\n"
  example_cfg+= "dset_run_dict = {\"/DoubleElectron/Run2011B-v1/RAW\" : get_runs('/MinimumBias/Run2011B-v1/RAW')}\n"
  example_cfg+= "cfg_path = /my/abs/path/my_rereco_pp.py"
  example_cfg+= "release = CMSSW_4_2_8_patch3\n"
  example_cfg+= "globaltag = GR_R_42_V20::All\n"
  example_cfg+= "\n  --> For more help please see the example_requests.conf file!\n"
  # Here we define an option parser to handle commandline options..
  usage = 'usage: %prog <options>\n'
  usage+= '\n\nExample cfg:\n'
  usage+= example_cfg
  # https://docs.python.org/2/library/optparse.html
  parser = optparse.OptionParser(usage,option_class=ExtendedOption)

  parser.add_option('--arch', help='SCRAM_ARCH', dest='scramarch')
  parser.add_option('--release', help='Production release', dest='release')
  parser.add_option('--request-type', help='Request type: "MonteCarlo","MonteCarloFromGEN","ReDigi"' , dest='request_type')
  parser.add_option('--conditions', help='Conditions Global Tag' , dest='globaltag')
  parser.add_option('--request-id', help='Request identifier' , dest='request_id')
  parser.add_option('--input-ds', help='Input Data Set name' , dest='input_name')
  parser.add_option('--blocks', help='comma separated list of input blocks to be processed' , dest='blocks')  
  parser.add_option('--pileup-ds', help='Pile-Up input Data Set name' , dest='pu_dataset')
  parser.add_option('--cfg_path', help='Alias for step 1 configuration' , dest='cfg_path')

  for i in range(max_step):
      s=i+1
      parser.add_option('--step%d-cfg'%s, help='step %d configuration'%s, dest='step%d_cfg'%s)
      parser.add_option('--step%d--docID'%s, help='step %d configuration docId'%s, dest='step%d_docID'%s)
      parser.add_option('--keep-step%d'%s, help='step %d output keeping flag'%s, dest='keep_step%d'%s, action='store_true')
      parser.add_option('--step%d-output'%s, help='step %d output moule'%s, dest='step%d_output'%s)

      
  parser.add_option('--priority',help='priority flag' ,dest='priority')
  parser.add_option('--primary-dataset',help='primary dataset name' ,dest='primary_dataset')
  parser.add_option('--time-event',help='time per event in seconds (Default 10)' , dest='time_event', default=10)
  parser.add_option('--filter-eff',help='filter efficiency' ,dest='filter_eff')
  parser.add_option('--number-events',help='number of events' ,dest='number_events', default=0)
  parser.add_option('--events-per-job', help='number of events per job (for LHE production)' , dest='events_per_job', default=0)
  parser.add_option('--events-per-lumi',help='number of events per lumisection (for request from scratch)', dest='events_per_lumi', default=100)
  parser.add_option('--version', help='submission version' , dest='version')
  parser.add_option('--cfg_db_file', help='File containing the cfg name docid pairs' , dest='cfg_db_file')
  parser.add_option('--user', help='The registered username' , dest='user')
  parser.add_option('--group', help='The group to which the user belong' , dest='group')
  parser.add_option('--lhe', help='specify that there is .lhe file in input', dest='lhe_input', default=False, action='store_true')

  ##New parametters as of 2012-08-22
  parser.add_option('--memory', help='RSS memory in MB (Default 1500)', dest='size_memory', default=2300)
  parser.add_option('--size-event', help='Expected size per event in KB (Default 2000)', dest='size_event', default=2000)
  parser.add_option('--test', help='To test things', action='store_true' , dest='test')
  parser.add_option('--wmtest', help='To inject requests to the cmsweb test bed', action='store_true' , dest='wmtest')
  parser.add_option('--wmtesturl', help='To inject to a specific testbed', dest='wmtesturl', default='cmsweb-testbed.cern.ch')
  parser.add_option('--includeparents', help='Include parents', action='store_true' , dest='includeparents')
  parser.add_option('--req_name', help='Set the name of the request', dest='req_name')
  parser.add_option('--process-string', help='string to be added in the name of the request' , dest='process_string',default='')
  parser.add_option('--processing-string', help='process string do be added in the second part of dataset name' , dest='processing_string',default='') 
  parser.add_option('--batch', help='Include in the WF batch number' , dest='batch')
  parser.add_option('--open-running-timeout', help='how long(finite) a request should remain opened, in seconds' , dest='open_running_timeout',default=43200)

  # Param to be inline with prep wmcontrol
  parser.add_option('--campaign', help='The name of the era (was: campaign; NO LNOGER)' , dest='campaign', default = "")
  # The config file
  parser.add_option('--req_file', help='The ini configuration to launch requests' , dest='req_file')
  parser.add_option('--url-dict', help='Pickup a dict from a given url', default="", dest='url_dict')

  parser.add_option('--force-lumis', help='Force lumis-based splitting',
                    action='store_true', dest='force_lumis')
  parser.add_option('--brute-force', help='Use brute force algorithm',
                    action='store_true', dest='brute_force')
  parser.add_option('--margin', help='Specify margin for splitting',
                    default=0.05, dest='margin')
  parser.add_option('--lumi-list', help='Specify lumisections',
                    default='', dest='lumi_list')
  return parser

#-------------------------------------------------------------------------------

banner=\
'###########################################################################\n'\
'#                                                                         #\n'\
'#    WMAControl: the swiss army knife for central requests submission     #\n'\
'#                                                                         #\n'\
'###########################################################################\n'

if __name__ == "__main__":

    print banner

    # Build a parser
    # https://docs.python.org/2/library/optparse.html
    parser = build_parser()

    # here we have all parameters, taken from commandline or config
    config = Configuration(parser)

    # loop on the requests and submit them
    loop_and_submit(config)
