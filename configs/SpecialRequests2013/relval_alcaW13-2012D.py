
# import the definition of the steps and input files:
from  Configuration.PyReleaseValidation.relval_steps import *

# here only define the workflows as a combination of the steps defined above:
workflows = Matrix()



# SingleMuSkim and MinBias
workflows[70001] = ['', ['ZMuSkim2012D','RECOSKIM']]
workflows[70002] = ['', ['MinimumBias2012D','RECOSKIM']]

# SingleMu JetHT DoubleElectron-Zskim SinglePhoton
workflows[70003] = ['', ['SingMu2012D','RECOSKIM']]
workflows[70004] = ['', ['JetHT2012D','RECOSKIM']]
workflows[70005] = ['', ['DoubEle2012D','RECOSKIM']]
workflows[70006] = ['', ['SingPho2012D','RECOSKIM']]

# SingleElectron
workflows[70007] = ['', ['SingEle2012D','RECOSKIM']]
