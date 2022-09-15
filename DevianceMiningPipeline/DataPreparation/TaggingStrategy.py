"""
This class provides a compact representation of the generation of a json file, which is associated to a tagging
of the dataset with a given function

@author: Giacomo Bergami
"""
import os
from opyenxes.data_out.XesXmlSerializer import XesXmlSerializer
#from DevianceMiningPipeline import ConfigurationFile

def write_log_file(log, filen):
    with open(filen, "w") as file:
        XesXmlSerializer().serialize(log, file)
        file.close()

def write_log_file_with_cond(log, filen, f):
    if not os.path.isfile(filen):
        print("Writing: "+filen)
        f(log)
        write_log_file(log, filen)

class TaggingStrategy:
    def __init__(self, experiment_name, fun):
        experiment_name = str(experiment_name)
        self.logname = experiment_name + ".xes"
        self.outputfolder = experiment_name +"_out"
        self.experiment_name = experiment_name
        self.json = experiment_name + ".json"
        self.fun = fun

    def will_dump_log(self, basepath):
        return not os.path.isfile(os.path.join(basepath, self.logname))

    def __call__(self, basepath, conf, log):
        #assert(isinstance(conf, ConfigurationFile))
        write_log_file_with_cond(log, os.path.join(basepath, self.logname), self.fun)
        conf.setLogName(self.logname)
        conf.setOutputFolder(self.outputfolder)
        conf.setExperimentName(self.experiment_name)
        conf.dump(self.json)
        return self

    def dump(self, conf):
        conf.setLogName(self.logname)
        conf.setOutputFolder(self.outputfolder)
        conf.setExperimentName(self.experiment_name)
        conf.dump(self.json)
        return self

    def getConfFile(self):
        return self.json