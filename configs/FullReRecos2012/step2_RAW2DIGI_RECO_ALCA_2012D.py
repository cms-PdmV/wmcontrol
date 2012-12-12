# Auto generated configuration file
# using: 
# Revision: 1.381.2.13 
# Source: /local/reps/CMSSW/CMSSW/Configuration/PyReleaseValidation/python/ConfigBuilder.py,v 
# with command line options: step2 --conditions GR_E_V31::All --scenario pp --process ALCA --data --eventcontent DQM -s RAW2DIGI:siStripDigis+siPixelDigis+gtDigis+gtEvmDigis+scalersRawToDigi,RECO:trackerlocalreco,ALCA:SiStripCalZeroBias+DQM --datatier DQM -n -1 --filein /store/data/Run2012A/MinimumBias/RAW/v1/000/191/856/B0C5FBDE-DC8A-E111-86C8-001D09F29597.root --no_exec --python_filename=step2_RAW2DIGI_RECO_ALCA_2012D.py
import FWCore.ParameterSet.Config as cms

process = cms.Process('ALCA')

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')
process.load('Configuration.StandardSequences.RawToDigi_Data_cff')
process.load('Configuration.StandardSequences.Reconstruction_Data_cff')
process.load('Configuration.StandardSequences.AlCaRecoStreams_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

# Input source
process.source = cms.Source("PoolSource",
    secondaryFileNames = cms.untracked.vstring(),
    fileNames = cms.untracked.vstring('/store/data/Run2012A/MinimumBias/RAW/v1/000/191/856/B0C5FBDE-DC8A-E111-86C8-001D09F29597.root')
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    version = cms.untracked.string('$Revision: 1.381.2.13 $'),
    annotation = cms.untracked.string('step2 nevts:-1'),
    name = cms.untracked.string('PyReleaseValidation')
)

# Output definition

process.DQMoutput = cms.OutputModule("PoolOutputModule",
    splitLevel = cms.untracked.int32(0),
    outputCommands = process.DQMEventContent.outputCommands,
    fileName = cms.untracked.string('step2_RAW2DIGI_RECO_ALCA.root'),
    dataset = cms.untracked.PSet(
        filterName = cms.untracked.string(''),
        dataTier = cms.untracked.string('DQM')
    )
)

# Additional output definition
process.ALCARECOStreamSiStripCalZeroBias = cms.OutputModule("PoolOutputModule",
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('pathALCARECOSiStripCalZeroBias')
    ),
    outputCommands = cms.untracked.vstring('drop *', 
        'keep *_ALCARECOSiStripCalZeroBias_*_*', 
        'keep *_calZeroBiasClusters_*_*', 
        'keep L1AcceptBunchCrossings_*_*_*', 
        'keep *_TriggerResults_*_*', 
        'keep *_MEtoEDMConverter_*_*'),
    fileName = cms.untracked.string('SiStripCalZeroBias.root'),
    dataset = cms.untracked.PSet(
        filterName = cms.untracked.string('SiStripCalZeroBias'),
        dataTier = cms.untracked.string('ALCARECO')
    ),
    eventAutoFlushCompressedSize = cms.untracked.int32(5242880)
)

# Other statements
process.ALCARECOStreamSiStripCalZeroBias.outputCommands.append("keep *_MEtoEDMConverter_*_*")
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'GR_E_V31::All', '')

# Path and EndPath definitions
process.raw2digi_step0 = cms.Path(process.siStripDigis)
process.raw2digi_step1 = cms.Path(process.siPixelDigis)
process.raw2digi_step2 = cms.Path(process.gtDigis)
process.raw2digi_step3 = cms.Path(process.gtEvmDigis)
process.raw2digi_step4 = cms.Path(process.scalersRawToDigi)
process.reconstruction_step = cms.Path(process.trackerlocalreco)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.DQMoutput_step = cms.EndPath(process.DQMoutput)
process.ALCARECOStreamSiStripCalZeroBiasOutPath = cms.EndPath(process.ALCARECOStreamSiStripCalZeroBias)

# Schedule definition
process.schedule = cms.Schedule(process.raw2digi_step0,process.raw2digi_step1,process.raw2digi_step2,process.raw2digi_step3,process.raw2digi_step4,process.reconstruction_step,process.pathALCARECOSiStripCalZeroBias,process.pathALCARECODQM,process.endjob_step,process.DQMoutput_step,process.ALCARECOStreamSiStripCalZeroBiasOutPath)

