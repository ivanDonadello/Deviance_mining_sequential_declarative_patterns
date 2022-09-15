"""
Main program for synthetic log generator for BPM area.

Generates .xes files

@author Joonas Puura
@author Giacomo Bergami

"""

from .simple import *
import os
import os.path



def write_if_not_exists(file_path):
    if not os.path.isfile(file_path):
        print("... Writing " + file_path)
        return (open(file_path, "w"))
    else:
        return None


def write_xeses(LOGS_FOLDER="data/logs"):
    print("Write Xeses files into data/logs/ (if missing): ")
    config_prev = {
        "label": "Label",
        "deviant": str(1),
        "nondeviant": str(0),
        "type": "int"
    }

    config = {
        "label": "class",
        "deviant": "true",
        "nondeviant": "false",
        "type": "string",
        "shuffle": True
    }

    config_2 = {
        "label": "Label",
        "deviant": str(1),
        "nondeviant": str(0),
        "type": "string",
        "shuffle": True
    }

    f = write_if_not_exists(os.path.join(LOGS_FOLDER, "minimum_test.xes"))
    if not f is None:
        f.write(str(SingleActivityScenario.minimum_test(config=config)))
        f.close()

    f = write_if_not_exists(os.path.join(LOGS_FOLDER, "class_single_extra_1.xes"))
    if not f is None:
        f.write(str(SingleActivityScenario.single_activity_extra_1(config=config)))
        f.close()

    f = write_if_not_exists(os.path.join(LOGS_FOLDER, "class_single_missing_1.xes"))
    if not f is None:
        f.write(str(SingleActivityScenario.single_activity_missing_1(config=config)))
        f.close()

    f = write_if_not_exists(os.path.join(LOGS_FOLDER, "class_activity_set_co_occur.xes"))
    if not f is None:
        f.write(str(ActivitySetScenario.activity_set_co_occur(config=config)))
        f.close()

    f = write_if_not_exists(os.path.join(LOGS_FOLDER, "init_test.xes"))
    if not f is None:
        f.write(str(SingleActivityScenario.init_test_scenario(config=config_2)))
        f.close()
