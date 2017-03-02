import sys
import optparse
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
        exit()
    workflows = options.workflows.split(',')
    print 'Approving requests: %s' % workflows
    if options.wmtest:
        wma.testbed(options.wmtesturl)
    for workflow in workflows:
        try:
            wma.approveRequest(wma.WMAGENT_URL, workflow)
        except Exception, e:
            random_sleep()
            print 'Something went wrong: %s,   trying again...' % str(e)
            # just try a second time
            wma.approveRequest(wma.WMAGENT_URL, workflow)


if __name__ == '__main__':
    options = getOptions()
    approveRequest(options)