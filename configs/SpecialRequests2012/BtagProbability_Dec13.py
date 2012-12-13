# Auto generated configuration file
# using: 
# Revision: 1.381.2.17 
# Source: /local/reps/CMSSW/CMSSW/Configuration/PyReleaseValidation/python/ConfigBuilder.py,v 
# with command line options: reco -s FILTER:Configuration/PyReleaseValidation/filterJet80.filterJet80,RAW2DIGI,RECO --data --conditions GR_R_53_V16D::All --custom_conditions=TrackerAlignment_Run2012C_offline,TrackerAlignmentRcd,frontier://FrontierPrep/CMS_COND_ALIGNMENT --eventcontent AOD --no_exec --datatier AOD --filein /store/data/Run2012C/MinimumBias/RAW/v1/000/199/812/7CFB9644-78D8-E111-B2B2-5404A63886CB.root -n 50 --python_filename=BtagProbability_Dec13.py
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
process.load('Configuration.StandardSequences.Reconstruction_Data_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(50)
)

# Input source
process.source = cms.Source("PoolSource",
    secondaryFileNames = cms.untracked.vstring(),
    fileNames = cms.untracked.vstring('/store/data/Run2012C/MinimumBias/RAW/v1/000/199/812/7CFB9644-78D8-E111-B2B2-5404A63886CB.root')
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    version = cms.untracked.string('$Revision: 1.381.2.17 $'),
    annotation = cms.untracked.string('reco nevts:50'),
    name = cms.untracked.string('PyReleaseValidation')
)

# Output definition

process.AODoutput = cms.OutputModule("PoolOutputModule",
    eventAutoFlushCompressedSize = cms.untracked.int32(15728640),
    outputCommands = process.AODEventContent.outputCommands,
    fileName = cms.untracked.string('reco_FILTER_RAW2DIGI_RECO.root'),
    dataset = cms.untracked.PSet(
        filterName = cms.untracked.string(''),
        dataTier = cms.untracked.string('AOD')
    ),
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('filtering_step')
    )
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'GR_R_53_V16D::All', 'TrackerAlignment_Run2012C_offline,TrackerAlignmentRcd,frontier://FrontierPrep/CMS_COND_ALIGNMENT')

process.filterJet80Filter = cms.EDFilter("TriggerResultsFilter",
    l1tIgnoreMask = cms.bool(False),
    l1tResults = cms.InputTag(""),
    l1techIgnorePrescales = cms.bool(False),
    hltResults = cms.InputTag("TriggerResults","","HLT"),
    triggerConditions = cms.vstring('HLT_PFJet80*'),
    throw = cms.bool(False),
    daqPartitions = cms.uint32(1)
)


process.filterJet80 = cms.Sequence(process.filterJet80Filter)

# Path and EndPath definitions
process.filtering_step = cms.Path(process.filterJet80)
process.raw2digi_step = cms.Path(process.RawToDigi)
process.reconstruction_step = cms.Path(process.reconstruction)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.AODoutput_step = cms.EndPath(process.AODoutput)

# Schedule definition
process.schedule = cms.Schedule(process.filtering_step,process.raw2digi_step,process.reconstruction_step,process.endjob_step,process.AODoutput_step)
# filter all path with the production filter sequence
for path in process.paths:
	if not path in ['raw2digi_step', 'reconstruction_step']: continue
	getattr(process,path)._seq = process.filterJet80 * getattr(process,path)._seq 

