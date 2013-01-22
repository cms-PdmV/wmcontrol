# Auto generated configuration file
# using: 
# Revision: 1.381.2.13 
# Source: /local/reps/CMSSW/CMSSW/Configuration/PyReleaseValidation/python/ConfigBuilder.py,v 
# with command line options: STEP2 --step RAW2DIGI,L1Reco,RECO,VALIDATION:validation_prod,DQM:DQMOfflinePOGMC --conditions START53_V16::All NoPileUp --geometry DB:ExtendedHFLibraryNoCastor --datamix NODATAMIXER --eventcontent RECODEBUG,DQM --datatier RECODEBUG,DQM --customise Configuration/GenProduction/noCastorHFSL_customise.customise_validation -n 100 --inline_custom --no_exec
import FWCore.ParameterSet.Config as cms

process = cms.Process('RECO')

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.RawToDigi_Data_cff')
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.Reconstruction_Data_cff')
process.load('Configuration.StandardSequences.Validation_cff')
process.load('DQMOffline.Configuration.DQMOffline_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(100)
)

# Input source
process.source = cms.Source("PoolSource",
    secondaryFileNames = cms.untracked.vstring(),
    fileNames = cms.untracked.vstring('file:STEP2_DIGI2RAW.root')
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    version = cms.untracked.string('$Revision: 1.381.2.13 $'),
    annotation = cms.untracked.string('STEP2 nevts:100'),
    name = cms.untracked.string('PyReleaseValidation')
)

# Output definition

process.RECODEBUGoutput = cms.OutputModule("PoolOutputModule",
    splitLevel = cms.untracked.int32(0),
    eventAutoFlushCompressedSize = cms.untracked.int32(5242880),
    outputCommands = process.RECODEBUGEventContent.outputCommands,
    fileName = cms.untracked.string('STEP2_RAW2DIGI_L1Reco_RECO_VALIDATION_DQM.root'),
    dataset = cms.untracked.PSet(
        filterName = cms.untracked.string(''),
        dataTier = cms.untracked.string('RECODEBUG')
    )
)

process.DQMoutput = cms.OutputModule("PoolOutputModule",
    splitLevel = cms.untracked.int32(0),
    outputCommands = process.DQMEventContent.outputCommands,
    fileName = cms.untracked.string('STEP2_RAW2DIGI_L1Reco_RECO_VALIDATION_DQM_inDQM.root'),
    dataset = cms.untracked.PSet(
        filterName = cms.untracked.string(''),
        dataTier = cms.untracked.string('DQM')
    )
)

# Additional output definition

# Other statements
process.mix.playback = True
process.RandomNumberGeneratorService.restoreStateLabel=cms.untracked.string("randomEngineStateProducer")
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'START53_V16::All', '')

# Path and EndPath definitions
process.raw2digi_step = cms.Path(process.RawToDigi)
process.L1Reco_step = cms.Path(process.L1Reco)
process.reconstruction_step = cms.Path(process.reconstruction)
process.dqmoffline_step = cms.Path(process.DQMOfflinePOGMC)
process.validation_step = cms.EndPath(process.validation_prod)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.RECODEBUGoutput_step = cms.EndPath(process.RECODEBUGoutput)
process.DQMoutput_step = cms.EndPath(process.DQMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.raw2digi_step,process.L1Reco_step,process.reconstruction_step,process.validation_step,process.dqmoffline_step,process.endjob_step,process.RECODEBUGoutput_step,process.DQMoutput_step)

# customisation of the process.

# Automatic addition of the customisation function from Configuration.GenProduction.noCastorHFSL_customise

def customise_gensim(process): 

    # extended geometric acceptance (full CASTOR acceptance)

    process.g4SimHits.Generator.MinEtaCut = cms.double(-6.7)
    process.g4SimHits.Generator.MaxEtaCut = cms.double(6.7)

    # use HF shower library instead of GFlash parameterization

    process.g4SimHits.HCalSD.UseShowerLibrary = cms.bool(True)
    process.g4SimHits.HCalSD.UseParametrize = cms.bool(False)
    process.g4SimHits.HCalSD.UsePMTHits = cms.bool(False)
    process.g4SimHits.HCalSD.UseFibreBundleHits = cms.bool(False)
    process.g4SimHits.HFShower.ApplyFiducialCut = cms.bool(True)
    process.g4SimHits.HFShowerLibrary.ApplyFiducialCut = cms.bool(False)
      
    return(process)

def customise_digi(process):

    process.mix.mixObjects.mixCH = cms.PSet(
        input = cms.VInputTag(cms.InputTag("g4SimHits","CaloHitsTk"), cms.InputTag("g4SimHits","EcalHitsEB"), cms.InputTag("g4SimHits","EcalHitsEE"), cms.InputTag("g4SimHits","EcalHitsES"), cms.InputTag("g4SimHits","EcalTBH4BeamHits"), cms.InputTag("g4SimHits","HcalHits"), cms.InputTag("g4SimHits","HcalTB06BeamHits"), cms.InputTag("g4SimHits","ZDCHITS")),
        type = cms.string('PCaloHit'),
        subdets = cms.vstring('CaloHitsTk',
            'EcalHitsEB',      
            'EcalHitsEE',      
            'EcalHitsES',      
            'EcalTBH4BeamHits',
            'HcalHits',        
            'HcalTB06BeamHits',
            'ZDCHITS')         
    )
    process.calDigi = cms.Sequence(process.ecalDigiSequence+process.hcalDigiSequence)
    process.DigiToRaw = cms.Sequence(process.csctfpacker+process.dttfpacker+process.gctDigiToRaw+process.l1GtPack+process.l1GtEvmPack+process.siPixelRawData+process.SiStripDigiToRaw+process.ecalPacker+process.esDigiToRaw+process.hcalRawData+process.cscpacker+process.dtpacker+process.rpcpacker+process.rawDataCollector)

    return(process) 

def customise_validation(process):

    process.mix.mixObjects.mixCH = cms.PSet(
        input = cms.VInputTag(cms.InputTag("g4SimHits","CaloHitsTk"), cms.InputTag("g4SimHits","EcalHitsEB"), cms.InputTag("g4SimHits","EcalHitsEE"), cms.InputTag("g4SimHits","EcalHitsES"), cms.InputTag("g4SimHits","EcalTBH4BeamHits"), cms.InputTag("g4SimHits","HcalHits"), cms.InputTag("g4SimHits","HcalTB06BeamHits"), cms.InputTag("g4SimHits","ZDCHITS")),
        type = cms.string('PCaloHit'),
        subdets = cms.vstring('CaloHitsTk',
            'EcalHitsEB',      
            'EcalHitsEE',      
            'EcalHitsES',      
            'EcalTBH4BeamHits',
            'HcalHits',        
            'HcalTB06BeamHits',
            'ZDCHITS')         
    )

    return(process)

#call to customisation function customise_validation imported from Configuration.GenProduction.noCastorHFSL_customise
process = customise_validation(process)

# End of customisation functions
