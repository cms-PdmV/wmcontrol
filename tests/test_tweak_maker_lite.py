import json
import re
import sys
import tempfile
import unittest
from functools import reduce
from pathlib import Path

sys.path.append(str(Path().cwd()))

from tests.utils import wmcontrol
from tests.utils.unittest import parametrize
from modules.tweak_maker_lite import FilterFilesFrom, MaxFilesToKeep


class TestInputFileFilter(unittest.TestCase):
    """Check the `TweakMakerLite` stability after patching the input files on config submission."""

    # Files should be removed
    _files_removed = [
        # BPH-GenericGSmearS-00004
        {
            "container_major_version": "el8",
            "arch": "el8_amd64_gcc10",
            "cmssw_release": "CMSSW_12_4_14_patch3",
            "output_config_file": "BPH-GenericGSmearS-00004_1_cfg.py",
            "content": [
                "EVENTS=252",
                (
                    r"cmsDriver.py  --python_filename BPH-GenericGSmearS-00004_1_cfg.py --eventcontent RAWSIM "
                    r"--customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM "
                    r"--fileout file:BPH-GenericGSmearS-00004.root --conditions 124X_mcRun3_2022_realistic_v12 "
                    r"--beamspot Realistic25ns13p6TeVEarly2022Collision --step GEN:pgen_smear,SIM --nThreads 8 "
                    r'--geometry DB:Extended --filein "dbs:/InclusiveDileptonMinBias_TuneCP5Plus_13p6TeV_pythia8/GenericNoSmearGEN-124X_mcRun3_2022_realistic_v12-v2/GEN" '
                    r"--era Run3 --no_exec --mc -n $EVENTS || exit $? ;"
                ),
            ],
        },
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

    # Files should remain unfiltered
    _files_untouched = [
        # B2G-RunIIFall17pLHE-00003
        {
            "container_major_version": "el6",
            "arch": "slc6_amd64_gcc630",
            "cmssw_release": "CMSSW_9_3_13",
            "output_config_file": "B2G-RunIIFall17pLHE-00003_1_cfg.py",
            "content": [
                "EVENTS=10000",
                (
                    r'cmsDriver.py Configuration/GenProduction/python/B2G-RunIIFall17pLHE-00003-fragment.py --python_filename B2G-RunIIFall17pLHE-00003_1_cfg.py '
                    r'--eventcontent LHE --customise Configuration/DataProcessing/Utils.addMonitoring --datatier LHE --fileout file:B2G-RunIIFall17pLHE-00003.root '
                    r'--conditions 93X_mc2017_realistic_v3 --step NONE --filein "lhe:12937" --no_exec --mc -n $EVENTS || exit $? ;'
                ),
            ],
            "expected_output": {
                "process.source.fileNames": 1
            },
        },
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
            "expected_output": {
                "process.source.fileNames": 502
            },
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

    @parametrize(_files_removed)
    def test_files_removed(self, **params):
        """Check files are removed based on the source type."""

        temp_as_path = Path(self.temp_folder.name)
        exit_code, stdout, _ = wmcontrol._run_wmupload(
            test_folder=temp_as_path, **params
        )
        self.assertEqual(0, exit_code)

        tweak_file_path = list(temp_as_path.glob("*.tweaks"))
        self.assertEqual(
            1, len(tweak_file_path), "There should be only a tweak file available!"
        )

        tweak_file = {}
        with open(file=tweak_file_path[0], encoding="utf-8") as f:
            tweak_file = json.load(f)

        for attrib in FilterFilesFrom:
            if attrib in tweak_file:
                value = tweak_file[attrib]
                self.assertLessEqual(
                    len(value),
                    MaxFilesToKeep,
                    msg="The list has more files than expected!",
                )

        couchid_file = list(temp_as_path.glob("*.couchID"))
        self.assertEqual(1, len(couchid_file), "The CouchID file should be available!")

        expected_ids = {"DocID": False, "Revision": False}
        for line in stdout.splitlines():
            content = line.strip()
            if "DocID" in content:
                remove_extra_spaces = re.sub(r" +", " ", content)
                self.assertTrue(
                    self._docid_regex.match(remove_extra_spaces),
                    "Document ID is invalid!",
                )
                expected_ids["DocID"] = True
            elif "Revision" in content:
                remove_extra_spaces = re.sub(r" +", " ", content)
                self.assertTrue(
                    self._revision_regex.match(remove_extra_spaces),
                    "Revision ID is invalid!",
                )
                expected_ids["Revision"] = True

        for expected in expected_ids:
            self.assertTrue(
                expected_ids[expected],
                msg="%s is not available in the stdout result!" % (expected),
            )

    @parametrize(_files_untouched)
    def test_files_not_removed(self, **params):
        """Check files remain unfiltered for some group of sources."""

        temp_as_path = Path(self.temp_folder.name)
        exit_code, stdout, _ = wmcontrol._run_wmupload(
            test_folder=temp_as_path, **params
        )
        self.assertEqual(0, exit_code)

        tweak_file_path = list(temp_as_path.glob("*.tweaks"))
        self.assertEqual(
            1, len(tweak_file_path), "There should be only a tweak file available!"
        )

        tweak_file = {}
        with open(file=tweak_file_path[0], encoding="utf-8") as f:
            tweak_file = json.load(f)

        for attrib, number_of_files in params["expected_output"].items():
            # Nested value
            value = reduce(lambda d, key: d[key], attrib.split('.'), tweak_file)
            self.assertEqual(len(value), number_of_files, "Number of files does not match!")

        couchid_file = list(temp_as_path.glob("*.couchID"))
        self.assertEqual(1, len(couchid_file), "The CouchID file should be available!")

        expected_ids = {"DocID": False, "Revision": False}
        for line in stdout.splitlines():
            content = line.strip()
            if "DocID" in content:
                remove_extra_spaces = re.sub(r" +", " ", content)
                self.assertTrue(
                    self._docid_regex.match(remove_extra_spaces),
                    "Document ID is invalid!",
                )
                expected_ids["DocID"] = True
            elif "Revision" in content:
                remove_extra_spaces = re.sub(r" +", " ", content)
                self.assertTrue(
                    self._revision_regex.match(remove_extra_spaces),
                    "Revision ID is invalid!",
                )
                expected_ids["Revision"] = True

        for expected in expected_ids:
            self.assertTrue(
                expected_ids[expected],
                msg="%s is not available in the stdout result!" % (expected),
            )

if __name__ == "__main__":
    unittest.main()
