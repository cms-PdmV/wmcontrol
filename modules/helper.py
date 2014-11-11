#! /usr/bin/env python

import json
import subset
import wma
import time


class SubsetByLumi():

    def __init__(self, dset_name, approx=0.05):
        """Subset by lumis

        Arguments
        dset_name -- dataset name
        approx -- the margin
        """
        self.dataset = dset_name
        self.approximation = approx

    def abort(self, reason=""):
        raise Exception("Something went wrong. Aborting. " + reason)

    def api(self, method, field, value, detail=False):
        """Constructs query and returns DBS3 response
        """
        if detail:
            res = wma.generic_get(wma.WMAGENT_URL,
                                  wma.DBS3_URL + "%s?%s=%s&detail=%s"
                                  % (method, field, value, detail))
        else:
            res = wma.generic_get(wma.WMAGENT_URL, wma.DBS3_URL
                                  + "%s?%s=%s" % (method, field, value))
        try:
            return json.loads(res)
        except:
            self.abort("Could not load the answer from DBS3")

    def parse_files(self, files):
        """Parse DBS3 JSON
        """
        f_list = []
        e = 0
        for f in files:
            f_dict = {}
            f_dict['name'] = f['logical_file_name']
            f_dict['events'] = f['event_count']
            e += f['event_count']
            f_list.append(f_dict)
        return f_list, e

    def run(self, events, brute=False):
        """Runs subset generation

        Arguments
        events -- number of events in subset
        brute -- if brute force
        """
        # get files per dataset
        files = self.api('files', 'dataset', self.dataset, True)
        files, total = self.parse_files(files)

        # if total number of events is not valid number, abort
        if not total:
            self.abort("Reason 1")

        # break if the input is incorrect
        if total * (1 - self.approximation) < events:
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
        if abs(devi) > total * self.approximation:
            treshold = abs(devi)
            # extend list of lumis
            extended['add'] = (devi > 0)
            if extended['add']:
                for f in sorted(files, key=lambda e: e['events'], reverse=True):
                    if not f in data:
                        extended['data'].append(f)
                        treshold = treshold - f['events']
                    if treshold < 0:
                        break
            else:
                for f in sorted(data, key=lambda e: e['events'], reverse=True):
                    extended['data'].append(f)
                    data.remove(f)
                    treshold = treshold - f['events']
                    if treshold < 0:
                        break

        # proceed for best fit
        rep = {}
        for d in data:
            if d not in extended['data']:
                # get run number and lumis per file
                # if we could have one post query here with a list of files that'd be great
                res = self.api('filelumis', 'logical_file_name', d['name'])
                try:
                    rep[str(res[0]['run_num'])] += res[0]['lumi_section_num']
                except KeyError:
                    rep[str(res[0]['run_num'])] = res[0]['lumi_section_num']

        if extended['data']:
            # remove/add some lumis from trash for fit
            devi = abs(devi)
            for ex in extended['data']:
                # if we could have one post query here with a list of files that'd be great
                res = self.api('filelumis', 'logical_file_name', ex['name'])
                if devi < ex['events']:
                    index = int(abs(devi) / (float(ex['events'] / len(res[0]['lumi_section_num']))))
                    devi -= index * (ex['events']) / len(res[0]['lumi_section_num'])
                    if extended['add']:
                        res[0]['lumi_section_num'] = res[0]['lumi_section_num'][:index]
                    else:
                        res[0]['lumi_section_num'] = res[0]['lumi_section_num'][index:]
                else:
                    devi -= ex['events']
                try:
                    rep[str(res[0]['run_num'])] += res[0]['lumi_section_num']
                except KeyError:
                    rep[str(res[0]['run_num'])] = res[0]['lumi_section_num']

        # if still too big, inform and proceed
        if abs(devi) > total * self.approximation:
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

        return rep
