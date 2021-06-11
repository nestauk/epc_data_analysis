import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from typing import Union

from epc_data_analysis import get_yaml_config, Path, PROJECT_DIR
from epc_data_analysis.analysis.notebooks.notebook_utils import my_widgets

import warnings

warnings.simplefilter("ignore", category=UserWarning)


# Load config file
epc_data_config = get_yaml_config(
    Path(str(PROJECT_DIR) + "/epc_data_analysis/config/base.yaml")
)
FIG_PATH = str(PROJECT_DIR) + epc_data_config["FIGURE_PATH"]


def plot_distribution_by_category(
    df: pd.DataFrame,
    category: str,
    normalize: bool = False,
    color: str = "lightseagreen",
    plot_title: str = None,
    save_filename: Union[str, None] = "",
    y_label: str = "",
    x_label: str = "",
    y_ticklabel_type: str = None,
):

    # print("Total items:", df.shape[0])

    if normalize:
        category_counts = round(df[category].value_counts(normalize=True) * 100, 2)
        y_ticklabel_type = "%"
    else:
        category_counts = df[category].value_counts()

    category_counts.plot(kind="bar", color=color)

    if plot_title is None:
        plot_title = "Distribution of {}".format(category.lower())
        if normalize:
            plot_title += " (%)"

    plt.title(plot_title)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.xticks(rotation=0)

    ax = plt.gca()

    if y_ticklabel_type == "k":
        division_type = "k"
        division_int = 1000

    elif y_ticklabel_type == "m":
        division_type = "m"
        division_int = 1000000

    elif y_ticklabel_type == "" or y_ticklabel_type is None:
        division_type = ""
        division_int = 1

    elif y_ticklabel_type == "%":
        division_type = "%"
        division_int = 1

    else:
        raise IOError("Invalid value: y_ticklabel has to be '', 'm', or 'k'")

    ylabels = [
        "{:.0f}".format(x / division_int) + division_type for x in ax.get_yticks()
    ]

    ax.set_yticklabels(ylabels)

    highest_count = max([cty for cty in category_counts.values])

    for i, cty in enumerate(category_counts.values):
        ax.text(
            i,
            cty + highest_count / 80,
            str(round(cty / division_int)) + division_type,
            horizontalalignment="center",
        )

    ax.set_ylim([0.0, int(highest_count + highest_count / 8)])

    plt.tight_layout()

    if save_filename is not None:
        if save_filename == "":
            save_filename = plot_title

        plt.savefig(FIG_PATH + save_filename + ".png", dpi=300)

    plt.show()


def plot_feature_by_subcategories(
    df: pd.DataFrame,
    feature_of_interest: str,
    category: str,
    subcategory: str,
    plot_title: str = None,
    y_label: str = "",
    x_label: str = "",
    save_filename: Union[str, None] = "",
    plot_kind: str = "hist",
):

    """Plot current and potential energy effiency for different tenure types."""

    tag = ""

    if subcategory is not None:
        df = df.loc[df[category] == subcategory]
        tag = " for " + str(subcategory)

    if plot_title is None:
        plot_title = feature_of_interest + tag

    # Plot current energy efficiency
    ratings = df[feature_of_interest].value_counts().sort_index()

    if plot_kind == "hist":
        ratings.plot(kind=plot_kind, bins=30, color="lightseagreen")
    else:
        ratings.plot(kind=plot_kind, color="lightseagreen")

    plt.title(plot_title)
    plt.xticks(rotation=0)

    plt.tight_layout()

    if save_filename is not None:
        if save_filename == "":
            save_filename = plot_title

        plt.savefig(FIG_PATH + save_filename + ".png", dpi=300)

    plt.show()


def plot_groups_by_other_groups(
    df,
    feature_1,
    feature_2,
    feature_1_order=None,
    feature_2_order=None,
    plot_title=None,
    y_label="",
    x_label="",
    plot_kind="bar",
    color_list=None,
    use_color_list=False,
    y_ticklabel_type=None,
    normalize=False,
):

    df = df[df[feature_1].notna()]
    df = df[df[feature_2].notna()]

    feature_1_types = list(set(df[feature_1].sort_index()))
    feature_2_types = list(set(df[feature_2].sort_index()))

    if feature_1_order is not None:
        feature_1_types = feature_1_order

    feat_bar_dict = {}

    for feat2 in feature_2_types:
        dataset_of_interest = df.loc[df[feature_2] == feat2][feature_1]
        data_of_interest = dataset_of_interest.value_counts()
        feat_bar_dict[feat2] = data_of_interest

    group_by_group = pd.DataFrame(feat_bar_dict, index=feature_1_types)

    if feature_2_order is not None:
        group_by_group = group_by_group[feature_2_order]

    if color_list is None:
        color_list = ["green", "greenyellow", "yellow", "orange", "red"]

    if use_color_list:

        group_by_group.plot(
            kind=plot_kind,
            color=color_list,
            # color=["green", "greenyellow", "yellow", "orange", "red"]
            # color=list("rggkymg"),
        )

    else:

        group_by_group.plot(
            kind=plot_kind,
            # color=color_list,
            # color=["green", "greenyellow", "yellow", "orange", "red"]
            # color=list("rggkymg"),
            cmap="RdYlGn",
        )

    # Change legen order, not used ehre
    # ax = plt.gca()
    # handles, labels = ax.get_legend_handles_labels()
    # handle_label_dict =  {k:v for (k,v) in zip(labels, handles)}
    # new_labels = ['Very Good', 'Good', 'Average', 'Poor', 'Very Poor']
    # new_handles = [handle_label_dict[new_label] for new_label in new_labels]

    ax = plt.gca()

    if y_ticklabel_type == "k":
        division_type = "k"
        division_int = 1000

    elif y_ticklabel_type == "m":
        division_type = "m"
        division_int = 1000000

    elif y_ticklabel_type == "" or y_ticklabel_type is None:
        division_type = ""
        division_int = 1

    elif y_ticklabel_type == "%":
        division_type = "%"
        division_int = 1

    else:
        raise IOError("Invalid value: y_ticklabel has to be '', 'm', or 'k'")

    ylabels = [
        "{:.0f}".format(x / division_int) + division_type for x in ax.get_yticks()
    ]

    ax.set_yticklabels(ylabels)

    if plot_title is None:
        plot_title = feature_2 + " by " + feature_1
        if normalize:
            plot_title += " (%)"

    plt.title(plot_title)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.xticks(rotation=0)

    plt.tight_layout()
    plt.savefig(FIG_PATH + feature_2 + "_by_" + feature_1 + ".png")
    plt.show()


def plot_groups_by_other_groups_2(
    df,
    feature_1,
    feature_2,
    feature_1_order=None,
    feature_2_order=None,
    plot_title=None,
    y_label="",
    x_label="",
    color_list=None,
    y_ticklabel_type=None,
    normalize=False,
):

    df = df[df[feature_1].notna()]
    df = df[df[feature_2].notna()]

    feature_1_types = list(set(df[feature_1].sort_index()))
    feature_2_types = list(set(df[feature_2].sort_index()))

    feature_1 = [
        "MAINHEAT_ENERGY_EFF",
        "HOT_WATER_ENERGY_EFF",
        "FLOOR_ENERGY_EFF",
        "WINDOWS_ENERGY_EFF",
        "WALLS_ENERGY_EFF",
        "ROOF_ENERGY_EFF",
        "MAINHEATC_ENERGY_EFF",
        "LIGHTING_ENERGY_EFF",
    ]

    # if feature_1_order is not None:
    #   feature_1_types = feature_1_order

    feat_bar_dict = {}

    for feat2 in feature_2_types:
        dataset_of_interest = df.loc[df[feature_2] == feat2][feature_1]
        data_of_interest = dataset_of_interest.value_counts()
        feat_bar_dict[feat2] = data_of_interest

    group_by_group = pd.DataFrame(feat_bar_dict, index=feature_1_types)

    # if feature_2_order is not None:
    #    group_by_group = group_by_group[feature_2_order]

    if color_list is None:
        color_list = ["green", "greenyellow", "yellow", "orange", "red"]

    group_by_group.plot(
        kind="bar",
        # color=color_list,
        # color=["green", "greenyellow", "yellow", "orange", "red"]
        # color=list("rggkymg"),
        colormap="Greens_r",
    )

    # Change legen order, not used ehre
    # ax = plt.gca()
    # handles, labels = ax.get_legend_handles_labels()
    # handle_label_dict =  {k:v for (k,v) in zip(labels, handles)}
    # new_labels = ['Very Good', 'Good', 'Average', 'Poor', 'Very Poor']
    # new_handles = [handle_label_dict[new_label] for new_label in new_labels]

    ax = plt.gca()

    if y_ticklabel_type == "k":
        division_type = "k"
        division_int = 1000

    elif y_ticklabel_type == "m":
        division_type = "m"
        division_int = 1000000

    elif y_ticklabel_type == "" or y_ticklabel_type is None:
        division_type = ""
        division_int = 1

    elif y_ticklabel_type == "%":
        division_type = "%"
        division_int = 1

    else:
        raise IOError("Invalid value: y_ticklabel has to be '', 'm', or 'k'")

    ylabels = [
        "{:.0f}".format(x / division_int) + division_type for x in ax.get_yticks()
    ]

    ax.set_yticklabels(ylabels)

    if plot_title is None:
        plot_title = feature_2 + " by " + feature_1
        if normalize:
            plot_title += " (%)"

    plt.title(plot_title)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.xticks(rotation=0)

    plt.tight_layout()
    plt.savefig(FIG_PATH + feature_2 + "_by_" + feature_1 + ".png")
    plt.show()
