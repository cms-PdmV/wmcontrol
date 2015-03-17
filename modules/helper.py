#! /usr/bin/env python

import json
import subset
import urllib
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
        self.wmagenturl = 'cmsweb.cern.ch'
        self.dbs3url = '/dbs/prod/global/DBSReader/'

    def abort(self, reason=""):
        raise Exception("Something went wrong. Aborting. " + reason)

    def api(self, method, field, value, detail=False, post=False):
        """Constructs query and returns DBS3 response
        """
        if not self.connection:
            self.refresh_connection(self.wmagenturl)

        # this way saves time for creating connection per every request
        for i in range(self.connection_attempts):
            try:
                if post:
                    params = {}
                    params[field] = value
                    res = wma.httppost(self.connection, self.dbs3url +
                                       method, params).replace("'", '"')
                else:
                    if detail:
                        res = wma.httpget(self.connection, self.dbs3url
                                          + "%s?%s=%s&detail=%s"
                                          % (method, field, value, detail))
                    else:
                        res = wma.httpget(self.connection, self.dbs3url +
                                          "%s?%s=%s" % (method, field, value))
                break
            except Exception:
                # most likely connection terminated
                self.refresh_connection(self.wmagenturl)
        try:
            return json.loads(res)
        except:
            self.abort("Could not load the answer from DBS3: " + wma.DBS3_URL
                       + "%s?%s=%s&detail=%s" % (method, field, value, detail))

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

        if not self.connection:
            self.refresh_connection(self.wmagenturl)

        if not only_lumis:
            # try with blocks first
            res = self.api('blocksummaries', 'dataset', self.dataset, True)
            blocks, total = self.parse(res, 'block_name', 'num_event')
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
                    devi += f['events']
                    if treshold < 0:
                        break

        # get a list of lumis (full list added)
        rep = {}
        if len(data):
            res = self.api('filelumis', 'logical_file_name',
                           [d['name'] for d in data if d not
                            in extended['data']], post=True)
            for r in res:
                try:
                    rep[str(r['run_num'])] += r['lumi_section_num']
                except KeyError:
                    rep[str(r['run_num'])] = r['lumi_section_num']

        # get extended list of lumis (only some will be added)
        if len(extended['data']):
            ext = extended['data']
            res = self.api('filelumis', 'logical_file_name',
                           [e['name'] for e in ext], post=True)
            for i, e in enumerate(ext):
                for r in res:
                    if e['name'] == r['logical_file_name']:
                        ext[i]['lumi_section_num'] = r['lumi_section_num']
                        ext[i]['run_num'] = r['run_num']
                        break
            for e in ext:
                if abs(devi) < e['events']:
                    # process only part of res
                    avlum = float(e['events']) / len(e['lumi_section_num'])
                    i = int(len(e['lumi_section_num']) - abs(devi)/avlum)
                    devi -= (len(e['lumi_section_num']) - abs(i))*avlum
                    e['lumi_section_num'] = e['lumi_section_num'][i:]
                else:
                    # process full res
                    devi -= e['events']
                try:
                    rep[str(e['run_num'])] += e['lumi_section_num']
                except KeyError:
                    rep[str(e['run_num'])] = e['lumi_section_num']

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
