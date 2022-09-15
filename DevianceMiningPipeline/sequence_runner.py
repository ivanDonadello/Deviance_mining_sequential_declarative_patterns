"""
Python wrapper to extract sequence encodings from logs.
Requires GoSwift.jar in the same folder as it runs it.
Might need to change VMOptions dependent on the version of Java the machine is running on

"""
import subprocess
from DevianceMiningPipeline.utils.PathUtils import *


JAR_NAME = "GoSwift.jar"  # Jar file to run
#OUTPUT_FOLDER = "outputlogs/"  # Where to put output files
#INPUT_FOLDER = "logs/"  # Where input logs are located

## This is needed for one java version.. One for Java 8 and other for later
#VMoptions = " --add-modules java.xml.bind"
VMOptions = ""
## All parameters to run the program with.


def create_output_filename(input_log, name):
    """
    Create output json file name corresponding to the trial parameters
    :param input_log: input log filenae
    :param name: name of the trial
    :return:
    """
    prefix = input_log
    if (input_log.endswith(".xes")):
        prefix = prefix[:prefix.find(".xes")]

    filename = prefix + "_" + name + ".json"

    return filename


def create_call_params(inp_path, results_folder, paramString, inputFile=None, outputFile=None):
    params = paramString.split()

    if outputFile:
        params.append("--outputFile")
        #outputPath = os.path.join(results_folder, "outputlogs")
        os.makedirs(results_folder, exist_ok=True)
        params.append(os.path.join(results_folder, outputFile))
    if inputFile:
        params.append("--logFile")
        params.append(os.path.join(inp_path, inputFile[0]))
        if inputFile[1]:
            params.append("--requiresLabelling")

    return params

def create_call_params2(inp_path, results_folder, paramString, inputFile=None, outputFile=None):
    params = paramString.split()
    #if outputFile:
    params.append("--outputFile")
    #outputPath = os.path.join(results_folder, "outputlogs")
    os.makedirs(results_folder, exist_ok=True)
    params.append(os.path.join(results_folder, outputFile))
    #if inputFile:
    params.append("--logFile")
    params.append(inputFile)
    #    if inputFile[1]:
    #        params.append("--requiresLabelling")
    return params

def call_params(inp_path, results_folder, paramString, inputFile, outputFile, err_logger):
    """
    Function to call java subprocess
    TODO: Send sigkill when host process (this one dies) to also kill the subprocess calls
    :param paramString:
    :param inputFile:
    :return:
    """

    print("Started working on {}".format(inputFile[0]))
    parameters = create_call_params(inp_path, results_folder, paramString, inputFile, outputFile)
    FNULL = open(os.devnull, 'w')  # To write output to devnull, we dont care about it

    # No java 8
    #subprocess.call(["java", "-jar", "--add-modules", "java.xml.bind", JAR_NAME] + parameters, stdout=FNULL,
    #                stderr=open("errorlogs/error_" + outputFile, "w"))  # blocking

    print(" ".join(["java", "-jar",  JAR_NAME] + parameters))
    # Java 8
    subprocess.call(["java", "-jar",  JAR_NAME] + parameters, stdout=FNULL,
                    stderr=open(os.path.join(err_logger, "error_" + outputFile), "w"))  # blocking

    print("Done with {}".format(str(parameters)))


# def move_files(split_nr, folder, results_folder):
#     """
#     Move generated encodings
#     :param split_nr: number of cv split
#     :param folder: folder for encoding at end location
#     :param results_folder: resulting folder
#     :return:
#     """
#     # source = './output/'
#     # dest1 = './' + results_folder + '/split' + str(split_nr) + "/" + folder + "/"
#     #
#     # files = os.listdir(source)
#     #
#     # ## Moves all files in the folder to detination
#     # for f in files:
#     #     shutil.move(source+f, dest1)

def genParamStrings(sequence_threshold):
    return [
        ("--coverageThreshold {} ".format(sequence_threshold) + "--featureType Sequence --minimumSupport 0.1 --patternType MR --encodingType Frequency", "SequenceMR", "mr"),
        ("--coverageThreshold {} ".format(sequence_threshold) + "--featureType Sequence --minimumSupport 0.1 --patternType MRA --encodingType Frequency", "SequenceMRA", "mra"),
        ("--coverageThreshold {} ".format(sequence_threshold) + "--featureType Sequence --minimumSupport 0.1 --patternType TR --encodingType Frequency", "SequenceTR", "tr"),
        ("--coverageThreshold {} ".format(sequence_threshold) + "--featureType Sequence --minimumSupport 0.1 --patternType TRA --encodingType Frequency", "SequenceTRA", "tra"),
    ]

def run_sequences(inp_path, log_path, results_folder, err_logger, max_splits, sequence_threshold=5):
    """
    Runs GoSwift.jar with 4 different sets of parameters, to create sequential encodings.
    :param log_path:
    :param results_folder:
    :param sequence_threshold:
    :return:
    """
    ## Input parameters to GoSwift.jar
    paramStrings = genParamStrings(sequence_threshold)
    strategies = list()

    for paramString, techName, folder in paramStrings:
        print("Working on {} @{}".format(techName, folder))
        strategies.append(folder)
        for splitNr in range(max_splits):
            outputPath = FileNameUtils.embedding_path(splitNr, results_folder, folder)
            os.makedirs(outputPath, exist_ok=True)
            inputFile = (log_path.format(splitNr+1), False)
            outputFilename = create_output_filename(inputFile[0], techName)
            call_params(inp_path, outputPath, paramString, inputFile, outputFilename, err_logger)

            # The jar will directly write to t
            move_files('./output/', results_folder, splitNr + 1, folder)
    return strategies

def generateSequences(inp_path, log_path, results_folder, sequence_threshold=5):
    yamlPart = {}
    mkdir_test('./output/')
    for paramString, techName, folder in genParamStrings(sequence_threshold):
        outputFilename = create_output_filename(log_path, techName)
        parameters = create_call_params2(inp_path, results_folder, paramString, log_path, outputFilename)
        print(" ".join(["java", "-jar", JAR_NAME] + parameters))
        subprocess.call(["java", "-jar", JAR_NAME] + parameters)  # blocking
        res = move_files('./output/', results_folder, 0, folder)
        yamlPart[folder] = os.path.abspath(os.path.join(res, "globalLog.csv"))
    return yamlPart