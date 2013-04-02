import FWCore.ParameterSet.Config as cms

def runDepMC(process):
    from SimGeneral.Configuration.RandomRunSource import RandomRunSource
    pincoponco = cms.untracked.vstring('') 
    pincoponco = process.source.fileNames 
    process.source = RandomRunSource("PoolSource") 
# weight the three runs according to integral luminosity; 3 runs are the last runs (from DBS) of 2012B,C,D
# dbs search --query='find dataset,max(run) where dataset = /MinimumBias/Run2012D-PromptReco-v1/RECO'
    process.source.setRunDistribution([(197495,5.3),(198913,7.0),(209634,7.3)])
    process.source.fileNames = pincoponco 
    #print "ciao"
    return(process)
