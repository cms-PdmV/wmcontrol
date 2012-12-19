# Auto generated configuration file
# using: 
# Revision: 1.381.2.6 
# Source: /local/reps/CMSSW/CMSSW/Configuration/PyReleaseValidation/python/ConfigBuilder.py,v 
# with command line options: HcalQpll_3TS_dec19 -s RAW2DIGI,L1Reco,RECO,DQM --processName RECO --data --scenario pp --datatier RECO,DQM --eventcontent RECO,DQM --conditions GR_P_V41::All --python_filename HcalQpll_3TS.py --no_exec --custom_conditions=HcalRecoParams_v9.0_offline,HcalRecoParamsRcd,frontier://FrontierProd/CMS_COND_44X_HCAL --filein /store/data/Run2012C/JetHT/RAW/v1/000/199/812/0C450FA0-6BD8-E111-BB28-BCAEC5329727.root -n 10

#salavt:
#as has been just discussed at the meeting, I'm sending you the tag with
#3TS ("compromise" solution from some recent HCAL study)
#for all 3 QPLLs (2xHB-, 1xHB+, 3x36=108 channels in total) in question:
#HcalRecoParams_v9.0_offline
#cmscond_list_iov  -c frontier://FrontierProd/CMS_COND_44X_HCAL  -t   HcalRecoParams_v9.0_offline


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
    fileNames = cms.untracked.vstring('/store/data/Run2012C/JetHT/RAW/v1/000/199/812/0C450FA0-6BD8-E111-BB28-BCAEC5329727.root')
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    version = cms.untracked.string('$Revision: 1.381.2.6 $'),
    annotation = cms.untracked.string('HcalQpll_3TS_dec19 nevts:10'),
    name = cms.untracked.string('PyReleaseValidation')
)

# Output definition

process.RECOoutput = cms.OutputModule("PoolOutputModule",
    splitLevel = cms.untracked.int32(0),
    eventAutoFlushCompressedSize = cms.untracked.int32(5242880),
    outputCommands = process.RECOEventContent.outputCommands,
    fileName = cms.untracked.string('HcalQpll_3TS_dec19_RAW2DIGI_L1Reco_RECO_DQM.root'),
    dataset = cms.untracked.PSet(
        filterName = cms.untracked.string(''),
        dataTier = cms.untracked.string('RECO')
    )
)

process.DQMoutput = cms.OutputModule("PoolOutputModule",
    splitLevel = cms.untracked.int32(0),
    outputCommands = process.DQMEventContent.outputCommands,
    fileName = cms.untracked.string('HcalQpll_3TS_dec19_RAW2DIGI_L1Reco_RECO_DQM_inDQM.root'),
    dataset = cms.untracked.PSet(
        filterName = cms.untracked.string(''),
        dataTier = cms.untracked.string('DQM')
    )
)

# Additional output definition

# Other statements
process.GlobalTag.globaltag = 'GR_P_V41::All'
process.GlobalTag.toGet = cms.VPSet()
process.GlobalTag.toGet.append(cms.PSet(tag=cms.string("HcalRecoParams_v9.0_offline"),record=cms.string("HcalRecoParamsRcd"),connect=cms.untracked.string("frontier://FrontierProd/CMS_COND_44X_HCAL"),))

# Path and EndPath definitions
process.raw2digi_step = cms.Path(process.RawToDigi)
process.L1Reco_step = cms.Path(process.L1Reco)
process.reconstruction_step = cms.Path(process.reconstruction)
process.dqmoffline_step = cms.Path(process.DQMOffline)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.RECOoutput_step = cms.EndPath(process.RECOoutput)
process.DQMoutput_step = cms.EndPath(process.DQMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.raw2digi_step,process.L1Reco_step,process.reconstruction_step,process.dqmoffline_step,process.endjob_step,process.RECOoutput_step,process.DQMoutput_step)

