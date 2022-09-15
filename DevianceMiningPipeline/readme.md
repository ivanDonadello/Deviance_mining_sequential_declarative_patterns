

# Overview of Methods in Business Process Deviance Mining

## Files


### DevianceMiningPipeline folder

Main code for pipeline is in folder DevianceMiningPipeline. In there we have files. In order to run the pipeline, start looking at benchmarks.py on how to describe experiments..

* benchmarks.py - Experiment setup. Main file to run.
* ExperimentRunner.py - Main code for experiment pipelining
* sequence\_runner.py - Code to run sequence mining algorithms
* payload\_extractor.py - Code to extract payload features
* declaredevmining.py - Declare constraint mining
* ddm\_newmethod\_fixed\_new.py - Code to run data-aware declare constraint mining
* baseline\_runner.py - Extract single activities as features
* deviancecommon.py - Common shared functions
* declaretemplate\*.py - Definitions of declare and data-declare templates

* Configuration for payload attributes is kept in "\*.cfg" files.


### RulesExtraction

Code to extract rules from sklearn decision tree, run weka's JRip and calculate statistics on rule lengths, ruleset sizes. Also contains extracted rules.

### LogGeneration
Code to generate synthetic logs used in trials.

### DataVisualization
Jupyter notebooks for creation of plots of experiment results


### ExperimentResults

Experiment results in xls files



## Dependencies

- GoSwift.jar - For sequence mining TRA, MRA, TR, MR. Depends on Java 8. Check 
- skfeature - Feature selection
- Opyenxes for manipulating xes format
- sklearn for ML models
- Weka for RIPPER


