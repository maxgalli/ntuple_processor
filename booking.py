from .utils import Dataset
from .utils import Friend
from .utils import Ntuple

from .utils import Action
from .utils import BookCount
from .utils import BookHisto

from ROOT import TFile

import os
import re
import json

import logging
logger = logging.getLogger(__name__)


class DatasetFromDatabase:
    """Fake class introduced to simulate a static behavior for
    the dataset, in order for it to be created only once.
    The function can be called with the name 'dataset_from_database'
    from the API.

    Attributes:
        dataset (Dataset): Dataset object created with the function
        inner_dataset_from_database
    """
    def __init__(self):
        self.path_to_database = None

    def __call__(
            self,
            dataset_name, path_to_database,
            queries, folder,
            files_base_directories,
            friends_base_directories):
        if self.path_to_database is None:
            self.path_to_database = path_to_database
        dataset = self.inner_dataset_from_database(
            dataset_name, self.path_to_database,
            queries, folder,
            files_base_directories,
            friends_base_directories)
        return dataset

    def inner_dataset_from_database(
            self,
            dataset_name, path_to_database,
            queries, folder,
            files_base_directories,
            friends_base_directories):
        """Create a Dataset object from a database
        in JSON format. In this specific case (KAPPA
        database), a dataset will have the following
        format (all folder names are equal):
            ntuple1: /file_base_dir/root_file1/folder/ntuple
                friend1: /friend1_base_dir/root_file1/folder/ntuple
                friend2: /friend2_base_dir/root_file1/folder/ntuple
            ntuple2: /file_base_dir/root_file2/folder/ntuple
                friend1: /friend1_base_dir/root_file2/folder/ntuple
                friend2: /friend2_base_dir/root_file2/folder/ntuple
            ntuple3: /file_base_dir/root_file3/folder/ntuple
                friend1: /friend1_base_dir/root_file3/folder/ntuple
                friend2: /friend2_base_dir/root_file3/folder/ntuple
            (...)

        Args:
            dataset_name (str): Name of the dataset
            path_to_database (str): Absolute path to a json file
            queries (dict, list): Dictionary or list of dictionaries
                containing queries to retrieve specific .root files
            folder (str): Name of the TDirectoryFile
            files_base_directories (str, list): Path (list of paths) to
                the files base directory (directories)
            friends_base_directories (str, list): Path (list of paths) to
                the friends base directory (directories)

        Returns:
            dataset (Dataset): Dataset object containing TTrees
        """
        def load_database(path_to_database):
            if not os.path.exists(path_to_database):
                logger.fatal('No database available for {}'.format(
                    path_to_database))
                raise FileNotFoundError(
                    'No database available for {}'.format(
                        path_to_database))
            return json.load(open(path_to_database, "r"))

        def check_recursively(entry, query, database):
            for attribute in query:
                q_att = query[attribute]
                d_att = database[entry][attribute]
                if isinstance(d_att, str) or isinstance(d_att, str):
                    result = re.match(q_att, d_att)
                    if result == None:
                        return False
                elif isinstance(d_att, bool):
                    if not q_att == d_att:
                        return False
                else:
                    raise Exception
            return True

        def get_nicks_with_query(database, query):
            nicks = []
            if isinstance(query, list):
                for s_query in query:
                    for entry in database:
                        passed = check_recursively(
                            entry, s_query, database)
                        if passed:
                            nicks.append(entry)
            else:
                for entry in database:
                    passed = check_recursively(
                        entry, query, database)
                    if passed:
                        nicks.append(entry)
            return nicks

        def get_complete_filenames(directory, files):
            full_paths = []
            for f in files:
                full_paths.append(
                    os.path.join(
                        directory, f, "{}.root".format(f)
                        )
                    )
            return full_paths

        def get_full_tree_name(
                folder, path_to_root_file, tree_name):
            root_file = TFile(path_to_root_file)
            if root_file.IsZombie():
                logger.fatal(
                    'File {} does not exist, abort'.format(
                        path_to_root_file))
                raise FileNotFoundError(
                    'File {} does not exist, abort'.format(
                        path_to_root_file))
            else:
                if folder not in root_file.GetListOfKeys():
                    raise NameError(
                        'Folder not in {}\n'.format(path_to_root_file))
                full_tree_name = '/'.join([folder, tree_name])
                return full_tree_name

        database = load_database(path_to_database)
        names = get_nicks_with_query(database, queries)

        # E.g.: file_base_dir/file_name.root
        root_files = get_complete_filenames(
            files_base_directories, names)
        logger.debug('%%%%%%%%%% Creating dataset {}, get root files:\n\t{}'.format(
            dataset_name, root_files))
        ntuples = []

        # E.g.: file_base_dir/file_name1.root/folder/ntuple
        #       file_base_dir/file_name2.root/folder/ntuple
        for (root_file, name) in zip(root_files, names):
            tdf_tree = get_full_tree_name(
                folder, root_file, 'ntuple')
            if tdf_tree:
                #logger.debug('Get tree {} from file {}'.format(
                    #tdf_tree, root_file))
                friends = []
                friend_paths = []
                for friends_base_directory in friends_base_directories:
                    friend_paths.append(os.path.join(
                        friends_base_directory, name, "{}.root".format(name)))
                for friend_path in friend_paths:
                    if os.path.isfile(friend_path):
                        friends.append(Friend(friend_path, tdf_tree))
                    else:
                        logger.fatal(
                            'File {} does not exist, abort'.format(
                                friend_path))
                        raise FileNotFoundError(
                            'File {} does not exist, abort'.format(
                                friend_path))
                ntuples.append(Ntuple(root_file, tdf_tree, friends))
        dataset = Dataset(dataset_name, ntuples)

        # Debug
        def debug_dataset():
            logger.debug('%%%%%%%%%% Creating dataset {}, analyze ntuples'.format(dataset_name))
            for n, ntuple in enumerate(ntuples):
                logger.debug('Ntuple {}:\n\tPath: {}\n\tFolder: {}'.format(
                    n, ntuple.path, ntuple.directory))
                for m, friend in enumerate(ntuple.friends):
                    logger.debug('\n\tFriend {} of ntuple {}:\n\tPath: {}\n\tFolder: {}'.format(
                        m, n, friend.path, friend.directory))
        #logger.debug(debug_dataset())

        return dataset

dataset_from_database = DatasetFromDatabase()

class AnalysisFlowUnit:
    """
    Building block of a minimal analysis flow, consisting
    of a dataset, a set of selections to apply on the data
    and an action.

    Attributes:
        dataset (Dataset): Set of TTree objects to run the
            analysis on
        selections (list): List of Selection-type objects
        action (Action): Action to perform on the processed
            dataset, can be 'BookHisto' or 'BookCount'
    """
    def __init__(
            self,
            dataset, selections, action = None):
        self.__set_dataset(dataset)
        self.__set_selections(selections)
        self.__set_action(action)

    def __str__(self):
        layout = '\n'.join([
            'Dataset: {}'.format(self.dataset.name),
            'Selections: {}'.format(self.selections),
            'Action: {}'.format(self.action)])
        return layout

    def book_count(self):
        self.action = BookCount()

    def book_histo(self, binning, variable):
        self.action = BookHisto(
            self.binning, self.variable)

    def __set_dataset(self, dataset):
        if isinstance(dataset, Dataset):
            self.dataset = dataset
        else:
            raise TypeError(
                'TypeError: not a Dataset object.')

    def __set_selections(self, selections):
        if isinstance(selections, list):
            self.selections = selections
        else:
            raise TypeError(
                'TypeError: not a list object.')

    def __set_action(self, action):
        if isinstance(action, Action):
            self.action = action
        else:
            raise TypeError(
                    'TypeError: not an Action object.')


class AnalysisFlowManager:
    """
    Manager of all the AnalysisFlowUnit objects that are created.
    It can both be initialized with a variable amount of AnalysisFlowUnit
    objects as arguments or with no arguments, with the above mentioned
    objects added in a second time with the functions 'book_count' and
    'book_histo'.

    Args:
        *args (AnalysisFlowUnit): Objects with the structure [dataset,
            selections, action]

    Attributes:
        booked_units (list): List of the booked units, updated during
            initialization or with the functions 'book_count' and
            'booked_histo'
    """

    def __init__(self, *args):
        self.booked_units = [arg for arg in args]

    def book_count(self,
            dataset, selections):
        self.booked_units.append(
            AnalysisFlowUnit(
                dataset, selections, BookCount()))

    def book_histo(self,
            dataset, selections,
            binning, variable):
        self.booked_units.append(
            AnalysisFlowUnit(
                dataset, selections, BookHisto(
                    binning, variable)))
