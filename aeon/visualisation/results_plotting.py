"""Plotting tools for estimator results."""

__all__ = [
    "plot_boxplot_median",
    "plot_scatter_predictions",
    "plot_scatter",
    "plot_multi_comparison_matrix",
]

__author__ = ["dguijo"]

import warnings

import numpy as np

from aeon.utils.validation._dependencies import _check_soft_dependencies


def plot_boxplot_median(
    results,
    labels,
    plot_type="violin",
    outliers=True,
    title=None,
    y_min=None,
    y_max=None,
):
    """
    Plot a box plot of distributions from the median.

    Each row of results is an independent experiment for each element in names. This
    function works out the deviation from the median for each row, then plots a
    boxplot variant of each column.

    Parameters
    ----------
    results: np.array
        Scores (either accuracies or errors) of dataset x strategy
    labels: list of estimators
        List with names of the estimators
    plot_type: str, default = "violin"
        This function can create four sort of distribution plots: "violin", "swarm",
        "boxplot" or "strip". "violin" plot features a kernel density estimation of the
        underlying distribution. "swarm" draws a categorical scatterplot with points
        adjusted to be non-overlapping. "strip" draws a categorical scatterplot using
        jitter to reduce overplotting.
    outliers: bool, default = True
        Only applies when plot_type is "boxplot".
    title: str, default = None
        Title to be shown in the top of the plot.
    y_min: float, default = None
        Min value for the y_axis of the plot.
    y_max: float, default = None
        Max value for the y_axis of the plot.

    Returns
    -------
    fig: matplotlib.figure
        Figure created.

    Example
    -------
    >>> from aeon.visualisation.results_plotting import plot_boxplot_median
    >>> from aeon.benchmarking.results_loaders import get_estimator_results_as_array
    >>> methods = ["IT", "WEASEL-Dilation", "HIVECOTE2", "FreshPRINCE"]
    >>> results = get_estimator_results_as_array(estimators=methods) # doctest: +SKIP
    >>> plot = plot_boxplot_median(results[0], methods) # doctest: +SKIP
    >>> plot.show() # doctest: +SKIP
    >>> plot.savefig("boxplot.pdf") # doctest: +SKIP
    """
    _check_soft_dependencies("matplotlib", "seaborn")
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Obtains deviation from median for each independent experiment.
    medians = np.median(results, axis=1)
    sum_results_medians = results + medians[:, np.newaxis]

    deviation_from_median = np.divide(
        results,
        sum_results_medians,
        out=np.zeros_like(results),
        where=sum_results_medians != 0,
    )

    fig = plt.figure(figsize=(10, 6), layout="tight")

    # Plots violin or boxplots
    if plot_type == "violin":
        plot = sns.violinplot(
            data=deviation_from_median,
            linewidth=0.2,
            palette="pastel",
            bw=0.3,
        )
    elif plot_type == "boxplot":
        plot = sns.boxplot(
            data=deviation_from_median,
            palette="pastel",
            showfliers=outliers,
        )
    elif plot_type == "swarm":
        plot = sns.swarmplot(
            data=deviation_from_median,
            linewidth=0.2,
            palette="pastel",
        )
    elif plot_type == "strip":
        plot = sns.stripplot(
            data=deviation_from_median,
            linewidth=0.2,
            palette="pastel",
        )
    else:
        raise ValueError(
            "plot_type must be one of 'violin', 'boxplot', 'swarm' or 'strip'."
        )

    # Modifying limits for y-axis.
    if y_min is None and (
        (plot_type == "boxplot" and outliers) or (plot_type != "boxplot")
    ):
        y_min = np.around(np.amin(deviation_from_median) - 0.05, 2)

    if y_max is None and (
        (plot_type == "boxplot" and outliers) or (plot_type != "boxplot")
    ):
        y_max = np.around(np.amax(deviation_from_median) + 0.05, 2)

    plot.set_ylim(y_min, y_max)

    # Setting labels for x-axis. Rotate only if labels are too long.
    plot.set_xticks(np.arange(len(labels)))
    label_lengths = np.array([len(i) for i in labels])
    if (sum(label_lengths) > 40) or (max(label_lengths[:-1] + label_lengths[1:]) > 20):
        plot.set_xticklabels(labels, rotation=45, ha="right")
    else:
        plot.set_xticklabels(labels)

    # Setting title if provided.
    if title is not None:
        plot.set_title(rf"{title}")

    return fig


def plot_scatter_predictions(
    y,
    y_pred,
    title=None,
):
    """Plot a scatter that compares actual and predicted values for a given dataset.

    This scatter is generally useful for plotting predictions for Time Series Extrinsic
    Regression approaches, since the output is continuous. In case of Time Series
    Classification it will be similar to a confusion matrix.

    Parameters
    ----------
    y: np.array
        Actual values.
    y_pred: np.array
        Predicted values.
    title: str, default = None
        Title to be shown in the top of the plot.

    Returns
    -------
    fig: matplotlib.figure
        Figure created.

    Example
    -------
    >>> from aeon.visualisation.results_plotting import plot_scatter_predictions
    >>> from aeon.datasets import load_covid_3month
    >>> from aeon.regression.feature_based import FreshPRINCERegressor  # doctest: +SKIP
    >>> X_train, y_train = load_covid_3month(split="train")
    >>> X_test, y_test = load_covid_3month(split="test")
    >>> fp = FreshPRINCERegressor(n_estimators=10)  # doctest: +SKIP
    >>> fp.fit(X_train, y_train)  # doctest: +SKIP
    >>> y_pred_fp = fp.predict(X_test)  # doctest: +SKIP
    >>> plot = plot_scatter_predictions(y_test, y_pred_fp, title="FP-Covid3Month")\
        # doctest: +SKIP
    >>> plot.show()  # doctest: +SKIP
    >>> plot.savefig("scatterplot_predictions.pdf")\
        # doctest: +SKIP
    """
    _check_soft_dependencies("matplotlib", "seaborn")
    import matplotlib.pyplot as plt
    import seaborn as sns

    fig = plt.figure(figsize=(10, 6), layout="tight")
    min_value = min(y.min(), y_pred.min()) * 0.97
    max_value = max(y.max(), y_pred.max()) * 1.03

    p_x, p_y = [min_value, max_value], [min_value, max_value]
    plt.plot(p_x, p_y, color="black", alpha=0.5, zorder=1)

    plot = sns.scatterplot(
        x=y,
        y=y_pred,
        zorder=2,
        color="wheat",
        edgecolor="black",
        lw=2,
    )

    # Setting x and y limits
    plot.set_ylim(min_value, max_value)
    plot.set_xlim(min_value, max_value)

    # Setting labels for x and y axis
    plot.set_xlabel("Actual values")
    plot.set_ylabel("Predicted values")

    if title is not None:
        plot.set_title(rf"{title}")

    return fig


def plot_scatter(
    results,
    method_A,
    method_B,
    metric="accuracy",
    lower_better=False,
    statistic_tests=True,
    title=None,
    figsize=(10, 6),
    color_palette="tab10",
):
    """Plot a scatter that compares datasets' results achieved by two methods.

    Parameters
    ----------
    results : np.array
        Scores (either accuracies or errors) of dataset x strategy.
    method_A : str
        Method name of the first approach.
    method_B : str
        Method name of the second approach.
    metric : str, default = "accuracy"
        Metric to be used for the comparison.
    lower_better : bool, default = False
        If True, lower values are considered better, i.e. errors.
    statistic_tests : bool, default = True
        If True, paired ttest and wilcoxon p-values are shown in the bottom of the plot.
    title : str, default = None
        Title to be shown in the top of the plot.
    figsize : tuple, default = (10, 6)
        Size of the figure.
    color_palette : str, default = "tab10"
        Color palette to be used for the plot.

    Returns
    -------
    fig: matplotlib.figure
        Figure created.

    Example
    -------
    >>> from aeon.visualisation.results_plotting import plot_scatter
    >>> from aeon.benchmarking.results_loaders import get_estimator_results_as_array
    >>> methods = ["InceptionTimeClassifier", "WEASEL-Dilation"]
    >>> results = get_estimator_results_as_array(estimators=methods)
    >>> plot = plot_scatter(results[0], methods[0], methods[1])  # doctest: +SKIP
    >>> plot.show()  # doctest: +SKIP
    >>> plot.savefig("scatterplot.pdf")  # doctest: +SKIP
    """
    _check_soft_dependencies("matplotlib", "seaborn")
    import matplotlib.pyplot as plt
    import seaborn as sns
    from matplotlib.offsetbox import AnchoredText

    palette = sns.color_palette(color_palette, n_colors=3)

    if results.shape[1] != 2:
        raise ValueError("Please provide a results array only for 2 methods.")

    if statistic_tests:
        fig, ax = plt.subplots(figsize=figsize, gridspec_kw=dict(bottom=0.2))
    else:
        fig, ax = plt.subplots(figsize=figsize)

    min_value = max(results.min() * 0.97, 0)
    max_value = results.max() * 1.03

    if metric in ["accuracy", "R2", "CCR", "AUC", "F1", "Kappa", "AUPRC"]:
        max_value = min(max_value, 1.001)
        if lower_better:
            raise ValueError("lower_better must be False when metric is 'accuracy'.")
    elif metric in ["error", "RMSE", "MSE", "MAE", "AMAE", "MAPE", "SMAPE"]:
        if not lower_better:
            raise ValueError("lower_better must be True when metric is 'error'.")

    x, y = [min_value, max_value], [min_value, max_value]
    plt.plot(x, y, color="black", alpha=0.5, zorder=1)

    # Choose the appropriate order for the methods. Best method is shown in the y-axis.
    if (results[:, 0].mean() <= results[:, 1].mean() and not lower_better) or (
        results[:, 0].mean() >= results[:, 1].mean() and lower_better
    ):
        first = results[:, 1]
        first_method = method_B
        second = results[:, 0]
        second_method = method_A
    else:
        first = results[:, 0]
        first_method = method_A
        second = results[:, 1]
        second_method = method_B

    differences = [
        0 if i - j == 0 else (1 if i - j > 0 else -1) for i, j in zip(first, second)
    ]
    # This line helps displaying ties on top of losses and wins, as in general there
    # are less number of ties than wins/losses.
    differences, first, second = map(
        np.array,
        zip(*sorted(zip(differences, first, second), key=lambda x: -abs(x[0]))),
    )

    first_median = np.median(first)
    second_median = np.median(second)

    plot = sns.scatterplot(
        x=second,
        y=first,
        hue=differences,
        hue_order=[1, 0, -1] if lower_better else [-1, 0, 1],
        palette=palette,
        zorder=2,
    )

    # Draw the median value per method as a dashed line from 0 to the median value.
    plt.plot(
        [first_median, min_value] if not lower_better else [first_median, max_value],
        [first_median, first_median],
        linestyle="--",
        color=palette[2],
        zorder=3,
    )

    plt.plot(
        [second_median, second_median],
        [second_median, min_value] if not lower_better else [second_median, max_value],
        linestyle="--",
        color=palette[0],
        zorder=3,
    )

    legend_median = AnchoredText(
        "*Dashed lines represent the median",
        loc="lower right" if lower_better else "upper right",
        prop=dict(size=8),
        bbox_to_anchor=(1.01, 1.07 if lower_better else -0.07),
        bbox_transform=ax.transAxes,
    )
    ax.add_artist(legend_median)

    # Compute the W, T, and L per methods
    if lower_better:
        differences = [-i for i in differences]
        ax = plt.gca()
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position("top")
        ax.spines["top"].set_visible(True)
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position("right")
        ax.spines["right"].set_visible(True)

    # Setting labels for x and y axis
    plot.set_ylabel(f"{first_method} {metric}\n(mean: {first.mean():.4f})", fontsize=13)
    plot.set_xlabel(
        f"{second_method} {metric}\n(mean: {second.mean():.4f})", fontsize=13
    )

    wins_A = losses_B = sum(i == 1 for i in differences)
    ties_A = ties_B = sum(i == 0 for i in differences)
    losses_A = wins_B = sum(i == -1 for i in differences)

    # Setting x and y limits
    plot.set_ylim(min_value, max_value)
    plot.set_xlim(min_value, max_value)

    # Remove legend
    plot.get_legend().remove()

    # Setting text with W, T and L for each method
    anc = AnchoredText(
        f"{first_method} wins here\n[{wins_A}W, {ties_A}T, {losses_A}L]",
        loc="upper left" if not lower_better else "lower right",
        frameon=True,
        prop=dict(
            color=palette[2],
            fontweight="bold",
            fontsize=13,
            ha="center",
        ),
    )
    anc.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    anc.patch.set_color("wheat")
    anc.patch.set_edgecolor("black")
    anc.patch.set_alpha(0.5)
    ax.add_artist(anc)

    anc = AnchoredText(
        f"{second_method} wins here\n[{wins_B}W, {ties_B}T, {losses_B}L]",
        loc="lower right" if not lower_better else "upper left",
        frameon=True,
        prop=dict(
            color=palette[0],
            fontweight="bold",
            fontsize=13,
            ha="center",
        ),
    )
    anc.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    anc.patch.set_color("wheat")
    anc.patch.set_edgecolor("black")
    anc.patch.set_alpha(0.5)
    ax.add_artist(anc)

    # Setting title if provided.
    if title is not None:
        plot.set_title(rf"{title}", fontsize=16)

    # Adding p-value if desired.
    if statistic_tests:
        if np.all(results[:, 0] == results[:, 1]):
            # raise warning
            warnings.warn(
                f"Estimators {method_A} and {method_B} have the same performance"
                "on all datasets. This may cause problems when forming cliques.",
                stacklevel=2,
            )

            p_value_t = 1
            p_value_w = 1

        else:
            from scipy.stats import ttest_rel, wilcoxon

            p_value_t = ttest_rel(
                first,
                second,
                alternative="less" if lower_better else "greater",
            )[1]

            p_value_w = wilcoxon(
                first,
                second,
                zero_method="wilcox",
                alternative="less" if lower_better else "greater",
            )[1]

        ttes = f"Paired t-test for equality of means, p-value={p_value_t:.3f}"
        wil = f"Wilcoxon test for equality of medians, p-value={p_value_w:.3f}"

        plt.figtext(
            0.5,
            0.03 if not lower_better else 0.13,
            f"{wil}\n{ttes}",
            fontsize=10,
            wrap=True,
            horizontalalignment="center",
            bbox=dict(
                facecolor="wheat",
                edgecolor="black",
                boxstyle="round,pad=0.5",
                alpha=0.5,
            ),
        )

    fig.tight_layout()
    return fig


def plot_multi_comparison_matrix():
    """
    Wrap for the Multi Comparison Matrix presented by Ismail-Fawaz et al. [1].

    Parameters
    ----------
    TODO: Add parameters

    Returns
    -------
    TODO: Add returns

    Example
    -------
    TODO: Add example

    References
    ----------
    [1] Ismail-Fawaz, A., Dempster, A., Tan, C. W., Herrmann, M., Miller, L.,
        Schmidt, D. F., ... & Webb, G. I. (2023). An Approach to Multiple Comparison
        Benchmark Evaluations that is Stable Under Manipulation of the Comparate Set.
        arXiv preprint arXiv:2305.11921.
    """
    pass
