# Auto generated configuration file
# using: 
# Revision: 1.381.2.18 
# Source: /local/reps/CMSSW/CMSSW/Configuration/PyReleaseValidation/python/ConfigBuilder.py,v 
# with command line options: reco -s FILTER:Configuration/PyReleaseValidation/filterZeroBias.filterZeroBias,RAW2DIGI,RECO --data --conditions GR_R_53_V18::All --eventcontent RAWRECO --no_exec --datatier RAW-RECO --filein /store/data/Run2012C/MinimumBias/RAW/v1/000/202/299/0AB4E9C2-27F8-E111-BAE8-001D09F24664.root -n 50 --python_filename=filter0BinMinBias_RAWRECO_feb25.13.py
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
    fileNames = cms.untracked.vstring('/store/data/Run2012C/MinimumBias/RAW/v1/000/202/299/0AB4E9C2-27F8-E111-BAE8-001D09F24664.root')
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    version = cms.untracked.string('$Revision: 1.381.2.18 $'),
    annotation = cms.untracked.string('reco nevts:50'),
    name = cms.untracked.string('PyReleaseValidation')
)

# Output definition

process.RAWRECOoutput = cms.OutputModule("PoolOutputModule",
    splitLevel = cms.untracked.int32(0),
    eventAutoFlushCompressedSize = cms.untracked.int32(5242880),
    outputCommands = process.RAWRECOEventContent.outputCommands,
    fileName = cms.untracked.string('reco_FILTER_RAW2DIGI_RECO.root'),
    dataset = cms.untracked.PSet(
        filterName = cms.untracked.string(''),
        dataTier = cms.untracked.string('RAW-RECO')
    ),
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('filtering_step')
    )
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'GR_R_53_V18::All', '')

process.ZeroBiasFilter = cms.EDFilter("TriggerResultsFilter",
    l1tIgnoreMask = cms.bool(False),
    l1tResults = cms.InputTag(""),
    l1techIgnorePrescales = cms.bool(False),
    hltResults = cms.InputTag("TriggerResults","","HLT"),
    triggerConditions = cms.vstring('HLT_ZeroBias*'),
    throw = cms.bool(False),
    daqPartitions = cms.uint32(1)
)


process.filterZeroBias = cms.Sequence(process.ZeroBiasFilter)

# Path and EndPath definitions
process.filtering_step = cms.Path(process.filterZeroBias)
process.raw2digi_step = cms.Path(process.RawToDigi)
process.reconstruction_step = cms.Path(process.reconstruction)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.RAWRECOoutput_step = cms.EndPath(process.RAWRECOoutput)

# Schedule definition
process.schedule = cms.Schedule(process.filtering_step,process.raw2digi_step,process.reconstruction_step,process.endjob_step,process.RAWRECOoutput_step)
# filter all path with the production filter sequence
for path in process.paths:
	if not path in ['raw2digi_step', 'reconstruction_step']: continue
	getattr(process,path)._seq = process.filterZeroBias * getattr(process,path)._seq 

