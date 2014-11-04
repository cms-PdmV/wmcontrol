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
            raise Exception("Could not load the answer from DBS3")

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
        # break if the input is incorrect
        if total * self.approximation < events:
            raise Exception("Couldn't generate desired subset." +
                            "Desired subset is almost equal or bigger" +
                            "than total number of events")
        job = subset.Generate(brute)
        # get best fit list and deviation
        data, devi = job.run(files, events)

        # if deviation to big, raise exception
        if devi <= total * self.approximation:
            rep = {}
            for d in data:
                # get run number and lumis per file
                res = self.api('filelumis', 'logical_file_name', d['name'])
                try:
                    rep[str(res[0]['run_num'])] += res[0]['lumi_section_num']
                except KeyError:
                    rep[str(res[0]['run_num'])] = res[0]['lumi_section_num']
        else:
            raise Exception("Couldn't generate desired subset." +
                            "Deviation too big. Perhaps try brute force")

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
