"""

@author: joonas
"""

import numpy as np

def fisher_calculation(X, y):
    # Calculates fisher score
    """
    Calculate fisher score
    https://papers.nips.cc/paper/2909-laplacian-score-for-feature-selection.pdf
    :param data:
    :return:
    """

    #print(X[0,:])
    # Find mean and variance for full dataset

    #for i in range(X.shape[1]):
    #    print(X[:,i].dtype)
    feature_mean = np.mean(X, axis=0)
    #feature_var = np.var(X, axis=0)

    # Find variance for each class, maybe do normalization as well??
    # ID's for
    n_positive = (y == 1).sum()
    n_negative = (y == 0).sum()

    # Split positive and neg samples
    pos_samples = X[y == 1]
    neg_samples = X[y == 0]

    # get variance and mean for positive and negative labels for all features
    pos_variances = np.var(pos_samples, axis=0)
    neg_variances = np.var(neg_samples, axis=0)

    # get means
    pos_means = np.mean(pos_samples, axis=0)
    neg_means = np.mean(neg_samples, axis=0)

    #print(pos_variances)
    #print(neg_variances)

    # Calculate Fisher score for each feature
    Fr = np.zeros(X.shape[1])

    for i in range(X.shape[1]):
        Fr[i] = n_positive * np.power(pos_means[i] - feature_mean[i], 2) + \
                n_negative * np.power(neg_means[i] - feature_mean[i], 2)

        compute = (n_positive * pos_variances[i] + n_negative * neg_variances[i])
        if (compute == 0):
            print("WARNING: Division by zero (avoiding it by returning zero)")
            Fr[i] = 0
        else:
            Fr[i] /= (n_positive * pos_variances[i] + n_negative * neg_variances[i])

    return Fr