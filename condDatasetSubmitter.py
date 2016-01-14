#! /usr/bin/env python


import os
import sys
import re
from optparse import OptionParser
import datetime
import json

sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/prod/devel/')
from phedex import phedex

  
DRYRUN=False

#-------------------------------------------------------------------------------

def createOptionParser():
  global DRYRUN
  usage=\
  """
  ConditionValidation.py --gt <GT> --run <run> --conds <condition json>
  """

  parser = OptionParser(usage)
  parser.add_option("--newgt",
                    dest="newgt",
                    help="new global tag containing tag to be tested")
  parser.add_option("--gt",
                    dest="gt",
                    help="common/reference global tag to both submissions")
  parser.add_option("--basegt",
                    dest="basegt",
                    default="",
                    help="common global tag to base RECO+HLT/HLT+RECO submissions")
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
                    choices=['HLT','PR','RECO+HLT','HLT+RECO'],
                    default='HLT')
  parser.add_option("--DQM",
                    help="Specify what is the DQM sequence needed for PR",
                    default=None)
  parser.add_option("--HLT",
                    help="Specify which default HLT menu: SameAsRun uses the HLT menu corrresponding to the run, Custom lets you choose it explicitly",
                    choices=['SameAsRun','GRun','Custom'],
                    default=None)
  parser.add_option("--HLTCustomMenu",
                    help="Specify a custom HLT menu",
                    default=None)
  parser.add_option("--recoCmsswDir",
                    help="CMSSW base directory for RECO step if different from HLT step (supported for HLT+RECO type)",
                    default=None)
  parser.add_option("--noSiteCheck",
                    help="Prevents the site check to be operated",
                    default=False,
                    action='store_true')
                     
  (options,args) = parser.parse_args()

#  if not options.gt or not options.run or not options.conds:
#      parser.error("options --run, --gt and --conds are mandatory")
  if not options.newgt or not options.gt or not options.run:
      parser.error("options --newgt, --run, and --gt  are mandatory")

  CMSSW_VERSION='CMSSW_VERSION'
  if not os.environ.has_key(CMSSW_VERSION):
    print "CMSSW not properly set. Exiting"
    sys.exit(1)
  options.release = os.getenv(CMSSW_VERSION)
  
  CMSSW_BASE='CMSSW_BASE'
  options.hltCmsswDir = os.getenv(CMSSW_BASE)

  options.recoRelease = None
  if options.recoCmsswDir:
    path_list = options.recoCmsswDir.split('/')
    for path in path_list:
      if path.find("CMSSW")!=-1:
        options.recoRelease = path  
    
  if options.dry:
    DRYRUN=True

  options.ds=options.ds.split(',')
  options.run = options.run.split(',')

  return options

#-------------------------------------------------------------------------------

def getConfCondDictionary(conditions_filename):
  # read the tags fromt eh list
  #newCtags=eval(open(options.conds).read())
  
  ConfCondList=[ ('REFERENCE.py',options.gt) ]
  ConfCondDictionary={
      'REFERENCE.py':options.gt
      }
    
  #for (i,condbunch) in enumerate(newCtags):
  #    ConfCondDictionary['NEWCONDITIONS%s.py'%i]='%s'%('+'.join(map(lambda r : ','.join(r),condbunch)))
  #    ConfCondList.append( ('NEWCONDITIONS%s.py'%i, '%s'%('+'.join(map(lambda r : ','.join(r),condbunch))) ) )

  ConfCondDictionary['NEWCONDITIONS0.py']=options.newgt
  ConfCondList.append( ('NEWCONDITIONS0.py', options.newgt ) ) 
  #return ConfCondDictionary
  return ConfCondList

#-------------------------------------------------------------------------------

def isPCLReady(run):
  mydict = json.loads(os.popen('curl -L --cookie ~/private/ssocookie.txt --cookie-jar ~/private/ssocookie.txt https://cms-conddb-prod.cern.ch/pclMon/get_latest_runs?run_class=Cosmics% -k').read())

  #print mydict
  
  #for line in os.popen('curl -s http://cms-alcadb.web.cern.ch/cms-alcadb/Monitoring/PCLTier0Workflow/log.txt').read().split('\n'):
  #  if not line: continue
  #  spl=line.split()
  #  if spl[0]==str(run):
  #    ready=eval(spl[7])
  #    print "\n\n\tPCL ready for ",run,"\n\n"
  #    return ready
  
  return False

def isAtSite(ds, run):
  blocks=[]
  #dbsq1='dbs search --noheader --production --query "find block,block.status where dataset = %s and run = %s"'%(ds,run)
  #os.system('curl https://cmsweb.cern.ch/das/cli --insecure > das_client.py')
  #os.system('chmod a+x das_client.py')
  dbsq1='./das_client.py --limit=0 --query="block dataset=%s run=%s"'%(ds,run)
  ph=phedex(ds)
  print dbsq1
  for line in os.popen(dbsq1):
      if line.find("#")==-1: continue
      block=line.split()[0]
      #status=int(line.split()[1])
      #if status!=0:
      #  print block,'not closed'
      #  continue

      for b in filter(lambda b :b.name==block,ph.block):
        for replica in filter(lambda r : r.custodial=='y',b.replica):
          if replica.complete!='y':
            print block,'not complete at custodial site'
          else:
            blocks.append('#'+block.split('#')[-1])
            
  if len(blocks)==0:
    print "No possible block for %s in %s"%(run,ds)
    return False
  else:
    print "\n\n\t Block testing at succeeded for %s in %s \n\n"%(run,ds)
    return list(set(blocks))

#-------------------------------------------------------------------------------
## decommissionned because we could run anywhere
#def checkIsAtFnal(run, ds):
#  if not isAtFnal (run, ds):
#    print "Run %s of %s is not at fnal. Impossible to continue." %(run, ds)
#    sys.exit(1)

#-------------------------------------------------------------------------------

def getDriverDetails(Type):
  HLTBase= {"reqtype":"HLT",
            "steps":"HLT,DQM", #replaced DQM:triggerOfflineDQMSource with DQM
            "procname":"HLT2",
            "datatier":"RAW,DQM ",
            "eventcontent":"FEVTDEBUGHLT,DQM",
            "inputcommands":'keep *,drop *_hlt*_*_HLT,drop *_TriggerResults_*_HLT',
            #"custcommands":'process.schedule.remove( process.HLTriggerFirstPath )',
            "custcommands":"process.load('Configuration.StandardSequences.Reconstruction_cff'); " +\
                           "process.hltTrackRefitterForSiStripMonitorTrack.src = 'generalTracks'; " +\
                           "\ntry:\n\tif process.RatesMonitoring in process.schedule: process.schedule.remove( process.RatesMonitoring );\nexcept: pass",
            "custconditions":"JetCorrectorParametersCollection_CSA14_V4_MC_AK4PF,JetCorrectionsRecord,frontier://FrontierProd/CMS_CONDITIONS,AK4PF",
            "inclparents":"True"}
  HLTRECObase={"steps":"RAW2DIGI,L1Reco,RECO",
               "procname":"RECO",
               "datatier":"RAW-RECO",
               "eventcontent":"RAWRECO",
               "inputcommands":'',
               "custcommands":'',               
               }

  if options.HLT:
    HLTBase.update({"steps":"HLT:%s,DQM"%(options.HLT)}) #replaced DQM:triggerOfflineDQMSource with DQM
  if Type=='HLT':
    return HLTBase
  elif Type=='RECO+HLT':
    HLTBase.update({'base':HLTRECObase})
    return HLTBase
  elif Type=='HLT+RECO':
    if options.HLT:
      HLTBase.update({"steps":"HLT:%s"%(options.HLT),
                      "custcommands":"\ntry:\n\tif process.RatesMonitoring in process.schedule: process.schedule.remove( process.RatesMonitoring );\nexcept: pass",
                      "custconditions":"",
                      "datatier":"RAW",
                      "eventcontent":"FEVTDEBUGHLT"})
    else:
      HLTBase.update({"steps":"HLT",
                      "custcommands":"\ntry:\n\tif process.RatesMonitoring in process.schedule: process.schedule.remove( process.RatesMonitoring );\nexcept: pass",
                      "custconditions":"",
                      "datatier":"RAW",
                      "eventcontent":"FEVTDEBUGHLT"})
    HLTRECObase={"steps":"RAW2DIGI,L1Reco,RECO,DQM", #replaced DQM:triggerOfflineDQMSource with DQM
                "procname":"RECO",
                "datatier":"RECO,DQMIO",
                "eventcontent":"RECO,DQM",
                "inputcommands":'keep *',
                #"custcommands":'\nfrom Configuration.Applications.ConfigBuilder import ConfigBuilder\nprocess.triggerOfflineDQMSource.visit(ConfigBuilder.MassSearchReplaceProcessNameVisitor("HLT", "HLT2", whitelist = ("subSystemFolder",)))'}
                #"custcommands":'\nfrom Configuration.Applications.ConfigBuilder import ConfigBuilder\nprocess.DQMOffline.visit(ConfigBuilder.MassSearchReplaceProcessNameVisitor("HLT", "HLT2", whitelist = ("subSystemFolder",)))'
                "custcommands":''}
    HLTBase.update({'recodqm':HLTRECObase})    
    return HLTBase
  elif Type=='PR':
    theDetails={"reqtype":"PR",
                "steps":"RAW2DIGI,L1Reco,RECO,DQM",
                "procname":"RECO",
                "datatier":"DQM ",
                "eventcontent":"DQM",
                "inputcommands":'',
                "custcommands":'',
                "inclparents":"False"}
    if options.DQM:
      theDetails["steps"]="RAW2DIGI,L1Reco,RECO,DQM:%s"%(options.DQM)
    return theDetails

#-------------------------------------------------------------------------------

def execme(command):
  if DRYRUN:
    print command
  else:
    print " * Executing: %s..."%command
    os.system(command)
    print " * Executed!"

#-------------------------------------------------------------------------------
def createHLTConfig(options):

  if options.HLT=="SameAsRun":    
    hlt_command="hltGetConfiguration --cff --offline " +\
                "run:%s "%options.run[0] +\
                "> %s/src/HLTrigger/Configuration/python/HLT_%s_cff.py"%(options.hltCmsswDir,options.HLT)
                
  elif options.HLT=="Custom":
    hlt_command="hltGetConfiguration --cff --offline " +\
                "%s "%options.HLTCustomMenu +\
                "> %s/src/HLTrigger/Configuration/python/HLT_%s_cff.py"%(options.hltCmsswDir,options.HLT)
      
  cmssw_command = "cd %s; eval `scramv1 runtime -sh`; cd -"%options.hltCmsswDir
  build_command = "cd %s/src; eval `scramv1 runtime -sh`; scram b; cd -"%options.hltCmsswDir
  execme(cmssw_command)
  execme(hlt_command)
  execme(build_command)

def createCMSSWConfigs(options,confCondDictionary,allRunsAndBlocks):

  details=getDriverDetails(options.Type)
  if options.DQM:
    details
  # Create the drivers
  #print confCondDictionary
  #for cfgname,custconditions in confCondDictionary.items():
  for c in confCondList:
    (cfgname,custgt) = c
    print "\n\n\tCreating for",cfgname,"\n\n"
    driver_command="cmsDriver.py %s " %details['reqtype']+\
       "-s %s " %details['steps'] +\
       "--processName %s " % details['procname'] +\
       "--data --scenario pp " +\
       "--datatier %s " % details['datatier'] +\
       "--eventcontent %s " %details['eventcontent']  +\
       "--conditions %s " %custgt +\
       "--python_filename %s " %cfgname +\
       "--no_exec --customise SLHCUpgradeSimulations/Configuration/muonCustoms.customise_csc_PostLS1 " +\
       "--dump_python " +\
       "-n 100 "
    if details['inputcommands']!="":
      driver_command += '--inputCommands "%s" '%details['inputcommands']
    if details['custconditions']!="":
      driver_command += '--custom_conditions="%s" ' %details['custconditions']
    if details['custcommands']!="":
      driver_command += '--customise_commands="%s" ' %details['custcommands']       

    cmssw_command = "cd %s; eval `scramv1 runtime -sh`; cd -"%options.hltCmsswDir
    execme(cmssw_command)
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
                      "--no_exec " +\
                      "-n 100 "
      execme(driver_command)
      
    recodqm = None
    if 'recodqm' in details:
      recodqm=details['recodqm']
      driver_command="cmsDriver.py %s " %details['reqtype']+\
                      "-s %s " %recodqm['steps'] +\
                      "--processName %s " % recodqm['procname'] +\
                      "--data --scenario pp " +\
                      "--datatier %s " % recodqm['datatier'] +\
                      "--eventcontent %s " %recodqm['eventcontent']  +\
                      "--conditions %s " %options.basegt +\
                      "--hltProcess HLT2 " +\
                      "--filein=file:HLT_HLT.root " +\
                      "--python_filename recodqm.py " +\
                      "--no_exec --customise Configuration/DataProcessing/RecoTLR.customisePromptRun2 " +\
                      "-n 100 " +\
                      "--customise_commands='%s' " %recodqm['custcommands']
      if options.recoCmsswDir:
        cmssw_command = "cd %s; eval `scramv1 runtime -sh`; cd -"%options.recoCmsswDir
        execme(cmssw_command)
      execme(driver_command)
      
      driver_command="cmsDriver.py step4 " +\
                      "-s HARVESTING:dqmHarvesting " +\
                      "--data --scenario pp " +\
                      "--filetype DQM " +\
                      "--conditions %s "%options.basegt +\
                      "--filein=file:HLT_RAW2DIGI_L1Reco_RECO_DQM_inDQM.root " +\
                      "--python_filename=step4_HARVESTING.py " +\
                      "--no_exec " +\
                      "-n 100 "
      execme(driver_command)
      

  #matched=re.match("(.*)::All",options.gt)
  #gtshort=matched.group(1)
  matched=re.match("(.*),(.*),(.*)",options.newgt)
  if matched: 
    gtshort=matched.group(1)
  else:
    gtshort=options.newgt
    
  matched=re.match("(.*),(.*),(.*)",options.gt)
  if matched: 
    refgtshort=matched.group(1)
  else:
    refgtshort=options.gt
    
  if base:
    subgtshort = gtshort
    refsubgtshort = refgtshort
    #matched=re.match("(.*)::All",options.basegt)
    #gtshort=matched.group(1)
    matched=re.match("(.*),(.*),(.*)",options.basegt)
    if matched:
      gtshort=matched.group(1)
    else:
      gtshort=options.basegt
      
  if recodqm:
    subgtshort = gtshort
    refsubgtshort = refgtshort
    #matched=re.match("(.*)::All",options.basegt)
    #gtshort=matched.group(1)
    matched=re.match("(.*),(.*),(.*)",options.basegt)
    if matched:
      gtshort=matched.group(1)
    else:
      gtshort=options.basegt

    
  
  # Creating the WMC cfgfile
  wmcconf_text= '[DEFAULT] \n'+\
                'group=ppd \n'+\
                'user=%s\n' %os.getenv('USER')
  if base or recodqm:
    wmcconf_text+='request_type= TaskChain \n'
  else:
    wmcconf_text+='request_type= ReReco \n'+\
                  'includeparents = %s \n' %details['inclparents']
  if recodqm:
    wmcconf_text+='priority = 999999 \n'+\
                  'release=%s\n' %options.release +\
                  'globaltag =%s \n' %subgtshort
  else:
    wmcconf_text+='priority = 999999 \n'+\
                  'release=%s\n' %options.release +\
                  'globaltag =%s \n' %gtshort
  wmcconf_text+='dset_run_dict= {'
  for ds in options.ds:
    wmcconf_text+='"%s" : [%s],\n '%(ds, ','.join(options.run+ map(lambda s :'"%s"'%(s),allRunsAndBlocks[ds])))
  wmcconf_text+='}\n\n'
  if base:
    wmcconf_text+='[HLT_validation]\n'+\
                   'cfg_path = reco.py\n' +\
                   'req_name = %s_RelVal_%s\n'%(details['reqtype'],options.run[0]) +\
                   '\n\n'
  elif recodqm:
    pass
  else:
    wmcconf_text+='[%s_default]\n' %details['reqtype'] +\
                   'cfg_path = REFERENCE.py\n' +\
                   'req_name = %s_reference_RelVal_%s\n'%(details['reqtype'],options.run[0]) ## take the first one of the list to label it

  task=2
  print confCondList
  for (i,c) in enumerate(confCondList):
    cfgname=c[0]
    if "REFERENCE" in cfgname:
      if base:
        wmcconf_text+='step%d_output = RAWRECOoutput\n'%task +\
                       'step%d_cfg = %s\n'%(task,cfgname) +\
                       'step%d_globaltag = %s\n'%(task,refsubgtshort) +\
                       'step%d_input = Task1\n\n'%task
        task+=1
        continue
      elif recodqm:
        label=cfgname.lower().replace('.py','')
        wmcconf_text+='\n\n[%s_%s]\n' %(details['reqtype'],label) +\
                       'KeepOutput = True\n' +\
                       'time_event = 1\n' +\
                       'processing_string = %s_%s_%s \n'%(str(datetime.date.today()),label,refsubgtshort) +\
                       'cfg_path = %s\n'%cfgname +\
                       'req_name = %s_%s_RelVal_%s\n'%(details['reqtype'],label,options.run[0]) +\
                       'globaltag = %s\n'%(refsubgtshort) +\
                       'step%d_output = FEVTDEBUGHLToutput\n'%task +\
                       'step%d_cfg = recodqm.py\n'%task +\
                       'step%d_globaltag = %s \n'%(task,gtshort) +\
                       'step%d_processstring = %s_%s_%s \n'%(task,str(datetime.date.today()),label,refsubgtshort) +\
                       'step%d_input = Task1\n'%task +\
                       'step%d_timeevent = 20\n'%task
        if options.recoRelease:
          wmcconf_text+='step%d_release = %s \n'%(task,options.recoRelease)
        wmcconf_text+='harvest_cfg=step4_HARVESTING.py\n\n'
      else:
        continue

    if base:
      wmcconf_text+='\n\n' +\
                     'step%d_output = RAWRECOoutput\n'%task +\
                     'step%d_cfg = %s\n'%(task,cfgname) +\
                     'step%d_globaltag = %s\n'%(task,subgtshort) +\
                     'step%d_input = Task1\n\n'%task
      task+=1
    elif recodqm:
      if "REFERENCE" in cfgname: continue
      label=cfgname.lower().replace('.py','')
      wmcconf_text+='\n\n[%s_%s]\n' %(details['reqtype'],label) +\
                     'KeepOutput = True\n' +\
                     'time_event = 1\n' +\
                     'processing_string = %s_%s_%s \n'%(str(datetime.date.today()),label,subgtshort) +\
                     'cfg_path = %s\n'%cfgname +\
                     'req_name = %s_%s_RelVal_%s\n'%(details['reqtype'],label,options.run[0]) +\
                     'globaltag = %s\n'%(subgtshort) +\
                     'step%d_output = FEVTDEBUGHLToutput\n'%task +\
                     'step%d_cfg = recodqm.py\n'%task +\
                     'step%d_globaltag = %s \n'%(task,gtshort) +\
                     'step%d_processstring = %s_%s_%s \n'%(task,str(datetime.date.today()),label,subgtshort) +\
                     'step%d_input = Task1\n'%task +\
                     'step%d_timeevent = 20\n'%task
      if options.recoRelease:
        wmcconf_text+='step%d_release = %s \n'%(task,options.recoRelease)
      wmcconf_text+='harvest_cfg=step4_HARVESTING.py\n\n'
    else:
      label=cfgname.lower().replace('.py','')
      wmcconf_text+='\n\n[%s_%s]\n' %(details['reqtype'],label) +\
                     'cfg_path = %s\n'%cfgname +\
                     'req_name = %s_%s_RelVal_%s\n'%(details['reqtype'],label,options.run[0])


  wmconf_name='%sConditionValidation_%s_%s_%s.conf'%(details['reqtype'],
                                                      options.release,
                                                      gtshort,
                                                      options.run[0])
  if not DRYRUN:
    wmcconf=open(wmconf_name,'w')    
    wmcconf.write(wmcconf_text)
    wmcconf.close()
  
  #execme('wmcontrol.py --test --req_file %s'%wmconf_name)
  #print 'Now execute:\nwmcontrol.py --req_file %s'%wmconf_name  
  execme('./wmcontrol.py --test --req_file %s'%wmconf_name)
  print 'Now execute:\n./wmcontrol.py --req_file %s'%wmconf_name  

#-------------------------------------------------------------------------------

if __name__ == "__main__":
  
  # Get the options
  options = createOptionParser()

  # Check for PCL availability
  for run in options.run:
    if not isPCLReady(run):
      print "The PCL is not ready for run:",run,"... ignoring for now"
      #print "The PCL is not ready for run:",run,"... aborting"
      #sys.exit(2)

  # Check if it is at FNAL
  allRunsAndBlocks={}
  if not options.noSiteCheck:
    for ds in options.ds:
      allRunsAndBlocks[ds]=[]
      for run in options.run:
        newblocks=isAtSite( ds, run)
        if newblocks==False:
          print "Cannot proceed with %s in %s"%(ds,run)
          sys.exit(1)
        else:
          allRunsAndBlocks[ds].extend(newblocks)

  #uniquing
  for ds in allRunsAndBlocks:
    allRunsAndBlocks[ds]=list(set(allRunsAndBlocks[ds]))
    
  # Read the group of conditions from the list in the file
  confCondList= getConfCondDictionary(options)
  
  # Create the cff
  if options.HLT in ["SameAsRun","Custom"]: createHLTConfig(options)
  
  # Create the cfgs, both for cmsRun and WMControl  
  createCMSSWConfigs(options,confCondList,allRunsAndBlocks)
