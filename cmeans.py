import numpy as np
import skfuzzy as fuzz
from scipy.spatial.distance import cdist


def eta():
    return 1


def update_clusters(x, u, m):
    um = u ** m
    v = um.dot(x.T) / np.atleast_2d(um.sum(axis=1)).T
    return v


def _fcm_criterion(x, v, n, m, metric):

    d = cdist(x.T, v, metric=metric).T

    # Sanitize Distances (Avoid Zeroes)
    d = np.fmax(d, np.finfo(x.dtype).eps)

    exp = -2. / (m - 1)
    d = d ** exp

    u = d / np.sum(d, axis=0, keepdims=1)

    return u


def _pcm_criterion(x, v, n, m, metric):

    d = cdist(x.T, v, metric=metric).T

    d = np.fmax(d, np.finfo(x.dtype).eps)

    d = d ** 2
    d /= n

    exp = 1. / (m - 1)
    d = d ** exp
    u = 1. / (1. + d)

    return u


def _cmeans(x, c, m, e, max_iterations, criterion_function, metric="euclidean", v0=None):
    """

    # Parameters

    `x` 2D array, size (S, N)  
        Data to be clustered. N is the number of data sets;
        S is the number of features within each sample vector. 

    `c` int  
        Number of clusters

    `m` float, optional  
        Fuzzifier

    `e` float, optional  
        Convergence threshold

    `max_iterations` int, optional  
        Maximum number of iterations

    `v0` array-like, optional  
        Initial cluster centers

    # Returns

    `v` 2D Array, size (S, c)  
        Cluster centers

    `u` 2D Array (S, N)  
        Final partitioned matrix

    `u0` 2D Array (S, N)  
        Initial partition matrix

    `d` 2D Array (S, N)  
        Distance Matrix

    `t` int  
        Number of iterations run

    `f` float  
        Final fuzzy partition coeffiient

    """

    if not x.any() or len(x) < 1 or len(x[0]) < 1:
        print("Error: Data is in incorrect format")
        return

    # Num Features, Datapoints
    S, N = x.shape

    if not c or c <= 0:
        print("Error: Number of clusters must be at least 1")

    if not m or m <= 1:
        print("Error: Fuzzifier must be greater than 1")
        return

    # Initialize the cluster centers
    # If the user doesn't provide their own starting points,
    if v0 is None or len(v0) != c:
        # Pick random values from dataset
        xt = x.T
        v0 = xt[np.random.choice(xt.shape[0], c, replace=False), :]

    # List of all cluster centers (Bookkeeping)
    v = np.zeros((max_iterations, c, S))
    v[0] = np.array(v0)

    # Membership Matrix Each Data Point in eah cluster
    u = np.zeros((max_iterations, c, N))

    n = eta()

    # Number of Iterations
    t = 0

    while t < max_iterations - 1:

        u[t] = criterion_function(x, v[t], n, m, metric)
        v[t + 1] = update_clusters(x, u[t], m)

        # Stopping Criteria
        if np.linalg.norm(v[t + 1] - v[t]) < e:
            break

        t += 1

    return v[t], u[t - 1], u[0], None, t, None

# Public Facing Functions


def pcm(x, c, m, e, max_iterations, metric="euclidean", v0=None):
    return _cmeans(x, c, m, e, max_iterations, _pcm_criterion, metric, v0)


def fcm(x, c, m, e, max_iterations, metric="euclidean", v0=None):
    return _cmeans(x, c, m, e, max_iterations, _fcm_criterion, metric, v0)