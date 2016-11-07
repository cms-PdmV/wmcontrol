#!/usr/bin/env python
'''Script that submits relval workflows for AlCa@HLT,Prompt condition validation
'''

__author__ = 'Javier Duarte'
__copyright__ = 'Copyright 2012, CERN CMS'
__credits__ = ['Giacomo Govi', 'Salvatore Di Guida', 'Miguel Ojeda', 'Andreas Pfeiffer']
__license__ = 'Unknown'
__maintainer__ = 'Javier Duarte'
__email__ = 'jduarte@caltech.edu'
__version__ = 1


import os
import sys
import logging
import optparse
import json
import errno
import ast

def execme(command, dryrun=False):
    '''Wrapper for executing commands.
    '''
    if dryrun:
        print command
    else:
        print " * Executing: %s..." % (command)
        os.system(command)
        print " * Executed!"

def getInput(default, prompt=''):
    '''Like raw_input() but with a default and automatic strip().
    '''

    answer = raw_input(prompt)
    if answer:
        return answer.strip()

    return default.strip()

def getInputChoose(optionsList, default, prompt=''):
    '''Makes the user choose from a list of options.
    '''

    while True:
        index = getInput(default, prompt)

        try:
            return optionsList[int(index)]
        except ValueError:
            logging.error('Please specify an index of the list (i.e. integer).')
        except IndexError:
            logging.error('The index you provided is not in the given list.')

def getInputRepeat(prompt=''):
    '''Like raw_input() but repeats if nothing is provided and automatic strip().
    '''

    while True:
        answer = raw_input(prompt)
        if answer:
            return answer.strip()

        logging.error('You need to provide a value.')

def main():
    '''Entry point.
    '''

    parser = optparse.OptionParser(usage='Usage: %prog <file> [<file> ...]\n')
    (options, arguments) = parser.parse_args()

    try:
        metadataFilename = arguments[0]
    except IndexError:
        logging.error('Need to suply a metadata text file name')
        return -3

    ## check that user has properly set up the WMA libraries in PYTHONPATH
    #try:
    #    pypath = os.environ['PYTHONPATH']
    #except:
    #    print "no PYTHONPATH defined in your environment; exiting"
    #    sys.exit()
    #else:
    #    if len ( filter( lambda r : "WMCore" in r, pypath.split(":") ) ) > 0 :
    #        print "hapy"
    #        pass
    #    else :
    #        print "no WMCore present in your PYTHONPATH; exiting"
    #        sys.exit()


    if True:
        try:
            with open(metadataFilename, 'rb') as metadataFile:
                pass
        except IOError as e:
            if e.errno != errno.ENOENT:
                logging.error('Impossible to open file %s (for other reason than not existing)', metadataFilename)
                return -4

            if getInput('y', '\nIt looks like the metadata file %s does not exist. Do you want me to create it and help you fill it?\nAnswer [y]: ' % metadataFilename).lower() != 'y':
                logging.error('Metadata file %s does not exist', metadataFilename)
                return -5
            # Wizard
            while True:
                print '''\nWizard for metadata
I will ask you some questions to fill the metadata file. For some of the questions there are defaults between square brackets (i.e. []), leave empty (i.e. hit Enter) to use them.'''

                typeList = ['HLT+RECO', 'PR', 'HLT+RECO+ALCA', 'PR+ALCA']

                print '\nTypes of workflow submissions'
                for (index, type) in enumerate(typeList):
                        print '   %s) %s' % (index, type)

                type = getInputChoose(typeList, '0', '\nWhich type of workflow submission\ntype [0]: ')

                if 'HLT+RECO' in type:
                    hlt_release = getInput('CMSSW_7_4_9_patch1', '\nWhich CMSSW release for HLT?\ne.g. CMSSW_7_4_9_patch1\nhlt_release [CMSSW_7_4_9_patch1]: ')

                pr_release = getInput('CMSSW_7_4_11_patch1', '\nWhich CMSSW release for Prompt Reco?\ne.g. CMSSW_7_4_11_patch1\npr_release [CMSSW_7_4_11_patch1]: ')

                if 'HLT+RECO' in type:
                    hlt_menu = getInput('orcoff:/cdaq/physics/Run2015/25ns14e33/v3.5/HLT/V7', '\nWhich HLT menu?\ne.g. orcoff:/cdaq/physics/Run2015/25ns14e33/v3.5/HLT/V7\nhlt_menu [orcoff:/cdaq/physics/Run2015/25ns14e33/v3.5/HLT/V7]: ')

                newgt = getInput('74X_dataRun2_HLTValidation_2015-09-07-08-26-15', '\nWhat is the new GT to be validated?\ne.g. 74X_dataRun2_HLTValidation_2015-09-07-08-26-15\nnewgt [74X_dataRun2_HLTValidation_2015-09-07-08-26-15]: ')

                gt = getInput('74X_dataRun2_HLT_v1', '\nWhat is the reference GT?\ne.g. 74X_dataRun2_HLT_v1\ngt [74X_dataRun2_HLT_v1]: ')

                if 'HLT+RECO' in type:
                    basegt = getInput('74X_dataRun2_Prompt_v1', '\nWhat is the common GT for Reco?\ne.g. 74X_dataRun2_Prompt_v1\nbasegt [74X_dataRun2_Prompt_v1]: ')

                ds = getInput('/HLTPhysics/Run2015C-v1/RAW', '\nWhat is the dataset to be used (comma-separated if more than one)?\ne.g. /HLTPhysics/Run2015C-v1/RAW\nds [/HLTPhysics/Run2015C-v1/RAW]: ')

                run_err_mess = 'The run value has to be an integer, a dictionary or empty (null).'
                runORrunLs  = getInput('254906', '\nWhich run number or run number+luminosity sections?\ne.g. 254906 or\n     [254906,254905] or\n     {\'256677\': [[1, 291], [293, 390]]}\nrunORrunLs [254906]: ')
                run = ''
                runLs = ''
                # do some type recognition and set run or runLs accordingly
                try:
                    if isinstance(runORrunLs, str) and "{" in runORrunLs :
                        runLs = ast.literal_eval(runORrunLs)                              # turn a string into a dict and check it's valid
                    elif isinstance(runORrunLs, dict):
                        runLs = runORrunLs                                    # keep dict
                    elif isinstance(runORrunLs, str) and "[" in runORrunLs :
                        run   = ast.literal_eval(runORrunLs)                              # turn a string into a list and check it's valid
                    elif isinstance(runORrunLs, str) :
                        run = int(runORrunLs)                                 # turn string into int
                    elif isinstance(runORrunLs, list):
                        run = runORrunLs                                      # keep list
                    else:
                        raise ValueError(run_err_mess)
                except ValueError:
                    logging.error(run_err_mess)


                b0T = getInput('n', '\nIs this for B=0T?\nAnswer [n]: ')
                hion = getInput('n', '\nIs this for Heavy Ions? Note B=0T is not compatible with Heavy Ions at the moment, also pA runs and Heavy Ions runs are mutually exclusive\nAnswer [n]: ')
                pa_run   = getInput('n', '\nIs this for pA run?\nAnswer [n]:')
                metadata = {
                    'PR_release': pr_release,
                    'options': {
                        'Type': type,
                        'newgt': newgt,
                        'gt': gt,
                        'ds': ds,
                        'run': run}}

                if runLs:
                    metadata['options']['runLs'] = runLs
                    metadata['options'].pop('run')


                if b0T.lower() == 'y':
                    metadata['options'].update({'B0T':''})
                if hion.lower() == 'y':
                    metadata['options'].update({'HIon':''})
                if pa_run.lower() == 'y':
                    metadata['options'].update({'pA':''})
                if 'HLT+RECO' in type:
                    metadata['HLT_release'] = hlt_release
                    metadata['options'].update({
                        'HLT': 'Custom',
                        'HLTCustomMenu': hlt_menu,
                        'basegt': basegt})
                    if metadata['PR_release'] != metadata['HLT_release']:
                        pr_release = metadata['PR_release']
                        metadata['options']['recoCmsswDir'] = '../%s/' % (pr_release)

                metadata = json.dumps(metadata, sort_keys=True, indent=4)
                print '\nThis is the generated metadata:\n%s' % (metadata)

                if getInput('n', '\nIs it fine (i.e. save in %s)?\nAnswer [n]: ' % (metadataFilename)).lower() == 'y':
                    break

            logging.info('Saving generated metadata in %s...', metadataFilename)
            with open(metadataFilename, 'wb') as metadataFile:
                metadataFile.write(metadata)
                logging.info('...%s file created.', metadataFilename)

    with open(metadataFilename, 'rb') as metadataFile:
        metadata = json.loads(metadataFile.read())
        print '\nexecute the following commands:\n'
        commands = []
        try:
            if metadata['HLT_release']:
                #commands.append('eval \'scramv1 project %s\'' % metadata['HLT_release'] )
                commands.append('scramv1 project %s' % (metadata['HLT_release']))
                commands.append('cd %s/src' % (metadata['HLT_release']))
                #commands.append('eval \'scramv1 runtime -sh\'')
                commands.append('cmsenv')
                commands.append('git cms-addpkg HLTrigger/Configuration')
                #commands.append('eval \'scramv1 b\'')
                commands.append('scramv1 b')
                commands.append('voms-proxy-init --voms cms')
                commands.append('source /afs/cern.ch/cms/PPD/PdmV/tools/subSetup_slc6.sh')
                commands.append('cd -')
                if metadata['PR_release'] != metadata['HLT_release']:
                    #commands.append('eval \'scramv1 project %s\'' % metadata['PR_release'])
                    commands.append('scramv1 project %s' % (metadata['PR_release']))
        except KeyError:
            #commands.append('eval \'scramv1 project %s\'' % metadata['PR_release'] )
            commands.append('scramv1 project %s' % (metadata['PR_release']))
            commands.append('cd %s/src' % (metadata['PR_release']))
            #commands.append('eval \'scramv1 runtime -sh\'')
            commands.append('cmsenv')
            commands.append('voms-proxy-init --voms cms')
            commands.append('source /afs/cern.ch/cms/PPD/PdmV/tools/subSetup_slc6.sh')
            commands.append('cd -')

        cond_submit_command = './condDatasetSubmitter.py '
        for key, val in metadata['options'].iteritems():
            # cond_submit_command += '--%s %s ' % ( key, val )
            if isinstance(val, list):
                cond_submit_command += '--%s "' % (key)
                for u in val:
                    cond_submit_command += '%s,' % (u)
                cond_submit_command = cond_submit_command[:-1]
                cond_submit_command += '" '
            elif isinstance(val, dict):
                cond_submit_command += '--%s "%s" ' % (key, val)
            else:
                cond_submit_command += '--%s %s ' % (key, val)

        commands.append(' git clone -b master git@github.com:cms-PdmV/wmcontrol.git  master-my-local-name    (**make sure that that PdmV master is the one you want to use**)')
        commands.append('cd wmcontrol')
        commands.append(cond_submit_command)

        # compose string representing runs, Which will be part of the filename
        # if run is int => single label; if run||runLs are list or dict, '_'-separated composite label
        run_label_for_fn = ''

        if 'run' in metadata['options'] and isinstance( metadata['options']['run'], int):
            run_label_for_fn = metadata['options']['run']
        else:
            # handle the list and dictionary case with the same code snippet
            thisRunKey = 'run'
            if 'runLs' in metadata['options']:
                thisRunKey = 'runLs'
            # loop over elements of a list or keys of a dictionary
            for oneRun in metadata['options'][thisRunKey]:
                if run_label_for_fn != '':
                    run_label_for_fn += '_'
                run_label_for_fn += str(oneRun)

        try:
            if metadata['HLT_release']:
                commands.append('./wmcontrol.py --req_file HLTConditionValidation_%s_%s_%s.conf |& tee wmcontrol.HLT.1.log' % (
                        metadata['HLT_release'], metadata['options']['basegt'], run_label_for_fn))
        except KeyError:
            commands.append('./wmcontrol.py --req_file PRConditionValidation_%s_%s_%s.conf |& tee wmcontrol.PR.1.log' % (
                        metadata['PR_release'], metadata['options']['newgt'], run_label_for_fn))

        commands.append('rm *.couchID')

        dryrun = True
        # now execute commands
        for command in commands:
            execme(command, dryrun)

if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',
            level=logging.INFO)

    sys.exit(main())
