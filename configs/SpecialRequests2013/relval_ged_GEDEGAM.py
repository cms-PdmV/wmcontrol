
# import the definition of the steps and input files:
from  Configuration.PyReleaseValidation.relval_steps import *

# here only define the workflows as a combination of the steps defined above:
workflows = Matrix()

workflows[4000] = ['', ['TTbar','DIGI','RECODBG']]
workflows[4001] = ['', ['TTbar','DIGIPU1','RECOPUDBG']]

workflows[4002] = ['', ['ZEE','DIGI','RECO']]
workflows[4003] = ['', ['ZMM','DIGI','RECO']]

workflows[4004] = ['QCD_FlatPt_15_3000', ['QCD_FlatPt_15_3000HS','DIGI','RECO']]
workflows[4005] = ['QCD_FlatPt_15_3000', ['QCD_FlatPt_15_3000HS','DIGIPU1','RECOPU1']]

workflows[4006] = ['SingleEle_FlatPt_1_300_CustomEvC', ['SingleEle_FlatPt_1_300_CustomEvCHS','DIGIEGMGED','RECOPUEGMGED']]
workflows[4007] = ['SingleGamma_FlatPt_1_300_CustomEvC', ['SingleGamma_FlatPt_1_300_CustomEvCHS','DIGIEGMGED','RECOPUEGMGED']]

workflows[4010] = ['QCD_Pt_30_80_BCtoE_CustomEvC', ['QCD_Pt_30_80_BCtoE_CustomEvCHS','DIGIEGMGED','RECOPUEGMGED']]
workflows[4011] = ['QCD_Pt_80_170_BCtoE_CustomEvC', ['QCD_Pt_80_170_BCtoE_CustomEvCHS','DIGIEGMGED','RECOPUEGMGED']]
workflows[4012] = ['ZEE_CustomEvC', ['ZEE_CustomEvCHS','DIGIEGMGED','RECOPUEGMGED']]
workflows[4013] = ['PhotonJet_Pt_10EvC', ['PhotonJet_Pt_10EvCHS','DIGIEGMGED','RECOPUEGMGED']]
workflows[4014] = ['QCDForPF_EvC', ['QCDForPF_EvCHS','DIGIEGMGEDPF','RECOPUEGMGEDPF']]
