import FWCore.ParameterSet.Config as cms
from HLTrigger.HLTfilters.triggerResultsFilter_cfi import triggerResultsFilter
ZeroBiasFilter = triggerResultsFilter.clone(
    hltResults              = cms.InputTag('TriggerResults','','HLT'),   # HLT results   - set to empty to ignore HLT
    l1tResults              = cms.InputTag(''),                 # L1 GT results - set to empty to ignore L1
    l1tIgnoreMask           = cms.bool(False),                  # use L1 mask
    l1techIgnorePrescales   = cms.bool(False),                  # read L1 technical bits from PSB#9, bypassing the prescales
    daqPartitions           = cms.uint32(0x01),                 # used by the definition of the L1 mask
    throw                   = cms.bool(False),                  # if HLT path not in the table, crash/ignore according to true/false
    triggerConditions       = cms.vstring(
    'HLT_ZeroBias*')
    )
filterZeroBias = cms.Sequence( ZeroBiasFilter )
