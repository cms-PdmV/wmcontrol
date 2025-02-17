"""Provide some functions for creating a script for running `wmcontrol` modules."""

import copy
import os
import re
import socket
import subprocess
import uuid
import warnings


def _run_using(**kwargs):
    """Create an auxiliary scripts and run its instructions using a specific OS version.

    Args:
        **containter_major_version (str): Container architecture to use
            e.g: el7, el8, el9.
        **script_name (str): Script name, e.g: Testing.sh
        **run (list[str]): Embedded instructions to execute.

    Returns:
        list[str]: A bash script.
    """
    container_major_version = kwargs["container_major_version"]
    script_name = kwargs["script_name"]
    run = kwargs["run"]
    placeholder = str(uuid.uuid4()).strip().split("-")[0]

    # Prepare the script
    script = [
        "cat <<'%s' > '%s'" % (placeholder, script_name),
    ]
    script += run
    script += [
        "",
        "%s" % (placeholder),
        "",
        "chmod +x '%s'" % (script_name),
        'if [ -e "/cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/%s:amd64" ]; then'
        % (container_major_version),
        '   CONTAINER_NAME="%s:amd64"' % (container_major_version),
        'elif [ -e "/cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/%s:x86_64" ]; then'
        % (container_major_version),
        '   CONTAINER_NAME="%s:x86_64"' % (container_major_version),
        "else",
        '   echo "Could not find amd64 or x86_64 for el8"',
        "   exit 1",
        "fi",
        "",
        "singularity run --no-home /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/$CONTAINER_NAME $(echo $(pwd)/%s)"
        % (script_name),
        "",
    ]

    return script


def _generate_files(**kwargs):
    """Create an auxiliary script that run procedures in a `cmssw` environment.

    Args:
        **containter_major_version (str): Container architecture to use
            e.g: el7, el8, el9.
        **arch (str): CMSSW SCRAM architecture, e.g: el8_amd64_gcc10.
        **cmssw_release (str): CMSSW release, e.g: CMSSW_12_4_14_patch3
        **script_name (str): Script name, e.g: Testing.sh
        **run (list[str]): Embedded instructions to execute.

    Returns:
        list[str]: A bash script for creating a tweak file.
    """
    args = copy.deepcopy(kwargs)
    arch = args["arch"]
    cmssw_release = args["cmssw_release"]
    run = args["run"]

    # Prepare execution environment
    embedded = [
        "#!/bin/bash",
        "export SCRAM_ARCH=%s" % (arch),
        "source /cvmfs/cms.cern.ch/cmsset_default.sh",
        "scram p CMSSW %s" % (cmssw_release),
        "cd ./%s/src" % (cmssw_release),
        "eval `scram runtime -sh`",
        "scram b",
        "cd '../../'",
        "",
    ]

    # Include content
    embedded += run
    args["run"] = embedded
    return _run_using(**args)


def _create_tweak_script(**kwargs):
    """Create an auxiliary script for generating the tweak file

    Args:
        **containter_major_version (str): Container architecture to use
            e.g: el7, el8, el9.
        **arch (str): CMSSW SCRAM architecture, e.g: el8_amd64_gcc10.
        **cmssw_release (str): CMSSW release, e.g: CMSSW_12_4_14_patch3
        **output_config_file (str): Python filename provided to cmsDriver.py via `--python-filename`.
        **content (list[str]): Content to be embedded for running the simulation via
            cmsDriver.py steps.

    Returns:
        list[str]: A bash script for creating a tweak file.
    """
    args = copy.deepcopy(kwargs)
    content = args["content"]
    output_config_file = args["output_config_file"]

    # Embedded instructions
    embedded = []
    embedded += content

    # Check Python version
    embedded += [
        "",
        "if command -v python3 &> /dev/null; then",
        "   PYTHON_CMD='python3'",
        "else",
        "   PYTHON_CMD='python'",
        "fi",
        'echo "Using Python as: $PYTHON_CMD"',
        "$PYTHON_CMD --version",
    ]

    # Create the tweak file
    embedded += [
        "",
        'WMCONTROL_PATH="$HOME/wmcontrol"',
        'if [ ! -e "$WMCONTROL_PATH" ]; then',
        '   echo "The wmcontrol repo is not available at: $WMCONTROL_PATH. Please clone and checkout!"',
        "   exit 1",
        "fi",
        "",
        'export PATH="${WMCONTROL_PATH}:${PATH}"',
        "$PYTHON_CMD `which wmupload.py` --create-tweak %s || exit $?"
        % (output_config_file),
    ]

    args["script_name"] = "TestCreateTweak.sh"
    args["run"] = embedded
    return _generate_files(**args)


def _upload_tweak_script(**kwargs):
    """Create an auxiliary script for uploading the configuration to ReqMgr2 testbed.

    Args:
        **output_config_file (str): Python filename provided to cmsDriver.py via `--python-filename`.

    Returns:
        list[str]: A bash script for uploading the config file.
    """
    args = copy.deepcopy(kwargs)
    output_config_file = args["output_config_file"]
    script_name = "TestUploadTweak.sh"

    # Check Python version
    embedded = [
        "#!/bin/bash",
        "",
        "if command -v python3 &> /dev/null; then",
        "   PYTHON_CMD='python3'",
        "else",
        "   PYTHON_CMD='python'",
        "fi",
        'echo "Using Python as: $PYTHON_CMD"',
        "$PYTHON_CMD --version",
        "",
        'WMCONTROL_PATH="$HOME/wmcontrol"',
        'if [ ! -e "$WMCONTROL_PATH" ]; then',
        '   echo "The wmcontrol repo is not available at: $WMCONTROL_PATH. Please clone and checkout!"',
        "   exit 1",
        "fi",
        "",
        'export PATH="${WMCONTROL_PATH}:${PATH}"',
        '$PYTHON_CMD `which wmupload.py` -u "$(whoami)" -g "Testing" --from-tweak --wmtest %s || exit $?'
        % (output_config_file),
    ]

    args["run"] = embedded
    args["script_name"] = script_name
    args["container_major_version"] = "el9"
    return _run_using(**args)


def _run_wmupload(test_folder=None, execute=True, submit_to_reqmgr=True, **kwargs):
    """Create an execute a test script for validating the wmupload module.

    The resulting script uses several programs distributed only in CERN nodes.
    Consider executing it via `lxplus` nodes.

    Args:
        test_folder (str): Path to the temporary folder to execute the test script.
            If `None`, it will be set to the current working directory.
        execute (bool): Execute the test script.
        submit_to_reqmgr (bool): Include the upload script instructions for
            uploading to ReqMgr2.

        **containter_major_version (str): Container architecture to use
            e.g: el7, el8, el9.
        **arch (str): CMSSW SCRAM architecture, e.g: el8_amd64_gcc10.
        **cmsw_release (str): CMSSW release, e.g: CMSSW_12_4_14_patch3
        **output_config_file (str): Python filename provided to cmsDriver.py via `--python-filename`.
        **content (list[str]): Content to be embedded for running the simulation via
            cmsDriver.py steps.

    Returns:
        The exit code, standard output, and standard error result of the execution of
            the script. `None` in case the execution is skipped.
    """
    test_folder_path = test_folder if test_folder else os.getcwd()
    wrapper_script_name = "%s/Testing-%s.sh" % (test_folder_path, str(uuid.uuid4()))
    wrapper_script = [
        "#!/bin/bash",
        "export APPTAINER_BINDPATH='/afs,/cvmfs,/cvmfs/grid.cern.ch/etc/grid-security:/etc/grid-security,/eos,/etc/pki/ca-trust,/run/user,/var/run/user'",
        'export SINGULARITY_CACHEDIR="/tmp/$(whoami)/singularity"',
        'echo "Running test script at: $(hostname)"',
        'echo "Test working folder is: $(pwd -P)"',
        'voms-proxy-init --voms cms --out "$(pwd)/voms_proxy.txt" --hours 4',
        'export X509_USER_PROXY="$(pwd)/voms_proxy.txt"',
        "",
    ]

    # Include tweak script
    wrapper_script += _create_tweak_script(**kwargs)

    # Include uploader script
    if submit_to_reqmgr:
        wrapper_script += _upload_tweak_script(**kwargs)

    with open(file=wrapper_script_name, mode="w", encoding="utf-8") as f:
        f.writelines("\n".join(wrapper_script))

    # Execute
    if not execute:
        return None

    hostname = socket.getfqdn()
    if not re.match(r"^lxplus[0-9]{3,4}\.cern\.ch$", hostname):
        warnings.warn(
            (
                "You're running outside CERN lxplus nodes. "
                "Make sure all the required modules by the test script are available via $PATH"
            ),
            RuntimeWarning,
        )

    result = subprocess.run(
        ["bash", wrapper_script_name],
        capture_output=True,
        text=True,
        check=True,
        cwd=test_folder_path,
    )
    return (result.returncode, result.stdout, result.stderr)


def _patch_config(**kwargs):
    """Create an auxiliary script for patching the config file."""
    args = copy.deepcopy(kwargs)
    output_config_file = args["output_config_file"]
    max_files_to_keep = args["max_files_to_keep"]
    script_name = "TestPatchConfig.sh"

    # Check Python version
    embedded = [
        "#!/bin/bash",
        "",
        "if command -v python3 &> /dev/null; then",
        "   PYTHON_CMD='python3'",
        "else",
        "   PYTHON_CMD='python'",
        "fi",
        'echo "Using Python as: $PYTHON_CMD"',
        "$PYTHON_CMD --version",
        "",
        'WMCONTROL_PATH="$HOME/wmcontrol"',
        'if [ ! -e "$WMCONTROL_PATH" ]; then',
        '   echo "The wmcontrol repo is not available at: $WMCONTROL_PATH. Please clone and checkout!"',
        "   exit 1",
        "fi",
        "",
        'export PYTHONPATH="${WMCONTROL_PATH}:${PATH}"',
        "",
        # Create a Python script to import and run
        "cat << 'PythonFile' > 'execute_patch.py'",
        "from modules.config_file_patch import FilterFilesFromConfigFile",
        "patcher = FilterFilesFromConfigFile(%s)" % (max_files_to_keep),
        "patcher.patch('%s')" % (output_config_file),
        "",
        "PythonFile",

        # Execute it        
        '$PYTHON_CMD execute_patch.py',
    ]

    args["run"] = embedded
    args["script_name"] = script_name
    args["container_major_version"] = "el9"
    return _run_using(**args)


def _run_config_patcher(test_folder=None, max_files_to_keep=5, execute=True, **kwargs):
    """Create an execute a test script for patching a configuration file.

    The resulting script uses several programs distributed only in CERN nodes.
    Consider executing it via `lxplus` nodes.

    Args:
        test_folder (str): Path to the temporary folder to execute the test script.
            If `None`, it will be set to the current working directory.
        execute (bool): Execute the test script.

        **containter_major_version (str): Container architecture to use
            e.g: el7, el8, el9.
        **arch (str): CMSSW SCRAM architecture, e.g: el8_amd64_gcc10.
        **cmsw_release (str): CMSSW release, e.g: CMSSW_12_4_14_patch3
        **output_config_file (str): Python filename provided to cmsDriver.py via `--python-filename`.
        **content (list[str]): Content to be embedded for running the simulation via
            cmsDriver.py steps.

    Returns:
        The exit code, standard output, and standard error result of the execution of
            the script. `None` in case the execution is skipped.
    """
    test_folder_path = test_folder if test_folder else os.getcwd()
    wrapper_script_name = "%s/Testing-%s.sh" % (test_folder_path, str(uuid.uuid4()))
    wrapper_script = [
        "#!/bin/bash",
        "export APPTAINER_BINDPATH='/afs,/cvmfs,/cvmfs/grid.cern.ch/etc/grid-security:/etc/grid-security,/eos,/etc/pki/ca-trust,/run/user,/var/run/user'",
        'export SINGULARITY_CACHEDIR="/tmp/$(whoami)/singularity"',
        'echo "Running test script at: $(hostname)"',
        'echo "Test working folder is: $(pwd -P)"',
        'voms-proxy-init --voms cms --out "$(pwd)/voms_proxy.txt" --hours 4',
        'export X509_USER_PROXY="$(pwd)/voms_proxy.txt"',
        "",
    ]

    # Generate the configuration file
    args = copy.deepcopy(kwargs)
    args["script_name"] = "TestConfigFile.sh"
    args["run"] = args["content"]
    wrapper_script += _generate_files(**args)

    # Patch the configuration
    args = copy.deepcopy(kwargs)
    args["max_files_to_keep"] = max_files_to_keep
    wrapper_script += _patch_config(**args)

    with open(file=wrapper_script_name, mode="w", encoding="utf-8") as f:
        f.writelines("\n".join(wrapper_script))

    # Execute
    if not execute:
        return None

    hostname = socket.getfqdn()
    if not re.match(r"^lxplus[0-9]{3,4}\.cern\.ch$", hostname):
        warnings.warn(
            (
                "You're running outside CERN lxplus nodes. "
                "Make sure all the required modules by the test script are available via $PATH"
            ),
            RuntimeWarning,
        )

    result = subprocess.run(
        ["bash", wrapper_script_name],
        capture_output=True,
        text=True,
        check=True,
        cwd=test_folder_path,
    )
    return (result.returncode, result.stdout, result.stderr)
