library(scmamp)

data <- read.table("/Users/ivan/PycharmProjects/dev_min/CompleteDevianceMining/python_pipeline/results/dt_table_CD.csv", header=TRUE, sep=",", strip.white = TRUE)
data <- read.table("/Users/ivan/PycharmProjects/dev_min/CompleteDevianceMining/python_pipeline/results/rk_table_CD.csv", header=TRUE, sep=",", strip.white = TRUE)
data <- data[, 2:ncol(data)]
plotCD(data, alpha=0.05)