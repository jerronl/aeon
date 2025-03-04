"""
Implements Baxter-King bandpass filter transformation.

Please see the original library
(https://github.com/statsmodels/statsmodels/blob/main/statsmodels/tsa/filters/bk_filter.py)
"""

__author__ = ["klam-data", "pyyim", "mgorlin"]
__all__ = ["BKFilter"]


import numpy as np
import pandas as pd

from aeon.transformations.base import BaseTransformer


class BKFilter(BaseTransformer):
    """Filter a times series using the Baxter-King filter.

    This is a wrapper around statsmodels' bkfilter function
    (see 'sm.tsa.filters.bk_filter.bkfilter').

    The Baxter-King filter is intended for economic and econometric time series
    data and deals with the periodicity of the business cycle. Applying their
    band-pass filter to a series will produce a new series that does not contain
    fluctuations at a higher or lower frequency than those of the business cycle.
    Baxter-King follow Burns and Mitchell's work on business cycles, which suggests
    that U.S. business cycles typically last from 1.5 to 8 years.

    Parameters
    ----------
    low : float
        Minimum period for oscillations. Baxter and King recommend a value of 6
        for quarterly data and 1.5 for annual data.

    high : float
        Maximum period for oscillations. BK recommend 32 for U.S. business cycle
        quarterly data and 8 for annual data.

    K : int
        Lead-lag length of the filter. Baxter and King suggest a truncation
        length of 12 for quarterly data and 3 for annual data.

    Notes
    -----
    Returns a centered weighted moving average of the original series.

    References
    ----------
    Baxter, M. and R. G. King. "Measuring Business Cycles: Approximate
        Band-Pass Filters for Economic Time Series." *Review of Economics and
        Statistics*, 1999, 81(4), 575-593.

    Examples
    --------
    >>> from aeon.transformations.bkfilter import BKFilter # doctest: +SKIP
    >>> import pandas as pd # doctest: +SKIP
    >>> import statsmodels.api as sm # doctest: +SKIP
    >>> dta = sm.datasets.macrodata.load_pandas().data # doctest: +SKIP
    >>> index = pd.date_range(start='1959Q1', end='2009Q4', freq='Q') # doctest: +SKIP
    >>> dta.set_index(index, inplace=True) # doctest: +SKIP
    >>> bk = BKFilter(6, 24, 12) # doctest: +SKIP
    >>> cycles = bk.fit_transform(X=dta[['realinv']]) # doctest: +SKIP
    """

    _tags = {
        "input_data_type": "Series",
        # what is the abstract type of X: Series, or Panel
        "output_data_type": "Series",
        # what abstract type is returned: Primitives, Series, Panel
        "instancewise": True,
        "univariate-only": False,
        "X_inner_type": "np.ndarray",
        "y_inner_type": "None",
        "enforce_index_type": [pd.RangeIndex],
        "fit_is_empty": True,
        "transform-returns-same-time-index": False,
        "capability:unequal_length": True,
        "capability:missing_values": False,
        "remember_data": False,
        "python_dependencies": "statsmodels",
    }

    def __init__(
        self,
        low=6,
        high=32,
        K=12,
    ):
        self.low = low
        self.high = high
        self.K = K
        super(BKFilter, self).__init__()

    def _transform(self, X, y=None):
        """Transform X and return a transformed version.

        private _transform containing core logic, called from transform

        Parameters
        ----------
        X : array_like
        A 1 or 2d ndarray. If 2d, variables are assumed to be in columns.

        Returns
        -------
        transformed cyclical version of X
        """
        from scipy.signal import fftconvolve
        from statsmodels.tools.validation import PandasWrapper, array_like

        pw = PandasWrapper(X)
        X = array_like(X, "X", maxdim=2)
        omega_1 = 2.0 * np.pi / self.high
        omega_2 = 2.0 * np.pi / self.low
        bweights = np.zeros(2 * self.K + 1)
        bweights[self.K] = (omega_2 - omega_1) / np.pi
        j = np.arange(1, int(self.K) + 1)
        weights = 1 / (np.pi * j) * (np.sin(omega_2 * j) - np.sin(omega_1 * j))
        bweights[self.K + j] = weights
        bweights[: self.K] = weights[::-1]
        bweights -= bweights.mean()
        if X.ndim == 2:
            bweights = bweights[:, None]
        X = fftconvolve(X, bweights, mode="valid")

        return pw.wrap(X, append="cycle", trim_start=self.K, trim_end=self.K)

    @classmethod
    def get_test_params(cls, parameter_set="default"):
        """Return testing parameter settings for the estimator.

        Parameters
        ----------
        parameter_set : str, default="default"
            Name of the set of test parameters to return, for use in tests. If no
            special parameters are defined for a value, will return `"default"` set.
            There are currently no reserved values for transformers.

        Returns
        -------
        params : dict or list of dict, default = {}
            Parameters to create testing instances of the class
            Each dict are parameters to construct an "interesting" test instance, i.e.,
            `MyClass(**params)` or `MyClass(**params[i])` creates a valid test instance.
            `create_test_instance` uses the first (or only) dictionary in `params`
        """
        params = {"low": 6, "high": 24, "K": 12}
        return params
