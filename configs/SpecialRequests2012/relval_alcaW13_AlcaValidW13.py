
# import the definition of the steps and input files:
from  Configuration.PyReleaseValidation.relval_steps import *

# here only define the workflows as a combination of the steps defined above:
workflows = Matrix()

#minbias for TK
workflows[20001] = ['', ['RunMinBias2012A','RECOSKIM']]
workflows[20002] = ['', ['RunMinBias2012B','RECOSKIM']]
workflows[20003] = ['', ['RunMinBias2012C','RECOSKIM']]
workflows[30001] = ['', ['RunMinBias2012AOldAPE','RECOSKIM']]
workflows[30002] = ['', ['RunMinBias2012BOldAPE','RECOSKIM']]
workflows[30003] = ['', ['RunMinBias2012COldAPE','RECOSKIM']]
# single mu for TK
workflows[20004] = ['', ['RunMu2012A','RECOSKIM']]
workflows[30004] = ['', ['RunMu2012AOldAPE','RECOSKIM']]
workflows[20005] = ['', ['RunMu2012B','RECOSKIM']]
workflows[30005] = ['', ['RunMu2012BOldAPE','RECOSKIM']]
workflows[20006] = ['', ['RunMu2012C','RECOSKIM']]
workflows[30006] = ['', ['RunMu2012COldAPE','RECOSKIM']]
# zmu skim for TK
workflows[20007] = ['', ['ZMuSkim2012A','RECOSKIM']]
workflows[20008.1] = ['', ['ZMuSkim2012Bv1','RECOSKIM']]
workflows[20008.2] = ['', ['ZMuSkim2012Bv2','RECOSKIM']]
workflows[20009.2] = ['', ['ZMuSkim2012Cv2','RECOSKIM']]
workflows[20009.3] = ['', ['ZMuSkim2012Cv3','RECOSKIM']]

#2012A for calorimeters
workflows[20010] = ['', ['RunJet2012Acalo','RECOSKIM']]
workflows[20011] = ['', ['RunElectron2012Acalo','RECOSKIM']]
workflows[20012] = ['', ['ZElSkim2012Acalo','RECOSKIM']]
workflows[20013] = ['', ['RunPhoton2012Acalo','RECOSKIM']]

#2012B for calorimeters
workflows[20014] = ['', ['RunJetHT2012Bcalo','RECOSKIM']]
workflows[20015] = ['', ['RunElectron2012Bcalo','RECOSKIM']]
workflows[20016] = ['', ['ZElSkim2012Bcalo','RECOSKIM']]
workflows[20017] = ['', ['RunPhoton2012Bcalo','RECOSKIM']]

#2012C for calorimeters
workflows[20018] = ['', ['RunJetHT2012Ccalo','RECOSKIM']]
workflows[20019] = ['', ['RunElectron2012Ccalo','RECOSKIM']]
workflows[20020] = ['', ['ZElSkim2012Ccalo','RECOSKIM']]
workflows[20021] = ['', ['RunPhoton2012Ccalo','RECOSKIM']]



#--command "--conditions <a GT >"
#workflows[20004] = ['', ['RunMu2012A','RECOSKIM']]


    
