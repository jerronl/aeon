"""Unit tests for (dunder) composition functionality attached to the base class."""

__author__ = ["fkiraly"]
__all__ = []

from sklearn.preprocessing import StandardScaler

from aeon.classification import DummyClassifier
from aeon.classification.compose import ClassifierPipeline
from aeon.classification.convolution_based import RocketClassifier
from aeon.transformations.collection.pad import PaddingTransformer
from aeon.transformations.exponent import ExponentTransformer
from aeon.transformations.impute import Imputer
from aeon.utils._testing.collection import make_nested_dataframe_data
from aeon.utils._testing.estimator_checks import _assert_array_almost_equal


def test_dunder_mul():
    """Test the mul dunder method."""
    RAND_SEED = 42
    X, y = make_nested_dataframe_data(
        n_cases=10, n_timepoints=20, random_state=RAND_SEED
    )

    X_test, _ = make_nested_dataframe_data(
        n_cases=10, n_timepoints=20, random_state=RAND_SEED
    )

    t1 = ExponentTransformer(power=4)
    t2 = ExponentTransformer(power=0.25)

    c = DummyClassifier()
    t12c_1 = t1 * (t2 * c)
    t12c_2 = (t1 * t2) * c
    t12c_3 = t1 * t2 * c

    assert isinstance(t12c_1, ClassifierPipeline)
    assert isinstance(t12c_2, ClassifierPipeline)
    assert isinstance(t12c_3, ClassifierPipeline)

    y_pred = c.fit(X, y).predict(X_test)

    _assert_array_almost_equal(y_pred, t12c_1.fit(X, y).predict(X_test))
    _assert_array_almost_equal(y_pred, t12c_2.fit(X, y).predict(X_test))
    _assert_array_almost_equal(y_pred, t12c_3.fit(X, y).predict(X_test))


def test_mul_sklearn_autoadapt():
    """Test auto-adapter for sklearn in mul."""
    RAND_SEED = 42
    X, y = make_nested_dataframe_data(
        n_cases=10, n_timepoints=20, random_state=RAND_SEED
    )

    X_test, _ = make_nested_dataframe_data(
        n_cases=10, n_timepoints=20, random_state=RAND_SEED
    )
    t1 = ExponentTransformer(power=2)
    t2 = StandardScaler()
    c = DummyClassifier()

    t12c_1 = t1 * (t2 * c)
    t12c_2 = (t1 * t2) * c
    t12c_3 = t1 * t2 * c

    assert isinstance(t12c_1, ClassifierPipeline)
    assert isinstance(t12c_2, ClassifierPipeline)
    assert isinstance(t12c_3, ClassifierPipeline)

    y_pred = t12c_1.fit(X, y).predict(X_test)

    _assert_array_almost_equal(y_pred, t12c_2.fit(X, y).predict(X_test))
    _assert_array_almost_equal(y_pred, t12c_3.fit(X, y).predict(X_test))


def test_missing_unequal_tag_inference():
    """Test that ClassifierPipeline infers missing/unequal tags correctly."""
    c = RocketClassifier(num_kernels=100)
    c1 = ExponentTransformer() * PaddingTransformer() * ExponentTransformer() * c
    c2 = ExponentTransformer() * ExponentTransformer() * c
    c3 = Imputer() * ExponentTransformer() * c
    c4 = ExponentTransformer() * Imputer() * c

    assert c1.get_tag("capability:unequal_length")
    assert not c2.get_tag("capability:unequal_length")
    assert c3.get_tag("capability:missing_values")
    assert not c4.get_tag("capability:missing_values")
