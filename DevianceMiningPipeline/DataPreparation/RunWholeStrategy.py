"""
This class sets all the main pipeline parameters, and calls a dataset configuration file

@author: Giacomo Bergami
"""

import os
import jsonpickle
from DevianceMiningPipeline.DataPreparation.ConfigurationFile import ConfigurationFile
from DevianceMiningPipeline.DataPreparation.TaggingStrategy import TaggingStrategy

class RunWholeStrategy:
    def __init__(self, LOGS_FOLDER, DATA_EXP, missing_literal = None, doNr0 = True, ranges = None, max_splits = 5, threshold_split = 0.1):
        self.doNr0 = doNr0
        self.ranges = ranges
        if ranges is None:
           self.ranges=[5, 10, 15, 20, 25, 30]
        self.max_splits = max_splits
        self.LOGS_FOLDER = LOGS_FOLDER
        self.DATA_EXP = DATA_EXP
        self.c = threshold_split
        self.missing_literal = missing_literal

    def __call__(self, obj):
        assert (isinstance(obj, TaggingStrategy))
        conf = jsonpickle.decode(open(obj.getConfFile()).read())
        assert (isinstance(conf, ConfigurationFile))
        conf.run(self.LOGS_FOLDER, self.DATA_EXP, self.ranges, self.doNr0, max_splits=self.max_splits, threshold_split=self.c)

    def getCompleteLogPath(self, filename):
        return os.path.join(self.LOGS_FOLDER, filename)

    def getLogsFolder(self):
        return self.LOGS_FOLDER