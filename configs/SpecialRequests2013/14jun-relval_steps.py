from __future__ import print_function

class InputInfo(object):
    def __init__(self,label,dataSet,run=0,files=1000,events=2000000,location='CAF') :
        self.run = [run]
        self.files = files
        self.events = events
        self.location = location
        self.label = label
        self.dataSet = dataSet
        self.split = None
        
    def lumiRanges(self):
        return None

    def dbs(self):
        command='dbs search --noheader --query "find file where dataset like '+self.dataSet
        def requ(r):
            return 'run=%d'%(r,)
        if self.run!=0:
            pass  # this is a HACK GF
            #command+=' and ('+' or '.join(map(requ,self.run))+' )'
        command+='"'
        return command
    
    def __str__(self):
        return 'input from: %s with run: %s'%(self.dataSet,str(self.run))
    
# merge dictionaries, with prioty on the [0] index
def merge(dictlist,TELL=False):
    import copy
    last=len(dictlist)-1
    if TELL: print(last,dictlist)
    if last==0:
        # ONLY ONE ITEM LEFT
        return copy.copy(dictlist[0])
    else:
        reducedlist=dictlist[0:max(0,last-1)]
        if TELL: print(reducedlist)
        # make a copy of the last item
        d=copy.copy(dictlist[last])
        # update with the last but one item
        d.update(dictlist[last-1])
        # and recursively do the rest
        reducedlist.append(d)
        return merge(reducedlist,TELL)


# step1 gensim
step1Defaults = {'--relval'      : None, # need to be explicitly set
                 '-s'            : 'GEN,SIM',
                 '-n'            : 10,
                 '--conditions'  : 'START42_V14B:All',    # this is for MC 7 TeV validation campaign
#                 '--conditions'  : 'START44_V9B:All',    # this is for MC 7 TeV validation campaign  <<<< this fails
#                 ---- Configuration BEGIN
#                 Error occurred while creating PoolDBESSource
#                 ---- PluginNotFound BEGIN
#                 Unable to find plugin 'CastorRecoParamsRcd@NewProxy'. Please check spelling of name.
#                 ---- PluginNotFound END
#                 ---- Configuration END
#                 '--conditions'  : 'auto:mc',
                 '--datatier'    : 'GEN-SIM',
                 '--eventcontent': 'RAWSIM',
                 }

step1 = {}

#### Production test section ####
step1['ProdMinBias']=merge([{'cfg':'MinBias_7TeV_cfi','--relval':'9000,100'},step1Defaults])
step1['ProdTTbar']=merge([{'cfg':'TTbar_Tauola_7TeV_cfi','--relval':'9000,50'},step1Defaults])
step1['ProdQCD_Pt_3000_3500']=merge([{'cfg':'QCD_Pt_3000_3500_7TeV_cfi','--relval':'9000,25'},step1Defaults])

step1['ProdMinBiasINPUT']={'INPUT':InputInfo(dataSet='/RelValProdMinBias/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM-RAW',label='prodmbrv',location='STD')}
step1['ProdTTbarINPUT']={'INPUT':InputInfo(dataSet='/RelValProdTTbar/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM-RAW',label='prodttbrv',location='STD')}
step1['ProdQCD_Pt_3000_3500INPUT']={'INPUT':InputInfo(dataSet='/RelValProdQCD_Pt_3000_3500/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM-RAW',label='qcd335',location='STD')}



#### data ####
step1['RunCosmicsA']={'INPUT':InputInfo(dataSet='/Cosmics/Run2010A-v1/RAW',label='cos2010A',run=142089,events=100000)}
step1['MinimumBias2010A']={'INPUT':InputInfo(dataSet='/MinimumBias/Run2010A-valskim-v6/RAW-RECO',label='run2010A',location='STD')}
step1['MinimumBias2010B']={'INPUT':InputInfo(dataSet='/MinimumBias/Run2010B-valskim-v2/RAW-RECO',label='run2010B')}
step1['WZMuSkim2010A']={'INPUT':InputInfo(dataSet='/Mu/Run2010A-WZMu-Nov4Skim_v1/RAW-RECO',label='wzMu2010A')}
step1['WZMuSkim2010B']={'INPUT':InputInfo(dataSet='/Mu/Run2010B-WZMu-Nov4Skim_v1/RAW-RECO',label='wzMu2010B')}
step1['WZEGSkim2010A']={'INPUT':InputInfo(dataSet='/EG/Run2010A-WZEG-Nov4Skim_v1/RAW-RECO',label='wzEG2010A')}
step1['WZEGSkim2010B']={'INPUT':InputInfo(dataSet='/Electron/Run2010B-WZEG-Nov4Skim_v1/RAW-RECO',label='wzEG2010B')}

step1['RunMinBias2010B']={'INPUT':InputInfo(dataSet='/MinimumBias/Run2010B-v1/RAW',label='mb2010B',run=149011,events=100000)}
step1['RunMu2010B']={'INPUT':InputInfo(dataSet='/Mu/Run2010B-v1/RAW',label='mu2010B',run=149011,events=100000)}
step1['RunElectron2010B']={'INPUT':InputInfo(dataSet='/Electron/Run2010B-v1/RAW',label='electron2010B',run=149011,events=100000)}
step1['RunPhoton2010B']={'INPUT':InputInfo(dataSet='/Photon/Run2010B-v1/RAW',label='photon2010B',run=149011,events=100000)}
step1['RunJet2010B']={'INPUT':InputInfo(dataSet='/Jet/Run2010B-v1/RAW',label='jet2010B',run=149011,events=100000)}

#### Standard release validation samples ####

stCond={'--conditions':'auto:startup'}
K9by25={'--relval':'9000,25'}
K9by50={'--relval':'9000,50'}
K9by100={'--relval':'9000,100'}
K9by250={'--relval':'9000,250'}

step1['MinBias']=merge([{'cfg':'MinBias_7TeV_cfi'},K9by100,step1Defaults])
step1['QCD_Pt_3000_3500']=merge([{'cfg':'QCD_Pt_3000_3500_7TeV_cfi'},K9by25,step1Defaults])
step1['QCD_Pt_80_120']=merge([{'cfg':'QCD_Pt_80_120_7TeV_cfi'},K9by50,step1Defaults])
step1['SingleElectronPt10']=merge([{'cfg':'SingleElectronPt10_cfi'},K9by250,step1Defaults])
step1['SingleElectronPt35']=merge([{'cfg':'SingleElectronPt35_cfi'},K9by250,step1Defaults])
step1['SingleGammaPt10']=merge([{'cfg':'SingleGammaPt10_cfi'},K9by100,step1Defaults])
step1['SingleGammaPt35']=merge([{'cfg':'SingleGammaPt35_cfi'},K9by100,step1Defaults])
step1['SingleMuPt10']=merge([{'cfg':'SingleMuPt10_cfi','--relval':'25000,250'},step1Defaults])
step1['SingleMuPt100']=merge([{'cfg':'SingleMuPt100_cfi','--relval':'9000,250'},step1Defaults])
step1['SingleMuPt1000']=merge([{'cfg':'SingleMuPt1000_cfi'},K9by100,step1Defaults])
step1['TTbar']=merge([{'cfg':'TTbar_Tauola_7TeV_cfi'},K9by50,step1Defaults])
step1['ZEE']=merge([{'cfg':'ZEE_7TeV_cfi'},K9by100,step1Defaults])
step1['Wjet_Pt_80_120']=merge([{'cfg':'Wjet_Pt_80_120_7TeV_cfi'},K9by100,step1Defaults])
step1['Wjet_Pt_3000_3500']=merge([{'cfg':'Wjet_Pt_3000_3500_7TeV_cfi'},K9by100,step1Defaults])
step1['LM1_sfts']=merge([{'cfg':'LM1_sfts_7TeV_cfi'},K9by100,step1Defaults])
step1['QCD_FlatPt_15_3000']=merge([{'cfg':'QCDForPF_7TeV_cfi'},K9by100,step1Defaults])

step1['CosmicsINPUT']={'INPUT':InputInfo(dataSet='/RelValCosmics/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM',label='Cosmicsrv',location='STD')}
step1['BeamHaloINPUT']={'INPUT':InputInfo(dataSet='/RelValBeamHalo/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM',label='BeamHalorv',location='STD')}

step1['MinBiasINPUT']={'INPUT':InputInfo(dataSet='/RelValMinBias/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM',label='MinBiasrv',location='STD')}
# had to add _2 for some reasons present in GEN-SIM name
step1['QCD_Pt_3000_3500INPUT']={'INPUT':InputInfo(dataSet='/RelValQCD_Pt_3000_3500_2/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM',label='QCD_Pt_3000_3500rv',location='STD')}
step1['QCD_Pt_80_120INPUT']={'INPUT':InputInfo(dataSet='/RelValQCD_Pt_80_120/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM',label='QCD_Pt_80_120rv',location='STD')}
step1['SingleElectronPt10INPUT']={'INPUT':InputInfo(dataSet='/RelValSingleElectronPt10/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM',label='SingleElectronPt10rv',location='STD')}
step1['SingleElectronPt35INPUT']={'INPUT':InputInfo(dataSet='/RelValSingleElectronPt35/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM',label='SingleElectronPt35rv',location='STD')}
step1['SingleGammaPt10INPUT']={'INPUT':InputInfo(dataSet='/RelValSingleGammaPt10/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM',label='SingleGammaPt10rv',location='STD')}
step1['SingleGammaPt35INPUT']={'INPUT':InputInfo(dataSet='/RelValSingleGammaPt35/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM',label='SingleGammaPt35rv',location='STD')}
step1['SingleMuPt10INPUT']={'INPUT':InputInfo(dataSet='/RelValSingleMuPt10/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM',label='SingleMuPt10rv',location='STD')}
step1['SingleMuPt100INPUT']={'INPUT':InputInfo(dataSet='/RelValSingleMuPt100/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM',label='SingleMuPt100rv',location='STD')}
step1['SingleMuPt1000INPUT']={'INPUT':InputInfo(dataSet='/RelValSingleMuPt1000/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM',label='SingleMuPt1000rv',location='STD')}
step1['TTbarINPUT']={'INPUT':InputInfo(dataSet='/RelValTTbar/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM',label='ttbarrv',location='STD')}
step1['ZEEINPUT']={'INPUT':InputInfo(dataSet='/RelValZEE/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM',label='ZEErv',location='STD')}
step1['Wjet_Pt_80_120INPUT']={'INPUT':InputInfo(dataSet='/RelValWjet_Pt_80_120/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM',label='Wjet_Pt_80_120rv',location='STD')}
step1['Wjet_Pt_3000_3500INPUT']={'INPUT':InputInfo(dataSet='/RelValWjet_Pt_3000_3500/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM',label='Wjet_Pt_3000_3500rv',location='STD')}
step1['LM1_sftsINPUT']={'INPUT':InputInfo(dataSet='/RelValLM1_sfts/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM',label='LM1_sftsrv',location='STD')}
step1['QCD_FlatPt_15_3000INPUT']={'INPUT':InputInfo(dataSet='/RelValQCD_FlatPt_15_3000/CMSSW_4_2_0_pre2-MC_311_V1-v1/GEN-SIM',label='QCD_FlatPt_15_3000rv',location='STD')}

   
step1['MinBias2']=merge([{'cfg':'MinBias_7TeV_cfi'},stCond,K9by100,step1Defaults])
step1['Higgs200ChargedTaus']=merge([{'cfg':'H200ChargedTaus_Tauola_7TeV_cfi'},stCond,K9by100,step1Defaults])
step1['QCD_Pt_3000_3500_2']=merge([{'cfg':'QCD_Pt_3000_3500_7TeV_cfi'},K9by25,stCond,step1Defaults])
step1['QCD_Pt_80_120_2']=merge([{'cfg':'QCD_Pt_80_120_7TeV_cfi'},K9by50,stCond,step1Defaults])
step1['JpsiMM']=merge([{'cfg':'JpsiMM_7TeV_cfi','--relval':'65250,725'},stCond,step1Defaults])
step1['TTbar2']=merge([{'cfg':'TTbar_Tauola_7TeV_cfi'},K9by50,stCond,step1Defaults])
step1['WE']=merge([{'cfg':'WE_7TeV_cfi'},K9by100,stCond,step1Defaults])
step1['WM']=merge([{'cfg':'WM_7TeV_cfi'},K9by100,stCond,step1Defaults])
step1['ZEE2']=merge([{'cfg':'ZEE_7TeV_cfi'},K9by100,stCond,step1Defaults])
step1['ZMM']=merge([{'cfg':'ZMM_7TeV_cfi','--relval':'18000,200'},stCond,step1Defaults])
step1['ZTT']=merge([{'cfg':'ZTT_Tauola_All_hadronic_7TeV_cfi'},K9by100,stCond,step1Defaults])
step1['H130GGgluonfusion']=merge([{'cfg':'H130GGgluonfusion_7TeV_cfi'},K9by100,stCond,step1Defaults])
step1['PhotonJets_Pt_10']=merge([{'cfg':'PhotonJet_Pt_10_7TeV_cfi'},K9by100,stCond,step1Defaults])
step1['QQH1352T_Tauola']=merge([{'cfg':'QQH1352T_Tauola_7TeV_cfi'},K9by100,stCond,step1Defaults])

step1['MinBias2INPUT']={'INPUT':InputInfo(dataSet='/RelValMinBias/CMSSW_4_2_0_pre2-START311_V1-v1/GEN-SIM',label='MinBiasrv',location='STD')}
step1['Higgs200ChargedTausINPUT']={'INPUT':InputInfo(dataSet='/RelValHiggs200ChargedTaus/CMSSW_4_2_0_pre2-START311_V1-v1/GEN-SIM',label='Higgs200ChargedTausrv',location='STD')}
#step1['QCD_Pt_3000_3500_2INPUT']={'INPUT':InputInfo(dataSet='/RelValQCD_Pt_3000_3500/CMSSW_4_2_0_pre2-START311_V1-v1/GEN-SIM',label='QCD_Pt_3000_3500rv',location='STD')}
# fix the line above
step1['QCD_Pt_3000_3500_2INPUT']={'INPUT':InputInfo(dataSet='/RelValQCD_Pt_3000_3500_2/CMSSW_4_2_0_pre2-START311_V1-v1/GEN-SIM',label='QCD_Pt_3000_3500rv',location='STD')}
step1['QCD_Pt_80_120_2INPUT']={'INPUT':InputInfo(dataSet='/RelValQCD_Pt_80_120/CMSSW_4_2_0_pre2-START311_V1-v1/GEN-SIM',label='QCD_Pt_80_120rv',location='STD')}
step1['JpsiMMINPUT']={'INPUT':InputInfo(dataSet='/RelValJpsiMM/CMSSW_4_2_0_pre2-START311_V1-v1/GEN-SIM',label='JpsiMMrv',location='STD')}
step1['TTbar2INPUT']={'INPUT':InputInfo(dataSet='/RelValTTbar/CMSSW_4_2_0_pre2-START311_V1-v1/GEN-SIM',label='ttbarrv',location='STD')}
step1['WEINPUT']={'INPUT':InputInfo(dataSet='/RelValWE/CMSSW_4_2_0_pre2-START311_V1-v1/GEN-SIM',label='WErv',location='STD')}
step1['ZEE2INPUT']={'INPUT':InputInfo(dataSet='/RelValZEE/CMSSW_4_2_0_pre2-START311_V1-v1/GEN-SIM',label='ZEErv',location='STD')}
step1['ZTTINPUT']={'INPUT':InputInfo(dataSet='/RelValZTT/CMSSW_4_2_0_pre2-START311_V1-v1/GEN-SIM',label='ZTTrv',location='STD')}
step1['H130GGgluonfusionINPUT']={'INPUT':InputInfo(dataSet='/RelValH130GGgluonfusion/CMSSW_4_2_0_pre2-START311_V1-v1/GEN-SIM',label='H130GGgluonfusionrv',location='STD')}
step1['PhotonJets_Pt_10INPUT']={'INPUT':InputInfo(dataSet='/RelValPhotonJets_Pt_10/CMSSW_4_2_0_pre2-START311_V1-v1/GEN-SIM',label='PhotonJets_Pt_10rv',location='STD')}
# step1['QQH1352T_TauolaINPUT']={'INPUT':InputInfo(dataSet='/RelValQQH1352T_Tauola_cfi/CMSSW_4_2_0_pre2-START311_V1-v1/GEN-SIM',label='QQH1352T_Tauola_cfirv',location='STD')}
# fix to the previous one: 
step1['QQH1352T_TauolaINPUT']={'INPUT':InputInfo(dataSet='/RelValQQH1352T_Tauola/CMSSW_4_2_0_pre2-START311_V1-v1/GEN-SIM',label='QQH1352T_Tauola_cfirv',location='STD')}
step1['WMINPUT']={'INPUT':InputInfo(dataSet='/RelValWM/CMSSW_4_2_0_pre2-START311_V1-v1/GEN-SIM',label='WMrv',location='STD')}
step1['ZMMINPUT']={'INPUT':InputInfo(dataSet='/RelValZMM/CMSSW_4_2_0_pre2-START311_V1-v1/GEN-SIM',label='WMrv',location='STD')}




step1['Cosmics']=merge([{'cfg':'UndergroundCosmicMu_cfi.py','--relval':'666000,7400','--scenario':'cosmics'},step1Defaults])
step1['BeamHalo']=merge([{'cfg':'BeamHalo_cfi.py','--scenario':'cosmics'},K9by100,step1Defaults])



step1UpgstdgeomDefaults={'-s':'GEN,SIM',
                  '--conditions':'DESIGN42_V17S::All',
                  '--eventcontent':'FEVTDEBUGHLT',
                  '--beamspot' : 'Gauss',
                  '--slhc' : 'stdgeom',
                  '--datatier' : 'GEN-SIM'
                  }

step1Upgpixphase1Defaults={'-s':'GEN,SIM',
                  '--conditions':'DESIGN42_V17S::All',
                  '--eventcontent':'FEVTDEBUGHLT',
                  '--beamspot' : 'Gauss',
                  '--slhc' : 'Phase1_R30F12',
                  '--datatier' : 'GEN-SIM'
                  }


step1['SingleMuPt10_UPGstd']=merge([{'cfg':'SingleMuPt10_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['SingleMuPt100_UPGstd']=merge([{'cfg':'SingleMuPt100_cfi','--relval':'9000,250'},step1UpgstdgeomDefaults])
step1['SingleMuPt1000_UPGstd']=merge([{'cfg':'SingleMuPt1000_cfi'},K9by100,step1UpgstdgeomDefaults])
step1['SingleElectronPt10_UPGstd']=merge([{'cfg':'SingleElectronPt10_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['SingleElectronPt35_UPGstd']=merge([{'cfg':'SingleElectronPt35_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['SingleGammaPt10_UPGstd']=merge([{'cfg':'SingleGammaPt10_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['SingleGammaPt35_UPGstd']=merge([{'cfg':'SingleGammaPt35_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])

step1['FourMuPt1_200_UPGstd']=merge([{'cfg':'FourMuPt1_200_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['FourTauPt1_200_UPGstd']=merge([{'cfg':'FourTauPt1_200_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['FourElectronPt1_50_UPGstd']=merge([{'cfg':'FourElectronPt1_50_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['FourGammaPt1_50_UPGstd']=merge([{'cfg':'FourGammaPt1_50_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['FourPiPt1_50_UPGstd']=merge([{'cfg':'FourPiPt1_50_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])

step1['H120_bbar_Zll_UPGstd14']=merge([{'cfg':'HERWIGPP_POWHEG_H120_bbar_Z_ll_14TeV_cff','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['H120_bbar_Zmm_UPGstd14']=merge([{'cfg':'HERWIGPP_POWHEG_H120_bbar_Z_mm_14TeV_cff','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['ZZ_MMorBB_UPGstd14']=merge([{'cfg':'ZZ_MMorBB_TuneZ2_14TeV_pythia6_tauola_cff','--relval':'25000,250'},step1UpgstdgeomDefaults])

step1['H130GGgluonfusion_UPGstd14']=merge([{'cfg':'H130GGgluonfusion_14TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['H130GGgluonfusion_UPGstd8']=merge([{'cfg':'H130GGgluonfusion_8TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])

step1['H200chargedTaus_Tauola_UPGstd14']=merge([{'cfg':'H200chargedTaus_Tauola_14TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['H200chargedTaus_Tauola_UPGstd8']=merge([{'cfg':'H200chargedTaus_Tauola_8TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])

step1['JpsiMM_UPGstd14']=merge([{'cfg':'JpsiMM_14TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['JpsiMM_UPGstd8']=merge([{'cfg':'JpsiMM_8TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])


step1['LM1_sfts_UPGstd14']=merge([{'cfg':'LM1_sfts_14TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['LM1_sfts_UPGstd8']=merge([{'cfg':'LM1_sfts_8TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])

step1['MinBias_UPGstd8']=merge([{'cfg':'MinBias_TuneZ2star_8TeV_pythia6_cff'},K9by100,step1UpgstdgeomDefaults])
step1['MinBias_UPGstd14']=merge([{'cfg':'MinBias_TuneZ2star_14TeV_pythia6_cff'},K9by100,step1UpgstdgeomDefaults])         

step1['PhotonJet_Pt10_UPGstd14']=merge([{'cfg':'PhotonJet_Pt10_14TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['PhotonJet_Pt10_UPGstd8']=merge([{'cfg':'PhotonJet_Pt10_8TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])

step1['QCDForPF_UPGstd14']=merge([{'cfg':'QCDForPF_14TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['QCDForPF_UPGstd8']=merge([{'cfg':'QCDForPF_8TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])

step1['QCD_Pt_3000_3500_UPGstd14']=merge([{'cfg':'QCD_Pt_3000_3500_14TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['QCD_Pt_3000_3500_UPGstd8']=merge([{'cfg':'QCD_Pt_3000_3500_8TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])

step1['QCD_Pt_80_120_UPGstd14']=merge([{'cfg':'QCD_Pt_80_120_14TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['QCD_Pt_80_120_UPGstd8']=merge([{'cfg':'QCD_Pt_80_120_8TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])

step1['QQH1352T_Tauola_UPGstd14']=merge([{'cfg':'QQH1352T_Tauola_14TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['QQH1352T_Tauola_UPGstd8']=merge([{'cfg':'QQH1352T_Tauola_8TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])

step1['TTbar_Tauola_UPGstd14']=merge([{'cfg':'TTbar_Tauola_14TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['TTbar_Tauola_UPGstd8']=merge([{'cfg':'TTbar_Tauola_8TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])

step1['WE_UPGstd14']=merge([{'cfg':'WE_14TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['WE_UPGstd8']=merge([{'cfg':'WE_8TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])

step1['WM_UPGstd14']=merge([{'cfg':'WM_14TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['WM_UPGstd8']=merge([{'cfg':'WM_8TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])

step1['WJet_Pt_3000_3500_UPGstd14']=merge([{'cfg':'WJet_Pt_3000_3500_14TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['WJet_Pt_3000_3500_UPGstd8']=merge([{'cfg':'WJet_Pt_3000_3500_8TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])

step1['WJet_Pt_80_120_UPGstd14']=merge([{'cfg':'WJet_Pt_80_120_14TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['WJet_Pt_80_120_UPGstd8']=merge([{'cfg':'WJet_Pt_80_120_8TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])

step1['ZEE_UPGstd14']=merge([{'cfg':'ZEE_14TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['ZEE_UPGstd8']=merge([{'cfg':'ZEE_8TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])

step1['ZMM_UPGstd14']=merge([{'cfg':'ZMM_14TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['ZMM_UPGstd8']=merge([{'cfg':'ZMM_8TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])

step1['ZTT_UPGstd14']=merge([{'cfg':'ZTT_14TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])
step1['ZTT_UPGstd8']=merge([{'cfg':'ZTT_8TeV_cfi','--relval':'25000,250'},step1UpgstdgeomDefaults])



step1['SingleMuPt10_UPGphase1']=merge([{'cfg':'SingleMuPt10_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['SingleMuPt100_UPGphase1']=merge([{'cfg':'SingleMuPt100_cfi','--relval':'9000,250'},step1Upgpixphase1Defaults])
step1['SingleMuPt1000_UPGphase1']=merge([{'cfg':'SingleMuPt1000_cfi'},K9by100,step1Upgpixphase1Defaults])
step1['SingleElectronPt10_UPGphase1']=merge([{'cfg':'SingleElectronPt10_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['SingleElectronPt35_UPGphase1']=merge([{'cfg':'SingleElectronPt35_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['SingleGammaPt10_UPGphase1']=merge([{'cfg':'SingleGammaPt10_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['SingleGammaPt35_UPGphase1']=merge([{'cfg':'SingleGammaPt35_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])

step1['FourMuPt1_200_UPGphase1']=merge([{'cfg':'FourMuPt1_200_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['FourTauPt1_200_UPGphase1']=merge([{'cfg':'FourTauPt1_200_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['FourElectronPt1_50_UPGphase1']=merge([{'cfg':'FourElectronPt1_50_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['FourGammaPt1_50_UPGphase1']=merge([{'cfg':'FourGammaPt1_50_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['FourPiPt1_50_UPGphase1']=merge([{'cfg':'FourPiPt1_50_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])

step1['H120_bbar_Zll_UPGphase1_14']=merge([{'cfg':'HERWIGPP_POWHEG_H120_bbar_Z_ll_14TeV_cff','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['H120_bbar_Zmm_UPGphase1_14']=merge([{'cfg':'HERWIGPP_POWHEG_H120_bbar_Z_mm_14TeV_cff','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['ZZ_MMorBB_UPGphase1_14']=merge([{'cfg':'ZZ_MMorBB_TuneZ2_14TeV_pythia6_tauola_cff','--relval':'25000,250'},step1Upgpixphase1Defaults])

step1['H130GGgluonfusion_UPGphase1_14']=merge([{'cfg':'H130GGgluonfusion_14TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['H130GGgluonfusion_UPGphase1_8']=merge([{'cfg':'H130GGgluonfusion_8TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])

step1['H200chargedTaus_Tauola_UPGphase1_14']=merge([{'cfg':'H200chargedTaus_Tauola_14TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['H200chargedTaus_Tauola_UPGphase1_8']=merge([{'cfg':'H200chargedTaus_Tauola_8TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])

step1['JpsiMM_UPGphase1_14']=merge([{'cfg':'JpsiMM_14TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['JpsiMM_UPGphase1_8']=merge([{'cfg':'JpsiMM_8TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])


step1['LM1_sfts_UPGphase1_14']=merge([{'cfg':'LM1_sfts_14TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['LM1_sfts_UPGphase1_8']=merge([{'cfg':'LM1_sfts_8TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])

step1['MinBias_UPGphase1_8']=merge([{'cfg':'MinBias_TuneZ2star_8TeV_pythia6_cff'},K9by100,step1Upgpixphase1Defaults])
step1['MinBias_UPGphase1_14']=merge([{'cfg':'MinBias_TuneZ2star_14TeV_pythia6_cff'},K9by100,step1Upgpixphase1Defaults])         

step1['PhotonJet_Pt10_UPGphase1_14']=merge([{'cfg':'PhotonJet_Pt10_14TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['PhotonJet_Pt10_UPGphase1_8']=merge([{'cfg':'PhotonJet_Pt10_8TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])

step1['QCDForPF_UPGphase1_14']=merge([{'cfg':'QCDForPF_14TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['QCDForPF_UPGphase1_8']=merge([{'cfg':'QCDForPF_8TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])

step1['QCD_Pt_3000_3500_UPGphase1_14']=merge([{'cfg':'QCD_Pt_3000_3500_14TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['QCD_Pt_3000_3500_UPGphase1_8']=merge([{'cfg':'QCD_Pt_3000_3500_8TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])

step1['QCD_Pt_80_120_UPGphase1_14']=merge([{'cfg':'QCD_Pt_80_120_14TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['QCD_Pt_80_120_UPGphase1_8']=merge([{'cfg':'QCD_Pt_80_120_8TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])

step1['QQH1352T_Tauola_UPGphase1_14']=merge([{'cfg':'QQH1352T_Tauola_14TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['QQH1352T_Tauola_UPGphase1_8']=merge([{'cfg':'QQH1352T_Tauola_8TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])

step1['TTbar_Tauola_UPGphase1_14']=merge([{'cfg':'TTbar_Tauola_14TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['TTbar_Tauola_UPGphase1_8']=merge([{'cfg':'TTbar_Tauola_8TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])

step1['WE_UPGphase1_14']=merge([{'cfg':'WE_14TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['WE_UPGphase1_8']=merge([{'cfg':'WE_8TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])

step1['WM_UPGphase1_14']=merge([{'cfg':'WM_14TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['WM_UPGphase1_8']=merge([{'cfg':'WM_8TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])

step1['WJet_Pt_3000_3500_UPGphase1_14']=merge([{'cfg':'WJet_Pt_3000_3500_14TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['WJet_Pt_3000_3500_UPGphase1_8']=merge([{'cfg':'WJet_Pt_3000_3500_8TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])

step1['WJet_Pt_80_120_UPGphase1_14']=merge([{'cfg':'WJet_Pt_80_120_14TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['WJet_Pt_80_120_UPGphase1_8']=merge([{'cfg':'WJet_Pt_80_120_8TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])

step1['ZEE_UPGphase1_14']=merge([{'cfg':'ZEE_14TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['ZEE_UPGphase1_8']=merge([{'cfg':'ZEE_8TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])

step1['ZMM_UPGphase1_14']=merge([{'cfg':'ZMM_14TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['ZMM_UPGphase1_8']=merge([{'cfg':'ZMM_8TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])

step1['ZTT_UPGphase1_14']=merge([{'cfg':'ZTT_14TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
step1['ZTT_UPGphase1_8']=merge([{'cfg':'ZTT_8TeV_cfi','--relval':'25000,250'},step1Upgpixphase1Defaults])
def changeRefRelease(step1s,listOfPairs):
    for s in step1s:
        if ('INPUT' in step1s[s]):
            oldD=step1[s]['INPUT'].dataSet
            for ref,newRef in listOfPairs:
                if  ref in oldD:
                    step1[s]['INPUT'].dataSet=oldD.replace(ref,newRef)
                                        
def addForAll(steps,d):
    for s in steps:
        steps[s].update(d)
    
#changeRefRelease(step1,[('CMSSW_4_2_0_pre2-START311_V1-v1','CMSSW_4_2_0_pre4-START42_V1-v1'),
#                        ('CMSSW_4_2_0_pre2-MC_311_V1-v1','CMSSW_4_2_0_pre4-MC_42_V1-v1')
#                        ])
# change to:
changeRefRelease(step1,[('CMSSW_4_2_0_pre2-START311_V1-v1','CMSSW_4_1_8_patch9-START311_V2-v1'),
                        ('CMSSW_4_2_0_pre2-MC_311_V1-v1','CMSSW_4_1_8_patch9-START311_V2-v1')
                        ])

#### fastsim section ####
##no forseen to do things in two steps GEN-SIM then FASTIM->end: maybe later
step1FastDefaults =merge([{'-s':'GEN,FASTSIM,HLT:GRun,VALIDATION', '--eventcontent':'FEVTDEBUGHLT','--datatier':'GEN-SIM-DIGI-RECO','--relval':'27000,1000'},step1Defaults])
K100byK1={'--relval':'100000,1000'}
step1['TTbarFS1']=merge([{'cfg':'TTbar_Tauola_7TeV_cfi'},K100byK1,step1FastDefaults])
step1['TTbarFS2']=merge([{'cfg':'TTbar_Tauola_7TeV_cfi'},K100byK1,stCond,step1FastDefaults])
step1['SingleMuPt10FS']=merge([{'cfg':'SingleMuPt10_cfi'},step1FastDefaults])
step1['SingleMuPt100FS']=merge([{'cfg':'SingleMuPt100_cfi'},step1FastDefaults])
step1['ZEEFS1']=merge([{'cfg':'ZEE_7TeV_cfi'},K100byK1,step1FastDefaults])
step1['ZEEFS2']=merge([{'cfg':'ZEE_7TeV_cfi'},K100byK1,stCond,step1FastDefaults])
step1['QCDFlatPt153000FS']=merge([{'cfg':'QCDForPF_7TeV_cfi'},step1FastDefaults])
step1['H130GGgluonfusionFS']=merge([{'cfg':'H130GGgluonfusion_7TeV_cfi'},step1FastDefaults])
##########################



# step2 
step2Defaults = { 'cfg'           : 'step2',
                  '-s'            : 'DIGI,L1,DIGI2RAW,HLT:GRun,RAW2DIGI,L1Reco',
                  '--datatier'    : 'GEN-SIM-DIGI-RAW-HLTDEBUG',
                  '--eventcontent': 'FEVTDEBUGHLT',
                  '--conditions'  : 'auto:mc',
                  }

step2 = {}

step2['DIGIPROD1']=merge([{'--eventcontent':'RAWSIM','--datatier':'GEN-SIM-RAW'},step2Defaults])
step2['DIGI1']=merge([step2Defaults])
step2['DIGI2']=merge([stCond,step2Defaults])
step2['DIGICOS']=merge([{'--scenario':'cosmics','--eventcontent':'FEVTDEBUG','--datatier':'GEN-SIM-DIGI-RAW'},stCond,step2Defaults])

#add this line when testing from an input file that is not strictly GEN-SIM
#addForAll(step2,{'--process':'DIGI'})

dataReco={'--conditions':'auto:com10',
          '-s':'RAW2DIGI,L1Reco,RECO,ALCA:SiStripCalZeroBias+SiStripCalMinBias,DQM',
          '--datatier':'RECO,DQM',
          '--eventcontent':'RECO,DQM',
          '--data':'',
          '--magField':'AutoFromDBCurrent',
          '--customise':'Configuration/DataProcessing/RecoTLR.customisePPData',
          '--inputCommands':'"keep *","drop *_*_*_RECO"',
          '--process':'reRECO',
          }
step2['RECOD']=merge([{'--scenario':'pp',},dataReco])
step2['RECOVALSKIM']=merge([{'--scenario':'pp','--customise':'Configuration/DataProcessing/RecoTLR.customiseVALSKIM','-s':'RAW2DIGI,L1Reco,RECO,DQM'},step2['RECOD']])
step2['RECOVALSKIMALCA']=merge([{'--scenario':'pp','--customise':'Configuration/DataProcessing/RecoTLR.customiseVALSKIM'},step2['RECOD']])


step2['RECOCOSD']=merge([{'--scenario':'cosmics',
                          '-s':'RAW2DIGI,L1Reco,RECO,L1HwVal,DQM,ALCA:MuAlCalIsolatedMu+DtCalib',
                          '--customise':'Configuration/DataProcessing/RecoTLR.customiseCosmicData'
                          },dataReco])


step2['RECOSTD']={'cfg' : 'dud',
                  '-s'  : 'DIGI,L1,DIGI2RAW,RAW2DIGI,L1Reco,RECO,VALIDATION,DQM',
                  '--eventcontent' : 'FEVTDEBUG,DQM',
                  '--datatier' : 'GEN-SIM-RECO,DQM',
                  '--conditions' : 'DESIGN42_V17S::All',
                  '--slhc' : 'stdgeom',
                  '--customise' : 'SLHCUpgradeSimulations/Geometry/customise_stdgeom.customise'
                  }

step2['STDPU']=merge([{'--customise':'SLHCUpgradeSimulations/Geometry/customise_stdgeom.customise_pu15_25ns'},step2['RECOSTD']])


step2['RECOPHASE1']={'cfg' : 'dud',
                  '-s'  : 'DIGI,L1,DIGI2RAW,RAW2DIGI,L1Reco,RECO,VALIDATION,DQM',
                  '--eventcontent' : 'FEVTDEBUG,DQM',
                  '--datatier' : 'GEN-SIM-RECO,DQM',
                  '--conditions' : 'DESIGN42_V17S::All',
                  '--slhc' : 'Phase1_R30F12',
                  '--customise' : 'SLHCUpgradeSimulations/Geometry/customise_phase1.customise'
                  }

step2['PHASE1PU']=merge([{'--customise':'SLHCUpgradeSimulations/Geometry/customise_phase1.customise_pu15_25ns'},step2['RECOPHASE1']])
# step3 
step3Defaults = { 'cfg'           : 'step3',
                  '-s'            : 'RAW2DIGI,L1Reco,RECO,VALIDATION,DQM',
                  '--filein'      : 'file:reco.root',
                  '--conditions'  : 'auto:mc',
                  '--no_exec'     : '',
                  '--datatier'    : 'GEN-SIM-RECO,DQM',
                  '--eventcontent': 'RECOSIM,DQM'
                  }

step3 = {}

step3['RECO1']=merge([step3Defaults])
step3['RECO2']=merge([stCond,step3Defaults])
step3['RECOPROD1']=merge([{ '-s' : 'RAW2DIGI,L1Reco,RECO', '--datatier' : 'GEN-SIM-RECO,AODSIM', '--eventcontent' : 'RECOSIM,AODSIM'},step3Defaults])
step3['RECOMU']=merge([{'-s':'RAW2DIGI,L1Reco,RECO,ALCA:MuAlCalIsolatedMu+DtCalib','--datatier':'GEN-SIM-RECO','--eventcontent':'RECOSIM'},stCond,step3Defaults])
step3['RECOCOS']=merge([{'-s':'RAW2DIGI,L1Reco,RECO,ALCA:MuAlCalIsolatedMu','--datatier':'GEN-SIM-RECO','--eventcontent':'RECOSIM','--scenario':'cosmics'},stCond,step3Defaults])
step3['RECOMIN']=merge([{'-s':'RAW2DIGI,L1Reco,RECO,ALCA:SiStripCalZeroBias+SiStripCalMinBias+EcalCalPhiSym+EcalCalPi0Calib+EcalCalEtaCalib,VALIDATION,DQM'},stCond,step3Defaults])
step3['RECOQCD']=merge([{'-s':'RAW2DIGI,L1Reco,RECO,ALCA:MuAlCalIsolatedMu+DtCalib+EcalCalPi0Calib+EcalCalEtaCalib,VALIDATION,DQM'},stCond,step3Defaults])

#add this line when testing from an input file that is not strictly GEN-SIM
#addForAll(step3,{'--hltProcess':'DIGI'})

step3['ALCACOSD']={'--conditions':'auto:com10',
                   '--datatier':'ALCARECO',
                   '--eventcontent':'ALCARECO',
                   '--scenario':'cosmics',
                   '-s':'ALCA:TkAlCosmics0T+MuAlGlobalCosmics+HcalCalHOCosmics+DQM'
                   }

   
# step4
step4Defaults = { 'cfg'           : 'step4',
                  '-s'            : 'ALCA:TkAlMuonIsolated+TkAlMinBias+EcalCalElectron+HcalCalIsoTrk+MuAlOverlaps',
                  '-n'            : 1000,
                  '--filein'      : 'file:reco.root',
                  '--conditions'  : 'auto:mc',
                  '--no_exec'     : '',
                  '--datatier'    : 'ALCARECO',
                  '--oneoutput'   : '',
                  '--eventcontent': 'ALCARECO',
                  }
step4 = {}

step4['ALCATT1']=merge([step4Defaults])
step4['ALCATT2']=merge([stCond,step4Defaults])
step4['ALCAMIN']=merge([{'-s':'ALCA:TkAlMinBias'},stCond,step4Defaults])
step4['ALCAQCD']=merge([{'-s':'ALCA:HcalCalIsoTrk+HcalCalDijets+HcalCalHO'},stCond,step4Defaults])
step4['ALCAMU']=merge([{'-s':'ALCA:MuAlOverlaps+TkAlMuonIsolated+TkAlZMuMu'},stCond,step4Defaults])
step4['ALCACOS']=merge([{'-s':'ALCA:TkAlCosmics0T+MuAlGlobalCosmics+HcalCalHOCosmics'},stCond,step4Defaults])
step4['ALCABH']=merge([{'-s':'ALCA:TkAlBeamHalo+MuAlBeamHaloOverlaps+MuAlBeamHalo'},stCond,step4Defaults])


#### for special wfs ###
step1['TTbar_REDIGI_RERECO']=merge([{'cfg':'TTbar_Tauola_7TeV_cfi',
                                     '-s':'GEN,SIM,DIGI,L1,DIGI2RAW,HLT:GRun,RAW2DIGI,L1Reco,RECO,ALCA:MuAlCalIsolatedMu+DtCalib,VALIDATION,DQM',
                                     '--datatier':'GEN-SIM-RECO,DQM',
                                     '--eventcontent':'FEVTDEBUGHLT,DQM'},
                                    K9by50,stCond,step1Defaults])
step2['REDIGI2RECO']=merge([{'-s':'DIGI,L1,DIGI2RAW,HLT:GRun,RAW2DIGI,L1Reco,RECO,VALIDATION,DQM',
                             '--customise':'Configuration/StandardSequences/DigiToRecoNoPU.customise',
                             '--filtername':'REDIGItoRECO',
                             '--process':'REDIGI'},
                            stCond,step3Defaults])
step3['RECOFROMRECO']=merge([{'-s':'RECO,ALCA:MuAlCalIsolatedMu+DtCalib',
                              '--filtername':'RECOfromRECO',
                              '--datatier':'GEN-SIM-RECO',
                              '--eventcontent':'RECOSIM'},
                             stCond,step3Defaults])

#HARVESTING upgrade
step3upgrade = { '-s':'HARVESTING:validationHarvesting+dqmHarvesting',
                   '--conditions':'DESIGN42_V17S::All',
                   '--mc':'',
                   '--filein':'file:step2_inDQM.root',
		   '--scenario':'pp',
		   '--harvesting' : 'AtRunEnd '                }


step3['HARVESTUPSTD']=merge([step3upgrade,{"--customise":"SLHCUpgradeSimulations.Geometry.customise_stdgeom",'--inline_cust':''}])
step3['HARVESTUPPH1']=merge([step3upgrade,{"--customise":"SLHCUpgradeSimulations.Geometry.customise_phase1","--inline_cust":''}])



# to handle things easier in other places, make a list of all the steps:
stepList = [step1, step2, step3, step4]

steps = {}

def updateme(aDict, anotherOne):
    for new_key in anotherOne:
        if not new_key in aDict:
            aDict[new_key] = anotherOne[new_key]
        else:
            print("Redefininig %s ? ==> no"%(new_key))
    
updateme(steps,step1)
updateme(steps,step2)
updateme(steps,step3)
updateme(steps,step4)


steps['RECO2'].pop('--filein')
