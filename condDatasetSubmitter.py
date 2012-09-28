#! /usr/bin/env python

import os
import sys
import re
from optparse import OptionParser
  
DRYRUN=False
PR_GT='GR_P_V40::All'

#-------------------------------------------------------------------------------

def createOptionParser():
  global DRYRUN
  usage=\
  """
  ConditionValidation.py --gt <GT> --run <run> --conds <condition json>
  """

  parser = OptionParser(usage)
  parser.add_option("--gt",
                    dest="gt",
                    default="",
                    help="common global tag to both submissions")
  parser.add_option("--basegt",
                    dest="basegt",
                    default="",
                    help="common global tag to base RECO+HLT submissions")
  parser.add_option("--run",
                    help="the run number to be processed, can be a comma separated list")
  parser.add_option("--ds",
                    help="dataset to be processed",
                    default="/MinimumBias/Run2012B-PromptReco-v1/RECO")
  parser.add_option("--conds",
                    help="List of new tag,record,connection_string triplets to be tested")
  parser.add_option("--dry",
                    default=False,
                    action='store_true')
  parser.add_option("--Type",
                    help="Defines the type of the workflow",
                    choices=['HLT','PR','RECO+HLT'],
                    default='HLT')
  
  (options,args) = parser.parse_args()

  if options.gt=="":
    print "o No GT assigned: assuming this is %s" %PR_GT
    options.gt=PR_GT

  if not options.gt or not options.run or not options.conds:
      parser.error("options --run, --gt and --conds are mandatory")

  CMSSW_VERSION='CMSSW_VERSION'
  if not os.environ.has_key(CMSSW_VERSION):
    print "CMSSW not properly set. Exiting"
    sys.exit(1)
  options.release = os.getenv(CMSSW_VERSION)  

  if options.dry:
    DRYRUN=True

  if ',' in options.run:
    options.run = options.run.split(',')
  else:
    options.run = [options.run]
  return options

#-------------------------------------------------------------------------------

def getConfCondDictionary(conditions_filename):
  # read the tags fromt eh list
  newCtags=eval(open(options.conds).read())

  ConfCondList=[ ('REFERENCE.py','') ]
  ConfCondDictionary={
      'REFERENCE.py':''
      }
    
  for (i,condbunch) in enumerate(newCtags):
      ConfCondDictionary['NEWCONDITIONS%s.py'%i]='%s'%('+'.join(map(lambda r : ','.join(r),condbunch)))
      ConfCondList.append( ('NEWCONDITIONS%s.py'%i, '%s'%('+'.join(map(lambda r : ','.join(r),condbunch))) ) )

  #return ConfCondDictionary
  return ConfCondList

#-------------------------------------------------------------------------------

def isAtFnal(ds, run):

  stopThere=False
  block=None
  dbsq1='dbs search --noheader --production --query "find block,block.status where dataset = %s and run = %s"'%(ds,run)
  print dbsq1
  for line in os.popen(dbsq1):
      block=line.split()[0]
      status=int(line.split()[1])
      if status!=0:
          print block,'not closed'
          stopThere=True
          continue
      available=False
      for line2 in os.popen('dbs search --noheader --production --query "find block,site where block = %s and site = cmssrm.fnal.gov"'%(block)):
          site=line2.split()[1]
          available=True
      if not available:
          print block,'is not at fnal'
          stopThere=True
          continue
      print block,site,status
  if not block:
      print "No block for %s in %s"%(run,ds)
      stopThere=True
  if stopThere:
      return False
  else:
      print "\n\n\t Block testing at fnal succeeded\n\n"
      return True

#-------------------------------------------------------------------------------
def checkIsAtFnal(run, ds):
  if not isAtFnal (run, ds):
    print "Run %s of %s is not at fnal. Impossible to continue." %(run, ds)
    sys.exit(1)

#-------------------------------------------------------------------------------

def getDriverDetails(Type):
  HLTBase= {"reqtype":"HLT",
            "steps":"HLT,DQM:triggerOfflineDQMSource",
            "procname":"HLT2",
            "datatier":"RAW,DQM ",
            "eventcontent":"FEVTDEBUGHLT,DQM",
            "inputcommands":'keep *,drop *_hlt*_*_HLT,drop *_TriggerResults_*_HLT',
            "custcommands":'process.schedule.remove( process.HLTriggerFirstPath )',
            "inclparents":"True"}
  HLTRECObase={"steps":"RAW2DIGI,L1Reco,RECO",
               "procname":"RECO",
               "datatier":"RAWRECO",
               "eventcontent":"RAWRECO",
               "inputcommands":'',
               "custcommands":'',               
               }
  if Type=='HLT':
    return HLTBase
  elif Type=='RECO+HLT':
    HLTBase.update({'base':HLTRECObase})
    return HLTBase
  elif Type=='PR':
    return {"reqtype":"PR",
            "steps":"RAW2DIGI,L1Reco,RECO,DQM",
            "procname":"RECO",
            "datatier":"DQM ",
            "eventcontent":"DQM",
            "inputcommands":'',
            "custcommands":'',
            "inclparents":"False"}


#-------------------------------------------------------------------------------

def execme(command):
  if DRYRUN:
    print command
  else:
    print " * Executing: %s..."%command
    os.system(command)
    print " * Executed!"

#-------------------------------------------------------------------------------

def createCMSSWConfigs(options,confCondDictionary):

  details=getDriverDetails(options.Type)
  
  # Create the drivers
  #print confCondDictionary
  #for cfgname,custconditions in confCondDictionary.items():
  for c in confCondList:
    (cfgname,custconditions) = c
    print "\n\n\tCreating for",cfgname,"\n\n"
    driver_command="cmsDriver.py %s " %details['reqtype']+\
       "-s %s " %details['steps'] +\
       "--processName %s " % details['procname'] +\
       "--data --scenario pp " +\
       "--datatier %s " % details['datatier'] +\
       "--eventcontent %s " %details['eventcontent']  +\
       "--conditions %s " %options.gt +\
       "--python_filename %s " %cfgname +\
       "--no_exec "       
    if details['custcommands']!="":
      driver_command += '--customise_commands="%s" ' %details['custcommands']       
    if details['inputcommands']!="":
      driver_command += '--inputCommands "%s" '%details['inputcommands']
    if custconditions!="":
      driver_command += '--custom_conditions="%s" ' %custconditions 

    execme(driver_command)

    base=None
    if 'base' in details:
      base=details['base']
      driver_command="cmsDriver.py %s " %details['reqtype']+\
                      "-s %s " %base['steps'] +\
                      "--processName %s " % base['procname'] +\
                      "--data --scenario pp " +\
                      "--datatier %s " % base['datatier'] +\
                      "--eventcontent %s " %base['eventcontent']  +\
                      "--conditions %s " %options.basegt +\
                      "--python_filename reco.py " +\
                      "--no_exec "       
      execme(driver_command)
      

  matched=re.match("(.*)::All",options.gt)
  gtshort=matched.group(1)
  if base:
    subgtshort=gtshort
    matched=re.match("(.*)::All",options.basegt)
    gtshort=matched.group(1)
    
  
  # Creating the WMC cfgfile
  wmcconf_text= '[DEFAULT] \n'+\
                'group=ppd \n'+\
                'user=%s\n' %os.getenv('USER')
  if base:
    wmcconf_text+='request_type= TaskChain \n'
  else:
    wmcconf_text+='request_type= ReReco \n'+\
                  'includeparents = %s \n' %details['inclparents']
  
  wmcconf_text+='priority = 1000000 \n'+\
                'release=%s\n' %options.release +\
                'globaltag =%s::All \n' %gtshort+\
                'dset_run_dict= {"%s" : [%s]}\n '%(options.ds, ','.join(options.run)) +\
                '\n\n'
  if base:
    wmcconf_text+='[HLT_validation]\n'+\
                   'cfg_path = reco.py\n' +\
                   'req_name = %s_RelVal_%s\n'%(details['reqtype'],options.run[0]) +\
                   '\n\n'
  else:
    wmcconf_text+='[%s_default]\n' %details['reqtype'] +\
                   'cfg_path = REFERENCE.py\n' +\
                   'req_name = %s_reference_RelVal_%s\n'%(details['reqtype'],options.run[0]) ## take the first one of the list to label it



  task=2
  for (i,c) in enumerate(confCondList):
    cfgname=c[0]
    if "REFERENCE" in cfgname:
      if base:
        wmcconf_text+='step%d_output = RAWRECOoutput\n'%task +\
                       'step%d_cfg = %s\n'%(task,cfgname) +\
                       'step%d_globaltag = %s::All\n'%(task,subgtshort) +\
                       'step%d_input = Task1\n\n'%task
        task+=1
        continue
      else:
        continue

    if base:
      wmcconf_text+='\n\n' +\
                     'step%d_output = RAWRECOoutput\n'%task +\
                     'step%d_cfg = %s\n'%(task,cfgname) +\
                     'step%d_globaltag = %s::All\n'%(task,subgtshort) +\
                     'step%d_input = Task1\n\n'%task
      task+=1
    else:
      label=cfgname.lower().replace('.py','')
      wmcconf_text+='\n\n[%s_%s]\n' %(details['reqtype'],label)+\
                     'cfg_path = %s\n'%cfgname+\
                     'req_name = %s_%s_RelVal_%s\n'%(details['reqtype'],label,options.run[0])


  wmconf_name='%sConditionValidation_%s_%s_%s.conf'%(details['reqtype'],
                                                      options.release,
                                                      gtshort,
                                                      options.run[0])
  if not DRYRUN:
    wmcconf=open(wmconf_name,'w')    
    wmcconf.write(wmcconf_text)
    wmcconf.close()
  
  execme('wmcontrol.py --test --req_file %s'%wmconf_name)
  print 'Now execute:\nwmcontrol.py --req_file %s'%wmconf_name  

#-------------------------------------------------------------------------------

if __name__ == "__main__":
  
  # Get the options
  options = createOptionParser()

  # Check if it is at FNAL
  for run in options.run:
    checkIsAtFnal( options.ds,run)

  # Read the group of conditions from the list in the file
  #confCondDictionary = getConfCondDictionary(options)
  confCondList= getConfCondDictionary(options)
  # Create the cfgs, both for cmsRun and WMControl  
  #createCMSSWConfigs(options,confCondDictionary)
  createCMSSWConfigs(options,confCondList)

