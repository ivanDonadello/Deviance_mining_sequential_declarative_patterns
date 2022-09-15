"""
Moving here the model utils functions

@author : joonas, Giacomo Bergami
"""

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.tree import DecisionTreeClassifier, _tree
import numpy as np

def evaluate_dt_model(clf, X_train, y_train, X_test, y_test) -> (dict, dict):
    """
    Evaluates the model
    :param y_test:
    :param predictions:
    :param probabilities:
    :return:
    """

    # predict on train data

    predictions = clf.predict(X_train)
    probabilities = clf.predict_proba(X_train).T[1]


    # get metrics
    train_accuracy = accuracy_score(y_train, predictions)
    train_precision = precision_score(y_train, predictions)
    train_rc = recall_score(y_train, predictions)
    train_f1 = f1_score(y_train, predictions)
    train_auc = roc_auc_score(y_train, probabilities)

    # predict on test data
    predictions = clf.predict(X_test)
    probabilities = clf.predict_proba(X_test).T[1]

    # get metrics
    test_accuracy = accuracy_score(y_test, predictions)
    test_precision = precision_score(y_test, predictions)
    test_rc = recall_score(y_test, predictions)
    test_f1 = f1_score(y_test, predictions)
    test_auc = 0
    try:
        test_auc = roc_auc_score(y_test, probabilities)
    except:
        test_auc = 0

    train_results = {
        "accuracy": train_accuracy,
        "precision": train_precision,
        "recall": train_rc,
        "f1": train_f1,
        "auc": train_auc
    }

    test_results = {
        "accuracy": test_accuracy,
        "precision": test_precision,
        "recall": test_rc,
        "f1": test_f1,
        "auc": test_auc
    }
    return train_results, test_results


def export_text2(decision_tree, feature_names=None,
                spacing=3, decimals=5, show_weights=False):
    """Build a text report showing the rules of a decision tree.

    Note that backwards compatibility may not be supported.

    Parameters
    ----------
    decision_tree : object
        The decision tree estimator to be exported.
        It can be an instance of
        DecisionTreeClassifier or DecisionTreeRegressor.

    feature_names : list of str, default=None
        A list of length n_features containing the feature names.
        If None generic names will be used ("feature_0", "feature_1", ...).

    max_depth : int, default=10
        Only the first max_depth levels of the tree are exported.
        Truncated branches will be marked with "...".

    spacing : int, default=3
        Number of spaces between edges. The higher it is, the wider the result.

    decimals : int, default=2
        Number of decimal digits to display.

    show_weights : bool, default=False
        If true the classification weights will be exported on each leaf.
        The classification weights are the number of samples each class.

    Returns
    -------
    report : string
        Text summary of all the rules in the decision tree.

    Examples
    --------

    >>> from sklearn.datasets import load_iris
    >>> from sklearn.tree import DecisionTreeClassifier
    >>> from sklearn.tree import export_text
    >>> iris = load_iris()
    >>> X = iris['data']
    >>> y = iris['target']
    >>> decision_tree = DecisionTreeClassifier(random_state=0, max_depth=2)
    >>> decision_tree = decision_tree.fit(X, y)
    >>> r = export_text(decision_tree, feature_names=iris['feature_names'])
    >>> print(r)
    |--- petal width (cm) <= 0.80
    |   |--- class: 0
    |--- petal width (cm) >  0.80
    |   |--- petal width (cm) <= 1.75
    |   |   |--- class: 1
    |   |--- petal width (cm) >  1.75
    |   |   |--- class: 2
    """
    tree_ = decision_tree.tree_
    class_names = decision_tree.classes_
    right_child_fmt = "{} {} <= {}\n"
    left_child_fmt = "{} {} >  {}\n"
    truncation_fmt = "{} {}\n"

    if (feature_names is not None and
            len(feature_names) != tree_.n_features):
        raise ValueError("feature_names must contain "
                         "%d elements, got %d" % (tree_.n_features,
                                                  len(feature_names)))

    if spacing <= 0:
        raise ValueError("spacing must be > 0, given %d" % spacing)

    if decimals < 0:
        raise ValueError("decimals must be >= 0, given %d" % decimals)

    if isinstance(decision_tree, DecisionTreeClassifier):
        value_fmt = "{}{} weights: {}\n"
        if not show_weights:
            value_fmt = "{}{}{}\n"
    else:
        value_fmt = "{}{} value: {}\n"

    if feature_names:
        feature_names_ = [feature_names[i] if i != _tree.TREE_UNDEFINED
                          else None for i in tree_.feature]
    else:
        feature_names_ = ["feature_{}".format(i) for i in tree_.feature]

    #export_text.report = ""

    def print_tree_recurse(node, depth, acc):
        #indent = ("|" + (" " * spacing)) * depth
        #indent = indent[:-spacing] + "-" * spacing

        if True:
            #info_fmt = ""
            #info_fmt_left = info_fmt
            #info_fmt_right = info_fmt

            if tree_.feature[node] != _tree.TREE_UNDEFINED:
                rules = []
                name = feature_names_[node]
                threshold = tree_.threshold[node]
                threshold = "{1:.{0}f}".format(decimals, threshold)
                rhs = "(" + right_child_fmt.format("", name, threshold).replace('\n', '').replace('\r', '').strip() + ")"
                #export_text.report += info_fmt_left
                if (len(acc) > 0):
                    rhs = " and " + rhs
                rules.extend(print_tree_recurse(tree_.children_left[node], depth+1, acc + rhs))

                lhs =  "(" + left_child_fmt.format("", name, threshold).replace('\n', '').replace('\r', '').strip() +")"
                if (len(acc) > 0):
                    lhs = " and " + lhs
                #export_text.report += info_fmt_right
                rules.extend(print_tree_recurse(tree_.children_right[node], depth+1, acc + lhs))
                return rules
            else:  # leaf
                value = None
                if tree_.n_outputs == 1:
                   value = tree_.value[node][0]
                else:
                   value = tree_.value[node].T[0]
                class_name = np.argmax(value)

                if (tree_.n_classes[0] != 1 and tree_.n_outputs == 1):
                   class_name = class_names[class_name]
                return [acc + " => Label=" + str(class_name) + " (0/0)"]
        # else:
        #     subtree_depth = _compute_depth(tree_, node)
        #     if subtree_depth == 1:
        #         _add_leaf(value, class_name, indent)
        #     else:
        #         trunc_report = 'truncated branch of depth %d' % subtree_depth
        #         export_text.report += truncation_fmt.format(indent,
        #                                                     trunc_report)

    return print_tree_recurse(0, 1, "")