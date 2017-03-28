import sys
import optparse
import time
from modules import wma


def getOptions():
    parser = optparse.OptionParser()
    parser.add_option('-w', '--workflows', help='Requests to be approved after batch announcement', dest='workflows', default='')
    parser.add_option('--wmtest', help='To inject requests to the cmsweb test bed', action='store_true' ,
                      dest='wmtest', default=False)
    parser.add_option('--wmtesturl', help='To inject to a specific testbed', dest='wmtesturl',
                      default='cmsweb-testbed.cern.ch')
    try:
        options,_ = parser.parse_args()
        return options
    except SystemExit:
        print "Error in parsing options"
        sys.exit(-1)


def approveRequest(options):
    if options.workflows == '':
        print 'No workflows found'
        sys.exit(-1)
    workflows = set(options.workflows.split(','))
    print 'Approving requests: %s' % workflows
    if options.wmtest:
        wma.testbed(options.wmtesturl)
    for workflow in workflows:
        tries = 1
        while tries < 3:
            try:
                if(wma.getWorkflowStatus(wma.WMAGENT_URL, workflow) == 'new'):
                    wma.approveRequest(wma.WMAGENT_URL, workflow)
                break
            except Exception, e:
                time.sleep(1)
                print 'Something went wrong: %s Try number: %s' % (str(e), tries)
                tries += 1


if __name__ == '__main__':
    options = getOptions()
    approveRequest(options)
