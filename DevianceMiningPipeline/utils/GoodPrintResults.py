import os
import pdb

confPrettyPrint = {"bs": "IA",
                    "bs_data": "Data+IA",
                   "dc": "Declare",
                    "dc_data": "Data+Declare",
                   "mr": "IA+MR",
                    "mr_data": "Data+IA+MR",
                   "tr": "IA+TR",
                    "tr_data": "Data+IA+TR",
                   "mra": "IA+MRA",
                    "mra_data": "Data+IA+MRA",
                   "tra": "IA+TRA",
                    "tra_data": "Data+IA+TRA",
                   "hybrid": "Hybrid",
                   "hybrid_data": "Data+Hybrid",
                   "payload": "Payload",
                   "dc_dwd": "Declare Data Aware",
                   "dc_dwd_payload": "Payload+Declare Data Aware",
                   "hybrid_dwd": "Hybrid+Declare Data Aware",
                   "hybrid_dwd_payload": "Hybrid+Payload+Declare Data Aware"
                   }

def do_dump_benchmark(all_results, results_folder, dt_max_depth, experiment_name):
    from .GoodPrintResults import printToFile
    line = None
    if (not os.path.exists(os.path.join(results_folder, "benchmarks.csv"))):
        line = "dataset,learner,outcome_type,strategy,conftype,confvalue,metrictype,metricvalue\n"
    with open(os.path.join(results_folder, "benchmarks.csv"), "a") as csvFile:
        with open(os.path.join(results_folder, "rules.txt"), "a") as rulesFile:
            if not (line is None):
                csvFile.write(line)
            printToFile(all_results, experiment_name, "Decision Tree", "max_depth", dt_max_depth, csvFile,
                        rulesFile)
            rulesFile.close()
        csvFile.close()

def printToFile(entry, dataset, lerner, conftype, confvalue, csvFile, rulesFile):
    import _io
    assert (isinstance(csvFile, _io.TextIOWrapper))
    for key in entry:
        ppKey = confPrettyPrint[key]
        elements = ["test"]
        for outcome_type in elements:
            print("Printing outcome for " + outcome_type + " and key " + ppKey +" ....")
            for (acc, auc, f1, precision, recall) in zip(entry[key][outcome_type].accuracies, entry[key][outcome_type].auc, entry[key][outcome_type].f1, entry[key][outcome_type].precision, entry[key][outcome_type].recall):
                csvFile.write(dataset + "," + lerner + "," + outcome_type + "," + ppKey + "," + conftype + "," + str(confvalue) + ",acc,"+str(acc)+"\n")
                csvFile.write(dataset + "," + lerner + "," + outcome_type + "," + ppKey + "," + conftype + "," + str(confvalue) + ",auc," + str(auc)+"\n")
                csvFile.write(dataset + "," + lerner + "," + outcome_type + "," + ppKey + "," + conftype + "," + str(confvalue) + ",f1," + str(f1)+"\n")
                csvFile.write(dataset + "," + lerner + "," + outcome_type + "," + ppKey + "," + conftype + "," + str(confvalue) + ",precision," + str(precision)+"\n")
                csvFile.write(dataset + "," + lerner + "," + outcome_type + "," + ppKey + "," + conftype + "," + str(confvalue) + ",recall," + str(recall)+"\n")
        print("Printing rules for key " + key)
        for ruleSet in entry[key]["rules"]:
            for rule in ruleSet:
                rulesFile.write(dataset + "::" + lerner + "::" + outcome_type + "::" + ppKey + "::" + conftype + "::" + str(confvalue) + "§\t" + rule+"\n")