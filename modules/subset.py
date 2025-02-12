#! /usr/bin/env python


class Generate():

    def __init__(self, bf=False):
        """Generate subset

        Arguments
        bf -- if brute force
        """
        self.brute_force = bf

    def run(self, data, target, approx=0.00):
        data = sorted(data, key=lambda e: e['events'], reverse=True)
        if len(data)> 10000 and not self.brute_force:
            print("Too many elements to handle for subset, resorting to brute force algorithm")
            self.brute_force = True
        if self.brute_force:
            return self.knapsack_variant(data, target, approx)
        else:
            return self.first_fit_decreasing(data, target)

    def knapsack_variant(self, dataset, target, approx=0.00):
        """Brute force solution

        dataset -- input array of dicts {events, name}
        target -- (int) target number of events
        approx -- (float) acceptable margin
        """
        deviation = target
        subset = []
        for i, d in enumerate(dataset):
            diff = target - d['events']

            # if stored deviation is bigger then the difference
            if abs(deviation) > abs(diff):
                deviation = diff
                subset = [d]

            # break algo if subset is good enough
            if abs(diff) <= target*float(approx):
                return subset, deviation

            # if diff gt 0, check rest of array recursively
            if diff > 0:
                s, m = self.run(dataset[i+1:], diff)
                if abs(deviation) > abs(m):
                    deviation = m
                    subset = [d]
                    subset += s
                    if abs(diff) <= target*float(approx):
                        return subset, deviation

        return subset, deviation

    def first_fit_decreasing(self, dataset, target_num_events):
        """Solution based on first fit decreasing algo
        """
        bins = []
        import tqdm
        for d in tqdm.tqdm(dataset):
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
                target_num_events - the_bin['space'])
