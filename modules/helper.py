#! /usr/bin/env python

import json
import subset
import wma


class SubsetByLumi():

    def __init__(self, dset_name, approx=0.05):
        """Subset by lumis

        Arguments
        dset_name -- dataset name
        approx -- the margin
        """
        self.dataset = dset_name
        self.approximation = approx
        self.connection = None
        self.connection_attempts = 3

    def abort(self, reason=""):
        raise Exception("Something went wrong. Aborting. " + reason)

    def api(self, method, field, value, detail=False):
        """Constructs query and returns DBS3 response
        """
        if not self.connection:
            self.refresh_connection(wma.WMAGENT_URL)

        # this way saves time for creating connection per every request
        for i in range(self.connection_attempts):
            try:
                if detail:
                    res = wma.httpget(self.connection,
                                      wma.DBS3_URL + "%s?%s=%s&detail=%s"
                                      % (method, field, value, detail))
                else:
                    res = wma.httpget(self.connection, wma.DBS3_URL
                                      + "%s?%s=%s" % (method, field, value))
                break
            except Exception:
                # most likely connection terminated
                self.refresh_connection(wma.WMAGENT_URL)
        try:
            return json.loads(res)
        except:
            self.abort("Could not load the answer from DBS3")

    def parse(self, inlist, name, events):
        """Parse DBS3 JSON
        """
        ret = []
        total = 0
        for i in inlist:
            i_dict = {}
            i_dict['name'] = i[name]
            i_dict['events'] = i[events]
            ret.append(i_dict)
            total += i[events]
        return ret, total

    def refresh_connection(self, url):
        self.connection = wma.init_connection(url)

    def run(self, events, brute=False, only_lumis=False):
        """Runs subset generation

        Arguments
        events -- number of events in subset
        brute -- if brute force
        only_lumis -- skip trying to split by block
        """
        if not only_lumis:
            # try with blocks first
            res = self.api('blocksummaries', 'dataset', self.dataset, True)
            blocks, total = self.parse(res, 'block_name', 'num_evernt')
            if total - events * self.approximation < events:
                # if there is no need of splitting read whole dataset
                print ("Desired subset is almost equal or bigger than total " +
                       "number of events")
                data, devi = (blocks, 0)
            else:
                # get best fit list and deviation
                job = subset.Generate(brute)
                data, devi = job.run(blocks, events)
            if not len(data):
                # when no data something is wrong with the response
                self.abort("Reason 2")
            if abs(devi) <= events * self.approximation:
                # deviation good enough to return block
                res = []
                for d in data:
                    res.append(d['name'])
                return ('blocks', map(lambda x: x.encode('ascii'), res))
            print "Block based splitting not enough. Trying with lumis."

        # get files per dataset
        files = self.api('files', 'dataset', self.dataset, True)
        files, total = self.parse(files, 'logical_file_name', 'event_count')

        # if total number of events is not valid number, abort
        if not total:
            self.abort("Reason 1")

        # break if the input is incorrect
        if total - events * self.approximation < events:
            print ("Couldn't generate desired subset. Desired subset is " +
                   "almost equal or bigger than total number of events")
            data, devi = (files, 0)
        else:
            # get best fit list and deviation
            job = subset.Generate(brute)
            data, devi = job.run(files, events)
            if not len(data):
                self.abort("Reason 2")

        extended = {}
        extended['data'] = []
        # if deviation to big, create file backup or trash some lumis
        if abs(devi) > events * self.approximation:
            treshold = abs(devi)
            # extend list of lumis
            extended['add'] = (devi > 0)
            if extended['add']:
                for f in sorted(files,
                                key=lambda e: e['events'], reverse=True):
                    if f not in data:
                        extended['data'].append(f)
                        treshold = treshold - f['events']
                    if treshold < 0:
                        break
            else:
                for f in sorted(data, key=lambda e: e['events'], reverse=True):
                    data.remove(f)
                    extended['data'].append(f)
                    treshold = treshold - f['events']
                    if treshold < 0:
                        break

        # proceed for best fit
        rep = {}
        for d in data:
            if d not in extended['data']:
                # get run number and lumis per file
                # if we could have one post query here with a list of files
                # that'd be great
                res = self.api('filelumis', 'logical_file_name', d['name'])
                try:
                    rep[str(res[0]['run_num'])] += res[0]['lumi_section_num']
                except KeyError:
                    rep[str(res[0]['run_num'])] = res[0]['lumi_section_num']

        if extended['data']:
            # remove/add some lumis from trash for fit
            devi = abs(devi)
            for ex in extended['data']:
                # if we could have one post query here with a list of files
                # that'd be great
                res = self.api('filelumis', 'logical_file_name', ex['name'])
                if devi < ex['events']:
                    # sorry
                    index = int(abs(devi) / float(ex['events'] / len(
                                res[0]['lumi_section_num'])))
                    devi -= index * ex['events'] / len(
                        res[0]['lumi_section_num'])
                    if extended['add']:
                        res[0]['lumi_section_num'] = res[0][
                            'lumi_section_num'][:index]
                    else:
                        res[0]['lumi_section_num'] = res[0][
                            'lumi_section_num'][index:]
                else:
                    devi -= ex['events']
                try:
                    rep[str(res[0]['run_num'])] += res[0]['lumi_section_num']
                except KeyError:
                    rep[str(res[0]['run_num'])] = res[0]['lumi_section_num']

        # if still too big, inform and proceed
        if abs(devi) > events * self.approximation:
            print ("Couldn't generate desired subset. Deviation too big. " +
                   "Perhaps try brute force. Proceeding anyway")

        # generate ranges
        for run, lumis in rep.iteritems():
            current = None
            sections = []
            for l in sorted(lumis):
                if current is None:
                    t = []
                    t.append(l)
                elif current+1 != l:
                    t.append(current)
                    sections.append(t)
                    t = []
                    t.append(l)
                current = l
            t.append(l)
            sections.append(t)
            rep[run] = sections

        return 'lumis', rep
