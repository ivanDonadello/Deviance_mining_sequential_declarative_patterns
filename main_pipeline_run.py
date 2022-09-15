from DevianceMiningPipeline.DataPreparation import RunWholeStrategy
from DevianceMiningPipeline.DataPreparation import ConfigurationFile
import gc

def printWithColor(str):
     print("\x1b[6;30;42m " + str + "\x1b[0m")

def runWholeConfiguration(pipeline_conf, original_log_path, conf, map_as_strategy):
    assert (isinstance(original_log_path, str))
    assert (isinstance(map_as_strategy, dict))
    #assert (isinstance(pipeline_conf, RunWholeStrategy))
    #assert (isinstance(conf, ConfigurationFile))

    logs_folder = pipeline_conf.getLogsFolder()
    full_path = pipeline_conf.getCompleteLogPath(original_log_path)

    printWithColor(
        "Guaranteeing that the logs used for the testing have unique trace ids (it is required for better training the dataset)")
    from DevianceMiningPipeline.DataPreparation.RetagLogWithUniqueIds import changeLog
    if True:
        dictJson = dict()
        doLoadFile = False
        for key, value in map_as_strategy.items():
            printWithColor("Setting Up configuration: " + key)
            from DevianceMiningPipeline.DataPreparation.TaggingStrategy import TaggingStrategy
            jsonFile = TaggingStrategy(key, value)
            dictJson[key] = jsonFile
            doLoadFile = doLoadFile or jsonFile.will_dump_log(logs_folder)

        if doLoadFile:
            printWithColor("Loading the log file")
            _, log = changeLog(full_path, False)
            for key, value in map_as_strategy.items():
                printWithColor("Dumping Log configuration: " + key)
                dictJson[key](logs_folder, conf, log)
            del log
        else:
            for key, value in map_as_strategy.items():
                printWithColor("Dumping Log configuration: " + key)
                dictJson[key].dump(conf)

    for key in dictJson:
        gc.collect()
        jsonFile = dictJson[key]
        printWithColor("Running configuration: " + key)
        assert isinstance(jsonFile, TaggingStrategy)
        pipeline_conf(jsonFile)