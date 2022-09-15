"""

Defines high-level function predicates for the log

@author: Giacomo Bergami <bergamigiacomo@gmail.com>
"""
from opyenxes.data_in.XUniversalParser import XUniversalParser
from opyenxes.model import XAttributeBoolean, XAttributeLiteral, XAttributeTimestamp, XAttributeDiscrete, XAttributeContinuous
from opyenxes.factory.XFactory import XFactory
from enum import Enum
import numpy
from .deviancecommon import xes_to_positional
import itertools

def n_slices(n, list_):
    for i in range(len(list_) + 1 - n):
        yield list_[i:i+n]

def n_setSlice(n, list_):
    for slice in itertools.combinations(list_,n):
        sliceS = set(slice)
        if (len(sliceS)==n):
            yield sliceS

def isSublist(list_, sub_list):
    for slice_ in n_slices(len(sub_list), list_):
        if slice_ == sub_list:
            return True
    return False

def traceAsListOfEvents(trace):
    return list(map(lambda x: str(x.get_attributes()["concept:name"].get_value()), trace))

def isTraceSublistOf(trace, sublist):
    return isSublist(traceAsListOfEvents(trace), sublist)

def compileIsTraceSublistOf(sublist):
    return lambda x : isTraceSublistOf(x, sublist)

def countPatternExactOccurrence(trace, pat, threshold):
    pattern = list(pat)
    npatt = len(pattern)
    return sum(map(lambda x: 1 if x == pattern else 0, n_slices(npatt, traceAsListOfEvents(trace)))) >= threshold

def compileCountPatternExact(pat, threshold):
    return lambda x : countPatternExactOccurrence(x, pat, threshold)

def countPatternOccurrence(trace, pattern, threshold):
    sPattern = set(pattern)
    npatt = len(pattern)
    return sum(map(lambda x: 1 if x == sPattern else 0, n_setSlice(npatt, traceAsListOfEvents(trace)))) >= threshold

def compileCountPattern(pat, threshold):
    return lambda x : countPatternOccurrence(x, pat, threshold)

def hasTraceAttributeWithValue(trace, attribute, value):
    if attribute in trace.get_attributes():
        return trace.get_attributes()[attribute].get_value() == value
    else:
        return False

def hasIthEventAttributeWithValue(trace, attribute, value, ith):
    event = trace[ith]
    if attribute in event.get_attributes():
        return event.get_attributes()[attribute].get_value() == value
    else:
        return False

def hasEventAttributeWithValue(trace, attribute, value):
    for event in trace:
        if attribute in event.get_attributes():
            if event.get_attributes()[attribute].get_value() == value:
                return True
    return False


def compileTraceAttributeWithValue(attribute, value):
    return lambda x: hasTraceAttributeWithValue(x, attribute, value)

def compileIthEventAttributeWithValue(attribute, value, ith):
    return lambda x: hasIthEventAttributeWithValue(x, attribute, value, ith)

def compileEventAttributeWithValue(attribute, value):
    return lambda x: hasEventAttributeWithValue(x, attribute, value)

def extractAttributeValues(x, attribute):
    if attribute in x.get_attributes():
        return x.get_attributes()[attribute].get_value()
    else:
        return None

class SatCases(Enum):
        VacuitySat = 0
        NotSat = 1
        NotVacuitySat = 2
        Sat = 3

checkSatSwitch = {'VacuitySat': lambda x: x == 0, 'NotSat': lambda x: x<0, 'NotVacuitySat': lambda x : x>0, 'Sat': lambda x: x>=0}
def checkSat(trace, function, event_name_list, SatCheck):
    """
    Checks the satisfiability of the condition using all the parameters

    :param trace:               Trace to be tested with a Joonas' predicate
    :param function:            Function to be called for returning the predicate's value
    :param event_name_list:     Event names to be used to instantiate the predicate
    :param SatCheck:            The satisfiability condition to be checked for the predicate
    :return:
    """
    out, _  = function(trace, event_name_list)
    lam = checkSatSwitch[SatCheck.name]
    tes = lam(out)
    return tes

class SatProp:
    """
    This class makes each Joonas' predicate as a true predicate to be called, so to be uniform
    with a 1) intuitive concept of a predicate to be checked 2) separating the parameter instantiation
    from its check 3) Provide a compact representation of the predicate as a class
    """
    def __init__(selbst, function, event_name_list, SatCheck):
        """
        :param function:            Joonas' function to be checked
        :param event_name_list:     List for instantiating the predicate with the events' names
        :param SatCheck:            Satisfiability check for the predicate's outcome
        """
        assert(callable(function))
        selbst.function = function
        assert(isinstance(event_name_list, list))
        selbst.event_name_list = event_name_list
        assert (isinstance(SatCheck, SatCases))
        selbst.SatCheck = SatCheck

    def __call__(self, trace):
        """
        Checking the predicate via a trace
        :param trace:
        :return:        Whether the predicate was satisfied using a specific satisfiability condition
        """
        return checkSat(trace, self.function, self.event_name_list, self.SatCheck)

class SatAllProp:
    """
    Definition of a class checking that all the Satisfiability predicates were satisfied
    """
    def __init__(self, props):
        for x in props:
            assert(isinstance(x, SatProp))
        self.props = props

    def __call__(self, trace):
        return all(x(trace) for x in self.props)

class SatAnyProp:
    """
    Definition of a class checking that all the Satisfiability predicates were satisfied
    """
    def __init__(self, props):
        for x in props:
            assert(isinstance(x, SatProp))
        self.props = props

    def __call__(self, trace):
        return any(x(trace) for x in self.props)

def logTagger(log, predicate, doPropositional = False, doTests = True):
    """
    Tags the log using the predicate's satisfiability
    :param log:         Log to be tagget at each trace
    :param predicate:   Predicate used to tag the sequence
    :return:
    """
    nTot = 0
    nPred = 0
    propLog = dict()
    if doPropositional:
        for propTrace in xes_to_positional(log, False):
            propLog[propTrace["name"]] = propTrace["events"]
    for trace in log:
        nTot = nTot+1
        test = False
        if doPropositional:
            trace_name = trace.get_attributes()["concept:name"].get_value()
            test = predicate(propLog[trace_name])
        else:
            test = predicate(trace)
        if test:
            nPred = nPred + 1
        trace.get_attributes()["Label"] = XFactory.create_attribute_literal("Label","1" if test else "0")
    if doTests:
        assert (nPred < nTot)
        assert (nPred > 0)

def logRandomTagger(log, min = 0, max = 1, maxThreshold = 0.1):
    """
    Tags the log using the predicate's satisfiability
    :param log:         Log to be tagget at each trace
    :param predicate:   Predicate used to tag the sequence
    :return:
    """
    for (trace,prob) in zip(log, numpy.random.uniform(min, max, len(log))):
        trace.get_attributes()["Label"] = XFactory.create_attribute_literal("Label","1" if prob<=maxThreshold else "0")

def tagLogWithValueEqOverTraceAttn(log, attn, val):
    logTagger(log, compileTraceAttributeWithValue(attn, val))

def tagLogWithValueEqOverEventAttn(log, attn, val):
    logTagger(log, compileEventAttributeWithValue(attn, val))

def tagLogWithValueEqOverIthEventAttn(log, attn, val, ith):
    logTagger(log, compileIthEventAttributeWithValue(attn, val, ith))

def tagLogWithExactSubsequence(log, subsequence):
    logTagger(log, compileIsTraceSublistOf(subsequence))

def tagLogWithExactOccurrence(log, pat, threshold):
        logTagger(log, compileCountPatternExact(pat, threshold))

def tagLogWithOccurrence(log, pat, threshold):
    logTagger(log, compileCountPattern(pat, threshold))

def tagLogWithSatAllProp(log, functionEventNamesList, SatCheck):
    logTagger(log, SatAllProp([SatProp(x,y, SatCheck) for (x,y) in functionEventNamesList]), True)

def tagLogWithSatAnyProp(log, functionEventNamesList, SatCheck):
    logTagger(log, SatAnyProp([SatProp(x,y, SatCheck) for (x,y) in functionEventNamesList]), True)

def ignoreTagging():
    pass