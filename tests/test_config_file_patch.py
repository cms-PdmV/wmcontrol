import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.append(str(Path().cwd()))

from tests.utils import wmcontrol
from tests.utils.unittest import parametrize


class TestFilterFilesFromConfigFile(unittest.TestCase):
    """Check the configuration file is modified properly."""

    # A truncated configuration file should be created
    _creates_truncated_file = [
        # JME-RunIII2024Summer24DR-00002
        {
            "container_major_version": "el8",
            "arch": "el8_amd64_gcc12",
            "cmssw_release": "CMSSW_14_0_19_patch2",
            "output_config_file": "JME-RunIII2024Summer24DR-00002_1_cfg.py",
            "content": [
                "EVENTS=252",
                (
                    r"cmsDriver.py --python_filename JME-RunIII2024Summer24DR-00002_1_cfg.py --eventcontent RAWSIM --pileup Flat_10_50_25ns "
                    r"--customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM-RAW --fileout file:JME-RunIII2024Summer24DR-00002_0.root "
                    r'--pileup_input "dbs:/MinBias_TuneCP5_13p6TeV-pythia8/RunIII2024Summer24GS-140X_mcRun3_2024_realistic_v20-v1/GEN-SIM" '
                    r'--conditions 140X_mcRun3_2024_realistic_v26 --customise_commands "process.mix.input.nbPileupEvents.probFunctionVariable = cms.vint32(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120) \n '
                    r'process.mix.input.nbPileupEvents.probValue = cms.vdouble(0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446,0.00826446)" '
                    r'--step DIGI,L1,DIGI2RAW,HLT:2024v14 --geometry DB:Extended --filein "dbs:/QCD_Bin-PT-15to7000_Par-PT-flat2022_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24GS-140X_mcRun3_2024_realistic_v26-v2/GEN-SIM" '
                    r"--era Run3_2024 --no_exec --mc -n $EVENTS || exit $? ;"
                ),
            ],
        },
        # HIG-RunIISummer20UL16DIGIPremix-13259
        {
            "container_major_version": "el7",
            "arch": "slc7_amd64_gcc700",
            "cmssw_release": "CMSSW_10_6_17_patch1",
            "output_config_file": "HIG-RunIISummer20UL16DIGIPremix-13259_1_cfg.py",
            "content": [
                "EVENTS=560",
                (
                    r'cmsDriver.py  --python_filename HIG-RunIISummer20UL16DIGIPremix-13259_1_cfg.py --eventcontent PREMIXRAW '
                    r'--customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM-DIGI --fileout file:HIG-RunIISummer20UL16DIGIPremix-13259.root '
                    r'--pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer20ULPrePremix-UL16_106X_mcRun2_asymptotic_v13-v1/PREMIX" --conditions 106X_mcRun2_asymptotic_v13 '
                    r'--step DIGI,DATAMIX,L1,DIGI2RAW --procModifiers premix_stage2 --geometry DB:Extended --filein file:HIG-RunIISummer20UL16SIM-13264.root --datamix PreMix '
                    r'--era Run2_2016 --runUnscheduled --no_exec --mc -n $EVENTS || exit $? ;'
                ),
            ],
        },
    ]

    # No truncated configuration file should be created
    _not_creates_truncated_file = [
        # BPH-RunIII2024Summer24pLHEGS-00001
        {
            "container_major_version": "el8",
            "arch": "el8_amd64_gcc12",
            "cmssw_release": "CMSSW_14_0_19",
            "output_config_file": "BPH-RunIII2024Summer24pLHEGS-00001_1_cfg.py",
            "content": [
                "EVENTS=3088",
                (
                    r'cmsDriver.py Configuration/GenProduction/python/BPH-RunIII2024Summer24pLHEGS-00001-fragment.py --python_filename BPH-RunIII2024Summer24pLHEGS-00001_1_cfg.py '
                    r'--eventcontent LHE --customise Configuration/DataProcessing/Utils.addMonitoring --datatier LHE --fileout file:BPH-RunIII2024Summer24pLHEGS-00001_0.root '
                    r'--conditions 140X_mcRun3_2024_realistic_v26 --step NONE --filein "lhe:20022" --era Run3_2024 --no_exec --mc -n $EVENTS || exit $? ;'
                ),
            ],
        }
    ]

    # On configuration upload: No truncated configuration file should be created
    # The size is lower than the threshold and the original file must be uploaded
    _config_size_under_limit = [
        # B2G-Run3Summer23BPixDRPremix-00003
        {
            "container_major_version": "el8",
            "arch": "el8_amd64_gcc11",
            "cmssw_release": "CMSSW_13_0_14",
            "output_config_file": "B2G-Run3Summer23BPixDRPremix-00003_1_cfg.py",
            "content": [
                "EVENTS=1041",
                (
                    r'cmsDriver.py --python_filename B2G-Run3Summer23BPixDRPremix-00003_1_cfg.py --eventcontent PREMIXRAW --customise Configuration/DataProcessing/Utils.addMonitoring '
                    r'--datatier GEN-SIM-RAW --fileout file:B2G-Run3Summer23BPixDRPremix-00003_0.root --pileup_input "dbs:/Neutrino_E-10_gun/Run3Summer21PrePremix-Summer23BPix_130X_mcRun3_2023_realistic_postBPix_v1-v1/PREMIX" '
                    r'--conditions 130X_mcRun3_2023_realistic_postBPix_v6 --step DIGI,DATAMIX,L1,DIGI2RAW,HLT:2023v12 --procModifiers premix_stage2 --geometry DB:Extended --filein file:B2G-Run3Summer23BPixwmLHEGS-00005.root '
                    r'--datamix PreMix --era Run3_2023 --no_exec --mc -n $EVENTS || exit $? ;'
                ),
            ],
        },
        # B2G-RunIISummer16DR80-00007
        {
            "container_major_version": "el6",
            "arch": "slc6_amd64_gcc530",
            "cmssw_release": "CMSSW_8_0_31",
            "output_config_file": "B2G-RunIISummer16DR80-00007_1_cfg.py",
            "content": [
                "EVENTS=252",
                (
                    r'cmsDriver.py --python_filename B2G-RunIISummer16DR80-00007_1_cfg.py --eventcontent RAWSIM --pileup 2016_25ns_Moriond17MC_PoissonOOTPU '
                    r'--customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM-RAW --fileout file:B2G-RunIISummer16DR80-00007_0.root '
                    r'--pileup_input "dbs:/MinBias_TuneCUETP8M1_13TeV-pythia8/RunIISummer15GS-MCRUN2_71_V1_ext1-v1/GEN-SIM" --conditions 80X_mcRun2_asymptotic_2016_TrancheIV_v6 '
                    r'--step DIGI,L1,DIGI2RAW,HLT:@frozen2016 --filein file:B2G-RunIISummer15wmLHEGS-03742.root --era Run2_2016 --no_exec --mc -n $EVENTS || exit $? ;'
                ),
            ],
        },
    ]

    _docid_regex = re.compile(r"^DocID: [a-z0-9]+$")
    _revision_regex = re.compile(r"^Revision: [0-9]-[a-z0-9]+$")

    def setUp(self):
        super().setUp()
        self.temp_folder = tempfile.TemporaryDirectory()

    def tearDown(self):
        if hasattr(self, "temp_folder"):
            if isinstance(self.temp_folder, tempfile.TemporaryDirectory):
                self.temp_folder.cleanup()
        super().tearDown()

    @parametrize(_creates_truncated_file)
    def test_config_is_truncated(self, **params):
        temp_as_path = Path(self.temp_folder.name)
        exit_code, stdout, _ = wmcontrol._run_config_patcher(
            test_folder=temp_as_path,
            max_files_to_keep=1,
            **params
        )
        self.assertEqual(0, exit_code)

        modified_config_path = list(temp_as_path.glob("*-wmupload.py"))
        self.assertEqual(
            1, len(modified_config_path), "There should be only a modified configuration file!"
        )

        # Make sure there are no other errors when executing the statements
        params["output_config_file"] = str(modified_config_path[0])
        params["content"] = []
        exit_code, stdout, _ = wmcontrol._run_wmupload(
            test_folder=temp_as_path, submit_to_reqmgr=False, **params
        )
        self.assertEqual(0, exit_code)

    @parametrize(_not_creates_truncated_file)
    def test_config_not_truncated(self, **params):
        temp_as_path = Path(self.temp_folder.name)
        exit_code, stdout, _ = wmcontrol._run_config_patcher(
            test_folder=temp_as_path,
            max_files_to_keep=1,
            **params
        )
        self.assertEqual(0, exit_code)

        modified_config_path = list(temp_as_path.glob("*-wmupload.py"))
        self.assertEqual(
            0, len(modified_config_path), "There must not be a modified configuration file!"
        )


    @parametrize(_config_size_under_limit)
    def test_original_config_is_uploaded(self, **params):
        temp_as_path = Path(self.temp_folder.name)
        exit_code, stdout, _ = wmcontrol._run_wmupload(
            test_folder=temp_as_path, submit_to_reqmgr=True, **params
        )
        self.assertEqual(0, exit_code)

        modified_config_path = list(temp_as_path.glob("*-wmupload.py"))
        self.assertEqual(
            0, len(modified_config_path), "There must not be a modified configuration file!"
        )


if __name__ == "__main__":
    unittest.main()
