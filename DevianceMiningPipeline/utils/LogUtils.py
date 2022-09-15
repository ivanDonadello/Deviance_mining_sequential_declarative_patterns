from DevianceMiningPipeline.utils import TraceUtils
from DevianceMiningPipeline.deviancecommon import xes_to_positional, xes_to_data_positional

def abstract_split(log, train_id, test_id, log_conversion = None, id_extractor = None):
    """
    Abstract function performing splitting

    :param log:                 loaded XES log
    :param train_id:            Id of the rows belonging to the training set
    :param test_id:             Id of the rows belonging to the testing set
    :param log_conversion:      Whether we need to convert the log to a specific representation. Otherwise, the log is preserved as it is
    :param id_extractor:        The function used to extract the id for a given trace in the transformed log
    :return:
    """
    if id_extractor is None:
        id_extractor = TraceUtils.getTraceId
    converted_log = log
    if log_conversion is not None:
        converted_log = log_conversion(log)

    assert (isinstance(train_id, set))
    assert (isinstance(test_id, set))
    train_log = []
    test_log = []

    for trace in converted_log:
        traceId = id_extractor(trace)
        if traceId in train_id:
            train_log.append(trace)
        elif traceId in test_id:
            test_log.append(trace)
        else:
            assert False

    assert (len(train_log)>0)
    assert (len(test_log)>0)
    return (train_log, test_log)

def xes_to_data_propositional_split(log, train_id, test_id, doForce):
    return abstract_split(log, train_id, test_id, lambda x: xes_to_data_positional(x, forceSomeElements=doForce), lambda x: x["name"])

def xes_to_propositional_split(log, train_id, test_id):
    return abstract_split(log, train_id, test_id, xes_to_positional, lambda x: x["name"])

def xes_to_tracelist_split(log, train_id, test_id):
    return abstract_split(log, train_id, test_id)

