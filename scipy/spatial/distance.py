import numpy as np

def cdist(A, B, metric='euclidean'):
    A = np.asarray(A)
    B = np.asarray(B)
    if metric == 'euclidean' or metric is None:
        # compute pairwise euclidean distances
        if A.ndim == 1:
            A = A.reshape(1, -1)
        if B.ndim == 1:
            B = B.reshape(1, -1)
        diff = A[:, None, :] - B[None, :, :]
        dist = np.sqrt(np.sum(diff**2, axis=2))
        return dist
    else:
        return cdist(A, B, metric='euclidean')
