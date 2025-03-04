"""Rotation Forest test code."""
import numpy as np

from aeon.classification.sklearn import RotationForestClassifier
from aeon.datasets import load_unit_test


def test_contracted_rotf():
    """Test of RotF contracting and train estimate on unit test data."""
    # load unit test data
    X_train, y_train = load_unit_test(split="train", return_type="numpy2d")

    rotf = RotationForestClassifier(
        time_limit_in_minutes=5,
        contract_max_n_estimators=5,
        save_transformed_data=True,
        random_state=0,
    )
    rotf.fit(X_train, y_train)

    assert len(rotf.estimators_) > 0

    # test train estimate
    train_proba = rotf._get_train_probs(X_train, y_train)
    assert isinstance(train_proba, np.ndarray)
    assert train_proba.shape == (len(X_train), 2)
    np.testing.assert_almost_equal(train_proba.sum(axis=1), 1, decimal=4)
