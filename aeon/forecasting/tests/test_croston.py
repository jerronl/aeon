import numpy as np
import pytest

from aeon.datasets import load_PBS_dataset
from aeon.forecasting.croston import Croston

# test the Croston's Method against the R package


@pytest.mark.parametrize(
    "smoothing, fh, r_forecast",
    [
        (0.1, np.array([10]), 0.8688921),
        (0.5, np.array([5]), 0.6754646),
        (0.05, np.array([15]), 1.405808),
    ],
)
def test_Croston_against_r_implementation(smoothing, fh, r_forecast):
    """
    Testing forecasted values estimated by the R package of the Croston's method
    against the Croston method in aeon.
    R code to generate the hardcoded value for fh=10:
    ('PBS_dataset.csv' contains the data from 'load_PBS_dataset()'):

        PBS_file <- read.csv(file = '/content/PBS_dataset.csv')[,c('Scripts')]
        y <- ts(PBS_file)
        demand=ts(y)
        forecast <- croston(y,h = 10)
    Output:
        0.8688921
    """
    y = load_PBS_dataset()
    forecaster = Croston(smoothing)
    forecaster.fit(y)
    y_pred = forecaster.predict(fh=fh)
    np.testing.assert_almost_equal(y_pred, np.full(len(fh), r_forecast), decimal=5)
