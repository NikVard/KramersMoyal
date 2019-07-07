import numpy as np
from scipy.signal import convolve
from .binning import histogramdd


def kmc_kernel_estimator(timeseries: np.ndarray, bins: np.ndarray,
                         kernel: callable, bw: float,
                         powers: np.ndarray):
    """
    Estimates Kramers-Moyal coefficients from a timeseries using a kernel
    estimator method.

    Parameters
    ----------
    timeseries: np.ndarray
        The D-dimensional timeseries (N, D)

    bins: np.ndarray
        The number of bins for each dimension

    kernel: callable
        Kernel used to calculate the Kramers-Moyal coefficients

    bw: float
        Desired bandwidth of the kernel

    Returns
    -------
    kmc: np.ndarray
      The calculated Kramers-Moyal coefficients

    edges: np.ndarray
          The bin edges of the calculated Kramers-Moyal coefficients
    """

    def cartesian_product(arrays: np.ndarray):
        # Taken from https://stackoverflow.com/questions/11144513
        la = len(arrays)
        arr = np.empty([len(a) for a in arrays] + [la], dtype=np.float64)
        for i, a in enumerate(np.ix_(*arrays)):
            arr[..., i] = a
        return arr.reshape(-1, la)

    # Calculate derivatives and its powers
    grads = np.diff(timeseries, axis=0)
    weights = np.prod(np.power(grads[..., None], powers), axis=1)

    # Get weighted histogram
    hist, edges = histogramdd(timeseries[1:, ...], bins=bins,
                              weights=weights, density=True)

    # Generate kernel
    mesh = cartesian_product(edges)
    kernel_ = kernel(mesh, bw=bw).reshape(*(edge.size for edge in edges))
    kernel_ /= np.sum(kernel_)

    kmc = list()
    # Convolve with kernel for all powers
    for p in range(powers.shape[1]):
        kmc.append(convolve(kernel_, hist[..., p], mode='same'))

    return np.stack(kmc, axis=-1), edges
