# Auto generated configuration file
# using: 
# Revision: 1.381.2.18 
# Source: /local/reps/CMSSW/CMSSW/Configuration/PyReleaseValidation/python/ConfigBuilder.py,v 
# with command line options: reco -s RAW2DIGI,FILTER:hcallaserhbhehffilter2012_cff.hcallLaser2012AntiFilter,L1Reco,RECO,DQM --data --python recoW13-2012C-keepDQMonly-AntiFilter.py --customise Configuration/DataProcessing/RecoTLR.customisePrompt --no_exec --conditions FT_R_53_V18::All --eventcontent DQM --datatier DQM --no_exec --filein=file:/data/franzoni/data/Run2012C-MinimumBias-RAW-v1-000202016-FC906D11-36F3-E111-94C2-001D09F28E80.root -n 10
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
process.load('DQMOffline.Configuration.DQMOffline_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(10)
)

# Input source
process.source = cms.Source("PoolSource",
    secondaryFileNames = cms.untracked.vstring(),
    fileNames = cms.untracked.vstring('file:/data/franzoni/data/Run2012C-MinimumBias-RAW-v1-000202016-FC906D11-36F3-E111-94C2-001D09F28E80.root')
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    version = cms.untracked.string('$Revision: 1.381.2.18 $'),
    annotation = cms.untracked.string('reco nevts:10'),
    name = cms.untracked.string('PyReleaseValidation')
)

# Output definition

process.DQMoutput = cms.OutputModule("PoolOutputModule",
    splitLevel = cms.untracked.int32(0),
    outputCommands = process.DQMEventContent.outputCommands,
    fileName = cms.untracked.string('reco_RAW2DIGI_FILTER_L1Reco_RECO_DQM.root'),
    dataset = cms.untracked.PSet(
        filterName = cms.untracked.string(''),
        dataTier = cms.untracked.string('DQM')
    ),
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('filtering_step')
    )
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'FT_R_53_V18::All', '')

process.hcallaserhbhehffilter2012 = cms.EDFilter("HcalLaserHBHEHFFilter2012",
    forceFilterTrue = cms.untracked.bool(False),
    filterHF = cms.bool(True),
    HBHEcalibThreshold = cms.double(15.0),
    verbose = cms.untracked.bool(False),
    minCalibChannelsHBHELaser = cms.int32(20),
    minCalibChannelsHFLaser = cms.int32(10),
    WriteBadToFile = cms.untracked.bool(False),
    digiLabel = cms.InputTag("hcalDigis"),
    prefix = cms.untracked.string(''),
    filterHBHE = cms.bool(True),
    CalibTS = cms.vint32(3, 4, 5, 6),
    minFracDiffHBHELaser = cms.double(0.3)
)


process.hcallLaser2012AntiFilter = cms.Sequence(~process.hcallaserhbhehffilter2012)

# Path and EndPath definitions
process.raw2digi_step = cms.Path(process.RawToDigi)
process.filtering_step = cms.Path(process.hcallLaser2012AntiFilter)
process.L1Reco_step = cms.Path(process.L1Reco)
process.reconstruction_step = cms.Path(process.reconstruction)
process.dqmoffline_step = cms.Path(process.DQMOffline)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.DQMoutput_step = cms.EndPath(process.DQMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.raw2digi_step,process.filtering_step,process.L1Reco_step,process.reconstruction_step,process.dqmoffline_step,process.endjob_step,process.DQMoutput_step)
# filter all path with the production filter sequence
for path in process.paths:
	if not path in ['L1Reco_step', 'reconstruction_step', 'dqmoffline_step']: continue
	getattr(process,path)._seq = process.hcallLaser2012AntiFilter * getattr(process,path)._seq 

# customisation of the process.

# Automatic addition of the customisation function from Configuration.DataProcessing.RecoTLR
from Configuration.DataProcessing.RecoTLR import customisePrompt 

#call to customisation function customisePrompt imported from Configuration.DataProcessing.RecoTLR
process = customisePrompt(process)

# End of customisation functions
