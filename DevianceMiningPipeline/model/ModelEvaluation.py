"""

@author: joonas
"""
import numpy as np

class ModelEvaluation:
    def __init__(self, name, ):
        self.name = name
        self.accuracies = []
        self.precision = []
        self.recall = []
        self.f1 = []
        self.auc = []

    def add_to_file(self, filePath, text):
        #with open(filePath, "a+") as f:
        #    f.write(text + "\n")
        pass

    def add_results(self, accuracy, precision, rc, f1, auc):
        self.accuracies.append(accuracy)
        self.precision.append(precision)
        self.recall.append(rc)
        self.f1.append(f1)
        self.auc.append(auc)

    def add_results_dict(self, results):
        self.accuracies.append(results["accuracy"])
        self.precision.append(results["precision"])
        self.recall.append(results["recall"])
        self.f1.append(results["f1"])
        self.auc.append(results["auc"])

    def print_statistics(self):
        print("Statistics for {}".format(self.name))
        print("Accuracy mean:", np.mean(self.accuracies))
        print("Accuracy std:", np.std(self.accuracies))
        print("Precision mean:", np.mean(self.precision))
        print("Precision std:", np.std(self.precision))
        print("Recall mean:", np.mean(self.recall))
        print("Recall std:", np.std(self.recall))
        print("F1 mean:", np.mean(self.f1))
        print("F1 std:", np.std(self.f1))
        print("AUC mean:", np.mean(self.auc))
        print("AUC std:", np.std(self.auc))
        print("")

    def print_statistics_drive(self):
        print("Statistics for {}".format(self.name))
        print("{} {} {} {} {} {} {} {} {} {}".format(np.mean(self.accuracies),
                                                     np.std(self.accuracies), np.mean(self.auc), np.std(self.auc),
                                                     np.mean(self.f1), np.std(self.f1),
                                                     np.mean(self.recall), np.std(self.recall), np.mean(self.precision),
                                                     np.std(self.precision)))
        print("")

    def write_statistics_file(self, filePath):
        text = "Statistics for {}".format(self.name) + "\n" + "{} {} {} {} {} {} {} {} {} {}".format(
            np.mean(self.accuracies),
            np.std(self.accuracies), np.mean(self.auc), np.std(self.auc), np.mean(self.f1), np.std(self.f1),
            np.mean(self.recall), np.std(self.recall), np.mean(self.precision), np.std(self.precision)) + "\n"
        #self.add_to_file(filePath, text)

    def write_statistics_file_noname(self, filePath):
        text = "{} {} {} {} {} {} {} {} {} {}".format(
            np.mean(self.accuracies),
            np.std(self.accuracies), np.mean(self.auc), np.std(self.auc), np.mean(self.f1), np.std(self.f1),
            np.mean(self.recall), np.std(self.recall), np.mean(self.precision), np.std(self.precision))
        #self.add_to_file(filePath, text)