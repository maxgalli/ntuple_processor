import logging
logger = logging.getLogger(__name__)

import itertools



class NtupleBase:

    def __init__(self, path, directory):
        self.path = path
        self.directory = directory

    def __str__(self):
        layout = '(' + self.path \
                + ', ' + self.directory \
                + ')'
        return layout


class Friend(NtupleBase):

    def __init__(self,
            path, directory, tag = None):
        NtupleBase.__init__(self, path, directory)
        self.tag = tag

    def __str__(self):
        if self.tag is None:
            return NtupleBase.__str__(self)
        else:
            layout = '(' + self.path \
                    + ', ' + self.directory \
                    + ', ' + 'tag = {}'.format(self.tag) \
                    + ')'
        return layout


class Ntuple(NtupleBase):

    def __init__(self, path, directory, friends = []):
        NtupleBase.__init__(self, path, directory)
        self.friends = self.__add_tagged_friends(friends)

    def __add_tagged_friends(self, friends):
        for f1,f2 in itertools.combinations(friends, 2):
            l1 = f1.path.split('/')
            l2 = f2.path.split('/')
            tags = list(set(l1).symmetric_difference(set(l2)))
            if tags:
                for t in tags:
                    if t in l1 and f1.tag is None:
                        f1.tag = t
                    elif t in l2 and f2.tag is None:
                        f2.tag = t
        return friends


class Dataset:

    def __init__(self, name, ntuples):
        self.name = name
        self.ntuples = ntuples

    def __str__(self):
        return 'Dataset-{}'.format(self.name)

    def add_to_ntuples(*new_ntuples):
        for new_ntuple in new_ntuples:
            self.ntuples.append(new_ntuple)


class Selection:
    def __init__(
            self, name = None,
            cuts = None, weights = None):
        self.name = name
        self.set_cuts(cuts)
        self.set_weights(weights)

    def __str__(self):
        return 'Selection-{}'.format(self.name)

    def set_cuts(self, cuts):
        if cuts is not None:
            try:
                self.__check_format(cuts)
                self.cuts = cuts
            except TypeError as err:
                print(err, 'Cuts assigned to empty list')
                self.cuts = []
        else:
            self.cuts = []

    def set_weights(self, weights):
        if weights is not None:
            try:
                self.__check_format(weights)
                self.weights = weights
            except TypeError as err:
                print(err, 'Weights assigned to empty list')
                self.weights = []
        else:
            self.weights = []

    def __check_format(self, list_of_dtuples):
        if isinstance(list_of_dtuples, list):
            for dtuple in list_of_dtuples:
                if isinstance(dtuple, tuple)\
                        and len(dtuple) == 2:
                    return True
                else:
                    raise TypeError(
                            'TypeError: tuples of lenght 2 are needed.\n')
        else:
            raise TypeError(
                    'TypeError: a list of tuples is needed.\n')


class Binning:
    def __init__(self,
            name, edges):
        self.name = name
        self.edges = edges
        self.nbins = len(edges) - 1


class Action:
    def __init__(self,
            name, variable):
        self.name = name
        self.variable = variable

    def __str__(self):
        return '{}-{}'.format(self.name, self.variable)


class BookCount(Action):
    def __init__(self, variable):
        Action.__init__(self, 'BookCount', variable)


class BookHisto(Action):
    def __init__(
            self,
            variable, edges):
        Action.__init__(self, 'BookHisto', variable)
        self.binning = Binning(
            variable, edges)
