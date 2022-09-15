# Generated from wordy_conf.g by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .wordy_confParser import wordy_confParser
else:
    from wordy_confParser import wordy_confParser

# This class defines a complete listener for a parse tree produced by wordy_confParser.
class wordy_confListener(ParseTreeListener):

    # Enter a parse tree produced by wordy_confParser#pipeline.
    def enterPipeline(self, ctx:wordy_confParser.PipelineContext):
        pass

    # Exit a parse tree produced by wordy_confParser#pipeline.
    def exitPipeline(self, ctx:wordy_confParser.PipelineContext):
        pass


    # Enter a parse tree produced by wordy_confParser#dataset_path.
    def enterDataset_path(self, ctx:wordy_confParser.Dataset_pathContext):
        pass

    # Exit a parse tree produced by wordy_confParser#dataset_path.
    def exitDataset_path(self, ctx:wordy_confParser.Dataset_pathContext):
        pass


    # Enter a parse tree produced by wordy_confParser#exp_folder.
    def enterExp_folder(self, ctx:wordy_confParser.Exp_folderContext):
        pass

    # Exit a parse tree produced by wordy_confParser#exp_folder.
    def exitExp_folder(self, ctx:wordy_confParser.Exp_folderContext):
        pass


    # Enter a parse tree produced by wordy_confParser#data_dump.
    def enterData_dump(self, ctx:wordy_confParser.Data_dumpContext):
        pass

    # Exit a parse tree produced by wordy_confParser#data_dump.
    def exitData_dump(self, ctx:wordy_confParser.Data_dumpContext):
        pass


    # Enter a parse tree produced by wordy_confParser#with_dec_depth.
    def enterWith_dec_depth(self, ctx:wordy_confParser.With_dec_depthContext):
        pass

    # Exit a parse tree produced by wordy_confParser#with_dec_depth.
    def exitWith_dec_depth(self, ctx:wordy_confParser.With_dec_depthContext):
        pass


    # Enter a parse tree produced by wordy_confParser#with_splcies.
    def enterWith_splcies(self, ctx:wordy_confParser.With_splciesContext):
        pass

    # Exit a parse tree produced by wordy_confParser#with_splcies.
    def exitWith_splcies(self, ctx:wordy_confParser.With_splciesContext):
        pass


    # Enter a parse tree produced by wordy_confParser#par_exp_name.
    def enterPar_exp_name(self, ctx:wordy_confParser.Par_exp_nameContext):
        pass

    # Exit a parse tree produced by wordy_confParser#par_exp_name.
    def exitPar_exp_name(self, ctx:wordy_confParser.Par_exp_nameContext):
        pass


    # Enter a parse tree produced by wordy_confParser#log.
    def enterLog(self, ctx:wordy_confParser.LogContext):
        pass

    # Exit a parse tree produced by wordy_confParser#log.
    def exitLog(self, ctx:wordy_confParser.LogContext):
        pass


    # Enter a parse tree produced by wordy_confParser#output.
    def enterOutput(self, ctx:wordy_confParser.OutputContext):
        pass

    # Exit a parse tree produced by wordy_confParser#output.
    def exitOutput(self, ctx:wordy_confParser.OutputContext):
        pass


    # Enter a parse tree produced by wordy_confParser#ignores.
    def enterIgnores(self, ctx:wordy_confParser.IgnoresContext):
        pass

    # Exit a parse tree produced by wordy_confParser#ignores.
    def exitIgnores(self, ctx:wordy_confParser.IgnoresContext):
        pass


    # Enter a parse tree produced by wordy_confParser#conf.
    def enterConf(self, ctx:wordy_confParser.ConfContext):
        pass

    # Exit a parse tree produced by wordy_confParser#conf.
    def exitConf(self, ctx:wordy_confParser.ConfContext):
        pass


    # Enter a parse tree produced by wordy_confParser#child.
    def enterChild(self, ctx:wordy_confParser.ChildContext):
        pass

    # Exit a parse tree produced by wordy_confParser#child.
    def exitChild(self, ctx:wordy_confParser.ChildContext):
        pass


    # Enter a parse tree produced by wordy_confParser#payload.
    def enterPayload(self, ctx:wordy_confParser.PayloadContext):
        pass

    # Exit a parse tree produced by wordy_confParser#payload.
    def exitPayload(self, ctx:wordy_confParser.PayloadContext):
        pass


    # Enter a parse tree produced by wordy_confParser#nth_event.
    def enterNth_event(self, ctx:wordy_confParser.Nth_eventContext):
        pass

    # Exit a parse tree produced by wordy_confParser#nth_event.
    def exitNth_event(self, ctx:wordy_confParser.Nth_eventContext):
        pass


    # Enter a parse tree produced by wordy_confParser#trace.
    def enterTrace(self, ctx:wordy_confParser.TraceContext):
        pass

    # Exit a parse tree produced by wordy_confParser#trace.
    def exitTrace(self, ctx:wordy_confParser.TraceContext):
        pass


    # Enter a parse tree produced by wordy_confParser#procedural.
    def enterProcedural(self, ctx:wordy_confParser.ProceduralContext):
        pass

    # Exit a parse tree produced by wordy_confParser#procedural.
    def exitProcedural(self, ctx:wordy_confParser.ProceduralContext):
        pass


    # Enter a parse tree produced by wordy_confParser#exact_subseq.
    def enterExact_subseq(self, ctx:wordy_confParser.Exact_subseqContext):
        pass

    # Exit a parse tree produced by wordy_confParser#exact_subseq.
    def exitExact_subseq(self, ctx:wordy_confParser.Exact_subseqContext):
        pass


    # Enter a parse tree produced by wordy_confParser#occurences.
    def enterOccurences(self, ctx:wordy_confParser.OccurencesContext):
        pass

    # Exit a parse tree produced by wordy_confParser#occurences.
    def exitOccurences(self, ctx:wordy_confParser.OccurencesContext):
        pass


    # Enter a parse tree produced by wordy_confParser#model.
    def enterModel(self, ctx:wordy_confParser.ModelContext):
        pass

    # Exit a parse tree produced by wordy_confParser#model.
    def exitModel(self, ctx:wordy_confParser.ModelContext):
        pass


    # Enter a parse tree produced by wordy_confParser#vacuity_sat.
    def enterVacuity_sat(self, ctx:wordy_confParser.Vacuity_satContext):
        pass

    # Exit a parse tree produced by wordy_confParser#vacuity_sat.
    def exitVacuity_sat(self, ctx:wordy_confParser.Vacuity_satContext):
        pass


    # Enter a parse tree produced by wordy_confParser#not_sat.
    def enterNot_sat(self, ctx:wordy_confParser.Not_satContext):
        pass

    # Exit a parse tree produced by wordy_confParser#not_sat.
    def exitNot_sat(self, ctx:wordy_confParser.Not_satContext):
        pass


    # Enter a parse tree produced by wordy_confParser#not_vac_sat.
    def enterNot_vac_sat(self, ctx:wordy_confParser.Not_vac_satContext):
        pass

    # Exit a parse tree produced by wordy_confParser#not_vac_sat.
    def exitNot_vac_sat(self, ctx:wordy_confParser.Not_vac_satContext):
        pass


    # Enter a parse tree produced by wordy_confParser#sat.
    def enterSat(self, ctx:wordy_confParser.SatContext):
        pass

    # Exit a parse tree produced by wordy_confParser#sat.
    def exitSat(self, ctx:wordy_confParser.SatContext):
        pass


    # Enter a parse tree produced by wordy_confParser#sat_some.
    def enterSat_some(self, ctx:wordy_confParser.Sat_someContext):
        pass

    # Exit a parse tree produced by wordy_confParser#sat_some.
    def exitSat_some(self, ctx:wordy_confParser.Sat_someContext):
        pass


    # Enter a parse tree produced by wordy_confParser#sat_all.
    def enterSat_all(self, ctx:wordy_confParser.Sat_allContext):
        pass

    # Exit a parse tree produced by wordy_confParser#sat_all.
    def exitSat_all(self, ctx:wordy_confParser.Sat_allContext):
        pass


    # Enter a parse tree produced by wordy_confParser#template.
    def enterTemplate(self, ctx:wordy_confParser.TemplateContext):
        pass

    # Exit a parse tree produced by wordy_confParser#template.
    def exitTemplate(self, ctx:wordy_confParser.TemplateContext):
        pass


    # Enter a parse tree produced by wordy_confParser#trueV.
    def enterTrueV(self, ctx:wordy_confParser.TrueVContext):
        pass

    # Exit a parse tree produced by wordy_confParser#trueV.
    def exitTrueV(self, ctx:wordy_confParser.TrueVContext):
        pass


    # Enter a parse tree produced by wordy_confParser#falseV.
    def enterFalseV(self, ctx:wordy_confParser.FalseVContext):
        pass

    # Exit a parse tree produced by wordy_confParser#falseV.
    def exitFalseV(self, ctx:wordy_confParser.FalseVContext):
        pass


    # Enter a parse tree produced by wordy_confParser#string_list.
    def enterString_list(self, ctx:wordy_confParser.String_listContext):
        pass

    # Exit a parse tree produced by wordy_confParser#string_list.
    def exitString_list(self, ctx:wordy_confParser.String_listContext):
        pass


    # Enter a parse tree produced by wordy_confParser#int_list.
    def enterInt_list(self, ctx:wordy_confParser.Int_listContext):
        pass

    # Exit a parse tree produced by wordy_confParser#int_list.
    def exitInt_list(self, ctx:wordy_confParser.Int_listContext):
        pass


    # Enter a parse tree produced by wordy_confParser#number.
    def enterNumber(self, ctx:wordy_confParser.NumberContext):
        pass

    # Exit a parse tree produced by wordy_confParser#number.
    def exitNumber(self, ctx:wordy_confParser.NumberContext):
        pass


