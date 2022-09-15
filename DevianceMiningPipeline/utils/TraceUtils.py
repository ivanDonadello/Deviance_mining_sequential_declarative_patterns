"""
Utility functions for XES traces
"""
from opyenxes.data_in.XUniversalParser import XUniversalParser
from opyenxes.data_out.XesXmlSerializer import XesXmlSerializer
from opyenxes.model import XAttributeBoolean, XAttributeLiteral, XAttributeTimestamp, XAttributeDiscrete, XAttributeContinuous
from opyenxes.factory.XFactory import XFactory

def getTraceLabel(trace):
    return str(trace.get_attributes()["Label"])

def isTraceLabelPositive(trace):
    return str(trace.get_attributes()["Label"]) == "1"

def getTraceId(trace):
    return str(trace.get_attributes()["concept:name"])

def trace_to_label_map(log):
    d = dict()
    for trace in log:
        d[getTraceId(trace)] = getTraceLabel(trace)
    return d

def propositionalized_trace_to_label_map(log):
    d = dict()
    for trace in log:
        d[trace["name"]] = trace["label"]
    return d

#trace_attribs = trace.get_attributes()
#        trace_name = trace_attribs["concept:name"].get_value()