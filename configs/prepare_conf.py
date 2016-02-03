#
# eval `scramv1 runtime -csh`
# if we don't source subSetupAuto we need grid proxy and crab env:
#   source  /afs/cern.ch/cms/ccs/wm/scripts/Crab/crab.sh
#   voms-proxy-init

import os
import  sys, time, json

from modules.wma import ConnectionWrapper
from Configuration.Skimming.autoSkim import autoSkim
from Configuration.AlCa.autoAlca import autoAlca
# USING LOCAL autoAlca.py
##TO-DO add option to use local instance
# for now comented out
#from autoAlca import autoAlca
print autoSkim
print autoAlca

DBS3_CONNECT = ConnectionWrapper()

customera = {}
customera["Run2015B"] = 'customiseDataRun2Common'
customera["Run2015C_50ns"] = 'customiseDataRun2Common_50nsRunsAfter253000'
customera["Run2015C_25ns"] = 'customiseDataRun2Common_25ns'
customera["Run2015D"] = 'customiseDataRun2Common_25ns'

GT = "76X_dataRun2_v15"
campaign = "Run2015D"
proc_string = "16Dec2015"
num_core = "4"

jsonFile = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/DCSOnly/json_DCSONLY.txt'

with open(jsonFile) as data_file:
    data = json.load(data_file)
#print data.keys()
AlltheRuns = map(int,data.keys())
#print sorted(AlltheRuns)
#print "# of runs in the JSON: ", len(AlltheRuns)

# select runs in Run2015D
theRuns = filter(lambda x: x >= 256630, AlltheRuns)

# The RAW datasets to process must have AOD in Prompt
theDatasets = DBS3_CONNECT.api('datasets', 'dataset', '/*/Run2015D*/RAW')
theDatasetsAOD = DBS3_CONNECT.api('datasets', 'dataset', '/*/*Run2015D*PromptReco*/AOD')

#print theDatasets
#print theDatasetsAOD
theDatasetsToProcessAOD = []
theDatasetsToProcess = []

for mydataset in theDatasetsAOD:
    tempdataset = mydataset['dataset']
    theDatasetsToProcessAOD.append((tempdataset.split('/'))[1])
print theDatasetsToProcessAOD

nd = 0

# Write DEFAULT section of the conf file
master=file('master_'+campaign+'.conf','w')
master.write("[DEFAULT] \n")
master.write("group=ppd \n")
master.write("user=fabozzi \n")
master.write("request_type=ReReco \n")
master.write("release=CMSSW_7_6_3 \n")
master.write("globaltag="+GT+" \n")
master.write("\n")
master.write("campaign="+campaign+" \n")
master.write("\n")
master.write("processing_string="+proc_string+" \n")
master.write("\n")
master.write("priority=94000 \n")
master.write("time_event=4 \n")
master.write("size_event=1600 \n")
master.write("multicore="+num_core+" \n")
master.write("harvest_cfg=harvesting.py \n")


for oneDS in theDatasets:
    theDataset= oneDS['dataset']
    if (theDataset.split('/'))[1] in theDatasetsToProcessAOD:
        runs = DBS3_CONNECT.api('runs', 'dataset', theDataset)[0]['run_num']
#    print sorted(runs)
#    print "# of runs in the dataset: ", len(runs)

        inter = set(runs) & set(theRuns)
        if len(inter) > 0 :
#    if len(inter) == 0 :
#        print "++"
#        print "** %s  has no runs in commong with theRuns"%(theDataset)
#        print sorted(runs)
#    else :
            theDatasetsToProcess.append(theDataset)
#        print theDataset
#        print sorted(inter)
#        print "# of runs in the intersection: ", len(inter)
            nd = nd+1
            theruns = sorted(inter)
            temp = theDataset.split('/')
    #    print temp
            datasetstr = temp[1]
            runstr = temp[2]
            aodstr = temp[3]

# Write the workflow section of the conf file
            master.write("\n")
            master.write("["+campaign+"-"+datasetstr+"-"+proc_string+"]")
            master.write("\n")
            master.write("dset_run_dict={\""+theDataset+"\" : "+str(theruns)+" }")
            master.write("\n")
            master.write("cfg_path=reco_"+campaign+"_"+datasetstr+".py")
            master.write("\n")

# Prepare for Alca sequence, Skim sequence, and RECO customizations
            alcaseq = ''
            skimseq = ''
            recotier = ''
            keepreco = False

# Datasets for which we want to keep RECO output
            if ( (datasetstr == "NoBPTX") or (datasetstr == "DoubleMuon") or (datasetstr=="EmptyBX") or
            ("ZeroBias" in datasetstr) or (datasetstr == "MinimumBias") or ("SingleMu" in datasetstr) ) :
                keepreco = True
                recotier = 'RECO,'

# Datasets for which we want to make skims
            if datasetstr in autoSkim.keys():
                recotier = 'RECO,'

# Datasets for which we want to make Alca datasets
            if datasetstr in autoAlca.keys():
                alcaseq='ALCA:%s,'%(autoAlca[datasetstr])

# Datasets for which we need temporary RECO output just for skimming
            if ( (datasetstr in autoSkim.keys()) and (not(keepreco)) ) :
                master.write("transient_output = [\"RECOoutput\"]")
                master.write("\n")

# cmsDriver to make reco cfg
            reco_command = 'cmsDriver.py RECO -s RAW2DIGI,L1Reco,RECO,'+alcaseq+'EI,PAT,DQM:@standardDQM+@miniAODDQM --runUnscheduled --nThreads '+num_core+ ' --data --scenario pp --conditions %s --eventcontent %sAOD,MINIAOD,DQM --datatier %sAOD,MINIAOD,DQMIO --customise Configuration/DataProcessing/RecoTLR.%s --filein blah.root -n 100 --python_filename=reco_%s_%s.py --no_exec'%(GT, recotier, recotier, customera[campaign], campaign, datasetstr)
            print reco_command
            os.system(reco_command)

# write the skim parameters in conf file
            if datasetstr in autoSkim.keys():
                master.write("skim_cfg=skim_"+campaign+"_"+datasetstr+".py")
                master.write("\n")
                master.write("skim_name=skim_"+campaign+"_"+datasetstr)
                master.write("\n")

# cmsDriver to make skim cfg
                skim_command='cmsDriver.py skim -s SKIM:%s --data --no_output --conditions %s --runUnscheduled --nThreads %s --python_filename skim_%s_%s.py --no_exec'%(autoSkim[datasetstr],GT,num_core,campaign,datasetstr)
                print skim_command
                os.system(skim_command)

# write the requestID for the workflow in the conf file
            master.write("request_id=ReReco-"+campaign+"-"+proc_string+"-"+(format(nd, '04d'))+ "\n")

print
print
print "\n".join(theDatasetsToProcess)
