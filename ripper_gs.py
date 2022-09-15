import pandas as pd
import pdb
import math
import wittgenstein as lw
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import mutual_info_classif
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import StratifiedKFold
from sklearn import metrics
from sklearn.metrics import precision_recall_fscore_support
from sklearn.pipeline import Pipeline
import math


# dataset_df = pd.read_csv("data/experiments/bpi15B_decl2_results/split1/payload/dataset.csv")
dataset_df = pd.read_csv("dataset.csv")
y = dataset_df['Label'].values
X = dataset_df.drop(columns=['Case_ID', 'Label'])
clf = lw.RIPPER(random_state=10, k=2, verbosity=-3)
num_features = X.shape[1]
feat_strategy_a = 1 if round(math.sqrt(num_features)) < 1 else round(math.sqrt(num_features))
feat_strategy_b = 1 if round(0.2 * num_features) < 1 else round(0.2 * num_features)
feat_strategy_c = 1 if round(0.3 * num_features) < 1 else round(0.3 * num_features)
clf_parameters = {"feature_selection__k": [feat_strategy_a, feat_strategy_b, feat_strategy_c], "classifier__prune_size": [0.33]}
skf_grd_search = StratifiedKFold(n_splits=5, random_state=0, shuffle=True)

skf_cross_val = StratifiedKFold(n_splits=10, random_state=42, shuffle=True)
for train_index, test_index in skf_cross_val.split(X, y):
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y[train_index], y[test_index]
    selector = SelectKBest(mutual_info_classif)
    pipe = Pipeline(steps=[("feature_selection", selector), ("classifier", clf)])
    #pdb.set_trace()
    gsCV = GridSearchCV(pipe, clf_parameters, n_jobs=None, cv=skf_grd_search, scoring='f1')
    gsCV.fit(X_train, y_train)
    y_test_pred = gsCV.best_estimator_.predict(X_test)
    y_test_pred_score = gsCV.best_estimator_.predict_proba(X_test)[:, 1]
    y_test_pred = gsCV.best_estimator_.predict(X_test)
    y_test_pred_score = gsCV.best_estimator_.predict_proba(X_test)[:, 1]
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_test_pred, average='binary')
    fpr, tpr, _ = metrics.roc_curve(y_test, y_test_pred_score)
    auc = metrics.auc(fpr, tpr)
    print(prec, rec, f1, auc)

print("finito!!")