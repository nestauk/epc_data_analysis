# File: getters/easy_plotting.py
"""Functions to help plot and analyse dataframe.

Created May 2021
@author: Julia Suter
Last updated on 13/07/2021
"""

# ---------------------------------------------------------------------------------

# Imports
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

import re

from epc_data_analysis import get_yaml_config, Path, PROJECT_DIR
from typing import Union

import warnings

warnings.simplefilter("ignore", category=UserWarning)

# ---------------------------------------------------------------------------------

# Load config file
epc_data_config = get_yaml_config(
    Path(str(PROJECT_DIR) + "/epc_data_analysis/config/base.yaml")
)

# Where to store figures
FIG_PATH = str(PROJECT_DIR) + epc_data_config["FIGURE_PATH"]


def save_figure(plt, plot_title=None, file_extension=".png", dpi=500):
    """Create filename and save figure.

    Parameters
    ----------

    plt : matplotlib.pyplot
        Plot to save.

    plot_title: str, None, default=None
        Use plot title to generate filename.
        If None, use "figure" as filename.

    file_extension: str, default=".png"
        File extension, file format to save.

    dpi: int, default=500
        Dots per inches (dpi) determines how many pixels the figure comprises.


    Return
    ----------
        None"""

    # Tight layout
    plt.tight_layout()

    # Automatically generate filename
    if plot_title is not None:
        save_filename = plot_title
        save_filename = re.sub(" ", "_", save_filename)

    # Use "figure" as filename as default
    else:
        save_filename = "figure"

    # Save fig
    plt.savefig(FIG_PATH + save_filename + file_extension, dpi=dpi)


def get_readable_tick_labels(plt, ticklabel_type, axis):
    """Get more readable tick labels, e.g. 50k for 50000.

    Parameters
    ----------

    plt : matplotlib.pyplot
        Plot from which to get axes.

    ticklabel_type : {'', 'm', 'k' or '%'}, default=None
        Label type for ticklabel (y-axis or x-axis).

    axis : {'y', 'x'}
        For which axis to update the labels.

    Return
    ---------

    labels : list
        Updated tick labels for x or y axis.

    ax : plt.gca
        Current axes for plt.

    division_int : int
        By which number to divide values to match new tick labels.

    division_type : str
        Same as ticklabel_type, except for None (--> ""),
        representing string to display after updated tick values."""

    # Depending on ticklabel adjust display of numbers
    # e.g. (50000 --> 50k)

    # 1000 --> k
    if ticklabel_type == "k":
        division_type = "k"
        division_int = 1000

    # 1000000 --> m
    elif ticklabel_type == "m":
        division_type = "m"
        division_int = 1000000

    # "" or None --> ""
    elif ticklabel_type == "" or ticklabel_type is None:
        division_type = ""
        division_int = 1

    # % --> %
    elif ticklabel_type == "%":
        division_type = "%"
        division_int = 1

    else:
        raise IOError("Invalid value: ticklabel has to be '', 'm', 'k' or '%'")

    # Get axis and ticks
    ax = plt.gca()

    if axis == "y":
        ticks = ax.get_yticks()
    else:
        ticks = ax.get_xticks()

    # Get updated tick labels
    labels = ["{:.0f}".format(x / division_int) + division_type for x in ticks]

    return labels, ax, division_int, division_type


def plot_subcategory_distribution(
    df,
    category,
    normalize=False,
    color="lightseagreen",
    plot_title=None,
    y_label="",
    x_label="",
    y_ticklabel_type=None,
):
    """Plot distribution of subcategories/values of specific category/feature.

    Parameters
    ----------

    df : pd.DataFrame
        Dataframe to analyse and plot.

    category : str
        Category/column of interest for which distribution is plotted.

    normalise : bool, default=False
        If True, relative numbers (percentage) instead of absolute numbers.

    color : str
        Color of bars in plot.

    y_label : str, default=""
        Label for y-axis.

    x_label : str, default=""
        Label for x-axis.

    y_ticklabel_type : {'', 'm', 'k' or '%'}, default=None
        Label for yticklabel, e.g. 'k' when displaying numbers
        in more compact way for easier readability (50000 --> 50k).

    Return
    ---------
    None"""

    # Get relative numbers (percentage) instead of absolute numbers
    if normalize:

        # Get counts for every category
        category_counts = round(df[category].value_counts(normalize=True) * 100, 2)
        y_ticklabel_type = "%"

    else:
        # Get counts for every category
        category_counts = df[category].value_counts()

    # Plot category counts
    category_counts.plot(kind="bar", color=color)

    # Set plot title
    if plot_title is None:
        plot_title = "Distribution of {}".format(category.lower())
        if normalize:
            plot_title += " (%)"

    # Add titles and labels
    plt.title(plot_title)
    plt.xlabel(x_label)
    plt.xticks(rotation=0)
    plt.ylabel(y_label)

    # Get new yticklabels
    ax = plt.gca()

    yticklabels, ax, division_int, division_type = get_readable_tick_labels(
        plt, y_ticklabel_type, "y"
    )
    ax.set_yticklabels(yticklabels)

    # Adjust ylim in case of ylabel adjustment for easier readiablity (50000 --> 50k)
    highest_count = max(category_counts)

    for i, cty in enumerate(category_counts.values):
        ax.text(
            i,
            cty + highest_count / 80,
            str(round(cty / division_int)) + division_type,
            horizontalalignment="center",
        )

    ax.set_ylim([0.0, int(highest_count + highest_count / 8)])

    # Save figure
    save_figure(plt, plot_title)

    # Show plot
    plt.show()


def plot_feature_by_subcategories(
    df,
    feature_of_interest,
    category,
    subcategory=None,
    plot_title=None,
    y_label="",
    x_label="",
    plot_kind="hist",
):
    """Plot a feature/column by another feature/column's subcategories.
    For example, plot the energy efficiency (feature of interest) on y-axis
    by different tenure types (category) or specific tenure type (subcategory) on x-axis.

    Parameters
    ----------

    df : pd.DataFrame
        Dataframe to analyse and plot.

    feature_of_interest : str
        Feature to plot on y-axis.

    category : str
        Category to plot on x-axis.
        Show all subcategories/values.

    subcategory : str, default=None
        Only plot subcategories/values of given subcategory.

    plot_title : str = None
        Title to display above plot.
        If None, title is created automatically.
        Plot title is also used when saving file.

    y_label : str, default=""
        Label for y-axis.

    x_label : str, default=""
        Label for x-axis

    plot_kind : {"hist", "bar"}, default="hist"
        Type of plot."""

    # Tag for title
    tag = ""

    # Load data for specific subcategory (if given)
    if subcategory is not None:
        df = df.loc[df[category] == subcategory]
        tag = " for " + str(subcategory)

    # Create plot title
    if plot_title is None:
        plot_title = feature_of_interest + tag

    # Plot distribution for feature values/subcategories
    ratings = df[feature_of_interest].value_counts().sort_index()

    # Plot histogram with 30 bins
    if plot_kind == "hist":
        ratings.plot(kind=plot_kind, bins=30, color="lightseagreen")

    # Plot bar plot (or other types)
    else:
        ratings.plot(kind=plot_kind, color="lightseagreen")

    # Describe plot with title and labels
    plt.title(plot_title)
    plt.xticks(rotation=0)
    plt.ylabel(y_label)
    plt.xlabel(x_label)

    # Save figure
    save_figure(plt, plot_title)

    # Show plot
    plt.show()


def plot_subcats_by_other_subcats(
    df,
    feature_1,
    feature_2,
    feature_1_order=None,
    feature_2_order=None,
    plot_title=None,
    y_label="",
    x_label="",
    plot_kind="bar",
    plotting_colors=None,
    y_ticklabel_type=None,
):
    """Plot subcategories of given feature by subcategories of another feature.
    For example, plot and color-code the distribution of heating types (feature 2)
    on the different tenure types (feature 1).

    Parameters
    ----------

    df : pd.DataFrame
        Dataframe to analyse and plot.

    feature_1 : str
        Feature for which subcategories are plotted on x-axis.

    feature_2 : str
        Feature for which distribution is shown split per subcategory
        of feature 1. Feature 2 sbcategories are represented with differnet colors,
        explained with a color legend.

    feature_1_subcat_order : list, None, default=None
        The order in which feature 1 subcategories are displayed.

    feature_2_subcat_order : list, None, default=None
        The order in which feature 2 subcategories are displayed.

    plot_title : str = None
        Title to display above plot.
        If None, title is created automatically.
        Plot title is also used when saving file.

    y_label : str, default=""
        Label for y-axis.

    x_label : str, default=""
        Label for x-axis

    plot_kind : {"hist", "bar"}, default="hist"
        Type of plot.

    plotting_colors : list, str, None, default=None
        Ordered list of colors or color map to use when plotting feature 2.
        If list, use list of colors.
        If str, use corresponding matplotlib color map.
        If None, use default color list.

    y_ticklabel_type : {'', 'm', 'k' or '%'}, default=None
        Label for yticklabel, e.g. 'k' when displaying numbers
        in more compact way for easier readability (50000 --> 50k)."""

    # Remove all samples for which feature 1 or feature 2 is NaN.
    df = df[df[feature_1].notna()]
    df = df[df[feature_2].notna()]

    # Get set of values/subcategories for features.
    feature_1_values = list(set(df[feature_1].sort_index()))
    feature_2_values = list(set(df[feature_2].sort_index()))

    # Set order for feature 1 values/subcategories
    if feature_1_order is not None:
        feature_1_values = feature_1_order

    # Create a feature-bar dict
    feat_bar_dict = {}

    # For every feature 2 value/subcategory, get feature 1 values
    # e.g. for every tenure type, get windows energy efficiencies
    for feat2 in feature_2_values:
        dataset_of_interest = df.loc[df[feature_2] == feat2][feature_1]
        data_of_interest = dataset_of_interest.value_counts()
        feat_bar_dict[feat2] = data_of_interest

    # Save feature 2 subcategories by feature 1 subcategories as dataframe
    subcat_by_subcat = pd.DataFrame(feat_bar_dict, index=feature_1_values)

    # If feature 2 order is given, rearrange
    if feature_2_order is not None:
        subcat_by_subcat = subcat_by_subcat[feature_2_order]

    # If not defined, set default colors for plotting
    if plotting_colors is None:
        plotting_colors = ["green", "greenyellow", "yellow", "orange", "red"]

    # Use given colormap
    if isinstance(plotting_colors, str):
        cmap = plotting_colors
        subcat_by_subcat.plot(kind=plot_kind, cmap=cmap)  # recommended RdYlGn

    # or: use given color list
    elif isinstance(plotting_colors, list):
        subcat_by_subcat.plot(kind=plot_kind, color=plotting_colors)

    else:
        raise IOError("Invalid plotting_colors '{}'.".format(plotting_colors))

    # Get updated yticklabels
    ax = plt.gca()
    yticklabels, ax, _, _ = get_readable_tick_labels(plt, y_ticklabel_type, "y")
    ax.set_yticklabels(yticklabels)

    # Set plot title
    if plot_title is None:
        plot_title = feature_2 + " by " + feature_1

    # Describe plot with title and axes
    plt.title(plot_title)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.xticks(rotation=0)

    # Save figure
    save_figure(plt, plot_title)

    # Show plot
    plt.show()


def plot_correlation(
    df,
    feature_1,
    feature_2,
    with_hist_subplots=True,
    ylim_max=100,
    plot_title=None,
    y_label="",
    x_label="",
):
    """
    Parameters
    ----------
    df : pandas.DataFrame
     Dataframe which holds features for which to plot correlation.

    feature_1 : str
        Feature to plot on x-axis.

    feature_2 : str
        Feature to plot on y-axis.

    with_hist_subplots: bool, default=True
        Plot histogram subplots above and besides correlation plot
        for both features.

    ylim_max : int, default=100
        Limit for y-axis for better readbility

    plot_title : str = None
        Title to display above plot.
        If None, title is created automatically.
        Plot title is also used when saving file.

    y_label : str, default=""
        Label for y-axis.

    x_label : str, default=""
        Label for x-axis"""

    # Set plot title
    tag = " with hist subplots" if with_hist_subplots else ""

    if plot_title is None:
        plot_title = "Correlation " + feature_2 + " by " + feature_1 + tag

    # With subplots with histogram on sides
    if with_hist_subplots:

        # Set figure size
        fig = plt.figure(figsize=(8.5, 6.0))

        # Set GridSpec
        gs = GridSpec(4, 4)

        # Add scatter subplot
        ax_scatter = fig.add_subplot(gs[1:4, 0:3])

        # Set title and labels
        plt.title(plot_title)
        plt.xlabel(feature_1)
        plt.ylabel(feature_2)

        # Set Histogram subplot for feature 1
        ax_hist_x = fig.add_subplot(gs[0, 0:3], title=feature_1 + " Histogram")

        # Set Histogram subplot for feature 2
        ax_hist_y = fig.add_subplot(gs[1:4, 3])

        # Adjust position of label
        ax_hist_y.yaxis.set_label_position("right")
        ax_hist_y.set_ylabel(feature_2 + " Histogram", rotation=270, va="bottom")

        # Scatter plot for feature 1 and feature 2
        ax_scatter.scatter(df[feature_1], df[feature_2], alpha=0.1, s=5)

        # Add histogram for feature 1 and feature 2
        ax_hist_x.hist(df[feature_1])
        ax_hist_y.hist(df[feature_2], orientation="horizontal")

        # Set ylim max for all subplots with feature 1
        ax_hist_y.set_ylim([0.0, ylim_max])
        ax_scatter.set_ylim([0.0, ylim_max])

    else:

        # Create scatter flot with feature 1 and feature 2
        plt.scatter(df[feature_1], df[feature_2], alpha=0.1, s=2)

        # Set ylim
        ax = plt.gca()
        ax.set_ylim([0.0, ylim_max])

        # Set labels
        plt.xlabel(feature_1)  # or x_label
        plt.ylabel(feature_2)  # or y_label

    # Save figure
    save_figure(plt, plot_title)

    # Show plot
    plt.show()
