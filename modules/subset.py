#! /usr/bin/env python


class Generate():

    def __init__(self, bf=False):
        """Generate subset

        Arguments
        bf -- if brute force
        """
        self.brute_force = bf

    def run(self, data, target):
        data = sorted(data, key=lambda e: e['events'], reverse=True)
        if self.brute_force:
            return self.knapsack_variant(data, target)
        else:
            return self.first_fit_decreasing(data, target)

    def knapsack_variant(self, dataset, target_num_events):
        """Brute force solution
        """
        local_min = target_num_events
        subset = []
        for i, d in enumerate(dataset):
            diff = target_num_events - d['events']
            if abs(local_min) > abs(diff):
                local_min = diff
                subset = [d]
            if diff == 0:
                return subset, local_min
            if diff > 0:
                s, m = self.run(dataset[i+1:], diff)
                if abs(local_min) > abs(m):
                    local_min = m
                    subset = [d]
                    subset += s
                    if local_min == 0:
                        return subset, local_min
        return subset, local_min

    def first_fit_decreasing(self, dataset, target_num_events):
        """Solution based on first fit decreasing algo
        """
        bins = []
        for d in dataset:
            create_new = True
            # sort bins started with the fullest one
            bins = sorted(bins, key=lambda e: e['space'], reverse=True)
            for b in bins:
                # check if the item is added the space will be exceded
                if d['events'] + b['space'] <= target_num_events:
                    b['content'].append(d)
                    b['space'] += d['events']
                    create_new = False
                    break
            # if all bins will be overpacked, create new one
            if create_new:
                new_bin = {}
                new_bin['content'] = [d]
                new_bin['space'] = d['events']
                bins.append(new_bin)

        # if for some reason there is no bins
        if not len(bins):
            return ([], target_num_events)

        # check which bin has smallest deviation
        max_space = None
        for bin in bins:
            if max_space is None or abs(target_num_events -
                                        bin['space']) < max_space:
                max_space = abs(target_num_events - bin['space'])
                the_bin = bin

        return (the_bin['content'],
                abs(target_num_events - the_bin['space']))
