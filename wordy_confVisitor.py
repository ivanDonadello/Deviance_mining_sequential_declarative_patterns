# Generated from wordy_conf.g by ANTLR 4.7.2
from antlr4 import *

from DevianceMiningPipeline.DataPreparation.RunWholeStrategy import RunWholeStrategy
from main_pipeline_run import runWholeConfiguration
from DevianceMiningPipeline import ConfigurationFile
from DevianceMiningPipeline.LogTaggingViaPredicates import SatCases, tagLogWithSatAllProp, tagLogWithSatAnyProp, tagLogWithExactOccurrence, \
    tagLogWithOccurrence, tagLogWithExactSubsequence, tagLogWithValueEqOverTraceAttn, tagLogWithValueEqOverIthEventAttn
from DevianceMiningPipeline.declaretemplates_new import *

from wordy_confParser import wordy_confParser

# This class defines a complete generic visitor for a parse tree produced by wordy_confParser.

class wordy_confVisitor(ParseTreeVisitor):


    # Visit a parse tree produced by wordy_confParser#pipeline.
    def visitPipeline(self, ctx:wordy_confParser.PipelineContext):
        stratName = eval(ctx.stratName.text)

        dataset_path = self.visitDataset_path(ctx.dataset_path())
        exp_folder = self.visitExp_folder(ctx.exp_folder())
        generate_data = False
        if (ctx.data_dump() is not None):
            generate_data = True
        depths = self.visitWith_dec_depth(ctx.with_dec_depth())
        splitsNr = self.visitWith_splcies(ctx.with_splcies())
        pipeline = RunWholeStrategy(dataset_path,
                                    exp_folder,
                                    generate_data,
                                    depths,
                                    splitsNr)

        par_exp_name = self.visitPar_exp_name(ctx.par_exp_name())
        log = self.visitLog(ctx.log())
        auto_ignores = None
        if (ctx.ignores() is not None):
            auto_ignores = self.visitIgnores(ctx.ignores())
        conf = None
        if (ctx.conf() is not None):
            conf = self.visitConf(ctx.conf())
        cf = ConfigurationFile()
        cf.setExperimentName(par_exp_name)
        cf.setLogName(log)
        if auto_ignores is not None:
            cf.setAutoIgnore(auto_ignores)
        if conf is not None:
            cf.setPayloadSettings(conf)
        cf.dump(par_exp_name+".json")


        child_map = []
        for pair in ctx.child():
            child_map.append(self.visitChild(pair))
        child_map = dict(child_map)

        runWholeConfiguration(pipeline, log, cf, child_map)




    # Visit a parse tree produced by wordy_confParser#dataset_path.
    def visitDataset_path(self, ctx:wordy_confParser.Dataset_pathContext):
        return eval(str(ctx.STRING()))


    # Visit a parse tree produced by wordy_confParser#exp_folder.
    def visitExp_folder(self, ctx:wordy_confParser.Exp_folderContext):
        return eval(str(ctx.STRING()))


    # Visit a parse tree produced by wordy_confParser#data_dump.
    def visitData_dump(self, ctx:wordy_confParser.Data_dumpContext):
        return None


    # Visit a parse tree produced by wordy_confParser#with_dec_depth.
    def visitWith_dec_depth(self, ctx:wordy_confParser.With_dec_depthContext):
        return self.visitInt_list(ctx.int_list())


    # Visit a parse tree produced by wordy_confParser#par_exp_name.
    def visitPar_exp_name(self, ctx:wordy_confParser.Par_exp_nameContext):
        return eval(str(ctx.STRING()))

    # Visit a parse tree produced by wordy_confParser#log.
    def visitLog(self, ctx:wordy_confParser.LogContext):
        return eval(str(ctx.STRING()))


    # Visit a parse tree produced by wordy_confParser#output.
    def visitOutput(self, ctx:wordy_confParser.OutputContext):
        return eval(str(ctx.STRING()))


    # Visit a parse tree produced by wordy_confParser#ignores.
    def visitIgnores(self, ctx:wordy_confParser.IgnoresContext):
        return self.visitString_list(ctx.string_list())


    # Visit a parse tree produced by wordy_confParser#conf.
    def visitConf(self, ctx:wordy_confParser.ConfContext):
        return eval(str(ctx.STRING()))

    # Visit a parse tree produced by wordy_confParser#with_splcies.
    def visitWith_splcies(self, ctx:wordy_confParser.With_splciesContext):
        return int(str(ctx.DIGIT()))


    # Visit a parse tree produced by wordy_confParser#child.
    def visitChild(self, ctx:wordy_confParser.ChildContext):
        childStrategy = eval(ctx.name.text)
        if ctx.model() is not None:
            return (childStrategy, self.visitModel(ctx.model()))
        elif ctx.payload() is not None:
            return (childStrategy, self.visitPayload(ctx.payload()))
        elif ctx.procedural() is not None:
            return (childStrategy, self.visitProcedural(ctx.procedural()))
        raise Exception("No case was provided!")


    # Visit a parse tree produced by wordy_confParser#payload.
    def visitPayload(self, ctx:wordy_confParser.PayloadContext):
        attributeName = eval(ctx.attrn.text)
        val = ""
        if (ctx.DIGIT() is not None):
            val = int(str(ctx.DIGIT()))
        elif (ctx.NUMBER() is not None):
            val = float(str(ctx.NUMBER()))
        elif (ctx.boolean() is not None):
            val = "TrueV" in str(type(ctx.boolean()))
        else:
            val = eval(ctx.STRING(1).text)
        payload = ctx.payload_type()
        payloadtype = str(type(payload))
        if "Nth_eventContext" in payloadtype:
            return self.visitNth_event(ctx.payload_type())(attributeName)(val)
        else:
            return self.visitTrace(ctx.payload_type())(attributeName)(val)


    # Visit a parse tree produced by wordy_confParser#nth_event.
    def visitNth_event(self, ctx:wordy_confParser.Nth_eventContext):
        eventNo = int(str(ctx.DIGIT()))
        return lambda key: lambda value: lambda trace: tagLogWithValueEqOverIthEventAttn(trace, key, value, eventNo)


    # Visit a parse tree produced by wordy_confParser#trace.
    def visitTrace(self, ctx:wordy_confParser.TraceContext):
        return lambda key: lambda value: lambda trace: tagLogWithValueEqOverTraceAttn(trace, key, value)


    # Visit a parse tree produced by wordy_confParser#procedural.
    def visitProcedural(self, ctx:wordy_confParser.ProceduralContext):
        pat = self.visitString_list(ctx.string_list())
        proc = ctx.procs()
        proctype = str(type(proc))
        if "Exact_subseqContext" in proctype:
            run = self.visitExact_subseq(proc)
        elif "OccurencesContext" in proctype:
            run = self.visitOccurences(proc)
        return run(pat)


    # Visit a parse tree produced by wordy_confParser#exact_subseq.
    def visitExact_subseq(self, ctx:wordy_confParser.Exact_subseqContext):
        return lambda pat: lambda x: tagLogWithExactSubsequence(x, pat)


    # Visit a parse tree produced by wordy_confParser#occurences.
    def visitOccurences(self, ctx:wordy_confParser.OccurencesContext):
        isExact = ctx.is_exact is not None
        nth     = int(str(ctx.DIGIT()))
        if isExact:
            return lambda pat: lambda x: tagLogWithExactOccurrence(x, pat, nth)
        else:
            return lambda pat: lambda x: tagLogWithOccurrence(x, pat, nth)


    # Visit a parse tree produced by wordy_confParser#model.
    def visitModel(self, ctx:wordy_confParser.ModelContext):
        sat_type = ctx.sat_type()
        satttype = str(type(sat_type))
        if "Vacuity_satContext" in satttype:
            sat_type = SatCases.VacuitySat
        elif "Not_satContext" in satttype:
            sat_type = SatCases.NotSat
        elif "Not_vac_satContext" in satttype:
            sat_type = SatCases.NotVacuitySat
        elif "SatContext" in satttype:
            sat_type = SatCases.Sat
        else:
            sat_type = None
        satswitch = ctx.satswitch()
        satstype = type(str(satswitch))
        if "Sat_someContext" in satstype:
            satswitch = False
        elif "Sat_allContext" in satstype:
            satswitch = True
        else:
            satswitch = None
        template_pairs = []
        for template in ctx.template():
            template_pairs.append( self.visitTemplate(template))
        if sat_type: #all
            return lambda x: tagLogWithSatAllProp(x, template_pairs, satswitch)
        else:        #exists
            return lambda x: tagLogWithSatAnyProp(x, template_pairs, satswitch)

    # Visit a parse tree produced by wordy_confParser#template.
    def visitTemplate(self, ctx:wordy_confParser.TemplateContext):
        template_name = eval(str(ctx.STRING()))
        template_function = template_map[template_name]
        return (template_function, self.visitString_list(ctx.string_list()))


    # Visit a parse tree produced by wordy_confParser#string_list.
    def visitString_list(self, ctx:wordy_confParser.String_listContext):
        return list(map(lambda x: eval(str(x)), ctx.STRING()))


    # Visit a parse tree produced by wordy_confParser#int_list.
    def visitInt_list(self, ctx:wordy_confParser.Int_listContext):
        return list(map(lambda x: int(str(x)), ctx.DIGIT()))


    # Visit a parse tree produced by wordy_confParser#number.
    def visitNumber(self, ctx:wordy_confParser.NumberContext):
        return float(str(ctx.NUMBER()))



del wordy_confParser