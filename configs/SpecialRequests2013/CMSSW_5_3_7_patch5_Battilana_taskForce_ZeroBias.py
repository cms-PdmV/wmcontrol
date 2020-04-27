from __future__ import print_function
# Auto generated configuration file
# using: 
# Revision: 1.381.2.13 
# Source: /local/reps/CMSSW/CMSSW/Configuration/PyReleaseValidation/python/ConfigBuilder.py,v 
# with command line options: -s RAW2DIGI,L1Reco,RECO,USER:EventFilter/HcalRawToDigi/hcallaserhbhehffilter2012_cff.hcallLaser2012Filter,DQM --data --conditions FT_R_53_V18::All --eventcontent AOD,DQM --datatier AOD,DQM --customise Configuration/DataProcessing/RecoTLR.customisePrompt --no_exec --python CMSSW_5_3_7_patch5_Battilana_taskForce_ZeroBias.py --inline_custom
import FWCore.ParameterSet.Config as cms

process = cms.Process('RECO')

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')
process.load('Configuration.StandardSequences.RawToDigi_Data_cff')
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.Reconstruction_Data_cff')
process.load('EventFilter.HcalRawToDigi.hcallaserhbhehffilter2012_cff')
process.load('DQMOffline.Configuration.DQMOffline_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(1)
)

# Input source
process.source = cms.Source("PoolSource",
    secondaryFileNames = cms.untracked.vstring(),
    fileNames = cms.untracked.vstring('file:-s_DIGI2RAW.root')
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    version = cms.untracked.string('$Revision: 1.381.2.13 $'),
    annotation = cms.untracked.string('-s nevts:1'),
    name = cms.untracked.string('PyReleaseValidation')
)

# Output definition

process.AODoutput = cms.OutputModule("PoolOutputModule",
    eventAutoFlushCompressedSize = cms.untracked.int32(15728640),
    outputCommands = process.AODEventContent.outputCommands,
    fileName = cms.untracked.string('-s_RAW2DIGI_L1Reco_RECO_USER_DQM.root'),
    dataset = cms.untracked.PSet(
        filterName = cms.untracked.string(''),
        dataTier = cms.untracked.string('AOD')
    )
)

process.DQMoutput = cms.OutputModule("PoolOutputModule",
    splitLevel = cms.untracked.int32(0),
    outputCommands = process.DQMEventContent.outputCommands,
    fileName = cms.untracked.string('-s_RAW2DIGI_L1Reco_RECO_USER_DQM_inDQM.root'),
    dataset = cms.untracked.PSet(
        filterName = cms.untracked.string(''),
        dataTier = cms.untracked.string('DQM')
    )
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'FT_R_53_V18::All', '')

# Path and EndPath definitions
process.raw2digi_step = cms.Path(process.RawToDigi)
process.L1Reco_step = cms.Path(process.L1Reco)
process.reconstruction_step = cms.Path(process.reconstruction)
process.user_step = cms.Path(process.hcallLaser2012Filter)
process.dqmoffline_step = cms.Path(process.DQMOffline)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.AODoutput_step = cms.EndPath(process.AODoutput)
process.DQMoutput_step = cms.EndPath(process.DQMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.raw2digi_step,process.L1Reco_step,process.reconstruction_step,process.user_step,process.dqmoffline_step,process.endjob_step,process.AODoutput_step,process.DQMoutput_step)

# customisation of the process.

# Automatic addition of the customisation function from Configuration.DataProcessing.RecoTLR

#gone with the fact that there is no difference between production and development sequence
#def customiseCommon(process):
#    return (process)


##############################################################################
def customisePPData(process):
    #deprecated process= customiseCommon(process)
    ##all customisation for data are now deprecated to Reconstruction_Data_cff
    #left as a place holder to alter production sequences in case of emergencies
    return process


##############################################################################
def customisePPMC(process):
    #deprecated process=customiseCommon(process)
    #left as a place holder to alter production sequences in case of emergencies    
    return process

##############################################################################
def customiseCosmicData(process):

    return process

##############################################################################
def customiseCosmicMC(process):
    
    return process
        
##############################################################################
def customiseVALSKIM(process):
    print("WARNING")
    print("this method is outdated, please use RecoTLR.customisePPData")
    process= customisePPData(process)
    return process
                
##############################################################################
def customiseExpress(process):
    process= customisePPData(process)

    import RecoVertex.BeamSpotProducer.BeamSpotOnline_cfi
    process.offlineBeamSpot = RecoVertex.BeamSpotProducer.BeamSpotOnline_cfi.onlineBeamSpotProducer.clone()
    
    return process

##############################################################################
def customisePrompt(process):
    process= customisePPData(process)

    #add the lumi producer in the prompt reco only configuration
    process.reconstruction_step+=process.lumiProducer
    return process

##############################################################################
##############################################################################

#gone with the fact that there is no difference between production and development sequence
#def customiseCommonHI(process):
#    return process

##############################################################################
def customiseExpressHI(process):
    #deprecated process= customiseCommonHI(process)

    import RecoVertex.BeamSpotProducer.BeamSpotOnline_cfi
    process.offlineBeamSpot = RecoVertex.BeamSpotProducer.BeamSpotOnline_cfi.onlineBeamSpotProducer.clone()
    
    return process

##############################################################################
def customisePromptHI(process):
    #deprecated process= customiseCommonHI(process)

    import RecoVertex.BeamSpotProducer.BeamSpotOnline_cfi
    process.offlineBeamSpot = RecoVertex.BeamSpotProducer.BeamSpotOnline_cfi.onlineBeamSpotProducer.clone()
    
    return process

##############################################################################

def planBTracking(process):

    # stuff from LowPtTripletStep_cff
    process.lowPtTripletStepSeeds.RegionFactoryPSet.RegionPSet.ptMin=0.3

    # stuff from PixelLessStep_cff
    process.pixelLessStepClusters.oldClusterRemovalInfo=cms.InputTag("tobTecStepClusters")
    process.pixelLessStepClusters.trajectories= cms.InputTag("tobTecStepTracks")
    process.pixelLessStepClusters.overrideTrkQuals=cms.InputTag('tobTecStepSelector','tobTecStep')
    process.pixelLessStepSeeds.RegionFactoryPSet.RegionPSet.ptMin = 0.7
    process.pixelLessStepSeeds.RegionFactoryPSet.RegionPSet.originRadius = 1.5

    # stuff from PixelPairStep_cff
    process.pixelPairStepSeeds.RegionFactoryPSet.RegionPSet.ptMin = 0.6

    # stuff from TobTecStep_cff
    process.tobTecStepClusters.oldClusterRemovalInfo=cms.InputTag("detachedTripletStepClusters")
    process.tobTecStepClusters.trajectories= cms.InputTag("detachedTripletStepTracks")
    process.tobTecStepClusters.overrideTrkQuals=cms.InputTag('detachedTripletStep')
    process.tobTecStepSeeds.RegionFactoryPSet.RegionPSet.originRadius = 5.0

    # stuff from DetachedTripletStep_cff
    process.detachedTripletStepSeeds.RegionFactoryPSet.RegionPSet.ptMin=0.35

    # stuff from iterativeTk_cff
    process.iterTracking = cms.Sequence(process.InitialStep*
                                        process.LowPtTripletStep*
                                        process.PixelPairStep*
                                        process.DetachedTripletStep*
                                        process.TobTecStep*
                                        process.PixelLessStep*
                                        process.generalTracks*
                                        process.ConvStep*
                                        process.conversionStepTracks
                                        )
    
    
    # stuff from RecoTracker_cff
    process.newCombinedSeeds.seedCollections=cms.VInputTag(
        cms.InputTag('initialStepSeeds'),
        cms.InputTag('pixelPairStepSeeds'),
    #    cms.InputTag('mixedTripletStepSeeds'),
        cms.InputTag('pixelLessStepSeeds')
        )

    # stuff from Kevin's fragment
    process.generalTracks.TrackProducers = (cms.InputTag('initialStepTracks'),
                                            cms.InputTag('lowPtTripletStepTracks'),
                                            cms.InputTag('pixelPairStepTracks'),
                                            cms.InputTag('detachedTripletStepTracks'),
                                            cms.InputTag('pixelLessStepTracks'),
                                            cms.InputTag('tobTecStepTracks'))
    process.generalTracks.hasSelector=cms.vint32(1,1,1,1,1,1)
    process.generalTracks.selectedTrackQuals = cms.VInputTag(cms.InputTag("initialStepSelector","initialStep"),
                                                             cms.InputTag("lowPtTripletStepSelector","lowPtTripletStep"),
                                                             cms.InputTag("pixelPairStepSelector","pixelPairStep"),
                                                             cms.InputTag("detachedTripletStep"),
                                                             cms.InputTag("pixelLessStepSelector","pixelLessStep"),
                                                             cms.InputTag("tobTecStepSelector","tobTecStep")
                                                             )
    process.generalTracks.setsToMerge = cms.VPSet( cms.PSet( tLists=cms.vint32(0,1,2,3,4,5), pQual=cms.bool(True) ) )


    if hasattr(process,'dqmoffline_step'):
        process.dqmoffline_step.remove(process.TrackMonStep4)
        #process.dqmoffline_step.remove(process.TrackMonStep5)
        
    return process

#call to customisation function customisePrompt imported from Configuration.DataProcessing.RecoTLR
process = customisePrompt(process)

# End of customisation functions
