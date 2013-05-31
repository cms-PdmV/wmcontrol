# Auto generated configuration file
# using: 
# Revision: 1.381.2.22 
# Source: /local/reps/CMSSW/CMSSW/Configuration/PyReleaseValidation/python/ConfigBuilder.py,v 
# with command line options: STEP1 --step DIGI,L1,DIGI2RAW,HLT:7E33v2 --conditions START53_V7N::All --runsAndWeightsForMC [(202299,1.)] --pileup fromDB --customise=Configuration/GenProduction/noCastorHFSL_customise.customise_digi --inline_custom --eventcontent RAWSIM --datatier GEN-SIM-RAW --no_exec -n 5 --filein=file:/data/franzoni/cmssw/53x/CMSSW_5_3_9_patch3_taskForceSamplesApril/src/MB8TeVEtanoCasHFShoLib__GEN-SIM__START53_V16-v2__00001__FE332103-9E59-E211-B8FF-001E4F32EF96.root --python_filename=neutrinogun-noCastorHFSL-May10customise-RD202299-NuGunDigiReco-50nsExtM300ns-keepDOES.py --customise_commands=process.RAWSIMoutput.outputCommands.extend(cms.untracked.vstring('keep *_simEcalTriggerPrimitiveDigis_*_*','keep *_simHcalTriggerPrimitiveDigis_*_*')) \n
import FWCore.ParameterSet.Config as cms

process = cms.Process('HLT')

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mix_fromDB_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.Digi_cff')
process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('Configuration.StandardSequences.DigiToRaw_cff')
process.load('HLTrigger.Configuration.HLT_7E33v2_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(200)
)

# Input source
process.source = cms.Source("PoolSource",
    secondaryFileNames = cms.untracked.vstring(),
    fileNames = cms.untracked.vstring('file:/data/franzoni/cmssw/53x/CMSSW_5_3_9_patch3_taskForceSamplesApril/src/MB8TeVEtanoCasHFShoLib__GEN-SIM__START53_V16-v2__00001__FE332103-9E59-E211-B8FF-001E4F32EF96.root'),
    setRunNumber = cms.untracked.uint32(202299)
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    version = cms.untracked.string('$Revision: 1.381.2.22 $'),
    annotation = cms.untracked.string('STEP1 nevts:5'),
    name = cms.untracked.string('PyReleaseValidation')
)

# Output definition

process.RAWSIMoutput = cms.OutputModule("PoolOutputModule",
    splitLevel = cms.untracked.int32(0),
    eventAutoFlushCompressedSize = cms.untracked.int32(5242880),
    outputCommands = process.RAWSIMEventContent.outputCommands,
    fileName = cms.untracked.string('STEP1_DIGI_L1_DIGI2RAW_HLT_PU.root'),
    dataset = cms.untracked.PSet(
        filterName = cms.untracked.string(''),
        dataTier = cms.untracked.string('GEN-SIM-RAW')
    )
)

# Additional output definition

# Other statements
import SimGeneral.Configuration.ThrowAndSetRandomRun as ThrowAndSetRandomRun
ThrowAndSetRandomRun.throwAndSetRandomRun(process.source,[(202299, 1.0)])
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'START53_V7N::All', '')

# Path and EndPath definitions
process.digitisation_step = cms.Path(process.pdigi)
process.L1simulation_step = cms.Path(process.SimL1Emulator)
process.digi2raw_step = cms.Path(process.DigiToRaw)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.RAWSIMoutput_step = cms.EndPath(process.RAWSIMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.digitisation_step,process.L1simulation_step,process.digi2raw_step)
process.schedule.extend(process.HLTSchedule)
process.schedule.extend([process.endjob_step,process.RAWSIMoutput_step])

# customisation of the process.

# Automatic addition of the customisation function from HLTrigger.Configuration.customizeHLTforMC

def customizeHLTforMC(process):
  """adapt the HLT to run on MC, instead of data
  see Configuration/StandardSequences/Reconstruction_Data_cff.py
  which does the opposite, for RECO"""

  # CSCHaloDataProducer - not used at HLT
  #if 'CSCHaloData' in process.__dict__:
  #  process.CSCHaloData.ExpectedBX = cms.int32(6)

  # EcalUncalibRecHitProducer - not used at HLT
  #if 'ecalGlobalUncalibRecHit' in process.__dict__:
  #  process.ecalGlobalUncalibRecHit.doEBtimeCorrection = cms.bool(False)
  #  process.ecalGlobalUncalibRecHit.doEEtimeCorrection = cms.bool(False)

  # HcalRecAlgoESProducer - these flags are not used at HLT (they should stay set to the default value for both data and MC)
  #if 'hcalRecAlgos' in process.__dict__:
  #  import RecoLocalCalo.HcalRecAlgos.RemoveAddSevLevel as HcalRemoveAddSevLevel
  #  HcalRemoveAddSevLevel.AddFlag(process.hcalRecAlgos, "HFDigiTime",     8)
  #  HcalRemoveAddSevLevel.AddFlag(process.hcalRecAlgos, "HBHEFlatNoise",  8)
  #  HcalRemoveAddSevLevel.AddFlag(process.hcalRecAlgos, "HBHESpikeNoise", 8)

  # PFRecHitProducerHCAL
  if 'hltParticleFlowRecHitHCAL' in process.__dict__:
    process.hltParticleFlowRecHitHCAL.ApplyPulseDPG      = cms.bool(False)
    process.hltParticleFlowRecHitHCAL.LongShortFibre_Cut = cms.double(1000000000.0)

  return process

#call to customisation function customizeHLTforMC imported from HLTrigger.Configuration.customizeHLTforMC
process = customizeHLTforMC(process)

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

#call to customisation function customise_digi imported from Configuration.GenProduction.noCastorHFSL_customise
process = customise_digi(process)

# End of customisation functions

# Customisation from command line
process.RAWSIMoutput.outputCommands.extend(cms.untracked.vstring('keep *_simEcalTriggerPrimitiveDigis_*_*','keep *_simHcalTriggerPrimitiveDigis_*_*')) 
